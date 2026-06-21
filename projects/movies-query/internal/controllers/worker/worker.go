package worker

import (
	"net"
	"os"
	"os/signal"
	"syscall"

	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

type Worker struct {
	config *WorkerConfig
}

func NewWorker(config *WorkerConfig) *Worker {
	return &Worker{config}
}

func (w *Worker) Run() {
	defer w.config.Close()

	sigs := make(chan os.Signal, 1)
	signal.Notify(sigs, syscall.SIGTERM)

	go w.handleUdp("8080")
	go w.config.Handler.Handle(w.config.Service.ID, w.config.MomChannel)

	select {
	case ok := <-w.config.Handler.GetDoneQueue():
		log.Infof("action: worker | result: success | message: all actors finished | ok: %v", ok)
	case <-sigs:
		w.config.Handler.Quit()
		log.Infof("action: worker | result: in_progress | message: waiting Done signal from ActorManager")
		<-w.config.Handler.GetDoneQueue()
		log.Infof("action: worker | result: success | message: Done signal received from ActorManager")
	}

	log.Infof("action: worker | result: success | message: worker finished | ok: true")
}

func (w *Worker) handleUdp(port string) {
	addr, err := net.ResolveUDPAddr("udp", ":"+port)
	if err != nil {
		log.Errorf("action: resolve_udp_addr | result: fail | error: %v", err)
		return
	}

	conn, err := net.ListenUDP("udp", addr)
	if err != nil {
		log.Errorf("action: listen_udp | result: fail | error: %v", err)
		return
	}
	defer conn.Close()

	log.Infof("action: listening_on_udp | result: success | port: %s", port)

	buffer := make([]byte, 1024)
	for {
		_, remoteAddr, err := conn.ReadFromUDP(buffer)
		if err != nil {
			log.Errorf("action: read_from_udp | result: fail | error: %v", err)
			continue
		}

		response := []byte{0x0A}
		response = append(response, []byte(w.config.Service.String())...)
		log.Infof("action: read_from_udp | result: success | info: sent message with service info")

		_, err = conn.WriteToUDP(response, remoteAddr)
		if err != nil {
			log.Errorf("action: write_to_udp | result: fail | error: %v", err)
		}
	}
}
