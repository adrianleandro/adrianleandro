package result

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

type ResultEventHandler struct {
	results     [][]string
	queryNumber int
	State       *state.State
}

func (f *ResultEventHandler) SetState(state *state.State) {
	f.State = state
}

func (f *ResultEventHandler) GetState() *state.State {
	return f.State
}

func NewResultEventHandler(queryNumber int) *ResultEventHandler {
	if queryNumber < 1 {
		log.Errorf("action: new_result_event_handler | result: error | error: invalid query number")
		return nil
	}
	return &ResultEventHandler{
		results:     make([][]string, 0),
		queryNumber: queryNumber,
	}
}

func (f *ResultEventHandler) HandleEvent(
	event broker.Delivery,
	msg *message.Message,
	channel broker.Channel,
	queues map[string]*queueinfo.QueueInfo,
) {
	if eof.IfMustBeSeenByPeersThenSendIt(f.State.Service.ID, msg, channel, queues["INBOX"]) {
		return
	}

	userQueue := "user_" + msg.Header.UserID.IntoString()
	records := serialization.RecordsFromMessage(msg)

	if len(records) == 0 && !msg.Header.IsLastMessage {
		log.Debugf("action: handle_event | result: skip | reason: no records and no EOF")
		return
	}

	queryMethod := f.GetQueryMethod()
	msg.Header.Method = queryMethod

	_, err := channel.QueueDeclare(userQueue)
	if err != nil {
		log.Errorf("action: handle_event | result: error | error: %v", err)
		return
	}

	log.Debugf(
		"action: handle_event | result: success | userQueue: %v | len_records: %v",
		userQueue,
		len(records),
	)

	transmission.PublishMessage(channel, userQueue, msg)
}

func (f *ResultEventHandler) GetQueryMethod() message.Method {
	switch f.queryNumber {
	case 1:
		return message.ResultQuery1
	case 2:
		return message.ResultQuery2
	case 3:
		return message.ResultQuery3
	case 4:
		return message.ResultQuery4
	case 5:
		return message.ResultQuery5
	default:
		log.Errorf("action: get_query_method | result: error | error: invalid query number")
		return message.ErrorMethod
	}
}
