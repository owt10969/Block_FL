package print

type Service interface {
    PrintMessage(message string, id string) error
}