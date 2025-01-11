package builder

import "Go-FederatedLearning/internal/service/print"

type ServiceBuilder struct { 
	withPrint bool
	// Other service
	// withImage bool
	// withModel bool
}

type ServiceContainer struct {
	PrintService print.Service
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

// Building selected service.
func (b *ServiceBuilder) Build() (*ServiceContainer) {
	container := &ServiceContainer{}

	if b.withPrint {
		container.PrintService = print.NewService()
	}

	return container
}

