package main

import (
	"Go-FederatedLearning/internal/app/builder"
	"Go-FederatedLearning/internal/app/container"
	"Go-FederatedLearning/internal/server"
	"log"
)

func main() {
	// Builder Pattern
	service := builder.NewServiceBuilder().
		WithPrintService().
		WithImageService().
		WithImageService
	Build()

	// Build Handler
	handlers := container.NewHandlerContainer(service)

	// Set & Start Server
	httpServer := server.NewHTTPServer(handlers.PrintHandler)
	httpServer.SetupRoutes()

	if err := httpServer.Start(":8080"); err != nil {
		log.Fatal("Server failed to start:", err)
	}
}
