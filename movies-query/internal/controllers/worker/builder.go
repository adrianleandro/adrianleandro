package worker

import (
	"github.com/distribuidos-unrust/tp/internal/communication/serialization"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/handler"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/queueinfo"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/service"
	"github.com/spf13/viper"
)

func Build(
	v *viper.Viper,
	queues map[string]*queueinfo.QueueInfo,
	eventHandler handler.EventHandler,
) *Worker {
	log.Debugf("action: build_worker | result: success | queues: %+v", queues)

	serviceName := service.ServiceNameFromString(v.GetString("INBOX_DOMAIN"))
	service := service.NewService(serviceName, service.ServiceID(v.GetInt("ID")))
	state, err := serialization.StateFromFile(service)
	if err != nil {
		log.Criticalf("action: state_from_inbox | result: fail | error: %v", err)
		return nil
	}
	eventHandler.SetState(state)

	handler := handler.NewSimpleHandler(queues, eventHandler)

	if handler == nil {
		log.Criticalf("action: new_actor_handler | result: fail | error: %v", "failed to create actor handler")
		return nil
	}

	config := NewWorkerConfig(
		service,
		handler,
		v.GetString("mom.url"),
	)

	if config == nil {
		log.Criticalf("action: new_worker_config | result: fail | error: %v", "failed to create worker config")
		return nil
	}

	return NewWorker(config)
}
