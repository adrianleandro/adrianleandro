package message

import "github.com/google/uuid"

type ID struct {
	id uuid.UUID
}

func NewID() (*ID, error) {
	id, err := uuid.NewRandom()
	if err != nil {
		return nil, err
	}
	return &ID{id: id}, nil
}

func NewIDFromBytes(b []byte) (*ID, error) {
	var id uuid.UUID
	err := id.UnmarshalBinary(b)
	if err != nil {
		return nil, err
	}
	return &ID{id: id}, nil
}

func NewNullID() *ID {
	return &ID{uuid.Nil}
}

func (id *ID) IntoBytes() ([]byte, error) {
	b, err := uuid.UUID(id.id).MarshalBinary()
	if err != nil {
		return nil, err
	}
	return b, nil
}

func (id *ID) IntoString() string {
	return id.id.String()
}
