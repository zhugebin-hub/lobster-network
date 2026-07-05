package lobster

import "fmt"

// Governance 治理管理器
type Governance struct {
	client *Client
}

// ProposalInfo 提案信息
type ProposalInfo struct {
	ProposalID string  `json:"proposal_id"`
	Title      string  `json:"title"`
	Description string `json:"description"`
	CreatorID  string  `json:"creator_id"`
	Status     string  `json:"status"`
	ForVotes   float64 `json:"for_votes"`
	AgainstVotes float64 `json:"against_votes"`
	CreatedAt  string  `json:"created_at"`
}

// CreateProposalRequest 创建提案请求
type CreateProposalRequest struct {
	Title       string `json:"title"`
	Description string `json:"description"`
	ProposalType string `json:"proposal_type,omitempty"`
}

// VoteRequest 投票请求
type VoteRequest struct {
	VoterID string `json:"voter_id"`
	Option  string `json:"option"`
	Reason  string `json:"reason,omitempty"`
}

// List 列出提案
func (g *Governance) List(status string) ([]ProposalInfo, error) {
	var result []ProposalInfo
	path := "/proposal"
	if status != "" {
		path += fmt.Sprintf("?status=%s", status)
	}
	err := g.client.Get(path, &result)
	if err != nil {
		return nil, fmt.Errorf("list proposals: %w", err)
	}
	return result, nil
}

// Create 创建提案
func (g *Governance) Create(req CreateProposalRequest) (*ProposalInfo, error) {
	var result ProposalInfo
	err := g.client.Post("/proposal", req, &result)
	if err != nil {
		return nil, fmt.Errorf("create proposal: %w", err)
	}
	return &result, nil
}

// Vote 投票
func (g *Governance) Vote(proposalID string, req VoteRequest) error {
	return g.client.Post(fmt.Sprintf("/proposal/%s/vote", proposalID), req, nil)
}

// CheckResult 检查提案结果
func (g *Governance) CheckResult(proposalID string) (string, error) {
	var result struct {
		Status string `json:"status"`
		Message string `json:"message"`
	}
	err := g.client.Post(fmt.Sprintf("/proposal/%s/check", proposalID), nil, &result)
	if err != nil {
		return "", fmt.Errorf("check result: %w", err)
	}
	return result.Message, nil
}

// Execute 执行提案
func (g *Governance) Execute(proposalID string) (string, error) {
	var result struct {
		Message string `json:"message"`
	}
	err := g.client.Post(fmt.Sprintf("/proposal/%s/execute", proposalID), nil, &result)
	if err != nil {
		return "", fmt.Errorf("execute proposal: %w", err)
	}
	return result.Message, nil
}