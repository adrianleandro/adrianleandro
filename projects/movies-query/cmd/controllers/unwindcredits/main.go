package main

import (
	"github.com/distribuidos-unrust/tp/internal/controllers/unwind"
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

	castIndex := v.GetInt("CAST_INDEX")
	idIndex := v.GetInt("MOVIE_INDEX")

	queues := map[string]*queueinfo.QueueInfo{
		"INBOX":  queueinfo.NewQueueInfo(v.GetString("INBOX_DOMAIN"), v.GetInt("INBOX_AMOUNT")),
		"OUTBOX": queueinfo.NewQueueInfo(v.GetString("OUTBOX_DOMAIN"), v.GetInt("OUTBOX_AMOUNT")),
	}

	eventHandler := unwind.NewUnwindCreditsHandler(castIndex, idIndex)
	worker := worker.Build(v, queues, eventHandler)
	if worker == nil {
		log.Criticalf("action: new_gateway | result: fail | error: %v", "failed to create gateway")
		return
	}
	worker.Run()
}
