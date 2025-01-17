// internal/service/image/imageService.go
package image

import (
	imageTypes "Go-FederatedLearning/internal/type/image"
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
	ConvertToVector(ctx context.Context, imgBytes []byte) (*imageTypes.ImageToVectorResponse, error)
}

type service struct {
	// 可以添加依賴，例如：
	// modelClient ModelClient
	// config     *Config
}

func NewService() Service {
	return &service{}
}

// logic - Img to Base64 encode
func (s *service) ConvertToVector(ctx context.Context, imgBytes []byte) (*imageTypes.ImageToVectorResponse, error) {
	// 1. 解碼圖片
	img, _, err := stdimage.Decode(bytes.NewReader(imgBytes))
	if err != nil {
		return nil, fmt.Errorf("failed to decode image: %w", err)
	}

	// 2. 獲取圖片資訊
	bounds := img.Bounds()
	width := bounds.Max.X
	height := bounds.Max.Y

	// 3. 計算特徵向量
	// 這裡是示例邏輯，實際應用中可能需要更複雜的圖片處理
	vector := []float64{
		float64(width),
		float64(height),
		float64(width * height),          // 面積
		float64(width) / float64(height), // 寬高比
	}

	encodedData := base64.StdEncoding.EncodeToString(imgBytes)

	// 4. 返回結果
	return &imageTypes.ImageToVectorResponse{
		Vector: vector,
		//ProcessID: fmt.Sprintf("img_%dx%d", width, height),
		ImageSize:   fmt.Sprintf("%dx%d", width, height),
		EncodeBytes: fmt.Sprintf("%v", encodedData),
	}, nil
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

