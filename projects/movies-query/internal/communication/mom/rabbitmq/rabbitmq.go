package rabbitmq

import "github.com/rabbitmq/amqp091-go"

func Dial(url string) (*amqp091.Connection, error) {
	return amqp091.Dial(url)
}

func QueueDeclare(ch *amqp091.Channel, queueName string) (amqp091.Queue, error) {
	queue, err := ch.QueueDeclare(
		queueName,
		true,
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		return amqp091.Queue{}, err
	}
	return queue, nil
}

func PublishToExchange(ch *amqp091.Channel, exchangeName string, queueName string, body []byte) error {
	err := ch.Publish(
		exchangeName,
		queueName,
		false,
		false,
		amqp091.Publishing{
			ContentType: "text/plain",
			Body:        body,
		},
	)
	return err

}
func Publish(ch *amqp091.Channel, queueName string, body []byte) error {
	return PublishToExchange(ch, "", queueName, body)
}

func Consume(ch *amqp091.Channel, queueName string) (<-chan amqp091.Delivery, error) {
	msgs, err := ch.Consume(
		queueName,
		"",
		false, // auto-ack
		false,
		false,
		false,
		nil,
	)
	return msgs, err
}

func SendString(ch *amqp091.Channel, queueName string, body string) error {
	return ch.Publish(
		"",
		queueName,
		false,
		false,
		amqp091.Publishing{
			ContentType: "text/plain",
			Body:        []byte(body),
		},
	)
}

func RecvString(ch *amqp091.Channel, queueName string) (string, error) {
	msgs, err := Consume(ch, queueName)
	if err != nil {
		return "", err
	}
	msg := <-msgs
	return string(msg.Body), nil
}
