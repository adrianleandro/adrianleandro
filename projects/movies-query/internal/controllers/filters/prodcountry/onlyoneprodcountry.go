package prodcountry

import "github.com/distribuidos-unrust/tp/internal/models"

type OnlyOneProdCountryComparer struct {
}

func NewOnlyOneProdCountryComparer() *OnlyOneProdCountryComparer {
	return &OnlyOneProdCountryComparer{}
}
func (c *OnlyOneProdCountryComparer) Compare(prodCountries []models.ProductionCountry) bool {
	return len(prodCountries) == 1
}
