package selector

import (
	"fmt"

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

type SelectorEventHandler struct {
	outboxAmount  int
	outboxIndexes [][]int
	State         *state.State
}

func (s *SelectorEventHandler) SetState(state *state.State) {
	s.State = state
}

func (s *SelectorEventHandler) GetState() *state.State {
	return s.State
}

func NewSelectorEventHandler(outboxAmount int, outboxIndexes [][]int) *SelectorEventHandler {
	return &SelectorEventHandler{
		outboxAmount:  outboxAmount,
		outboxIndexes: outboxIndexes,
	}
}

func (s *SelectorEventHandler) HandleEvent(
	event broker.Delivery,
	msg *message.Message,
	channel broker.Channel,
	queues map[string]*queueinfo.QueueInfo,
) {
	if eof.IfMustBeSeenByPeersThenSendIt(s.State.Service.ID, msg, channel, queues["INBOX"]) {
		return
	}
	msg.Header.ResetSeen()

	records := serialization.RecordsFromMessage(msg)
	log.Debugf("action: handle_event | result: success | len_records: %v", len(records))

	recordsByQuery := make([][][]string, s.outboxAmount)

	for _, record := range records {
		for i, indexes := range s.outboxIndexes {
			selectedRecord := SelectRecords(indexes, record)
			recordsByQuery[i] = append(recordsByQuery[i], selectedRecord)
		}
	}

	queueErrors := make([]string, 0)
	for i, records := range recordsByQuery {
		selectedMessage := serialization.RecordsIntoMessage(
			records,
			s.State.Service,
			message.MessageID(s.State.Inc()),
			msg.Header.UserID,
			msg.Header.IsLastMessage,
			message.Records,
		)
		selectedMessage.Header.ResetSeen()
		queueName := queues[GetQueueNameAt(i)].NextFromMessage(selectedMessage)
		err := transmission.PublishMessage(channel, queueName, selectedMessage)
		if err != nil {
			log.Errorf("action: publish_message | result: error | queue: %s | error: %v", queueName, err)
			queueErrors = append(queueErrors, queueName)
			continue
		}
		log.Debugf("action: publish_message | result: success | queue: %s | records: %v", queueName, records)
	}

	if len(queueErrors) > 0 {
		log.Errorf("action: publish_message | result: error | queue: %s", queueErrors)
	} else {
		log.Debugf("action: publish_message | result: success | queue: %s", "all queues")
	}
}

func SelectRecords(indexes []int, record []string) []string {
	selectedRecord := make([]string, len(indexes))
	for i, index := range indexes {
		if index < len(record) {
			selectedRecord[i] = record[index]
		}
	}
	return selectedRecord
}

func GetQueueNameAt(i int) string {
	return "OUTBOX_" + fmt.Sprint(i)
}
