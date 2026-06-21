package prodcountry

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

type ProdCountryHandler struct {
	index    int
	comparer ProdCountryComparer
	State    *state.State
}

func NewProdCountryHandler(index int, comparer ProdCountryComparer) *ProdCountryHandler {
	return &ProdCountryHandler{index: index, comparer: comparer, State: nil}
}

func (f *ProdCountryHandler) SetState(state *state.State) {
	f.State = state
}

func (f *ProdCountryHandler) GetState() *state.State {
	return f.State
}

func (f *ProdCountryHandler) HandleEvent(
	event broker.Delivery,
	msg *message.Message,
	channel broker.Channel,
	queues map[string]*queueinfo.QueueInfo,
) {
	if eof.IfMustBeSeenByPeersThenSendIt(f.State.Service.ID, msg, channel, queues["INBOX"]) {
		return
	}

	msg.Header.ResetSeen()

	records := serialization.RecordsFromMessage(msg)
	log.Debugf("action: handle_event | result: success | records: %v", len(records))
	filteredRecords := make([][]string, 0)

	for _, record := range records {
		if len(record) < (f.index + 1) {
			continue
		}

		log.Debugf("action: handle_event | result: success | record: %v", record)
		productionCountries, err := serialization.ProductionCountriesFromString(record[f.index])
		log.Debugf("action: handle_event | result: success | productionCountries: %+v", productionCountries)
		if err != nil {
			continue
		}
		if f.comparer.Compare(productionCountries) {
			filteredRecords = append(filteredRecords, record)
		}
	}

	log.Debugf("action: handle_event | result: success | filtered records: %v", filteredRecords)
	filteredMessage := serialization.RecordsIntoMessage(
		filteredRecords,
		f.State.Service,
		message.MessageID(f.State.Inc()),
		msg.Header.UserID,
		msg.Header.IsLastMessage,
		message.Records,
	)

	if len(filteredRecords) == 0 && !filteredMessage.Header.IsLastMessage {
		log.Debugf("action: handle_event | result: skip | reason: no records and no EOF")
		return
	}

	queueName := queues["OUTBOX"].NextFromMessage(filteredMessage)
	log.Debugf(
		"action: handle_event | result: success | queueName: %s | isLastMessage: %v",
		queueName,
		filteredMessage.Header.IsLastMessage,
	)
	transmission.PublishMessage(channel, queueName, filteredMessage)
}
