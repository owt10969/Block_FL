// H:\Workspace\Go-FederatedLearning\internal\app\container\container.go
package container

import (
	"Go-FederatedLearning/internal/app/builder"
	imagehandler "Go-FederatedLearning/internal/handler/image"
	printhandler "Go-FederatedLearning/internal/handler/print"
	globalhanlder "Go-FederatedLearning/internal/handler/global"
)

type HandlerContainer struct {
	PrintHandler *printhandler.Handler
	ImageHandler *imagehandler.Handler
	GlobalHandler *globalhandler.Handler
}

func NewHandlerContainer(service *builder.ServiceContainer) *HandlerContainer {
	return &HandlerContainer{
		PrintHandler: printhandler.NewHandler(service.PrintService),
		ImageHandler: imagehandler.NewHandler(service.ImageService),
		GlobalHandler: globalhandler.NewHander(service.GlobalService),
	}
}
