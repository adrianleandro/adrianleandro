package serialization

import (
	"github.com/distribuidos-unrust/tp/internal/communication/message"
	"github.com/distribuidos-unrust/tp/internal/communication/mom/broker"
	"github.com/distribuidos-unrust/tp/internal/controllers/counter/count"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/service"
)

func BodyIntoBytes(body *message.Body) ([]byte, error) {
	return body.Data, nil
}

func UserIDIntoBytes(userID message.ID) ([]byte, error) {
	return userID.IntoBytes()
}

func MethodIntoBytes(method message.Method) []byte {
	return Uint32IntoBytes(uint32(method))
}

func HeaderIntoBytes(header *message.Header) ([]byte, error) {
	bytes := make([]byte, 0)
	method := MethodIntoBytes(header.Method)
	userID, err := UserIDIntoBytes(header.UserID)
	if err != nil {
		return nil, err
	}

	isLastMessage := BoolIntoBytes(header.IsLastMessage)
	seen := Uint32IntoBytes(header.Seen)
	sourceName := Uint32IntoBytes(uint32(header.Source.Name))
	sourceID := Uint32IntoBytes(uint32(header.Source.ID))
	messageID := Uint32IntoBytes(uint32(header.MessageID))

	bytes = append(bytes, method...)
	bytes = append(bytes, userID...)
	bytes = append(bytes, isLastMessage...)
	bytes = append(bytes, seen...)
	bytes = append(bytes, sourceName...)
	bytes = append(bytes, sourceID...)
	bytes = append(bytes, messageID...)
	return bytes, nil
}

func MessageIntoBytes(message *message.Message) ([]byte, error) {
	bytes := make([]byte, 0)

	headerBytes, err := HeaderIntoBytes(message.Header)
	if err != nil {
		return nil, err
	}

	bodyBytes, err := BodyIntoBytes(message.Body)
	if err != nil {
		return nil, err
	}

	bytes = append(bytes, headerBytes...)
	bytes = append(bytes, bodyBytes...)

	return bytes, nil
}

func MessageFromBytes(bytes []byte) (*message.Message, error) {
	method := message.Method(Uint32FromBytes(bytes[0:4]))

	id, err := message.NewIDFromBytes(bytes[4:20])
	if err != nil {
		return nil, err
	}

	isLastMessage := BoolFromBytes(bytes[20:21])
	seen := Uint32FromBytes(bytes[21:25])
	source := service.NewService(
		service.ServiceName(Uint32FromBytes(bytes[25:29])),
		service.ServiceID(Uint32FromBytes(bytes[29:33])),
	)
	messageID := message.MessageID(Uint32FromBytes(bytes[33:37]))

	header := message.NewHeader(
		method,
		*id,
		isLastMessage,
		source,
		messageID,
	)
	header.Seen = seen

	data := bytes[37:]
	body := message.NewBody(data)

	message := message.NewMessage(header, body)
	return message, nil
}

func MessageFromEvent(event broker.Delivery) (*message.Message, error) {
	bytes := event.GetBody()
	return MessageFromBytes(bytes)
}

func MessageFromUserCount(
	userID message.ID,
	count *count.UserCount,
	source *service.Service,
	messageID message.MessageID,
) *message.Message {
	records := RecordsFromUserCount(count)
	msg := RecordsIntoMessage(records, source, messageID, userID, true, message.Count)
	return msg
}
