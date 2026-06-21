package message

type Method uint32

const (
	ErrorMethod Method = iota
	NullMethod
	GetId
	PostCredits
	PostMovies
	PostRatings
	GetResults
	Records
	Ranking
	Join
	Count
	ResultQuery1
	ResultQuery2
	ResultQuery3
	ResultQuery4
	ResultQuery5
)

func (method Method) String() string {
	switch method {
	case ErrorMethod:
		return "ErrorMethod"
	case NullMethod:
		return "NullMethod"
	case GetId:
		return "GetId"
	case PostCredits:
		return "PostCredits"
	case PostMovies:
		return "PostMovies"
	case PostRatings:
		return "PostRatings"
	case GetResults:
		return "GetResults"
	case Records:
		return "Records"
	case Ranking:
		return "Ranking"
	case Join:
		return "Join"
	case Count:
		return "Count"
	case ResultQuery1:
		return "ResultQuery1"
	case ResultQuery2:
		return "ResultQuery2"
	case ResultQuery3:
		return "ResultQuery3"
	case ResultQuery4:
		return "ResultQuery4"
	case ResultQuery5:
		return "ResultQuery5"
	default:
		panic("unknown method")
	}
}
