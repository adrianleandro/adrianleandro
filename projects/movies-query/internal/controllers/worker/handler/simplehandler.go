package handler

import (
	"github.com/distribuidos-unrust/tp/internal/communication/mom/broker"
	"github.com/distribuidos-unrust/tp/internal/communication/serialization"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/queueinfo"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/service"
	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

const INBOX = "INBOX"

type SimpleHandler struct {
	eventHandler EventHandler
	queues       map[string]*queueinfo.QueueInfo
	done         chan bool
	quit         chan bool
	keepRunning  bool
}

func NewSimpleHandler(queues map[string]*queueinfo.QueueInfo, eventHandler EventHandler) *SimpleHandler {
	return &SimpleHandler{
		eventHandler: eventHandler,
		queues:       queues,
		done:         make(chan bool),
		quit:         make(chan bool),
		keepRunning:  true,
	}
}

func (f *SimpleHandler) Handle(ID service.ServiceID, channel broker.Channel) {
	err := queueinfo.DeclareQueuesFromMap(channel, f.queues)
	if err != nil {
		log.Errorf("action: declare_queue | result: error | error: %v", err)
		f.done <- false
		return
	}

	inbox, err := channel.ConsumeFromQueue(f.queues[INBOX].Current(uint32(ID)))
	if err != nil {
		log.Errorf("action: consume | result: error | error: %v", err)
		f.done <- false
		return
	}

	for f.keepRunning {
		select {
		case event := <-inbox:
			f.HandleEvent(event, channel)
		case <-f.quit:
			log.Debugf("action: quit | result: success")
			f.keepRunning = false
		}
	}

	log.Debugf("action: handle_event | result: success | all events handled")
	f.done <- true
}

func (f *SimpleHandler) Quit() {
	log.Debugf("action: quit | result: success")
	f.quit <- true
}

func (f *SimpleHandler) GetDoneQueue() chan bool {
	return f.done
}

func (f *SimpleHandler) HandleEvent(
	event broker.Delivery,
	channel broker.Channel,
) {
	msg, err := serialization.MessageFromEvent(event)
	if err != nil {
		log.Errorf("action: handle_event | result: error | error: %v", err)
		event.Nack(false, false)
		return
	}

	state := f.eventHandler.GetState()
	if state.MessageHasBeenSeen(msg) {
		log.Debugf("action: handle_event | result: skip | reason: message already seen")
		event.Nack(false, false)
		return
	}

	f.eventHandler.HandleEvent(event, msg, channel, f.queues)

	state.Ack(msg)
	log.Debugf(
		"action: ack event | result: success | method: %s | userID: %s | messageID: %d | source: %s",
		msg.Header.Method.String(),
		msg.Header.UserID.IntoString(),
		msg.Header.MessageID,
		msg.Header.Source.String(),
	)

	err = serialization.StateIntoFile(state)
	if err != nil {
		log.Errorf("action: handle_event | result: error | error: %v", err)
	}
	log.Debugf(
		"action: saved state | result: success | method: %s | userID: %s | messageID: %d | source: %s",
		msg.Header.Method.String(),
		msg.Header.UserID.IntoString(),
		msg.Header.MessageID,
		msg.Header.Source.String(),
	)

	event.Ack(true)
	//time.Sleep(1 * time.Second)
}
