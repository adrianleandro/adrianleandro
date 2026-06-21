package request

import (
	"errors"
	"math"
	"time"

	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

func SleepTime(x uint32) time.Duration {
	i := x % 10
	sleepTime := math.Pow(2, float64(i))
	return time.Second * time.Duration(sleepTime)
}

func Retry(retry uint32, request Request, retryResponse chan error) {
	requesResponse := make(chan error, 1)
	for i := range retry {
		request.Run(requesResponse)
		err := <-requesResponse
		if err == nil {
			retryResponse <- nil
			return
		}
		sleepTime := SleepTime(i)
		log.Debugf("action: retry_request | result: error | error: %v | retry: %d / %d | sleep_time: %v",
			err,
			i,
			retry,
			sleepTime,
		)
		time.Sleep(sleepTime)
	}
	retryResponse <- errors.New("max retries reached, request failed")
}
