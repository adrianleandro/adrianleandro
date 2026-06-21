package rabbitmq

import "github.com/rabbitmq/amqp091-go"

type Delivery struct {
	delivery amqp091.Delivery
}

func NewDelivery(delivery amqp091.Delivery) *Delivery {
	return &Delivery{delivery: delivery}
}

func (d *Delivery) GetBody() []byte {
	return d.delivery.Body
}

func (d *Delivery) Ack(multiple bool) error {
	return d.delivery.Ack(multiple)
}

func (d *Delivery) Nack(multiple bool, requeue bool) error {
	return d.delivery.Nack(multiple, requeue)
}
