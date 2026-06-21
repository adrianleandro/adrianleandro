package queueinfo

import (
	"hash/fnv"
	"math/rand/v2"
	"strconv"

	"fmt"

	"github.com/distribuidos-unrust/tp/internal/communication/message"
	"github.com/distribuidos-unrust/tp/internal/communication/mom/broker"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/service"
	"github.com/op/go-logging"
	"github.com/spf13/viper"
)

var log = logging.MustGetLogger("log")

type QueueInfo struct {
	Domain string
	Amount int
}

func NewQueueInfo(domain string, amount int) *QueueInfo {
	if amount <= 0 {
		log.Criticalf("action: new_queue_info | result: fail | error: %v", "amount must be greater than 0")
		return nil
	}

	if domain == "" {
		log.Criticalf("action: new_queue_info | result: fail | error: %v", "domain must not be empty")
		return nil
	}

	return &QueueInfo{
		Domain: domain,
		Amount: amount,
	}
}

func (q *QueueInfo) Next() string {
	return q.Domain + "_" + strconv.Itoa(rand.IntN(q.Amount))
}

func (q *QueueInfo) NextFrom(i service.ServiceID) string {
	return q.Domain + "_" + strconv.Itoa(int((i+1)%service.ServiceID(q.Amount)))
}

func (q *QueueInfo) Current(i uint32) string {
	return q.Domain + "_" + fmt.Sprint(i)
}

func (q *QueueInfo) NextHash(s string) string {
	h := fnv.New32a()
	h.Write([]byte(s))
	hashValue := h.Sum32()
	i := hashValue % uint32(q.Amount)
	return q.Current(i)
}

func (q *QueueInfo) NextFromUint32(i uint32) string {
	return q.Current(i % uint32(q.Amount))
}

func (q *QueueInfo) NextFromMessage(msg *message.Message) string {
	return q.NextFromUint32(uint32(msg.Header.MessageID))
}

func (q *QueueInfo) NextRandomOrHash(isRandom bool, s string) string {
	if isRandom {
		return q.Next()
	}
	return q.NextHash(s)
}

func NewFromViper(v *viper.Viper, queues []string) map[string]*QueueInfo {
	infos := make(map[string]*QueueInfo)

	for _, name := range queues {
		domain := v.GetString(name + "_DOMAIN")
		amount := v.GetInt(name + "_AMOUNT")
		infos[name] = NewQueueInfo(domain, amount)
		log.Debugf("action: new_queue_info | result: success | queue: %s | domain: %s | amount: %d", name, domain, amount)
	}

	return infos
}

func (q *QueueInfo) DeclareQueues(channel broker.Channel) error {
	for i := range q.Amount {
		_, err := channel.QueueDeclare(q.Domain + "_" + strconv.Itoa(i))
		if err != nil {
			return err
		}
	}
	return nil
}

func DeclareQueuesFromMap(channel broker.Channel, queues map[string]*QueueInfo) error {
	for _, queue := range queues {
		err := queue.DeclareQueues(channel)
		if err != nil {
			return err
		}
	}
	return nil
}
