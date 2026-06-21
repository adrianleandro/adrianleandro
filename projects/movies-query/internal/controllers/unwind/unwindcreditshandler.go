package unwind

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

type CreditsHandler struct {
	castIndex int
	idIndex   int
	State     *state.State
}

func (h *CreditsHandler) SetState(state *state.State) {
	h.State = state
}

func (h *CreditsHandler) GetState() *state.State {
	return h.State
}

func NewUnwindCreditsHandler(castIndex, idIndex int) *CreditsHandler {
	return &CreditsHandler{
		castIndex: castIndex,
		idIndex:   idIndex,
	}
}

func (h *CreditsHandler) HandleEvent(
	event broker.Delivery,
	msg *message.Message,
	channel broker.Channel,
	queues map[string]*queueinfo.QueueInfo,
) {
	if eof.IfMustBeSeenByPeersThenSendIt(h.State.Service.ID, msg, channel, queues["INBOX"]) {
		return
	}

	msg.Header.ResetSeen()
	records := serialization.RecordsFromMessage(msg)

	results := make([][]string, 0)
	for _, record := range records {
		if len(record) <= h.castIndex || len(record) <= h.idIndex {
			log.Warningf("action: handle_event | result: skip | reason: not enough fields")
			continue
		}
		castMembers, err := serialization.CastMembersFromString(record[h.castIndex])
		if err != nil {
			log.Warningf("action: handle_event | result: skip | reason: %v", err)
			continue
		}

		for _, castMember := range castMembers {
			result := []string{
				record[h.idIndex],
				castMember.Name,
				"1",
			}
			results = append(results, result)
		}
	}

	log.Debugf("action: handle_event | result: success | actor: %v", results)

	filteredMessage := serialization.RecordsIntoMessage(
		results,
		h.State.Service,
		message.MessageID(h.State.Inc()),
		msg.Header.UserID,
		msg.Header.IsLastMessage,
		msg.Header.Method,
	)

	queueName := queues["OUTBOX"].NextFromMessage(filteredMessage)
	log.Debugf(
		"action: handle_event | result: success | queueName: %s | isLastMessage: %v",
		queueName,
		filteredMessage.Header.IsLastMessage,
	)

	transmission.PublishMessage(channel, queueName, filteredMessage)
}
