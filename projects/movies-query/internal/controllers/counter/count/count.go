package count

type Count struct {
	Data map[string]*UserCount
}

func NewCount() *Count {
	return &Count{
		Data: make(map[string]*UserCount),
	}
}

func (c *Count) Add(userID string, key string, amount float64) {
	if _, ok := c.Data[userID]; !ok {
		c.Data[userID] = NewUserCount()
	}

	c.Data[userID].Add(key, amount)
}

func (c *Count) Get(userID string) *UserCount {
	if _, ok := c.Data[userID]; !ok {
		c.Data[userID] = NewUserCount()
	}

	return c.Data[userID]
}
