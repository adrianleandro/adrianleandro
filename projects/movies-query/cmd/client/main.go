package main

import (
	"strconv"

	"github.com/distribuidos-unrust/tp/internal/client"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/service"
	"github.com/distribuidos-unrust/tp/utils"
	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

func main() {
	v, _ := utils.InitViperConfig()
	logLevel := v.GetString("log.level")
	if err := utils.InitLogger(logLevel); err != nil {
		log.Fatalf("Failed to initialize logger: %v", err)
	}
	log.Infof("Config file: %s", v.ConfigFileUsed())

	gatewayDomain := v.GetString("OUTBOX_DOMAIN")
	gatewayAmount := v.GetInt("OUTBOX_AMOUNT")
	port := v.GetString("gateway.port")
	id := v.GetInt("ID")

	gatewayID := id % gatewayAmount
	gatewayAddress := gatewayDomain + "_" + strconv.Itoa(gatewayID) + ":" + port

	clientConfig := client.NewClientConfig(
		gatewayAddress,
		v.GetString("client.credits"),
		v.GetString("client.movies"),
		v.GetString("client.ratings"),
		v.GetInt("client.batchSize"),
		v.GetInt("RESULTS_AMOUNT"),
		service.ServiceID(v.GetInt("ID")),
	)

	client := client.NewClient(clientConfig)
	client.Run()
}
