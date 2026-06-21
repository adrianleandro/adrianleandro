package handler

import (
	"github.com/distribuidos-unrust/tp/internal/communication/message"
	"github.com/distribuidos-unrust/tp/internal/communication/mom/broker"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/queueinfo"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/state"
)

type EventHandler interface {
	HandleEvent(
		event broker.Delivery,
		msg *message.Message,
		channel broker.Channel,
		queues map[string]*queueinfo.QueueInfo,
	)

	SetState(state *state.State)
	GetState() *state.State
}
