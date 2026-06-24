package lobster

import "fmt"

// Task 任务管理器
type Task struct {
	client *Client
}

// TaskInfo 任务信息
type TaskInfo struct {
	TaskID      string  `json:"task_id"`
	Title       string  `json:"title"`
	Description string  `json:"description"`
	PublisherID string  `json:"publisher_id"`
	AssigneeID  string  `json:"assignee_id"`
	Status      string  `json:"status"`
	RewardAmount float64 `json:"reward_amount"`
	CreatedAt   string  `json:"created_at"`
}

// CreateTaskRequest 创建任务请求
type CreateTaskRequest struct {
	Title       string  `json:"title"`
	Description string  `json:"description"`
	RewardAmount float64 `json:"reward_amount,omitempty"`
	TaskType    string  `json:"task_type,omitempty"`
}

// ClaimTaskRequest 领取任务请求
type ClaimTaskRequest struct {
	NodeID string `json:"node_id"`
}

// SubmitTaskRequest 提交任务请求
type SubmitTaskRequest struct {
	Result string `json:"result"`
}

// ReviewTaskRequest 审核任务请求
type ReviewTaskRequest struct {
	ReviewerID string `json:"reviewer_id"`
	Approved   bool   `json:"approved"`
	Feedback   string `json:"feedback,omitempty"`
}

// List 列出任务
func (t *Task) List(status string) ([]TaskInfo, error) {
	var result []TaskInfo
	path := "/task"
	if status != "" {
		path += fmt.Sprintf("?status=%s", status)
	}
	err := t.client.Get(path, &result)
	if err != nil {
		return nil, fmt.Errorf("list tasks: %w", err)
	}
	return result, nil
}

// Create 创建任务
func (t *Task) Create(req CreateTaskRequest) (*TaskInfo, error) {
	var result TaskInfo
	err := t.client.Post("/task", req, &result)
	if err != nil {
		return nil, fmt.Errorf("create task: %w", err)
	}
	return &result, nil
}

// Claim 领取任务
func (t *Task) Claim(taskID string, req ClaimTaskRequest) (*TaskInfo, error) {
	var result TaskInfo
	err := t.client.Post(fmt.Sprintf("/task/%s/claim", taskID), req, &result)
	if err != nil {
		return nil, fmt.Errorf("claim task: %w", err)
	}
	return &result, nil
}

// Submit 提交任务
func (t *Task) Submit(taskID string, req SubmitTaskRequest) (*TaskInfo, error) {
	var result TaskInfo
	err := t.client.Post(fmt.Sprintf("/task/%s/submit", taskID), req, &result)
	if err != nil {
		return nil, fmt.Errorf("submit task: %w", err)
	}
	return &result, nil
}

// Review 审核任务
func (t *Task) Review(taskID string, req ReviewTaskRequest) (*TaskInfo, error) {
	var result TaskInfo
	err := t.client.Post(fmt.Sprintf("/task/%s/review", taskID), req, &result)
	if err != nil {
		return nil, fmt.Errorf("review task: %w", err)
	}
	return &result, nil
}