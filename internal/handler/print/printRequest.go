package print

type PrintRequest struct {
    Message string `json:"message" binding:"required"`
    ID      string `json:"id" binding:"required"`
}