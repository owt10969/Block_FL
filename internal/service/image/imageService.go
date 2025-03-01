// internal/service/image/imageService.go
package image

import (
	imageTypes "Go-FederatedLearning/internal/type/image"
	"bytes"
	"context"
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

	// 4. 返回結果
	return &imageTypes.ImageToVectorResponse{
		Vector:    vector,
		ProcessID: fmt.Sprintf("img_%dx%d", width, height),
	}, nil
}
