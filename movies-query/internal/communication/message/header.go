package message

import "github.com/distribuidos-unrust/tp/internal/controllers/worker/service"

type Header struct {
	Method        Method
	UserID        ID
	IsLastMessage bool
	Seen          uint32
	Source        *service.Service
	MessageID     MessageID
}

func NewHeader(
	method Method,
	userID ID,
	isLastMessage bool,
	source *service.Service,
	messageID MessageID,
) *Header {
	return &Header{
		Method:        method,
		UserID:        userID,
		IsLastMessage: isLastMessage,
		Seen:          1,
		Source:        source,
		MessageID:     messageID,
	}
}

func (h *Header) IncSeen() {
	h.Seen++
}

func (h *Header) HasBeenSeenByEveryone(all uint32) bool {
	return h.Seen >= all
}

func (h *Header) ResetSeen() {
	h.Seen = 1
}
