package server

import (
	"Go-FederatedLearning/internal/handler/image"

	"github.com/gin-gonic/gin"
)

type ImageServer struct {
	engine       *gin.Engine
	imageHandler *image.Handler
}

func NewImageServer(imageHandler *image.Handler) *ImageServer {
	return &ImageServer{
		engine:       gin.Default(),
		imageHandler: imageHandler,
	}
}

func (s *ImageServer) SetupRoutes() {
	encode := s.engine.Group("encode/image")
	{
		imageGroup := encode.Group("/print")
		{
			imageGroup.GET("/raw", s.imageHandler.HandleImageToVector)
		}
	}
}

func (s *HTTPServer) Start(addr string) error {
	return s.engine.Run(addr)
}
