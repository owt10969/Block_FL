package print

import "fmt"

type service struct {
	// TODO: database, logger, etc..
}

func NewService() Service {
	return &service{}
}

func (s *service) PrintMessage(message string, id string) error {
	fmt.Printf("Printing messasge: %s with ID: %s\n", message, id)
	return nil
}