package client

import (
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/service"
)

type ClientConfig struct {
	gatewayAddress string
	creditsPath    string
	moviesPath     string
	ratingsPath    string
	batchSize      int
	result         int
	service        *service.Service
}

func NewClientConfig(
	gatewayAddress string,
	creditsPath string,
	moviesPath string,
	ratingsPath string,
	batchSize int,
	results int,
	ID service.ServiceID,
) *ClientConfig {
	return &ClientConfig{
		gatewayAddress: gatewayAddress,
		creditsPath:    creditsPath,
		moviesPath:     moviesPath,
		ratingsPath:    ratingsPath,
		batchSize:      batchSize,
		result:         results,
		service:        service.NewService(service.Client, ID),
	}
}
