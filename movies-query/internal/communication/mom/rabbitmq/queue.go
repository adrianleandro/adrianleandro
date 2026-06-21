package rabbitmq

import "github.com/rabbitmq/amqp091-go"

type Queue struct {
	queue *amqp091.Queue
}

func NewQueue(queue *amqp091.Queue) *Queue {
	return &Queue{
		queue: queue,
	}
}

func (q *Queue) GetName() string {
	return q.queue.Name
}
