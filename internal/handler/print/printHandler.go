package print

import (
	"net/http"
	printsvc "Go-FederatedLearning/internal/service/print"
	"github.com/gin-gonic/gin"
)

type Handler struct {
	printService printsvc.Service
}

func NewHandler(printService printsvc.Service) *Handler {
	return &Handler{
		printService: printService,
	}
}

func (h *Handler) HandlePrint(c *gin.Context) {
	var req PrintRequest 
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, PrintResponse{
			Status: false,
			Message: "Invalid request format",
		})
		return 
	}

	err := h.printService.PrintMessage(req.Message, req.ID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, PrintResponse{
			Status: false,
			Message: "Failed to print message.",
		})
		return 
	}

	c.JSON(http.StatusOK, PrintResponse{
		Status: true,
		Message: "Message printed successfully.",
	})
}