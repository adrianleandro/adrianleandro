package main

import (
	"github.com/distribuidos-unrust/tp/internal/controllers/usersplitter"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/queueinfo"
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

	prefix := v.GetString("PREFIX")
	queues := queueinfo.NewFromViper(v, []string{"INBOX"})

	eventHandler := usersplitter.NewUserSplitterEventHandler(prefix)
	worker := worker.Build(v, queues, eventHandler)
	if worker == nil {
		log.Criticalf("action: worker | result: fail | error: %v", "failed to create gateway")
		return
	}
	worker.Run()
}
