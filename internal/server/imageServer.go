// H:\Workspace\Go-FederatedLearning\internal\server\imageServer.go
package server

import (
	"Go-FederatedLearning/internal/handler/image"

	"github.com/gin-gonic/gin"
)

type ImageServer struct {
	imageHandler *image.Handler
}

func NewImageServer(imageHandler *image.Handler) *ImageServer {
	return &ImageServer{
		imageHandler: imageHandler,
	}
}

func (s *ImageServer) SetupRoutes(engine *gin.Engine) {
	encode := engine.Group("/encode/image")
	{
		imageGroup := encode.Group("/print")
		{
			imageGroup.GET("/raw", s.imageHandler.HandleImageToVector)
		}
	}
}
