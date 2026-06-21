package counter

import (
	"strconv"

	"github.com/distribuidos-unrust/tp/internal/communication/message"
	"github.com/distribuidos-unrust/tp/internal/communication/mom/broker"
	"github.com/distribuidos-unrust/tp/internal/communication/serialization"
	"github.com/distribuidos-unrust/tp/internal/communication/transmission"
	"github.com/distribuidos-unrust/tp/internal/controllers/counter/count"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/eof"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/queueinfo"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/service"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/state"
	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

type CounterEventHandler struct {
	KeyIndex   int
	ValueIndex int
	top        int
	ascending  bool
	minmax     bool
	Kind       Kind
	State      *state.State
}

func (h *CounterEventHandler) SetState(state *state.State) {
	h.State = state
}

func (h *CounterEventHandler) GetState() *state.State {
	return h.State
}

func NewCounterEventHandler(
	keyIndex int,
	valueIndex int,
	top int,
	ascending bool,
	minmax bool,
	Kind Kind,
) *CounterEventHandler {
	return &CounterEventHandler{
		KeyIndex:   keyIndex,
		ValueIndex: valueIndex,
		top:        top,
		ascending:  ascending,
		minmax:     minmax,
		Kind:       Kind,
	}
}

func (h *CounterEventHandler) HandleEvent(
	event broker.Delivery,
	msg *message.Message,
	channel broker.Channel,
	queues map[string]*queueinfo.QueueInfo,
) {
	switch msg.Header.Method {
	case message.Records:
		h.HandleRecords(msg, h.State.Service, event, channel, queues)
	case message.Count:
		h.HandleCount(msg, h.State.Service, event, channel, queues)
	default:
		log.Errorf("action: handle_event | result: error | error: unknown method: %s", msg.Header.Method.String())
	}
}

func (h *CounterEventHandler) HandleRecords(
	msg *message.Message,
	service *service.Service,
	event broker.Delivery,
	channel broker.Channel,
	queues map[string]*queueinfo.QueueInfo,
) {
	records := serialization.RecordsFromMessage(msg)
	userIDStr := msg.Header.UserID.IntoString()
	log.Debugf(
		"action: handle_event | result: success | len_records: %v | userIDStr: %s | records: %+v",
		len(records),
		userIDStr,
		records,
	)

	for _, record := range records {
		if len(record) < (h.KeyIndex + 1) {
			continue
		}

		key := record[h.KeyIndex]
		valueStr := record[h.ValueIndex]
		value, err := strconv.ParseFloat(valueStr, 64)
		if err != nil {
			log.Errorf("action: handle_event | result: error | error: %v", err)
			continue
		}

		h.State.Count.Add(userIDStr, key, value)
	}

	if msg.Header.IsLastMessage {
		countMessage := serialization.MessageFromUserCount(
			msg.Header.UserID,
			h.State.Count.Get(userIDStr),
			service,
			message.MessageID(h.State.Inc()),
		)
		countMessage.Header.Seen++
		transmission.PublishMessage(
			channel,
			queues["INBOX"].NextFrom(h.State.Service.ID),
			countMessage,
		)
	}
}

func (h *CounterEventHandler) HandleCount(
	msg *message.Message,
	service *service.Service,
	event broker.Delivery,
	channel broker.Channel,
	queues map[string]*queueinfo.QueueInfo,
) {
	records := serialization.RecordsFromMessage(msg)
	log.Debugf(
		"action: handle_count | result: success | records: %+v",
		records,
	)
	peerUserCount := serialization.RecordsIntoUserCount(records)
	myUserCount := h.State.Count.Get(msg.Header.UserID.IntoString())

	mergedUserCount := count.NewUserCount()
	mergedUserCount.Merge(peerUserCount)
	mergedUserCount.Merge(myUserCount)

	mergedMessage := serialization.MessageFromUserCount(
		msg.Header.UserID,
		mergedUserCount,
		h.State.Service,
		message.MessageID(h.State.Inc()),
	)

	mergedMessage.Header = msg.Header

	if eof.IfMustBeSeenByPeersThenSendIt(
		h.State.Service.ID,
		mergedMessage,
		channel,
		queues["INBOX"],
	) {
		return
	}

	calculatedRecords := Calculator(
		h.top,
		h.ascending,
		h.minmax,
		h.Kind,
		mergedUserCount,
	)
	log.Debugf(
		"action: handle_event | result: success | calculatedRecords: %+v",
		calculatedRecords,
	)
	countMessage := serialization.RecordsIntoMessage(
		calculatedRecords,
		h.State.Service,
		message.MessageID(h.State.Inc()),
		msg.Header.UserID,
		msg.Header.IsLastMessage,
		message.Records,
	)
	transmission.PublishMessage(
		channel,
		queues["OUTBOX"].NextFromMessage(countMessage),
		countMessage,
	)
}
