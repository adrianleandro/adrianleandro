package year

import (
	"time"

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

type Comparer string

const EQUAL Comparer = "EQUAL"
const GREATER Comparer = "GREATER"
const LESSER Comparer = "LESSER"

type YearHandler struct {
	Index    int
	Comparer Comparer
	Value    time.Time
	State    *state.State
}

func (f *YearHandler) SetState(state *state.State) {
	f.State = state
}

func (f *YearHandler) GetState() *state.State {
	return f.State
}

func NewYearHandler(index int, comparer Comparer, value string) *YearHandler {
	parsedValue, err := time.Parse("2006-01-02", value)
	if err != nil {
		log.Errorf("action: new_year_handler | result: error | error: %v", err)
		return nil
	}

	return &YearHandler{
		Index:    index,
		Comparer: comparer,
		Value:    parsedValue,
		State:    nil,
	}
}

func (f *YearHandler) HandleEvent(
	event broker.Delivery,
	msg *message.Message,
	channel broker.Channel,
	queues map[string]*queueinfo.QueueInfo,
) {
	if eof.IfMustBeSeenByPeersThenSendIt(f.State.Service.ID, msg, channel, queues["INBOX"]) {
		return
	}

	msg.Header.ResetSeen()

	records := serialization.RecordsFromMessage(msg)

	filteredRecords := make([][]string, 0)
	for _, record := range records {
		x := record[f.Index]
		date, err := time.Parse("2006-01-02", x)
		if err != nil {
			log.Errorf("action: handle_event | result: error | error: %v | string: %s", err, x)
			continue
		}
		if f.CompareAgainsFilter(date) {
			filteredRecords = append(filteredRecords, record)
		}
	}

	log.Debugf("action: handle_event | result: success | filtered records: %v", filteredRecords)
	filteredMessage := serialization.RecordsIntoMessage(
		filteredRecords,
		f.State.Service,
		message.MessageID(f.State.Inc()),
		msg.Header.UserID,
		msg.Header.IsLastMessage,
		message.Records,
	)

	if len(filteredRecords) == 0 && !filteredMessage.Header.IsLastMessage {
		log.Debugf("action: handle_event | result: skip | reason: no records and no EOF")
		return
	}

	queueName := queues["OUTBOX"].NextFromMessage(filteredMessage)
	log.Debugf(
		"action: handle_event | result: success | queueName: %s | isLastMessage: %v",
		queueName,
		filteredMessage.Header.IsLastMessage,
	)
	transmission.PublishMessage(channel, queueName, filteredMessage)
}

func (f *YearHandler) CompareAgainsFilter(x time.Time) bool {

	switch f.Comparer {
	case EQUAL:
		return x == f.Value
	case GREATER:
		return x.After(f.Value)
	case LESSER:
		return x.Before(f.Value)
	default:
		log.Errorf("action: compare | result: error | error: %v", "invalid comparer")
		return false
	}
}
