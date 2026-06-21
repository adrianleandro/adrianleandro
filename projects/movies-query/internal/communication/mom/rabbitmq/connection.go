package rabbitmq

import (
	"github.com/distribuidos-unrust/tp/internal/communication/mom/broker"
	"github.com/rabbitmq/amqp091-go"
)

type Connection struct {
	conn *amqp091.Connection
}

func NewConnection(conn *amqp091.Connection) *Connection {
	return &Connection{conn: conn}
}

func (c *Connection) Channel() (broker.Channel, error) {
	ch, err := c.conn.Channel()
	if err != nil {
		return nil, err
	}
	return NewChannel(ch), nil
}

func (c *Connection) Close() error {
	return c.conn.Close()
}
