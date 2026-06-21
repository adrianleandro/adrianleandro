package sharder

import (
	"github.com/distribuidos-unrust/tp/internal/communication/message"
	"github.com/distribuidos-unrust/tp/internal/communication/mom/broker"
	"github.com/distribuidos-unrust/tp/internal/communication/serialization"
	"github.com/distribuidos-unrust/tp/internal/communication/transmission"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/eof"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/queueinfo"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/state"
	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

type SharderHandler struct {
	index uint32
	State *state.State
}

func (f *SharderHandler) SetState(state *state.State) {
	f.State = state
}

func (f *SharderHandler) GetState() *state.State {
	return f.State
}

func NewSharderHandler(index uint32) *SharderHandler {
	return &SharderHandler{
		index: index,
	}
}

func (f *SharderHandler) HandleEvent(
	event broker.Delivery,
	msg *message.Message,
	channel broker.Channel,
	queues map[string]*queueinfo.QueueInfo,
) {
	if eof.MustBeSeenByPeers(msg, queues["INBOX"]) {
		log.Debugf(
			"action: handle_event | result: success | forwarding message to peers | ID: %d | seen: %d | amount: %d | next: %s",
			f.State.Service.ID,
			msg.Header.Seen,
			queues["INBOX"].Amount,
			queues["INBOX"].NextFrom(f.State.Service.ID),
		)
		eof.IncAndSendToNextPeers(f.State.Service.ID, msg, channel, queues["INBOX"])
		return
	}

	shards := map[string][][]string{}
	records := serialization.RecordsFromMessage(msg)
	log.Debugf("action: handle_event | result: success | ID: %d | len_msg: %d | userID: %s | method %s",
		f.State.Service.ID,
		len(records),
		msg.Header.UserID.IntoString(),
		msg.Header.Method.String(),
	)

	for _, record := range records {
		pk := record[f.index]
		key := queues["OUTBOX"].NextHash(pk)
		if _, ok := shards[key]; !ok {
			shards[key] = [][]string{}
		}
		log.Debugf("action: handle_event | result: success | ID: %d | shard_key: %s | record: %s",
			f.State.Service.ID,
			key,
			record,
		)
		shards[key] = append(shards[key], record)
	}

	for key, records := range shards {
		recordsMessage := serialization.RecordsIntoMessage(
			records,
			f.State.Service,
			message.MessageID(f.State.Inc()),
			msg.Header.UserID,
			false,
			message.Records,
		)
		recordsMessage.Header.Method = msg.Header.Method
		log.Debugf("action: handle_event | result: success | sending_to_output | ID: %d | next: %s | len_msg: %d | userID: %s | method: %s",
			f.State.Service.ID,
			key,
			len(records),
			recordsMessage.Header.UserID.IntoString(),
			recordsMessage.Header.Method.String(),
		)
		transmission.PublishMessage(channel, key, recordsMessage)
	}

	if !msg.Header.IsLastMessage {
		return
	}

	emptyRecords := [][]string{}
	emptyMessage := serialization.RecordsIntoMessage(
		emptyRecords,
		f.State.Service,
		message.MessageID(f.State.Inc()),
		msg.Header.UserID,
		true,
		msg.Header.Method,
	)
	queueName := queues["OUTBOX"].NextFromMessage(emptyMessage)

	log.Debugf("action: handle_event | result: success | sending_eof | ID: %d | next: %s | len_msg: %d | userID: %s | method: %s",
		f.State.Service.ID,
		queueName,
		len(emptyRecords),
		emptyMessage.Header.UserID.IntoString(),
		emptyMessage.Header.Method.String(),
	)

	err := transmission.PublishMessage(channel, queueName, emptyMessage)
	if err != nil {
		log.Errorf("action: publish_message | result: error | error: %v", err)
		return
	}
}
