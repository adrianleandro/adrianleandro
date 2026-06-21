package rabbitmq

import (
	"github.com/distribuidos-unrust/tp/internal/communication/mom/broker"
	"github.com/rabbitmq/amqp091-go"
)

type Broker struct {
}

func NewBroker() *Broker {
	return &Broker{}
}

func (b *Broker) Dial(url string) (broker.Connection, error) {
	conn, err := amqp091.Dial(url)
	if err != nil {
		return nil, err
	}
	return NewConnection(conn), nil
}
