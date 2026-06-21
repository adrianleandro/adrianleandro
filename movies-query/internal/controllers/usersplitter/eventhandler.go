package usersplitter

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

type UserSplitterEventHandler struct {
	prefix string
	State  *state.State
}

func (h *UserSplitterEventHandler) SetState(state *state.State) {
	h.State = state
}

func (h *UserSplitterEventHandler) GetState() *state.State {
	return h.State
}

func NewUserSplitterEventHandler(prefix string) *UserSplitterEventHandler {
	return &UserSplitterEventHandler{prefix: prefix}
}

func (h *UserSplitterEventHandler) HandleEvent(
	event broker.Delivery,
	msg *message.Message,
	channel broker.Channel,
	queues map[string]*queueinfo.QueueInfo,
) {
	ID := h.State.Service.ID

	if eof.MustBeSeenByPeers(msg, queues["INBOX"]) {
		log.Debugf(
			"action: handle_event | result: success | forwarding message to peers | ID: %d | seen: %d | amount: %d | next: %s",
			ID,
			msg.Header.Seen,
			queues["INBOX"].Amount,
			queues["INBOX"].NextFrom(ID),
		)
		eof.IncAndSendToNextPeers(ID, msg, channel, queues["INBOX"])
		return
	}
	msg.Header.ResetSeen()

	queueName := h.prefix + "_" + msg.Header.UserID.IntoString()
	_, err := channel.QueueDeclare(queueName)
	if err != nil {
		log.Errorf("action: handle_event | result: error | error: %v", err)
		return
	}

	records := serialization.RecordsFromMessage(msg)
	log.Debugf("action: handle_event | result: success | ID: %d | userID: %s | records: %v", ID, msg.Header.UserID.IntoString(), records)

	err = transmission.PublishMessage(channel, queueName, msg)
	if err != nil {
		log.Errorf("action: handle_event | result: error | error: %v", err)
		return
	}
}
