// internal/handler/global/globalHandler.go
package global

import (
	globalService "Go-FederatedLearning/internal/service/global"
	globalType "Go-FederatedLearning/internal/type/GlobalInfo"
	"errors"
)

type Handler struct {
	globalService globalService.Service
}

func NewHandler(globalService globalService.Service) *Handler {
	return &Handler{
		globalService: globalService,
	}
}

// 驗證Request用
func validateRequest(request *globalType.UserRequest) error {
	// UserID符合格式, Image不為空 (暫定), SessionID未過期
	if request.UserID == "" {
		return errors.New("UserID cannot be empty.")
	}
	if len(request.Image.Data) == 0 {
		return errors.New("image data cannot be empty.")
	}
	if request.Session == "" {
		return errors.New("Sessions cannot be empty.")
	}

	return nil
}

// 拆分Request -> image API (Python Model), Global API (Blockchain)

// Make hashvalue
func (h *Handler) HandleHashValue( c *gin.Context) {
	 var req globalType.UserRequest
	 
	 if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "Invalid JSON: " + err.Error(),
		})
		return
	 }

	 hxValue, err := h.globalService.ConverToHash(c.Request.Context, req)
	 if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message":　"HashValue generated",
		"Hashvalue": hxValue.HashValue
	})
}