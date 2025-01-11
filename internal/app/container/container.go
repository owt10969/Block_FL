package container

import (
	"Go-FederatedLearning/internal/app/builder"
	imagehandler "Go-FederatedLearning/internal/handler/image"
	printhandler "Go-FederatedLearning/internal/handler/print"
)

type HandlerContainer struct {
	PrintHandler *printhandler.Handler
	ImageHandler *imagehandler.Handler
}

func NewHandlerContainer(service *builder.ServiceContainer) *HandlerContainer {
	return &HandlerContainer{
		PrintHandler: printhandler.NewHandler(service.PrintService),
		ImageHandler: imagehandler.NewHandler(service.ImageService),
	}
}
