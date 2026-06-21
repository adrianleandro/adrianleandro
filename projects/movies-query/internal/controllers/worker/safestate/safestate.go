package safestate

import (
	"sync"

	"github.com/distribuidos-unrust/tp/internal/communication/message"
	"github.com/distribuidos-unrust/tp/internal/communication/serialization"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/service"
	"github.com/distribuidos-unrust/tp/internal/controllers/worker/state"
)

type SafeState struct {
	State *state.State
	Mutex *sync.Mutex
}

func NewSafeState(state *state.State) *SafeState {
	return &SafeState{
		State: state,
		Mutex: &sync.Mutex{},
	}
}

func NewSafeStateWithoutState() *SafeState {
	return &SafeState{
		State: nil,
		Mutex: &sync.Mutex{},
	}
}

func (s *SafeState) Inc() uint32 {
	s.Mutex.Lock()
	defer s.Mutex.Unlock()
	return s.State.Inc()
}

func (s *SafeState) Ack(msg *message.Message) {
	s.Mutex.Lock()
	defer s.Mutex.Unlock()
	s.State.Ack(msg)
}

func (s *SafeState) MessageHasBeenSeen(msg *message.Message) bool {
	s.Mutex.Lock()
	defer s.Mutex.Unlock()
	return s.State.MessageHasBeenSeen(msg)
}

func (s *SafeState) IntoFile() error {
	s.Mutex.Lock()
	defer s.Mutex.Unlock()
	return serialization.StateIntoFile(s.State)
}

func (s *SafeState) GetService() *service.Service {
	s.Mutex.Lock()
	defer s.Mutex.Unlock()
	return s.State.Service
}
