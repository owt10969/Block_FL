package server

import (
	"Go-FederatedLearning/internal/handler/print"

	"github.com/gin-gonic/gin"
)

type HTTPServer struct {
	engine       *gin.Engine
	printHandler *print.Handler
}

func NewHTTPServer(printHandler *print.Handler) *HTTPServer {
	return &HTTPServer{
		engine:       gin.Default(),
		printHandler: printHandler,
	}
}

func (s *HTTPServer) SetupRoutes() {
	v1 := s.engine.Group("/api/v1")
	{
		printGroup := v1.Group("/print")
		{
			printGroup.POST("/message", s.printHandler.HandlePrint)
		}
	}
}

func (s *HTTPServer) Start(addr string) error {
	return s.engine.Run(addr)
}
