package print

type PrintResponse struct {
    Status  bool   `json:"status"`
    Message string `json:"message,omitempty"`
}