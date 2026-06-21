package eof

import (
	"github.com/distribuidos-unrust/tp/internal/communication/message"
	"github.com/distribuidos-unrust/tp/internal/communication/mom/broker"
	"github.com/distribuidos-unrust/tp/internal/communication/transmission"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/queueinfo"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/service"
	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

func MustBeSeenByPeers(
	message *message.Message,
	peers *queueinfo.QueueInfo,
) bool {
	return message.Header.IsLastMessage && (!message.Header.HasBeenSeenByEveryone(uint32(peers.Amount)))
}

func IncAndSendToNextPeers(
	ID service.ServiceID,
	message *message.Message,
	channel broker.Channel,
	peers *queueinfo.QueueInfo,
) {
	nextPeerQueue := peers.NextFrom(ID)
	message.Header.IncSeen()
	transmission.PublishMessage(channel, nextPeerQueue, message)
}

func IfMustBeSeenByPeersThenSendIt(
	ID service.ServiceID,
	message *message.Message,
	channel broker.Channel,
	peersQueue *queueinfo.QueueInfo,
) bool {
	if MustBeSeenByPeers(message, peersQueue) {
		log.Debugf(
			"action: handle_event | result: success | forwarding message to peers | ID: %d | seen: %d | amount: %d | next: %s",
			ID,
			message.Header.Seen,
			peersQueue.Amount,
			peersQueue.NextFrom(ID),
		)
		IncAndSendToNextPeers(ID, message, channel, peersQueue)
		return true
	}
	return false
}
