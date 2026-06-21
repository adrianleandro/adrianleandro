package client

import (
	"fmt"

	"github.com/distribuidos-unrust/tp/internal/client/request"
	"github.com/distribuidos-unrust/tp/internal/client/routes"
	"github.com/distribuidos-unrust/tp/internal/communication/message"
	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

type Client struct {
	config *ClientConfig
}

func NewClient(clientConfig *ClientConfig) *Client {
	return &Client{
		config: clientConfig,
	}
}

func (c *Client) Run() {
	retry := uint32(100)

	getIdChannel := make(chan *message.ID)
	go routes.GetId(getIdChannel, c.config.gatewayAddress, c.config.service)
	userID := <-getIdChannel

	err := c.PostDatasets(retry, userID)
	if err != nil {
		log.Errorf("action: post_datasets | result: error | error: %v", err)
		return
	}

	resultChannel := make(chan bool)
	go routes.GetResults(
		userID,
		resultChannel,
		c.config.gatewayAddress,
		c.config.result,
		c.config.service,
	)

	<-resultChannel
	log.Infof("action: run | result: success | exit")
}

func (c *Client) PostDatasets(retry uint32, userID *message.ID) error {
	methods := []message.Method{
		message.PostCredits,
		message.PostMovies,
		message.PostRatings,
	}
	paths := []string{
		c.config.creditsPath,
		c.config.moviesPath,
		c.config.ratingsPath,
	}

	responses := make([]chan error, 0)
	for i, method := range methods {
		response := make(chan error)
		responses = append(responses, response)
		postDataRequest := request.NewPostDatasetRequest(
			userID,
			method,
			c.config.gatewayAddress,
			paths[i],
			c.config.batchSize,
			c.config.service,
		)
		go request.Retry(retry, postDataRequest, response)
	}

	acum := make([]error, 0)
	for i, response := range responses {
		err := <-response
		if err != nil {
			log.Errorf("action: post_datasets | result: error | method: %s | error: %v", methods[i].String(), err)
			acum = append(acum, err)
		} else {
			log.Infof("action: post_datasets | result: success")
		}
	}

	if len(acum) > 0 {
		log.Errorf("action: post_datasets | result: error | errors: %v", acum)
		return fmt.Errorf("failed to post datasets: %v", acum)
	}
	return nil
}
