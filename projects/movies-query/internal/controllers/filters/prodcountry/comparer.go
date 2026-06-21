package prodcountry

import "github.com/distribuidos-unrust/tp/internal/models"

type ProdCountryComparer interface {
	Compare(prodCountries []models.ProductionCountry) bool
}
