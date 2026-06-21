package rabbitmq

import (
	"sync"

	"github.com/distribuidos-unrust/tp/internal/communication/mom/broker"
	"github.com/rabbitmq/amqp091-go"
)

type Channel struct {
	mu sync.Mutex
	ch *amqp091.Channel
}

func NewChannel(ch *amqp091.Channel) *Channel {
	return &Channel{
		ch: ch,
	}
}

func (c *Channel) QueueDeclare(queueName string) (broker.Queue, error) {
	c.mu.Lock()
	defer c.mu.Unlock()

	queue, err := c.ch.QueueDeclare(
		queueName,
		false,
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		return nil, err
	}

	return NewQueue(&queue), nil
}

func (c *Channel) QueueDelete(queueName string) (int, error) {
	c.mu.Lock()
	defer c.mu.Unlock()
	return c.ch.QueueDelete(
		queueName,
		false,
		false,
		false,
	)
}

func (c *Channel) ConsumeFromQueue(queueName string) (<-chan broker.Delivery, error) {
	c.mu.Lock()
	defer c.mu.Unlock()
	msgs, err := c.ch.Consume(
		queueName,
		"",
		false,
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		return nil, err
	}

	deliveries := make(chan broker.Delivery)
	go func() {
		for msg := range msgs {
			delivery := NewDelivery(msg)
			deliveries <- delivery
		}
	}()
	return deliveries, nil

}

func (c *Channel) PublishToQueue(queueName string, body []byte) error {
	c.mu.Lock()
	defer c.mu.Unlock()
	return c.ch.Publish(
		"",
		queueName,
		false,
		false,
		amqp091.Publishing{
			ContentType: "text/plain",
			Body:        body,
		},
	)
}

func (c *Channel) Close() error {
	c.mu.Lock()
	defer c.mu.Unlock()
	return c.ch.Close()
}
