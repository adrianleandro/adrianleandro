package transmission

import (
	"net"

	"github.com/distribuidos-unrust/tp/internal/communication/message"
	"github.com/distribuidos-unrust/tp/internal/communication/mom/broker"
	"github.com/distribuidos-unrust/tp/internal/communication/serialization"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/service"
)

func PublishRecords(ch broker.Channel, queueName string, records [][]string) error {
	body := serialization.RecordsIntoString(records)
	return ch.PublishToQueue(queueName, []byte(body))
}

func ConsumeRecords(event broker.Delivery) [][]string {
	body := string(event.GetBody())
	return serialization.RecordsFromString(body)
}

func SendRecords(
	conn net.Conn,
	records [][]string,
	source *service.Service,
	messageID message.MessageID,
) (int, error) {
	recordsString := serialization.RecordsIntoString(records)
	bytes := []byte(recordsString)
	header := message.NewHeader(
		message.NullMethod,
		*message.NewNullID(),
		false,
		source,
		messageID,
	)
	body := message.NewBody(bytes)
	msg := message.NewMessage(header, body)
	return SendMessage(conn, msg)
}

func RecvRecords(conn net.Conn) ([][]string, error) {
	msg, err := RecvMessage(conn)
	if err != nil {
		return nil, err
	}

	str := string(msg.Body.Data)
	return serialization.RecordsFromString(str), nil
}
