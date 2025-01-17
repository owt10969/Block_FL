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
}

// 拆分Request -> image API (Python Model), Global API (Blockchain)
