// H:\Workspace\Go-FederatedLearning\internal\app\builder\service_builder.go
package builder

import (
	"Go-FederatedLearning/internal/service/global"
	"Go-FederatedLearning/internal/service/image"
	"Go-FederatedLearning/internal/service/print"
)

type ServiceBuilder struct {
	withPrint  bool
	withImage  bool
	withGlobal bool
	// Other service
	// withImage bool
	// withModel bool
}

type ServiceContainer struct {
	PrintService  print.Service
	ImageService  image.Service
	GlobalService global.Service
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

// Start ImageService with optional.
func (b *ServiceBuilder) WithImageService() *ServiceBuilder {
	b.withImage = true
	return b
}

func (b *ServiceBuildere) WithGlobalService() *ServiceBuilder {
	b.withGlobal = true
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

	if b.withGlobal {
		container.GlobalService = global.NewService()
	}

	return container
}
