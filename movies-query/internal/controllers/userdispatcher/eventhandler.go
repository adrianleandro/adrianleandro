package userdispatcher

import (
	"github.com/distribuidos-unrust/tp/internal/communication/message"
	"github.com/distribuidos-unrust/tp/internal/communication/mom/broker"
	"github.com/distribuidos-unrust/tp/internal/communication/serialization"
	"github.com/distribuidos-unrust/tp/internal/communication/transmission"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/queueinfo"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/state"
	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

type UserDispatcherEventHandler struct {
	prefix string
	State  *state.State
}

func (h *UserDispatcherEventHandler) SetState(state *state.State) {
	h.State = state
}

func (h *UserDispatcherEventHandler) GetState() *state.State {
	return h.State
}

func NewUserDispatcherEventHandler(prefix string) *UserDispatcherEventHandler {
	return &UserDispatcherEventHandler{prefix: prefix}
}

func (h *UserDispatcherEventHandler) HandleEvent(
	event broker.Delivery,
	msg *message.Message,
	channel broker.Channel,
	queues map[string]*queueinfo.QueueInfo,
) {
	ID := h.State.Service.ID

	queueName := h.prefix + "_" + msg.Header.UserID.IntoString()
	_, err := channel.QueueDeclare(queueName)
	if err != nil {
		log.Errorf("action: handle_event | result: error | error: %v", err)
		return
	}

	inbox, err := channel.ConsumeFromQueue(queueName)
	if err != nil {
		log.Errorf("action: handle_event | result: error | error: %v", err)
		return
	}

	for {
		e := <-inbox
		msg, err := serialization.MessageFromEvent(e)
		if err != nil {
			log.Errorf("action: handle_event | result: error | error: %v", err)
			continue
		}
		records := serialization.RecordsFromMessage(msg)
		msg.Header.ResetSeen()
		msg.Header.Method = message.Join
		queueName := queues["OUTBOX"].NextFromMessage(msg)
		log.Debugf(
			"action: handle_event | result: success | ID: %d | userID: %s | records: %v | queueName: %s | isLastMessage: %t",
			ID,
			msg.Header.UserID.IntoString(),
			records,
			queueName,
			msg.Header.IsLastMessage,
		)
		transmission.PublishMessage(channel, queueName, msg)

		if msg.Header.IsLastMessage {
			break
		}
	}

	msgCount, err := channel.QueueDelete(queueName)
	if err != nil {
		log.Errorf("action: handle_event | result: error | error: %v | msgCount: %d", err, msgCount)
		return
	}

	log.Debugf("action: handle_event | result: success | all events handled")
}
