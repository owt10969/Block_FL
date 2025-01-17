// internal/handler/image/imageHandler.go
package image

import (
	imageService "Go-FederatedLearning/internal/service/image"
	imageTypes "Go-FederatedLearning/internal/type/image"
	"bytes"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"

	"github.com/gin-gonic/gin"
)

const (
	maxFileSize = 10 << 20 // 10MB limit
)

type Handler struct {
	imageService imageService.Service
}

func NewHandler(imageService imageService.Service) *Handler {
	return &Handler{
		imageService: imageService,
	}
}

// 驗證Image File用
func validateImageFile(file *multipart.FileHeader) error {
	// 檢查文件大小
	if file.Size > maxFileSize {
		return fmt.Errorf("file too large, max size is %d bytes", maxFileSize)
	}

	// 檢查文件類型
	contentType := file.Header.Get("Content-Type")
	if contentType != "image/jpeg" && contentType != "image/png" {
		return fmt.Errorf("invalid file type: %s, only support jpeg/png", contentType)
	}

	return nil
}

// 讀取Image File用
func readImageFile(file *multipart.FileHeader) ([]byte, error) {
	openedFile, err := file.Open()
	if err != nil {
		return nil, fmt.Errorf("failed to open file: %w", err)
	}
	defer openedFile.Close()

	buffer := bytes.NewBuffer(nil)
	if _, err := io.Copy(buffer, openedFile); err != nil {
		return nil, fmt.Errorf("failed to read file: %w", err)
	}

	return buffer.Bytes(), nil
}

// 處理Image -> Vector(向量) Function (Call by imageServer.go)
func (h *Handler) HandleImageToVector(c *gin.Context) {
	// 1. 獲取上傳的文件
	file, err := c.FormFile("image")
	if err != nil {
		c.JSON(http.StatusBadRequest, imageTypes.ImageToVectorResponse{
			Error: "no image file uploaded",
		})
		return
	}

	// 2. 驗證文件
	if err := validateImageFile(file); err != nil {
		// Logic function will call from imageService.go
		c.JSON(http.StatusBadRequest, imageTypes.ImageToVectorResponse{
			Error: err.Error(),
		})
		return
	}

	// 3. 讀取文件內容
	imageData, err := readImageFile(file)
	//fmt.Printf("imageData: %v", imageData)
	if err != nil {
		c.JSON(http.StatusInternalServerError, imageTypes.ImageToVectorResponse{
			Error: err.Error(),
		})
		return
	}

	// 4. 調用服務處理圖片
	result, err := h.imageService.ConvertToVector(c.Request.Context(), imageData)
	if err != nil {
		c.JSON(http.StatusInternalServerError, imageTypes.ImageToVectorResponse{
			Error: err.Error(),
		})
		return
	}

	// 5. 返回結果
	c.JSON(http.StatusOK, result)
}
