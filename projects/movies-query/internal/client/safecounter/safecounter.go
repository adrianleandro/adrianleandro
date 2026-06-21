package safecounter

import "sync"

type SafeCounter struct {
	counter uint32
	mutex   sync.Mutex
}

func NewSafeCounter() *SafeCounter {
	return &SafeCounter{
		counter: 0,
		mutex:   sync.Mutex{},
	}
}

func (sc *SafeCounter) Increment() uint32 {
	sc.mutex.Lock()
	defer sc.mutex.Unlock()
	sc.counter++
	return sc.counter
}
