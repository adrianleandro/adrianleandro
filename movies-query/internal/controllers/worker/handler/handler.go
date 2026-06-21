package handler

import (
	"github.com/distribuidos-unrust/tp/internal/communication/mom/broker"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/service"
)

type Handler interface {
	Handle(ID service.ServiceID, momChannel broker.Channel)
	GetDoneQueue() chan bool
	Quit()
}
