package gateway

import (
	"net"

	"github.com/distribuidos-unrust/tp/internal/communication/message"
	"github.com/distribuidos-unrust/tp/internal/communication/mom/broker"
	"github.com/distribuidos-unrust/tp/internal/communication/transmission"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/queueinfo"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/safestate"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/service"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/state"
	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

type GatewayHandler struct {
	Listener           net.Listener
	MaxRequestHandlers int
	queues             map[string]*queueinfo.QueueInfo
	Done               chan bool
	MomChannel         broker.Channel
	Results            int
	SafeState          *safestate.SafeState
}

func (g *GatewayHandler) SetState(state *state.State) {
	g.SafeState.State = state
}

func NewGatewayHandler(
	address string,
	maxRequestHandlers int,
	queues map[string]*queueinfo.QueueInfo,
	results int,
) *GatewayHandler {
	ln, err := net.Listen("tcp", address)
	if err != nil {
		log.Criticalf("action: accept | result: fail | error: %v", err)
		return nil
	}

	return &GatewayHandler{
		Listener:           ln,
		MaxRequestHandlers: maxRequestHandlers,
		queues:             queues,
		Done:               make(chan bool),
		MomChannel:         nil,
		Results:            results,
		SafeState:          safestate.NewSafeStateWithoutState(),
	}
}

func (g *GatewayHandler) Quit() {
	g.Listener.Close()
}

func (g *GatewayHandler) GetDoneQueue() chan bool {
	return g.Done
}

func (g *GatewayHandler) Handle(ID service.ServiceID, momChannel broker.Channel) {
	g.MomChannel = momChannel

	if err := queueinfo.DeclareQueuesFromMap(g.MomChannel, g.queues); err != nil {
		log.Criticalf("action: declare_queues | result: fail | error: %v", err)
		return
	}

	defer g.Listener.Close()

	done := make(chan bool)
	go g.acceptConnections(done)
	<-done
}

func (g *GatewayHandler) acceptConnections(done chan bool) {
	connections := make(chan net.Conn)
	handleDone := make(chan bool)
	go g.handleConnection(connections, handleDone)

	for {
		conn, err := g.Listener.Accept()
		if err != nil {
			log.Criticalf("action: accept | result: fail | error: %v", err)
			break
		}

		connections <- conn
		log.Infof("action: accept | result: success | address: %s", conn.RemoteAddr().String())
	}

	<-handleDone
	done <- true
}

func (g *GatewayHandler) handleConnection(connections chan net.Conn, done chan bool) {
	requestDones := make([]chan bool, g.MaxRequestHandlers)
	for i := range g.MaxRequestHandlers {
		requestDone := make(chan bool)
		go g.handlerRequest(connections, requestDone)
		requestDones[i] = requestDone
	}

	for i := range g.MaxRequestHandlers {
		ok := <-requestDones[i]
		if ok {
			log.Infof("action: handle_connection_accept | result: success | ok: %s", ok)
		} else {
			log.Errorf("action: handle_connection_accept | result: fail | ok: %s", ok)
		}
	}

	done <- true
}

func (g *GatewayHandler) handlerRequest(connections chan net.Conn, done chan bool) {
	for {
		log.Infof("action: handler_request | result: waiting | message: waiting for connection")
		conn := <-connections
		defer conn.Close()

		msg, err := transmission.RecvMessage(conn)
		if err != nil {
			log.Errorf("action: recv_method | result: fail | error: %v", err)
			break
		}

		if (msg.Header.Method != message.GetId) && g.SafeState.MessageHasBeenSeen(msg) {
			log.Infof(
				"action: recv_method | result: success | method: %+v | user: %s | source: %s | messageID: %s| message: already seen",
				msg.Header.Method.String(),
				msg.Header.UserID.IntoString(),
				msg.Header.Source.String(),
				msg.Header.MessageID,
			)
			continue
		}

		log.Infof("action: recv_method | result: success | method: %+v", msg)
		g.Route(conn, msg)

		if msg.Header.Method == message.GetId {
			continue
		}

		g.SafeState.Ack(msg)
		log.Debugf(
			"action: ack_message | result: success | method: %s | userID: %s | messageID: %d | source: %s",
			msg.Header.Method.String(),
			msg.Header.UserID.IntoString(),
			msg.Header.MessageID,
			msg.Header.Source.String(),
		)

		err = g.SafeState.IntoFile()
		if err != nil {
			log.Errorf("action: save_state | result: fail | error: %v", err)
		}
	}

	log.Infof("action: handler_request_exit | result: success | message: connection closed")
	done <- true
}

func (g *GatewayHandler) Route(conn net.Conn, msg *message.Message) {
	switch msg.Header.Method {
	case message.ErrorMethod:
		return
	case message.PostCredits:
		PostDataset(conn, g.queues["CREDITS"], g.MomChannel, g.SafeState)
	case message.PostMovies:
		PostDataset(conn, g.queues["MOVIES"], g.MomChannel, g.SafeState)
	case message.PostRatings:
		PostDataset(conn, g.queues["RATINGS"], g.MomChannel, g.SafeState)
	case message.GetResults:
		GetResults(conn, g.MomChannel, g.Results, &msg.Header.UserID)
	case message.GetId:
		GetId(conn, g.MomChannel, g.SafeState)
	}
}
