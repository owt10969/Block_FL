package linebot

import (
	linebotSvc "Go-FederatedLearning/internal/service/linebot"
	"net/http"

	"github.com/gin-gonic/gin"
)

type Handler struct {
	lineBotservice linebotSvc.Service
	channelSecret  string
	channelToken   string
}

func NewHandler(botService linebotSvc.Service, channelSecret, channelToken string) *Handler {
	return &Handler{
		lineBotService: botService,
		channelSecret:  channelSecret,
		channelToken:   channelToken,
	}
}

func (h *Handler) WebhookHandler(c *gin.Context) {
	events, err := h.parseRequest(c)
	if err != nil {
		if err == linebot.ErrInvalidSignature {
			c.JSON(http.StatusBadRequest, gin.H{"error": "invalid signature"})
		} else {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		}
		return
	}

	for _, event := range events {
		if event.Type == linebot.EventTypeMessage {
			switch message := event.Message.(type) {
			case *linebot.TextMessage:
				replyContent := "你剛才說：" + message.Text
				if err := h.lineBotService.ReplyMessage(event.ReplyToken, replyContent); err != nil {
					c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
					return
				}
			}
		}
	}

	c.JSON(http.StatusOK, gin.H{"status": "ok"})
}

func (h *Handler) PushMessageHandler(c *gin.Context) {
	var req struct {
		UserID  string `json:"userId"`
		Message string `json:"message"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if err := h.lineBotService.PushMessage(req.UserID, req.Message); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"status": "message pushed"})
}

func (h *Handler) parseRequest(c *gin.Context) ([]*linebot.Event, error) {
	bot, err := linebot.New(h.channelSecret, h.channelToken)
	if err != nil {
		return nil, err
	}
	events, err := bot.ParseRequest(c.Request)
	if err != nil {
		return nil, err
	}
	return events, nil
}
