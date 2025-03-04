package server

import (
	"github.com/gin-gonic/gin"
)

type LineBotServer struct {
	engine         *gin.Engine
	lineBotHandler *linebotHandler.Handler
}

func NewLineBotServer(handler *linebotHandler.Handler) *LineBotServer {
	return &LineBotServer{
		engine:         gin.Default(),
		lineBotHandler: handler,
	}
}

func (s *LineBotServer) SetupRoutes() {
	s.engine.POST("/line/webhook", s.lineBotHandler.WebhookHandler)
	s.engine.POST("/line/push", s.lineBotHandler.PushMessageHandler)
}

func (s *LineBotServer) Start(addr string) error {
	s.SetupRoutes()
	return s.engine.Run(addr)
}
