package main

import (
	"github.com/distribuidos-unrust/tp/internal/controllers/filters/prodcountry"
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

	index := v.GetInt("INDEX")
	country := v.GetString("COUNTRY")
	comparer := prodcountry.NewContainsCountryComparer(country)
	eventHandler := prodcountry.NewProdCountryHandler(index, comparer)

	queues := queueinfo.NewFromViper(v, []string{"INBOX", "OUTBOX"})

	worker := worker.Build(v, queues, eventHandler)
	if worker == nil {
		log.Criticalf("action: new_gateway | result: fail | error: %v", "failed to create gateway")
		return
	}
	worker.Run()
}
