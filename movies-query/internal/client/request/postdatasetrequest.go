package request

import (
	"github.com/distribuidos-unrust/tp/internal/client/routes"
	"github.com/distribuidos-unrust/tp/internal/communication/message"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/service"
)

type PostDatasetRequest struct {
	userID         *message.ID
	method         message.Method
	gatewayAddress string
	datasetPath    string
	batchSize      int
	service        *service.Service
}

func NewPostDatasetRequest(
	userID *message.ID,
	method message.Method,
	gatewayAddress string,
	datasetPath string,
	batchSize int,
	service *service.Service,
) *PostDatasetRequest {
	return &PostDatasetRequest{
		userID:         userID,
		method:         method,
		gatewayAddress: gatewayAddress,
		datasetPath:    datasetPath,
		batchSize:      batchSize,
		service:        service,
	}
}

func (r *PostDatasetRequest) Run(response chan error) {
	go routes.PostDataset(
		r.userID,
		response,
		r.method,
		r.gatewayAddress,
		r.datasetPath,
		r.batchSize,
		r.service,
	)
}
