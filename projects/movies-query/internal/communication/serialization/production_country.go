package serialization

import (
	"encoding/json"
	"strings"

	"github.com/distribuidos-unrust/tp/internal/models"
)

func ProductionCountriesFromString(productionCountriesStr string) ([]models.ProductionCountry, error) {
	productionCountriesStr = strings.Replace(productionCountriesStr, "'", "\"", -1)
	productionCountries := make([]models.ProductionCountry, 0)
	dat := []byte(productionCountriesStr)
	if err := json.Unmarshal(dat, &productionCountries); err != nil {
		return nil, err
	}
	return productionCountries, nil
}
