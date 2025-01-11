package image

// 圖片轉向量 - Request
type ImageToVectorRequest struct {
	Image []byte `json:"image"` // base64 encoded image
}

// 圖片轉向量 - Response
type ImageToVectorResponse struct {
	Vector    []float64 `json:"vector"`
	Error     string    `json:"error, omitempty"`
	ProcessID string    `json:"process_id"`
}
