package container

import (
	"Go-FederatedLearning/internal/app/builder"
	imagehandler "Go-FederatedLearning/internal/handler/image"
	linebotHandler "Go-FederatedLearning/internal/handler/linebot"
	printhandler "Go-FederatedLearning/internal/handler/print"
	"Go-FederatedLearning/internal/service/linebot"
	"os"
)

type HandlerContainer struct {
	PrintHandler   *printhandler.Handler
	ImageHandler   *imagehandler.Handler
	lineBotHandler *linebotHandler.Handler
}

type ServiceContainer interface {
	GetLineBotService() linebot.Service
}

func NewHandlerContainer(service *builder.ServiceContainer) *HandlerContainer {
	lineBotHandler := linebotHandler.NewHandler(
		svcs.LineBotService,
		os.Getenv("LINE_CHANNEL_SECRET"),
		os.Getenv("LINE_CHANNEL_TOKEN"),
	)

	return &HandlerContainer{
		PrintHandler:   printhandler.NewHandler(service.PrintService),
		ImageHandler:   imagehandler.NewHandler(service.ImageService),
		LineBotHandler: lineBotHandler,
	}
}
