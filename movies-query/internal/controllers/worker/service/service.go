package service

import "fmt"

type ServiceName uint32
type ServiceID uint32

const (
	AverageRatio ServiceName = iota
	Client
	ContainsCountryAr
	ContainsCountryEs
	CreditDispatcher
	CreditsUnwinder
	CreditSplitter
	FilterByYearAfter2000
	FilterByYearBefore2010
	Gateway
	MovieCreditJoiner
	MovieCreditSharder
	MovieRatingJoiner
	MovieRatingSharder
	MoviesSelector
	OnlyOneProdCountry
	RatingDispatcher
	RatingSelector
	RatingSplitter
	Rentability
	ResultQ1
	ResultQ2
	ResultQ3
	ResultQ4
	ResultQ5
	Sentiment
	TopAppearances
	TopRanking
	TopRating
	YearSelector
)

var ServiceNames = map[ServiceName]string{
	AverageRatio:           "average_ratio",
	Client:                 "client",
	ContainsCountryAr:      "containscountry_ar",
	ContainsCountryEs:      "containscountry_es",
	CreditDispatcher:       "creditdispatcher",
	CreditsUnwinder:        "credits_unwinder",
	CreditSplitter:         "creditsplitter",
	FilterByYearAfter2000:  "filter_by_year_after_2000",
	FilterByYearBefore2010: "filter_by_year_before_2010",
	Gateway:                "gateway",
	MovieCreditJoiner:      "moviecreditjoiner",
	MovieCreditSharder:     "moviecreditsharder",
	MovieRatingJoiner:      "movieratingjoiner",
	MovieRatingSharder:     "movieratingsharder",
	MoviesSelector:         "moviesselector",
	OnlyOneProdCountry:     "onlyoneprodcountry",
	RatingDispatcher:       "ratingdispatcher",
	RatingSelector:         "ratingselector",
	RatingSplitter:         "ratingsplitter",
	Rentability:            "rentability",
	ResultQ1:               "resultq1",
	ResultQ2:               "resultq2",
	ResultQ3:               "resultq3",
	ResultQ4:               "resultq4",
	ResultQ5:               "resultq5",
	Sentiment:              "sentiment",
	TopAppearances:         "top_appearances",
	TopRanking:             "top_ranking",
	TopRating:              "top_rating",
	YearSelector:           "yearselector",
}

func ReverseServiceMap(m map[ServiceName]string) map[string]ServiceName {
	reversed := make(map[string]ServiceName)
	for k, v := range m {
		reversed[v] = k
	}
	return reversed
}

func ServiceNameFromString(name string) ServiceName {
	return ReverseServiceMap(ServiceNames)[name]
}

func (s ServiceName) String() string {
	return ServiceNames[s]
}

type Service struct {
	Name ServiceName
	ID   ServiceID
}

func NewService(name ServiceName, id ServiceID) *Service {
	return &Service{
		Name: name,
		ID:   id,
	}
}

func (s *Service) String() string {
	return s.Name.String() + "_" + fmt.Sprint(s.ID)
}
