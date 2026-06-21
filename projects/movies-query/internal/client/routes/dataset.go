package routes

import (
	"encoding/csv"
	"fmt"
	"io"
	"math"
	"net"
	"os"
	"time"

	"github.com/distribuidos-unrust/tp/internal/client/reader"
	"github.com/distribuidos-unrust/tp/internal/communication/message"
	"github.com/distribuidos-unrust/tp/internal/communication/serialization"
	"github.com/distribuidos-unrust/tp/internal/communication/transmission"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/service"
	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

func NewMethodMessage(
	userID message.ID,
	method message.Method,
	service *service.Service,
	messageID message.MessageID,
) *message.Message {
	header := message.NewHeader(
		method,
		userID,
		false,
		service,
		messageID,
	)
	body := message.NewBody([]byte{})
	return message.NewMessage(header, body)
}

func RetryPostDataset(
	retry uint32,
	userID *message.ID,
	resChannel chan error,
	method message.Method,
	gatewayAddress string,
	datasetPath string,
	batchSize int,
	service *service.Service,
) {
	success := false

	for i := range retry {
		log.Debugf("action: retry_post_dataset | result: start | retry: %d", i)
		channel := make(chan error)
		go PostDataset(
			userID,
			channel,
			method,
			gatewayAddress,
			datasetPath,
			batchSize,
			service,
		)
		res := <-channel
		if res == nil {
			log.Debugf("action: retry_post_dataset | result: success | retry: %d", i)
			success = true
			break
		}

		sleepTime := time.Duration(math.Pow(2, float64(i))) * time.Second
		log.Debugf("action: retry_post_dataset | result: error | error: %v | retry: %d | sleep_time: %v",
			res,
			i,
			sleepTime,
		)
		time.Sleep(sleepTime)
	}

	if success {
		log.Debugf("action: retry_post_dataset | result: success | user_id: %s", userID.IntoString())
		resChannel <- nil
	} else {
		log.Errorf("action: retry_post_dataset | result: error | user_id: %s", userID.IntoString())
		resChannel <- fmt.Errorf("failed to post dataset after %d retries", retry)
	}
}

func PostDataset(
	userID *message.ID,
	resChannel chan error,
	method message.Method,
	gatewayAddress string,
	datasetPath string,
	batchSize int,
	service *service.Service,
) {
	conn, err := net.Dial("tcp", gatewayAddress)
	if err != nil {
		log.Errorf("action: connect | result: error | error: %v", err)
		resChannel <- err
		return
	}
	defer conn.Close()

	messagesSent := 0
	msg := NewMethodMessage(
		*userID,
		method,
		service,
		message.MessageID(messagesSent),
	)

	if _, err := transmission.SendMessage(conn, msg); err != nil {
		log.Errorf("action: send_message | result: error | error: %v", err)
		resChannel <- err
		return
	}

	messagesSent++

	reader, err := reader.NewReader(datasetPath, batchSize)
	if err != nil {
		log.Errorf("action: new_read | result: error | error: %v", err)
		resChannel <- err
		return
	}

	defer reader.Close()

	for {
		records, readErr := reader.Read()
		if readErr != nil && readErr != io.EOF {
			log.Errorf("action: read | result: error | error: %v", readErr)
			continue
		}

		message := serialization.RecordsIntoMessage(
			records,
			service,
			message.MessageID(messagesSent),
			*userID,
			readErr == io.EOF,
			method,
		)

		_, err = transmission.SendMessage(conn, message)
		if err != nil {
			log.Errorf("action: send_message | result: error | error: %v", err)
			resChannel <- err
			return
		}

		log.Debugf(
			"action: send_message | result: success | len_records: %v | method: %s | messagesSent: %d | EOF: %v",
			len(records),
			message.Header.Method.String(),
			messagesSent,
			message.Header.IsLastMessage,
		)

		if readErr == io.EOF {
			break
		}
		messagesSent++
	}
	log.Debugf("action: read | result: success | message: %v", msg)
	resChannel <- nil
}

func GetResults(
	userID *message.ID,
	resChannel chan bool,
	gatewayAddress string,
	results int,
	service *service.Service,
) {
	log.Debugf("action: get_results | result: start | gateway_address: %s", gatewayAddress)
	conn, err := net.Dial("tcp", gatewayAddress)
	if err != nil {
		log.Errorf("action: connect | result: error | error: %v", err)
		resChannel <- false
		return
	}
	defer conn.Close()

	messageSent := 0
	message := NewMethodMessage(
		*userID,
		message.GetResults,
		service,
		message.MessageID(messageSent),
	)
	if _, err := transmission.SendMessage(conn, message); err != nil {
		log.Errorf("action: send_message | result: error | error: %v", err)
		resChannel <- false
		return
	}

	eofSeen := 0
	for eofSeen < results {
		message, err := transmission.RecvMessage(conn)
		if err != nil {
			log.Errorf("action: receive_records | result: error | error: %v", err)
			resChannel <- false
			return
		}
		records := serialization.RecordsFromMessage(message)
		PrintQuery(message.Header.Method, records, message.Header.UserID)

		if message.Header.IsLastMessage {
			eofSeen++
		}

		log.Debugf("action: receive_records | result: success | eofSeen: %v | message: %v", eofSeen, message)
	}
	resChannel <- true
}

func GetId(
	resChannel chan *message.ID,
	gatewayAddress string,
	service *service.Service,
) {
	messageSent := 0
	log.Debugf("action: get_id | result: start | gateway_address: %s", gatewayAddress)
	conn, err := net.Dial("tcp", gatewayAddress)
	if err != nil {
		log.Errorf("action: connect | result: error | error: %v", err)
		resChannel <- nil
		return
	}
	defer conn.Close()

	if _, err := transmission.SendMethod(
		conn,
		message.GetId,
		service,
		message.MessageID(messageSent),
	); err != nil {
		log.Errorf("action: send_message | result: error | error: %v", err)
		resChannel <- nil
		return
	}

	recvMessage, err := transmission.RecvMessage(conn)
	if err != nil {
		log.Errorf("action: receive_message | result: error | error: %v", err)
		resChannel <- nil
		return
	}
	log.Debugf("action: receive_message | result: success | message: %v", recvMessage)
	log.Debugf("action: receive_message | result: success | message: User ID %v", recvMessage.Header.UserID)
	resChannel <- &recvMessage.Header.UserID
}

func PrintQuery(method message.Method, records [][]string, userId message.ID) {
	switch method {
	case message.ResultQuery1:
		PrintQueryOneResults(records, userId)
	case message.ResultQuery2:
		PrintQueryTwoResults(records, userId)
	case message.ResultQuery3:
		PrintQueryThreeResults(records, userId)
	case message.ResultQuery4:
		PrintQueryFourResults(records, userId)
	case message.ResultQuery5:
		PrintQueryFiveResults(records, userId)
	default:
		log.Debugf("action: print_query | result: error | error: unknown method %d", method)
	}
}

func PrintQueryOneResults(records [][]string, userId message.ID) {
	saveToFile(records, []string{"title", "genre"}, 1, userId.IntoString())
}

func PrintQueryTwoResults(records [][]string, userId message.ID) {
	saveToFile(records, []string{"country", "budget"}, 2, userId.IntoString())
}

func PrintQueryThreeResults(records [][]string, userId message.ID) {
	saveToFile(records, []string{"title", "rating"}, 3, userId.IntoString())
}

func PrintQueryFourResults(records [][]string, userId message.ID) {
	saveToFile(records, []string{"actor", "appearances"}, 4, userId.IntoString())
}

func PrintQueryFiveResults(records [][]string, userId message.ID) {
	saveToFile(records, []string{"sentiment", "average ratio"}, 5, userId.IntoString())
}

func saveToFile(records [][]string, header []string, queryNumber int, userId string) {
	log.Debugf("%v", header)
	log.Debugf("records %v: %v", queryNumber, records)

	fileName := fmt.Sprintf("/app/data/%v-%s.csv", queryNumber, userId)
	file, err := os.OpenFile(fileName, os.O_APPEND|os.O_WRONLY|os.O_CREATE, 0600)
	if err != nil {
		log.Errorf("Error al crear archivo CSV: %v", err)
		return
	}
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	for _, record := range records {
		if err := writer.Write(record); err != nil {
			log.Errorf("Error al escribir registro en CSV: %v", err)
			continue
		}
		log.Debugf("%s", record)
	}

	log.Debugf("Resultados guardados en %v", fileName)
}
