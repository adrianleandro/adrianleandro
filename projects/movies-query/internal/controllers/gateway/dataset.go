package gateway

import (
	"net"

	"github.com/distribuidos-unrust/tp/internal/communication/message"
	"github.com/distribuidos-unrust/tp/internal/communication/mom/broker"
	"github.com/distribuidos-unrust/tp/internal/communication/serialization"
	"github.com/distribuidos-unrust/tp/internal/communication/transmission"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/queueinfo"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/safestate"
)

func PostDataset(
	conn net.Conn,
	queueInfo *queueinfo.QueueInfo,
	channel broker.Channel,
	safestate *safestate.SafeState,
) {
	for {
		msg, err := transmission.RecvMessage(conn)
		if err != nil {
			log.Errorf("action: recv_message | result: error | error: %+v", err)
			return
		}

		queueName := queueInfo.NextFromMessage(msg)
		records := serialization.RecordsFromMessage(msg)
		log.Debugf(
			"action: post_dataset | result: success | len_records: %v | queueName: %s",
			len(records),
			queueName,
		)

		msg.Header.Source = safestate.GetService()
		msg.Header.Method = message.Records
		err = transmission.PublishMessage(channel, queueName, msg)
		if err != nil {
			log.Errorf("action: publish_message | result: error | error: %v", err)
			return
		}

		if msg.Header.IsLastMessage {
			log.Debugf("action: is_last_message | result: success | message: %+v", msg)
			break
		}
	}
}

func GetResults(conn net.Conn, channel broker.Channel, results int, userID *message.ID) {
	log.Debugf("action: get_results | result: start")
	queueName := "user_" + userID.IntoString()
	log.Debugf("action: get_results | result: queue_name | queue_name: %v", queueName)

	_, err := channel.QueueDeclare(queueName)
	if err != nil {
		log.Errorf("action: declare_queue | result: error | error: %v", err)
		return
	}

	consumer, err := channel.ConsumeFromQueue(queueName)
	if err != nil {
		log.Errorf("action: consume_from_queue | result: error | error: %v", err)
		return
	}

	eofSeen := 0
	for eofSeen < results {
		event := <-consumer
		message, err := serialization.MessageFromEvent(event)
		if err != nil {
			log.Errorf("action: message_from_event | result: error | error: %v", err)
			return
		}

		if message.Header.IsLastMessage {
			eofSeen++
		}

		if _, err := transmission.SendMessage(conn, message); err != nil {
			log.Errorf("action: send_message | result: error | error: %v", err)
			return
		}
	}

	msgCount, err := channel.QueueDelete(queueName)
	if err != nil {
		log.Errorf("action: delete_queue | result: error | error: %v | msgCount: %d", err, msgCount)
		return
	}
	log.Debugf("action: send_message | result: success | eofSeen: %v", eofSeen)
}

func GetId(conn net.Conn, channel broker.Channel, safestate *safestate.SafeState) {
	log.Debugf("action: get_id | result: start")

	id, err := message.NewID()
	if err != nil {
		log.Errorf("action: get_id | result: error | error: %v", err)
		return
	}
	log.Infof("action: get_id | result: success | id: %s", id.IntoString())

	header := message.NewHeader(
		message.GetId,
		*id,
		true,
		safestate.GetService(),
		message.MessageID(safestate.Inc()),
	)
	body := message.NewBody([]byte{})
	response := message.NewMessage(header, body)

	if _, err := transmission.SendMessage(conn, response); err != nil {
		log.Errorf("action: send_message | result: error | error: %v", err)
		return
	}
	log.Debugf("action: send_message | result: success | message: %v", response)
}
