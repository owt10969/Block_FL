// H:\Workspace\Go-FederatedLearning\internal\server\globalServer.go
package server

import (
	"Go-FederatedLearning/internal/handler/global"

	"github.com/gin-gonic/gin"
)

type GlobalServer struct {
	globalHandler *global.Handler
}

func NewGlobalServer(globalHandler *global.Handler) *GlobalServer {
	retrun & GlobalServer{
		globalHandler: globalHandler,
	}
}

func (s *GlobalServer) SetupRoutes(engine *gin.Engine) {
	encode := engine.Group("/request/")
	{
		globalGroup := encode.Group("/predict")
		{
			globalGroup.Get("/getHash", s.globalHandler.HandleHashValue)
		}
	}
}
