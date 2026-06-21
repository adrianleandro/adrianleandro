package joiner

import (
	"github.com/distribuidos-unrust/tp/internal/communication/message"
	"github.com/distribuidos-unrust/tp/internal/communication/mom/broker"
	"github.com/distribuidos-unrust/tp/internal/communication/serialization"
	"github.com/distribuidos-unrust/tp/internal/communication/transmission"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/eof"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/queueinfo"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/state"
	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

type JoinerEventHandler struct {
	LeftIndex  int
	RightIndex int
	State      *state.State
}

func (e *JoinerEventHandler) SetState(state *state.State) {
	e.State = state
}

func (e *JoinerEventHandler) GetState() *state.State {
	return e.State
}

func NewJoinerEventHandler(leftIndex int, rightIndex int) *JoinerEventHandler {
	return &JoinerEventHandler{
		LeftIndex:  leftIndex,
		RightIndex: rightIndex,
	}
}

func (e *JoinerEventHandler) HandleEvent(
	event broker.Delivery,
	msg *message.Message,
	channel broker.Channel,
	queues map[string]*queueinfo.QueueInfo,
) {
	switch msg.Header.Method {
	case message.Records:
		e.HandleRecords(msg, event, channel, queues)
	case message.Join:
		e.HandleJoin(msg, event, channel, queues)
	default:
		log.Debugf("action: handle_event | result: error | error: unknown method %d", msg.Header.Method)
	}
}

func (h *JoinerEventHandler) HandleRecords(
	msg *message.Message,
	event broker.Delivery,
	channel broker.Channel,
	queues map[string]*queueinfo.QueueInfo,
) {
	records := serialization.RecordsFromMessage(msg)
	userID := msg.Header.UserID
	log.Debugf("action: handle_event | result: success | ID: %d | userID: %s | records: %v", h.State.Service.ID, msg.Header.UserID.IntoString(), records)

	msg.Header.ResetSeen()

	for _, record := range records {
		log.Debugf("action: handle_records | result: success | record: %v", record)
		key := record[h.LeftIndex]
		if _, ok := h.State.UserRecords[userID.IntoString()]; !ok {
			h.State.UserRecords[userID.IntoString()] = make(map[string][]string)
		}
		h.State.UserRecords[userID.IntoString()][key] = record
	}

	if msg.Header.IsLastMessage {
		msg := message.NewMethodMessage(
			message.Join,
			h.State.Service,
			message.MessageID(h.State.Inc()),
			userID,
		)
		queueName := queues["DISPATCHER"].NextFromMessage(msg)
		log.Debugf("action: handle_records | result: success | sending join message to dispatcher | ID: %d | queueName: %s", h.State.Service.ID, queueName)
		transmission.PublishMessage(channel, queueName, msg)
	}
}

func (h *JoinerEventHandler) HandleJoin(
	msg *message.Message,
	event broker.Delivery,
	channel broker.Channel,
	queues map[string]*queueinfo.QueueInfo,
) {
	records := serialization.RecordsFromMessage(msg)
	log.Debugf(
		"action: handle_join | result: success | ID: %d | userID: %s | records: %v | isLastMessage: %t",
		h.State.Service.ID,
		msg.Header.UserID.IntoString(),
		records,
		msg.Header.IsLastMessage,
	)

	joinedRecords := make([][]string, 0)
	for _, record := range records {
		if len(record) <= h.RightIndex {
			log.Warningf("action: handle_join | result: skip | reason: not enough fields")
			continue
		}
		key := record[h.RightIndex]
		newValues := h.State.UserRecords[msg.Header.UserID.IntoString()][key]

		if len(newValues) == 0 {
			//log.Warningf("action: handle_join | result: skip | reason: no matching record found")
			continue
		}

		record = append(record, newValues...)
		joinedRecords = append(joinedRecords, record)
		log.Debugf(
			"action: handle_join | result: success | key: %v | record: %v | newValues: %v | joinedRecord: %v",
			key,
			record,
			newValues,
			joinedRecords,
		)
	}

	joinedMessage := serialization.RecordsIntoMessage(
		joinedRecords,
		h.State.Service,
		message.MessageID(h.State.Inc()),
		msg.Header.UserID,
		false,
		message.Records,
	)

	if len(joinedRecords) == 0 && (!msg.Header.IsLastMessage) {
		log.Debugf("action: handle_join | result: skip | reason: no joined records and not last message")
		return
	}

	queueName := queues["OUTBOX"].NextFromMessage(joinedMessage)
	log.Debugf(
		"action: handle_join | result: success | ID: %d | userID: %s | records: %v | queueName: %s | length: %d",
		h.State.Service.ID,
		msg.Header.UserID.IntoString(),
		joinedRecords,
		queueName,
		len(joinedRecords),
	)
	transmission.PublishMessage(channel, queueName, joinedMessage)

	emptyMessage := serialization.RecordsIntoMessage(
		[][]string{},
		h.State.Service,
		message.MessageID(h.State.Inc()),
		msg.Header.UserID,
		msg.Header.IsLastMessage,
		message.Records,
	)

	if eof.MustBeSeenByPeers(msg, queues["INBOX"]) {
		log.Debugf(
			"action: handle_event | result: success | forwarding message to peers | ID: %d | seen: %d | amount: %d | next: %s",
			h.State.Service.ID,
			msg.Header.Seen,
			queues["INBOX"].Amount,
			queues["INBOX"].NextFrom(h.State.Service.ID),
		)
		eof.IncAndSendToNextPeers(h.State.Service.ID, msg, channel, queues["INBOX"])
		return
	}

	queueName = queues["OUTBOX"].NextFromMessage(emptyMessage)
	emptyMessage.Header.Method = message.Records
	log.Debugf(
		"action: handle_join | result: success | ID: %d | userID: %s | sending empty message to outbox | queueName: %s | method: %s",
		h.State.Service.ID,
		msg.Header.UserID.IntoString(),
		queueName,
		emptyMessage.Header.Method.String(),
	)
	emptyMessage.Header.ResetSeen()
	transmission.PublishMessage(channel, queueName, emptyMessage)
}
