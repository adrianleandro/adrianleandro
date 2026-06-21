package serialization

import (
	"strconv"
	"strings"

	"github.com/distribuidos-unrust/tp/internal/communication/message"
	"github.com/distribuidos-unrust/tp/internal/communication/mom/broker"
	"github.com/distribuidos-unrust/tp/internal/controllers/counter/count"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/service"
)

func RecordIntoString(record []string) string {
	return strings.Join(record, FIELDS_SEPARATOR)
}

func RecordsIntoString(records [][]string) string {
	acum := make([]string, 0)
	for _, record := range records {
		acum = append(acum, RecordIntoString(record))
	}
	return strings.Join(acum, RECORDS_SEPARATOR)
}

func RecordFromString(recordString string) []string {
	return strings.Split(recordString, FIELDS_SEPARATOR)
}

func RecordsFromString(recordsString string) [][]string {
	acum := make([][]string, 0)
	if recordsString == "" {
		return acum
	}

	rows := strings.SplitSeq(recordsString, RECORDS_SEPARATOR)
	for row := range rows {
		acum = append(acum, RecordFromString(row))
	}
	return acum
}

func RecordsFromEvent(event broker.Delivery) [][]string {
	body := string(event.GetBody())
	records := RecordsFromString(body)
	return records
}

func RecordsFromMessage(message *message.Message) [][]string {
	body := string(message.Body.Data)
	records := RecordsFromString(body)
	return records
}

func RecordsIntoMessage(
	records [][]string,
	source *service.Service,
	messageID message.MessageID,
	userID message.ID,
	isLastMessage bool,
	method message.Method,
) *message.Message {
	strRecods := RecordsIntoString(records)
	body := message.NewBody([]byte(strRecods))
	header := message.NewHeader(
		method,
		userID,
		isLastMessage,
		source,
		messageID,
	)
	msg := message.NewMessage(header, body)
	return msg
}

func RecordsFromUserCount(userCount *count.UserCount) [][]string {
	rows := make([][]string, 0)
	for key, metric := range userCount.Data {
		rows = append(
			rows,
			[]string{
				key,
				strconv.FormatFloat(metric.Sum, 'f', -1, 64),
				strconv.FormatFloat(metric.N, 'f', -1, 64),
			},
		)
	}
	return rows
}

func RecordsIntoUserCount(rows [][]string) *count.UserCount {
	userCount := count.NewUserCount()
	for _, row := range rows {
		if len(row) < 3 {
			continue
		}
		key := row[0]
		sum, err := strconv.ParseFloat(row[1], 64)
		if err != nil {
			continue
		}
		n, err := strconv.ParseFloat(row[2], 64)
		if err != nil {
			continue
		}
		metric := count.NewMetric()
		metric.Sum = sum
		metric.N = n
		userCount.Data[key] = metric
	}
	return userCount
}
