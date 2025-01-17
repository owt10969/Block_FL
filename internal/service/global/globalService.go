// internal/service/global/globalService.go
package global

import (
	Request "Go-FederatedLearning/internal/type/GlobalInfo"
	txInput "Go-FederatedLearning/internal/type/Blockchain"
	"bytes"
	"context"
	"encoding/base64"
	"encoding/hex"
	"crypto/sha256"
	"fmt"
	stdimage "image"
	_ "image/jpeg"
	_ "image/png"
)

// Service 定義服務介面
type Service interface {
	// TODO
}

type service struct {
	// TODO
}

func NewSerivce() Service {
	return &service{}
}

// logic - User info to hash-value (contain img).
func (s * service) ConverToHash(ctx, context.Context, request Request.UserRequest) (*txInput.transaction, error) {
	// 1. 提取需要資訊 -> DeviceID, UserID, Image, Context
	device_id := request.DeviceID
	user_id := request.UserID
	image := request.Image
	context := request.Context

	// 2. 雜湊
	hash := sha256.New() 
	hash.Write([]byte(device_id))
	hash.Write([]byte(user_id))
	hash.Write([]byte(image))
	hash.Write([]byte(context))
	hashBytes := hash.Sum(nil)
	hashString := hex.EncodeToString(hashBytes)

	// 3.回傳Result
	return &txInput.transaction{
		UserID: userID,
		HashValue: hashString,
	}, nil
}