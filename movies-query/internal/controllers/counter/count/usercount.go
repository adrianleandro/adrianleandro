package count

type UserCount struct {
	Data map[string]*Metric
}

func NewUserCount() *UserCount {
	return &UserCount{
		Data: make(map[string]*Metric),
	}
}

func (c *UserCount) Add(key string, amount float64) {
	if _, ok := c.Data[key]; !ok {
		c.Data[key] = NewMetric()
	}

	c.Data[key].Add(amount)
}

func (c *UserCount) Merge(other *UserCount) {
	for key, metric := range other.Data {
		if _, ok := c.Data[key]; !ok {
			c.Data[key] = NewMetric()
		}
		c.Data[key].Sum += metric.Sum
		c.Data[key].N += metric.N
	}
}
