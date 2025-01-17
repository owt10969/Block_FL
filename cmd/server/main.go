// H:\Workspace\Go-FederatedLearning\cmd\server\main.go
package main

import (
	"Go-FederatedLearning/internal/app/builder"
	"Go-FederatedLearning/internal/app/container"
	"Go-FederatedLearning/internal/server"
	"log"

	"github.com/gin-gonic/gin"
)

func main() {
	// Builder Pattern
	service := builder.NewServiceBuilder().
		WithPrintService().
		WithImageService().
		WithGlobalService().
		Build()

	// Build Handler
	handlers := container.NewHandlerContainer(service)

	// Create a single Gin engine
	engine := gin.Default()

	// Set & Start Server
	imageServer := server.NewImageServer(handlers.ImageHandler)
	imageServer.SetupRoutes(engine)

	printServer := server.NewHTTPServer(handlers.PrintHandler)
	printServer.SetupRoutes(engine)

	globalServer := server.NewHTTPServer(handlers.GlobalHandler)
	globalServer.SetupRoutes(engine)

	if err := engine.Run(":8080"); err != nil {
		log.Fatal("Server failed to start:", err)
	}
}
