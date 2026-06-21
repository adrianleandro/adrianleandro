package models

type Movie struct {
	Budget              string
	Genres              string
	Id                  string
	Overview            string
	ProductionCountries string
	ReleaseDate         string
	Revenue             string
	Title               string
}

func NewMovie(
	budget string,
	genres string,
	id string,
	overview string,
	productionCountries string,
	releaseDate string,
	revenue string,
	title string) *Movie {
	return &Movie{
		Budget:              budget,
		Genres:              genres,
		Id:                  id,
		Overview:            overview,
		ProductionCountries: productionCountries,
		ReleaseDate:         releaseDate,
		Revenue:             revenue,
		Title:               title,
	}
}
