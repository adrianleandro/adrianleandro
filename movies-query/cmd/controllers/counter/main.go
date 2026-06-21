package main

import (
	"github.com/distribuidos-unrust/tp/internal/controllers/counter"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/queueinfo"
	"github.com/distribuidos-unrust/tp/utils"
	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

func IntToBool(value int) bool {
	return value == 1
}

func main() {
	v, _ := utils.InitViperConfig()
	logLevel := v.GetString("log.level")
	if err := utils.InitLogger(logLevel); err != nil {
		log.Fatalf("action: init_logger | result: fail | error: %v", err)
	}

	keyIndex := v.GetInt("KEYINDEX")
	valueIndex := v.GetInt("VALUEINDEX")
	topNumber := v.GetInt("TOP")
	ascending := IntToBool(v.GetInt("ASCENDING"))
	minmax := IntToBool(v.GetInt("MINMAX"))
	kind := v.GetInt("KIND")

	queues := queueinfo.NewFromViper(v, []string{"INBOX", "OUTBOX"})

	eventHandler := counter.NewCounterEventHandler(
		keyIndex,
		valueIndex,
		topNumber,
		ascending,
		minmax,
		counter.Kind(kind),
	)
	worker := worker.Build(v, queues, eventHandler)
	if worker == nil {
		log.Criticalf("action: new_gateway | result: fail | error: %v", "failed to create gateway")
		return
	}
	worker.Run()
}
