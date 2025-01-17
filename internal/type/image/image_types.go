package image

// 圖片轉向量 - Request
type ImageToVectorRequest struct {
	// Image []byte `json:"image"` // base64 encoded image
	Data     string        `json:"data"`     // base64 encoded image
	Format   string        `json:"format"`   // jpeg, png, etc..
	Metadata ImageMetaData `json:"metadata"` // Image metadata

}

// 圖片轉向量 - Response
type ImageToVectorResponse struct {
	Vector      []float64 `json:"vector"`
	Error       string    `json:"error, omitempty"`
	ImageSize   string    `json:"process_id"`
	EncodeBytes string    `json:"EncodeBytes"`
}

type ImageMetaData struct {
	width       int    `json:"imgWidth"`
	height      int    `json:"imgHeight"`
	timestamp   string `json:"requestImgTimestamp"`
	colorspace  string `json:"imgColorSpace"`
	orientation string `json:"imgOrientation"`
}
