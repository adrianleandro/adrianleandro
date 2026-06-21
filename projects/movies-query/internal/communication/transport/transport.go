package transport

import (
	"encoding/binary"
	"net"
)

const UINT32_SIZE = 4

func RecvBytes(conn net.Conn, size uint32) ([]byte, error) {
	bytes := make([]byte, size)
	received_bytes := uint32(0)

	for received_bytes < size {
		n, err := conn.Read(bytes[received_bytes:])
		received_bytes += uint32(n)
		if err != nil {
			return bytes, err
		}
	}

	return bytes, nil
}

func RecvUint32(conn net.Conn) (uint32, error) {
	bytes, err := RecvBytes(conn, UINT32_SIZE)
	if err != nil {
		return 0, err
	}
	return binary.BigEndian.Uint32(bytes), nil
}

func RecvString(conn net.Conn) (string, error) {
	size, err := RecvUint32(conn)
	if err != nil {
		return "", err
	}

	bytes, err := RecvBytes(conn, size)
	if err != nil {
		return "", err
	}

	return string(bytes), nil
}

func SendBytes(conn net.Conn, msg []byte) (int, error) {
	size := len(msg)
	sent_bytes := 0

	for sent_bytes < size {
		n, err := conn.Write(msg[sent_bytes:])
		sent_bytes += n
		if err != nil {
			return sent_bytes, err
		}
	}

	return sent_bytes, nil
}

func SendUint32(conn net.Conn, entero uint32) (int, error) {
	bytes := make([]byte, UINT32_SIZE)
	binary.BigEndian.PutUint32(bytes, entero)
	return SendBytes(conn, bytes)
}

func SendString(conn net.Conn, texto string) (int, error) {
	bytes := []byte(texto)
	n, err := SendUint32(conn, uint32(len(bytes)))
	if err != nil {
		return n, err
	}

	return SendBytes(conn, bytes)
}
