package message

import "github.com/distribuidos-unrust/tp/internal/controllers/worker/service"

type Message struct {
	Header *Header
	Body   *Body
}

func NewMessage(header *Header, body *Body) *Message {
	return &Message{
		Header: header,
		Body:   body,
	}
}
func NewMethodMessage(
	method Method,
	source *service.Service,
	messageID MessageID,
	userID ID,
) *Message {
	header := NewHeader(
		method,
		userID,
		true,
		source,
		messageID,
	)
	body := NewBody(nil)
	return NewMessage(header, body)
}

func NewEmptyMessage(
	method Method,
	source *service.Service,
	messageID MessageID,
) *Message {
	header := NewHeader(
		method,
		*NewNullID(),
		true,
		source,
		messageID,
	)
	body := NewBody(nil)
	return NewMessage(header, body)
}
