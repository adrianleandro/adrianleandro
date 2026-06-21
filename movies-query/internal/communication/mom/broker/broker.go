package broker

type Delivery interface {
	GetBody() []byte
	Ack(multiple bool) error
	Nack(multiple bool, requeue bool) error
}

type Queue interface {
	GetName() string
}

type Channel interface {
	QueueDeclare(queueName string) (Queue, error)
	QueueDelete(queueName string) (int, error)
	PublishToQueue(queueName string, body []byte) error
	ConsumeFromQueue(queueName string) (<-chan Delivery, error)
	Close() error
}

type Connection interface {
	Channel() (Channel, error)
	Close() error
}

type Broker interface {
	Dial(url string) (Connection, error)
}

func DeclareQueues(channel Channel, queues []string) error {
	for _, q := range queues {
		if _, err := channel.QueueDeclare(q); err != nil {
			return err
		}
	}
	return nil
}
