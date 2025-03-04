package linebot

import (
	"fmt"
	"github.com/line/line-bot-sdk-go/linebot"
)

type service struct {
	bot *linebot.Client
}

func NewSerivce(channelSecret, channelToken string) (Service, error) {
	bot, err := linebot.New(channelSecret, channelToken)
	if err != nil {
		return nil, fmt.Errorf("failed to create line-bot client: %w", err)
	}
	return &service(bot: bot), nil
}

func (s *service) ReplyMessage(replyToken, message string) error {
	if _, err := s.bot.ReplyMessage(
		replyToken,
		linebot.NewTextMessage(message),
	).Do(); err != nil {
		return err
	}
	return nil
}

func (s *service) PushMessage(userID, message string) error {
	if _, err := s.bot.PushMessage(
		userID,
		linebot.NewTextMessage(message),
	).Do(); err != nil {
		return err
	}
	return nil
}