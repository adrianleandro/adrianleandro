package union

import (
	"strconv"

	"github.com/distribuidos-unrust/tp/internal/communication/message"
	"github.com/distribuidos-unrust/tp/internal/communication/mom/broker"
	"github.com/distribuidos-unrust/tp/internal/communication/serialization"
	"github.com/distribuidos-unrust/tp/internal/communication/transmission"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/eof"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/queueinfo"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/state"
	"github.com/op/go-logging"
)

var logger = logging.MustGetLogger("log")

type RentabilityHandler struct {
	budgetIndex  int
	revenueIndex int
	State        *state.State
}

func (b *RentabilityHandler) SetState(state *state.State) {
	b.State = state
}

func (b *RentabilityHandler) GetState() *state.State {
	return b.State
}

func NewRentabilityHandler(budgetIndex, revenueIndex int) *RentabilityHandler {
	return &RentabilityHandler{
		budgetIndex:  budgetIndex,
		revenueIndex: revenueIndex,
	}
}

func (b *RentabilityHandler) HandleEvent(
	event broker.Delivery,
	msg *message.Message,
	channel broker.Channel,
	queues map[string]*queueinfo.QueueInfo,
) {
	if eof.IfMustBeSeenByPeersThenSendIt(b.State.Service.ID, msg, channel, queues["INBOX"]) {
		return
	}

	records := serialization.RecordsFromMessage(msg)
	logger.Debugf("action: handle_event | result: success | len_records: %v | records: %v", len(records), records)
	results := make([][]string, 0)

	for i, record := range records {
		if len(record) < b.budgetIndex+1 || len(record) < b.revenueIndex+1 {
			logger.Errorf("action: handle_event | result: error | record: %v", record)
			continue
		}

		budgetStr := record[b.budgetIndex]
		revenueStr := record[b.revenueIndex]

		log.Debugf("action: handle_event | result: success | i: %d | budgetStr: %s | revenueStr: %s", i, budgetStr, revenueStr)
		budget, err := strconv.ParseFloat(budgetStr, 64)
		if err != nil || budget == 0 {
			continue
		}

		revenue, err := strconv.ParseFloat(revenueStr, 64)
		if err != nil || revenue == 0 {
			continue
		}

		ratio := revenue / budget
		ratioStr := strconv.FormatFloat(ratio, 'f', 4, 64)

		record = append(record, ratioStr)
		results = append(results, record)
	}

	log.Debugf("action: handle_event | result: success | processed_records: %v", results)
	rentabilityMsg := serialization.RecordsIntoMessage(
		results,
		b.State.Service,
		message.MessageID(b.State.Inc()),
		msg.Header.UserID,
		msg.Header.IsLastMessage,
		msg.Header.Method,
	)
	rentabilityMsg.Header.ResetSeen()
	transmission.PublishMessage(channel, queues["OUTBOX"].NextFromMessage(rentabilityMsg), rentabilityMsg)
}
