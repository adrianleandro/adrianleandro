package request

type Request interface {
	Run(response chan error)
}
