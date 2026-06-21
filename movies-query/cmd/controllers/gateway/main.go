package main

import (
	"github.com/distribuidos-unrust/tp/internal/controllers/gateway"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/queueinfo"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/service"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/state"
	"github.com/distribuidos-unrust/tp/utils"
	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

func main() {
	v, _ := utils.InitViperConfig()
	logLevel := v.GetString("log.level")
	if err := utils.InitLogger(logLevel); err != nil {
		log.Fatalf("action: init_logger | result: fail | error: %v", err)
	}

	queues := queueinfo.NewFromViper(
		v,
		[]string{"CREDITS", "MOVIES", "RATINGS"},
	)

	domain := v.GetString("gateway.domain")
	port := v.GetString("gateway.port")
	id := v.GetString("ID")
	address := domain + "_" + id + ":" + port

	handler := gateway.NewGatewayHandler(
		address,
		v.GetInt("gateway.maxRequestHandlers"),
		queues,
		v.GetInt("RESULTS_AMOUNT"),
	)

	if handler == nil {
		log.Criticalf("action: new_actor_handler | result: fail | error: %v", "failed to create actor handler")
		return
	}

	service := service.NewService(
		service.ServiceNameFromString(v.GetString("INBOX_DOMAIN")),
		service.ServiceID(v.GetInt("ID")),
	)

	state := state.NewState(service)
	handler.SetState(state)

	config := worker.NewWorkerConfig(
		service,
		handler,
		v.GetString("mom.url"),
	)

	worker := worker.NewWorker(config)

	if worker == nil {
		log.Criticalf("action: new_gateway | result: fail | error: %v", "failed to create gateway")
		return
	}
	worker.Run()
}
