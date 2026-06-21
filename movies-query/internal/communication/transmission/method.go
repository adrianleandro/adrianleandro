package transmission

import (
	"net"

	"github.com/distribuidos-unrust/tp/internal/communication/message"
	"github.com/distribuidos-unrust/tp/internal/communication/transport"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/service"
)

func SendMethod(
	conn net.Conn,
	method message.Method,
	source *service.Service,
	messageID message.MessageID,
) (int, error) {
	header := message.NewHeader(method, *message.NewNullID(), false, source, messageID)
	body := message.NewBody(nil)
	message := message.NewMessage(header, body)
	return SendMessage(conn, message)
}

func RecvMethod(conn net.Conn) (message.Method, error) {
	method, err := transport.RecvUint32(conn)
	if err != nil {
		return message.ErrorMethod, err
	}
	return message.Method(method), nil
}
