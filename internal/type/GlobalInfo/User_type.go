package GlobalInfo

import (
	"Go-FederatedLearning/internal/type/image"
)

// 地理位置資訊
type Location struct {
	Latitude  float64 `json:"latitude"`
	Longitude float64 `json:"longitude"`
}

// 裝置資訊
type DeviceInfo struct {
	Model        string  `json:"model"`
	OS           string  `json:"os"`
	BatteryLevel float64 `json:"battery_level"`
	Network      string  `json:"network"`
}

// 預處理選項 - 裁切 (crop)
type CropOptions struct {
	X      int `json:"x"`
	Y      int `json:"y"`
	Width  int `json:"width"`
	Height int `json:"height"`
}

// 預處理選項
type PreprocessingOptions struct {
	Crop             CropOptions `json:"crop"`
	AdjustBrightness bool        `json:"adjust_brightness"`
}

// Settings 裡的參數
type Settings struct {
	ReturnConfidence     bool                 `json:"return_confidence"`
	MaxPredictions       int                  `json:"max_predictions"`
	PreprocessingOptions PreprocessingOptions `json:"preprocessing_options"`
}

// 除錯資訊
type DebugInfo struct {
	EnableLogging bool   `json:"enable_logging"`
	LogLevel      string `json:"log_level"`
}

// 最上層的 UserRequest
type UserRequest struct {
	DeviceID       string                     `json:"device_id"`
	UserID         string                     `json:"user_id"`
	SessionID      string                     `json:"session_id"`
	Image          image.ImageToVectorRequest `json:"image"` // 從 image_types.go 引入
	Location       Location                   `json:"location"`
	DeviceInfo     DeviceInfo                 `json:"device_info"`
	Settings       Settings                   `json:"settings"`
	Context        string                     `json:"context"`
	NetworkQuality string                     `json:"network_quality"`
	Debug          DebugInfo                  `json:"debug"`
}

type UserResponse struct {
}
