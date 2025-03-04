package linebot

type Service interface {
	ReplyMessage(replyToken, message string) error
	PushMessage(userID, message string) error
}
