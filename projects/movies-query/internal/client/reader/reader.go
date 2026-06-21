package reader

import (
	"encoding/csv"
	"io"
	"os"
)

type Reader struct {
	file      *os.File
	reader    *csv.Reader
	batchSize int
}

func NewReader(path string, batchSize int) (*Reader, error) {
	file, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	reader := csv.NewReader(file)
	reader.Comma = ','
	reader.FieldsPerRecord = -1

	reader.Read() // Skip header

	return &Reader{
		file:      file,
		reader:    reader,
		batchSize: batchSize,
	}, nil
}

func (r *Reader) Read() ([][]string, error) {
	records := make([][]string, 0)

	EOFSeen := false

	for len(records) < r.batchSize && !EOFSeen {
		record, err := r.reader.Read()
		if err != nil {
			if err == io.EOF {
				EOFSeen = true
			} else {
				continue
			}
		}
		if records != nil {
			records = append(records, record)
		}
	}

	if EOFSeen {
		return records, io.EOF
	} else {
		return records, nil
	}
}

func (r *Reader) Close() error {
	return r.file.Close()
}
