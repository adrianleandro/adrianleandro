package serialization

import "encoding/binary"

func Uint32IntoBytes(value uint32) []byte {
	bytes := make([]byte, 4)
	binary.BigEndian.PutUint32(bytes, value)
	return bytes
}

func Uint32FromBytes(bytes []byte) uint32 {
	return binary.BigEndian.Uint32(bytes)
}

func BoolIntoBytes(value bool) []byte {
	if value {
		return []byte{1}
	}
	return []byte{0}
}

func BoolFromBytes(bytes []byte) bool {
	return bytes[0] == 1
}
