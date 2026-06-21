package worker

import (
	"github.com/distribuidos-unrust/tp/internal/communication/mom/broker"
	"github.com/distribuidos-unrust/tp/internal/communication/mom/rabbitmq"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/handler"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/service"
)

type WorkerConfig struct {
	Service       *service.Service
	Handler       handler.Handler
	MomConnection broker.Connection
	MomChannel    broker.Channel
}

func NewWorkerConfig(
	service *service.Service,
	handler handler.Handler,
	momURL string,
) *WorkerConfig {
	broker := rabbitmq.NewBroker()
	connection, err := broker.Dial(momURL)
	if err != nil {
		log.Criticalf("action: dial | result: fail | error: %v", err)
		return nil
	}
	channel, err := connection.Channel()
	if err != nil {
		log.Criticalf("action: channel | result: fail | error: %v", err)
		connection.Close()
		return nil
	}

	return &WorkerConfig{
		Service:       service,
		Handler:       handler,
		MomConnection: connection,
		MomChannel:    channel,
	}
}

func (w *WorkerConfig) Close() {
	if err := w.MomChannel.Close(); err != nil {
		log.Errorf("action: close_channel | result: fail | error: %v", err)
	}
	if err := w.MomConnection.Close(); err != nil {
		log.Errorf("action: close_connection | result: fail | error: %v", err)
	}
}
