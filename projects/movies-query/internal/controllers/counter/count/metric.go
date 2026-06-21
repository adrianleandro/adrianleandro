package count

type Metric struct {
	Sum float64
	N   float64
}

func NewMetric() *Metric {
	return &Metric{
		Sum: 0,
		N:   0,
	}
}

func (m *Metric) Add(value float64) {
	m.Sum += value
	m.N++
}

func (m *Metric) GetAverage() float64 {
	if m.N == 0 {
		return 0
	}
	return m.Sum / m.N
}
