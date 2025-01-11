package internal/

type Intiializer struct { 
	config *config.Config
}

func NewInitializer(cfg *config.Config) *Initialize {
	return &Initializer{config: cfg}
}

// Initialize 封裝所有初始化邏輯
func (i *Initializer) Initialize() (*Container, error) {
	
}