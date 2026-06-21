package message

type Body struct {
	Data []byte
}

func NewBody(data []byte) *Body {
	return &Body{
		Data: data,
	}
}
