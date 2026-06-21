package transmission

import (
	"net"

	"github.com/distribuidos-unrust/tp/internal/communication/message"
	"github.com/distribuidos-unrust/tp/internal/communication/mom/broker"
	"github.com/distribuidos-unrust/tp/internal/communication/serialization"
	"github.com/distribuidos-unrust/tp/internal/communication/transport"
	"github.com/distribuidos-unrust/tp/utils"
)

func SendMessage(conn net.Conn, message *message.Message) (int, error) {
	bytes, err := serialization.MessageIntoBytes(message)
	if err != nil {
		return 0, err
	}

	if _, err := transport.SendUint32(conn, uint32(len(bytes))); err != nil {
		return 0, err
	}
	return transport.SendBytes(conn, bytes)
}

func RecvMessage(conn net.Conn) (*message.Message, error) {
	size, err := transport.RecvUint32(conn)
	if err != nil {
		return nil, err
	}

	bytes, err := transport.RecvBytes(conn, size)
	if err != nil {
		return nil, err
	}
	return serialization.MessageFromBytes(bytes)
}

func PublishMessage(ch broker.Channel, queueName string, message *message.Message) error {
	v, _ := utils.InitViperConfig()
	times := v.GetInt("messageDuplication")
	if times <= 0 {
		times = 1
	}
	return publishMessageTimes(ch, queueName, message, times)
}

func publishMessageTimes(
	ch broker.Channel,
	queueName string,
	message *message.Message,
	times int,
) error {
	bytes, err := serialization.MessageIntoBytes(message)
	if err != nil {
		return err
	}
	for i := 0; i < times; i++ {
		if err := ch.PublishToQueue(queueName, bytes); err != nil {
			return err
		}
	}
	return nil
}
