package counter

import (
	"fmt"
	"sort"

	"github.com/distribuidos-unrust/tp/internal/controllers/counter/count"
)

type Kind int

const (
	SUM Kind = iota
	N
	AVERAGE
)

type KeyRow struct {
	key     string
	metrics []float64
}

func NewKeyRow(key string, metrics []float64) *KeyRow {
	return &KeyRow{
		key:     key,
		metrics: metrics,
	}
}

func Calculator(
	top int,
	ascending bool,
	minmax bool,
	index Kind,
	userCount *count.UserCount,
) [][]string {
	records := make([]*KeyRow, 0)
	for key, metric := range userCount.Data {
		if metric.N == 0 {
			continue
		}
		record := []float64{
			metric.Sum,
			metric.N,
			metric.GetAverage(),
		}
		log.Debugf(
			"action: calculator | result: success | key: %s | sum: %f | n: %f | average: %f",
			key,
			metric.Sum,
			metric.N,
			metric.GetAverage(),
		)
		keyrow := NewKeyRow(key, record)
		records = append(records, keyrow)
	}

	log.Debugf(
		"action: calculator | result: success | records: %v",
		records,
	)

	sort.Slice(records, func(i, j int) bool {
		if records[i].metrics[index] == records[j].metrics[index] {
			if ascending {
				return records[i].key > records[j].key
			}
			return records[i].key < records[j].key
		}

		if ascending {
			return records[i].metrics[index] < records[j].metrics[index]
		}
		return records[i].metrics[index] > records[j].metrics[index]
	})

	log.Debugf(
		"action: calculator | result: success | sorted_records: %v | len: %d",
		records,
		len(records),
	)

	size := len(records)
	if top > 0 {
		size = min(top, len(records))
	}

	resultsStr := make([][]string, 0)
	for _, record := range records {
		resultsStr = append(resultsStr, []string{
			record.key,
			fmt.Sprintf("%f", record.metrics[index]),
		})
	}

	if len(resultsStr) == 0 {
		return resultsStr
	}

	if minmax {
		return minMax(resultsStr)
	}

	log.Debugf(
		"action: calculator | result: success | results_str: %v | len: %d",
		resultsStr,
		len(resultsStr),
	)

	final := resultsStr[:size]
	log.Debugf(
		"action: calculator | result: success | final: %v | len: %d | minmax: %t",
		final,
		len(final),
		minmax,
	)

	log.Debugf(
		"action: calculator | result: success | final: %v | len: %d",
		final,
		len(final),
	)
	return final
}

func minMax(resultsStr [][]string) [][]string {
	minmaxResults := make([][]string, 0)
	minmaxResults = append(minmaxResults, resultsStr[0])
	minmaxResults = append(minmaxResults, resultsStr[len(resultsStr)-1])
	return minmaxResults
}
