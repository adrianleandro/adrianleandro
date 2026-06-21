package main

import (
	"encoding/json"
	"fmt"

	"github.com/distribuidos-unrust/tp/internal/controllers/selector"
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

	outboxAmount := v.GetInt("OUTBOXES_AMOUNT")
	log.Debugf("action: selector | result: success | outbox_amount: %d", outboxAmount)

	queueNames := make([]string, outboxAmount)
	indexes := make([][]int, outboxAmount)
	for i := range outboxAmount {
		queueNames[i] = "OUTBOX_" + fmt.Sprint(i)
		indexesStr := v.GetString(queueNames[i] + "_INDEXES")
		json.Unmarshal([]byte(indexesStr), &indexes[i])
		log.Debugf(
			"action: selector | result: success | queue: %s | indexes: %v | indexes_str: %s",
			queueNames[i],
			indexes[i],
			indexesStr,
		)
	}

	queueNames = append(queueNames, "INBOX")
	queues := queueinfo.NewFromViper(v, queueNames)

	eventHandler := selector.NewSelectorEventHandler(outboxAmount, indexes)
	worker := worker.Build(v, queues, eventHandler)
	if worker == nil {
		log.Criticalf("action: new_gateway | result: fail | error: %v", "failed to create gateway")
		return
	}
	worker.Run()
}
