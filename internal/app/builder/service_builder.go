package builder

import (
	"Go-FederatedLearning/internal/service/linebot"
	"Go-FederatedLearning/internal/service/print"
)

type ServiceBuilder struct {
	withPrint   bool
	withImage   bool
	withLineBot bool
	// Other service
	// withImage bool
	// withModel bool
}

type ServiceContainer struct {
	PrintService   print.Service
	ImageService   image.Service
	LineBotService linebot.Service
	// Other service..
}

func NewServiceBuilder() *ServiceBuilder {
	return &ServiceBuilder{}
}

// Start PrintService with optional.
func (b *ServiceBuilder) WithPrintService() *ServiceBuilder {
	b.withPrint = true
	return b
}

// Start LineBotService with optional.
func (b *ServiceBuilder) WithLineBotService() *ServiceBuilder {
	b.withLineBot = true
	return b
}

// Building selected service.
func (b *ServiceBuilder) Build() *ServiceContainer {
	container := &ServiceContainer{}

	if b.withPrint {
		container.PrintService = print.NewService()
	}
	if b.withImage {
		container.ImageService = image.NewService()
	}
	if b.withLineBot {
		channelSecret := os.Getenv("LINE_CHANNEL_SECRET")
		channelToken := os.Getenv("LINE_CHANNEL_TOKEN")

		botsvc, err := linebot.NewService(channelSecret, channelToken)
		if err != nil {
			panic(err)
		}
		container.LineBotService = botsvc
	}

	return container
}

func (b)