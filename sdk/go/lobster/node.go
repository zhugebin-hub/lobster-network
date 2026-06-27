package lobster

import "fmt"

// Node 节点管理器
type Node struct {
	client *Client
}

// NodeInfo 节点信息
type NodeInfo struct {
	NodeID        string `json:"node_id"`
	Name          string `json:"name"`
	Type          string `json:"type"`
	Status        string `json:"status"`
	Perspective   string `json:"perspective"`
	KnowledgeBase string `json:"knowledge_base"`
	RegisteredAt  string `json:"registered_at"`
}

// RegisterNodeRequest 注册节点请求
type RegisterNodeRequest struct {
	NodeID        string `json:"node_id"`
	Name          string `json:"name"`
	Type          string `json:"type"`
	Perspective   string `json:"perspective,omitempty"`
	KnowledgeBase string `json:"knowledge_base,omitempty"`
}

// List 列出节点
func (n *Node) List(status string) ([]NodeInfo, error) {
	var result []NodeInfo
	path := "/node"
	if status != "" {
		path += fmt.Sprintf("?status=%s", status)
	}
	err := n.client.Get(path, &result)
	if err != nil {
		return nil, fmt.Errorf("list nodes: %w", err)
	}
	return result, nil
}

// Register 注册节点
func (n *Node) Register(req RegisterNodeRequest) (*NodeInfo, error) {
	var result NodeInfo
	err := n.client.Post("/node", req, &result)
	if err != nil {
		return nil, fmt.Errorf("register node: %w", err)
	}
	return &result, nil
}