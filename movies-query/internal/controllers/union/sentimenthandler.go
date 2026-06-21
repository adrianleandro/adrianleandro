package union

import (
	"fmt"
	"github.com/distribuidos-unrust/tp/internal/communication/message"
	"github.com/distribuidos-unrust/tp/internal/communication/mom/broker"
	"github.com/distribuidos-unrust/tp/internal/communication/serialization"
	"github.com/distribuidos-unrust/tp/internal/communication/transmission"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/eof"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/queueinfo"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/state"
	"github.com/op/go-logging"
	"io"
	"net"
	"strings"
)

var log = logging.MustGetLogger("log")

type SentimentHandler struct {
	overviewIndex          int
	sentimentServerAddress string
	conn                   net.Conn
	State                  *state.State
}

func (s *SentimentHandler) SetState(state *state.State) {
	s.State = state
}

func (s *SentimentHandler) GetState() *state.State {
	return s.State
}

func NewSentimentHandler(overviewIndex int, address string) *SentimentHandler {
	return &SentimentHandler{
		overviewIndex:          overviewIndex,
		sentimentServerAddress: address,
	}
}

func (s *SentimentHandler) HandleEvent(
	event broker.Delivery,
	msg *message.Message,
	channel broker.Channel,
	queues map[string]*queueinfo.QueueInfo,
) {
	if eof.IfMustBeSeenByPeersThenSendIt(s.State.Service.ID, msg, channel, queues["INBOX"]) {
		return
	}

	records := serialization.RecordsFromMessage(msg)
	log.Debugf("action: handle_event | result: success | len_records: %v | records: %v", len(records), records)

	results := make([][]string, 0)
	for _, record := range records {
		log.Debugf("action: handle_event | result: success | record: %v", record)
		if record[s.overviewIndex] == "" {
			continue
		}
		resp, err := s.analyzeSentiment(record[s.overviewIndex])
		if err != nil {
			resp, err = isPositive(record[s.overviewIndex])
		}
		if err != nil {
			log.Errorf("action: handle_event | result: error | error: %v", err)
			continue
		}

		//resp, _ := isPositive(record[s.overviewIndex])
		record = append(record, resp)
		results = append(results, record)
	}

	log.Debugf("action: handle_event | result: success | processed_records: %v", results)

	resultsMsg := serialization.RecordsIntoMessage(
		results,
		s.State.Service,
		message.MessageID(s.State.Inc()),
		msg.Header.UserID,
		msg.Header.IsLastMessage,
		msg.Header.Method,
	)
	resultsMsg.Header.ResetSeen()
	log.Debugf(
		"action: handle_event | result: success | isLastMessage: %v | userID: %v | seen: %v",
		resultsMsg.Header.IsLastMessage,
		resultsMsg.Header.UserID,
		resultsMsg.Header.Seen,
	)
	transmission.PublishMessage(channel, queues["OUTBOX"].NextFromMessage(resultsMsg), resultsMsg)
}

func isPositive(text string) (string, error) {
	if len(text) == 0 {
		return "", fmt.Errorf("empty text")
	}

	primerCaracter := strings.ToUpper(string(text[0]))

	if primerCaracter >= "A" && primerCaracter <= "N" {
		return "POSITIVE", nil
	}
	return "NEGATIVE", nil

}

func (s *SentimentHandler) createSocket() error {
	conn, err := net.Dial("tcp", s.sentimentServerAddress)
	if err != nil {
		log.Criticalf(
			"action: connect | result: fail | error: %v",
			err,
		)
		return err
	}
	s.conn = conn
	return nil
}

func (s *SentimentHandler) analyzeSentiment(text string) (string, error) {
	retries := 0
	for {
		err := s.createSocket()

		if err != nil {
			log.Errorf("action: send_analyze_sentiment | result: fail | error: %v", err)
			retries++
			continue
		}

		formattedText := fmt.Sprintf("%v\n", text)
		bytesToWrite := []byte(formattedText)
		bytesWritten := 0
		writeErr := false
		for bytesWritten < len(bytesToWrite) {
			n, err := s.conn.Write(bytesToWrite[bytesWritten:])
			if err != nil {
				log.Errorf("action: write_analyze_sentiment | result: fail | error: %v", err)
				s.conn.Close()
				retries++
				writeErr = true
				break
			}
			bytesWritten += n
		}

		if writeErr {
			continue
		}

		msg := make([]byte, 1)

		_, err = io.ReadFull(s.conn, msg)
		if err != nil {
			s.conn.Close()
			log.Errorf("action: receive_analyze_sentiment | result: fail | error: %v", err)
			retries++
			continue
		}

		s.conn.Close()

		var sentiment string
		if msg[0] == '1' {
			sentiment = "POSITIVE"
		} else {
			sentiment = "NEGATIVE"
		}

		log.Infof("action: analyze_sentiment | result: success | sentiment: %v",
			sentiment,
		)

		return sentiment, nil
	}
}
