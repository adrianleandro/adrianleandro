package prodcountry

import (
	"strings"

	"github.com/distribuidos-unrust/tp/internal/models"
)

type ContainsCountryComparer struct {
	Country string
}

func NewContainsCountryComparer(country string) *ContainsCountryComparer {
	return &ContainsCountryComparer{Country: country}
}
func (c *ContainsCountryComparer) Compare(prodCountries []models.ProductionCountry) bool {
	for _, prod := range prodCountries {
		if strings.EqualFold(prod.Name, c.Country) {
			return true
		}
	}
	return false
}
