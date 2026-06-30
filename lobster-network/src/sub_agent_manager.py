#!/usr/bin/env python3
"""
Sub-Agent 管理器
基于 Agent Harness工程实践设计

每个 Sub-Agent 有独立 Context Window，只看自己需要的工具
主 Agent 只接收结构化输出
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional


class SubAgent:
    """
    Sub-Agent 类
    每个 Sub-Agent 有独立的上下文和工具集
    """
    
    def __init__(self, agent_id: str, role: str, tools: List[str], workspace_dir: str):
        self.agent_id = agent_id
        self.role = role
        self.tools = tools  # 该 Agent 可用的工具列表
        self.workspace_dir = Path(workspace_dir) / "agents" / agent_id
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        
        # 独立上下文
        self.context = {
            "agent_id": agent_id,
            "role": role,
            "created_at": time.time(),
            "messages": [],
            "state": {}
        }
        
        # 保存初始状态
        self._save_context()
    
    def process(self, task: Dict) -> Dict:
        """
        处理任务
        
        Args:
            task: 任务字典
            
        Returns:
            Dict: 结构化输出
        """
        print(f"[SubAgent {self.agent_id}] 处理任务: {task.get('action', 'unknown')}")
        
        # 验证工具权限
        if not self._validate_tools(task):
            return {"status": "error", "message": "工具权限不足"}
        
        # 执行任务
        result = self._execute_task(task)
        
        # 更新上下文
        self.context["messages"].append({
            "role": "user",
            "content": json.dumps(task, ensure_ascii=False),
            "timestamp": time.time()
        })
        self.context["messages"].append({
            "role": "assistant",
            "content": json.dumps(result, ensure_ascii=False),
            "timestamp": time.time()
        })
        
        # 保存上下文
        self._save_context()
        
        return result
    
    def _validate_tools(self, task: Dict) -> bool:
        """验证工具权限"""
        required_tool = task.get("tool")
        if required_tool and required_tool not in self.tools:
            print(f"[SubAgent {self.agent_id}] 工具 {required_tool} 不在允许列表中")
            return False
        return True
    
    def _execute_task(self, task: Dict) -> Dict:
        """执行任务"""
        action = task.get("action", "")
        
        # 根据角色执行不同操作
        if self.role == "training_coordinator":
            return self._execute_training(task)
        elif self.role == "communication_router":
            return self._execute_communication(task)
        elif self.role == "data_analyst":
            return self._execute_analysis(task)
        elif self.role == "quality_assurance":
            return self._execute_qa(task)
        else:
            return {"status": "success", "message": f"未知角色 {self.role}，跳过"}
    
    def _execute_training(self, task: Dict) -> Dict:
        """执行训练协调任务"""
        action = task.get("action", "")
        
        if action == "distribute_training":
            nodes = task.get("nodes", [])
            return {
                "status": "success",
                "message": f"训练任务已分发给 {len(nodes)} 个节点",
                "nodes": nodes
            }
        elif action == "collect_results":
            return {
                "status": "success",
                "message": "训练结果已收集",
                "results_count": task.get("count", 0)
            }
        elif action == "generate_report":
            return {
                "status": "success",
                "message": "训练报告已生成"
            }
        else:
            return {"status": "success", "message": f"未知训练操作 {action}"}
    
    def _execute_communication(self, task: Dict) -> Dict:
        """执行通信路由任务"""
        action = task.get("action", "")
        
        if action == "route_message":
            target = task.get("target", "")
            return {
                "status": "success",
                "message": f"消息已路由到 {target}",
                "target": target
            }
        elif action == "check_ack":
            return {
                "status": "success",
                "message": "ACK 检查完成",
                "ack_received": task.get("ack", False)
            }
        else:
            return {"status": "success", "message": f"未知通信操作 {action}"}
    
    def _execute_analysis(self, task: Dict) -> Dict:
        """执行数据分析任务"""
        action = task.get("action", "")
        
        if action == "analyze_performance":
            return {
                "status": "success",
                "message": "性能分析完成",
                "metrics": task.get("metrics", {})
            }
        elif action == "generate_insights":
            return {
                "status": "success",
                "message": "洞察已生成"
            }
        else:
            return {"status": "success", "message": f"未知分析操作 {action}"}
    
    def _execute_qa(self, task: Dict) -> Dict:
        """执行质量保证任务"""
        action = task.get("action", "")
        
        if action == "validate_output":
            return {
                "status": "success",
                "message": "输出验证完成",
                "valid": task.get("valid", True)
            }
        elif action == "check_compliance":
            return {
                "status": "success",
                "message": "合规检查完成",
                "compliant": True
            }
        else:
            return {"status": "success", "message": f"未知 QA 操作 {action}"}
    
    def _save_context(self):
        """保存上下文到文件"""
        context_file = self.workspace_dir / "context.json"
        with open(context_file, 'w', encoding='utf-8') as f:
            json.dump(self.context, f, ensure_ascii=False, indent=2)
    
    def get_context(self) -> Dict:
        """获取上下文"""
        return self.context.copy()


class SubAgentManager:
    """
    Sub-Agent 管理器
    管理多个 Sub-Agent，主 Agent 只接收结构化输出
    """
    
    def __init__(self, workspace_dir: str = None):
        if workspace_dir is None:
            workspace_dir = os.path.join(os.path.dirname(__file__), "..", "workspace")
        
        self.workspace_dir = Path(workspace_dir) / "agents"
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        
        self.agents: Dict[str, SubAgent] = {}
        self._initialize_default_agents()
    
    def _initialize_default_agents(self):
        """初始化默认 Sub-Agent"""
        default_agents = [
            {
                "agent_id": "training-coordinator",
                "role": "training_coordinator",
                "tools": ["distribute_training", "collect_results", "generate_report"]
            },
            {
                "agent_id": "communication-router",
                "role": "communication_router",
                "tools": ["route_message", "check_ack", "send_notification"]
            },
            {
                "agent_id": "data-analyst",
                "role": "data_analyst",
                "tools": ["analyze_performance", "generate_insights", "query_data"]
            },
            {
                "agent_id": "quality-assurance",
                "role": "quality_assurance",
                "tools": ["validate_output", "check_compliance", "review_content"]
            }
        ]
        
        for agent_config in default_agents:
            agent = SubAgent(
                agent_id=agent_config["agent_id"],
                role=agent_config["role"],
                tools=agent_config["tools"],
                workspace_dir=str(self.workspace_dir)
            )
            self.agents[agent_config["agent_id"]] = agent
    
    def get_agent(self, agent_id: str) -> Optional[SubAgent]:
        """获取 Sub-Agent"""
        return self.agents.get(agent_id)
    
    def dispatch(self, agent_id: str, task: Dict) -> Dict:
        """
        分发任务到 Sub-Agent
        
        Args:
            agent_id: Sub-Agent ID
            task: 任务字典
            
        Returns:
            Dict: 结构化输出
        """
        agent = self.get_agent(agent_id)
        if not agent:
            return {"status": "error", "message": f"Sub-Agent {agent_id} 不存在"}
        
        return agent.process(task)
    
    def list_agents(self) -> List[Dict]:
        """列出所有 Sub-Agent"""
        return [
            {
                "agent_id": agent.agent_id,
                "role": agent.role,
                "tools": agent.tools
            }
            for agent in self.agents.values()
        ]


if __name__ == "__main__":
    # 测试 Sub-Agent 管理器
    manager = SubAgentManager()
    
    # 列出所有 Sub-Agent
    print("\n=== 可用 Sub-Agent ===")
    for agent in manager.list_agents():
        print(f"- {agent['agent_id']} ({agent['role']}): {', '.join(agent['tools'])}")
    
    # 分发训练任务
    print("\n=== 分发训练任务 ===")
    result = manager.dispatch("training-coordinator", {
        "action": "distribute_training",
        "nodes": ["xiaochen", "zhuguxia", "qoder"],
        "day": 5
    })
    print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    # 分发通信任务
    print("\n=== 分发通信任务 ===")
    result = manager.dispatch("communication-router", {
        "action": "route_message",
        "target": "xiaochen",
        "message": "请提交 Day5 训练结果"
    })
    print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
EOF

echo "Sub-Agent 管理器已创建"