// H:\Workspace\Go-FederatedLearning\internal\server\printServer.go
package server

import (
	"Go-FederatedLearning/internal/handler/print"

	"github.com/gin-gonic/gin"
)

type PrintServer struct {
	printHandler *print.Handler
}

func NewHTTPServer(printHandler *print.Handler) *PrintServer {
	return &PrintServer{
		printHandler: printHandler,
	}
}

func (s *PrintServer) SetupRoutes(engine *gin.Engine) {
	v1 := engine.Group("/api/v1")
	{
		printGroup := v1.Group("/print")
		{
			printGroup.POST("/message", s.printHandler.HandlePrint)
		}
	}
}
