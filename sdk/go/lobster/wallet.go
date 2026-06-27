package lobster

import "fmt"

// Wallet 钱包管理器
type Wallet struct {
	client *Client
}

// WalletInfo 钱包信息
type WalletInfo struct {
	NodeID    string  `json:"node_id"`
	Address   string  `json:"address"`
	Balance   float64 `json:"balance"`
	Staked    float64 `json:"staked"`
	CreatedAt string  `json:"created_at"`
}

// BalanceResponse 余额响应
type BalanceResponse struct {
	NodeID  string  `json:"node_id"`
	Currency string `json:"currency"`
	Balance float64 `json:"balance"`
	Staked  float64 `json:"staked"`
}

// TransferRequest 转账请求
type TransferRequest struct {
	ToNodeID string  `json:"to_node_id"`
	Amount   float64 `json:"amount"`
	Currency string  `json:"currency,omitempty"`
	Memo     string  `json:"memo,omitempty"`
}

// Transaction 交易
type Transaction struct {
	TxID      string  `json:"tx_id"`
	FromNodeID string `json:"from_node_id"`
	ToNodeID  string  `json:"to_node_id"`
	Amount    float64 `json:"amount"`
	Currency  string  `json:"currency"`
	Timestamp string  `json:"timestamp"`
}

// Create 创建钱包
func (w *Wallet) Create(nodeID string) (*WalletInfo, error) {
	var result WalletInfo
	err := w.client.Post("/wallet", map[string]string{"node_id": nodeID}, &result)
	if err != nil {
		return nil, fmt.Errorf("create wallet: %w", err)
	}
	return &result, nil
}

// Get 获取钱包信息
func (w *Wallet) Get(nodeID string) (*WalletInfo, error) {
	var result WalletInfo
	err := w.client.Get(fmt.Sprintf("/wallet?node_id=%s", nodeID), &result)
	if err != nil {
		return nil, fmt.Errorf("get wallet: %w", err)
	}
	return &result, nil
}

// Balance 获取余额
func (w *Wallet) Balance(nodeID string, currency string) (*BalanceResponse, error) {
	var result BalanceResponse
	path := fmt.Sprintf("/wallet/%s/balance", nodeID)
	if currency != "" {
		path += fmt.Sprintf("?currency=%s", currency)
	}
	err := w.client.Get(path, &result)
	if err != nil {
		return nil, fmt.Errorf("get balance: %w", err)
	}
	return &result, nil
}

// Transfer 转账
func (w *Wallet) Transfer(nodeID string, req TransferRequest) (*Transaction, error) {
	var result Transaction
	err := w.client.Post(fmt.Sprintf("/wallet/%s/transfer", nodeID), req, &result)
	if err != nil {
		return nil, fmt.Errorf("transfer: %w", err)
	}
	return &result, nil
}

// Stake 质押
func (w *Wallet) Stake(nodeID string, amount float64) (string, error) {
	var result struct {
		Message string `json:"message"`
	}
	err := w.client.Post(fmt.Sprintf("/wallet/%s/stake", nodeID), map[string]float64{"amount": amount}, &result)
	if err != nil {
		return "", fmt.Errorf("stake: %w", err)
	}
	return result.Message, nil
}

// Unstake 解除质押
func (w *Wallet) Unstake(nodeID string, amount float64) (string, error) {
	var result struct {
		Message string `json:"message"`
	}
	err := w.client.Post(fmt.Sprintf("/wallet/%s/unstake", nodeID), map[string]float64{"amount": amount}, &result)
	if err != nil {
		return "", fmt.Errorf("unstake: %w", err)
	}
	return result.Message, nil
}

// Mine 挖矿
func (w *Wallet) Mine(nodeID string, emergenceScore float64) (string, error) {
	var result struct {
		Message string `json:"message"`
	}
	err := w.client.Post(fmt.Sprintf("/node/%s/mine", nodeID), map[string]float64{"emergence_score": emergenceScore}, &result)
	if err != nil {
		return "", fmt.Errorf("mine: %w", err)
	}
	return result.Message, nil
}