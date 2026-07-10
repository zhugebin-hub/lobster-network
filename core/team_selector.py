#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 团队选择器 (Team Selector)
基于能力画像、历史表现与任务需求，自动匹配最优节点组合。
作者：诸葛马 (Hermes) | 版本：V1.0 | 日期：2026-07-10
"""

import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime

@dataclass
class NodeProfile:
    """节点能力画像"""
    node_id: str
    role: str
    expertise: List[str]
    performance_score: float = 0.0
    availability: float = 1.0  # 0.0-1.0
    current_load: int = 0
    history: List[str] = field(default_factory=list)
    
    def to_dict(self):
        return asdict(self)

@dataclass
class TaskRequirement:
    """任务需求描述"""
    task_id: str
    title: str
    required_expertise: List[str]
    min_nodes: int = 1
    max_nodes: int = 3
    priority: str = "normal"  # low, normal, high, critical
    deadline: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)

class TeamSelector:
    """团队选择器核心引擎"""
    
    def __init__(self, config_path: str = "/home/admin/lobster-network/config/team_selector.json"):
        self.config_path = config_path
        self.nodes: Dict[str, NodeProfile] = {}
        self.history: List[Dict] = []
        self._load_config()
        print(f"👥 团队选择器初始化完成: {config_path}")
        
    def _load_config(self):
        """加载节点配置"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                data = json.load(f)
                for node_data in data.get("nodes", []):
                    self.nodes[node_data["node_id"]] = NodeProfile(**node_data)
        else:
            # 默认节点配置
            default_nodes = [
                {"node_id": "qoder", "role": "计算化学专家", "expertise": ["knowledge_graph", "screening", "docking"], "performance_score": 0.87, "availability": 0.9, "current_load": 2},
                {"node_id": "xiaochen", "role": "免疫学专家", "expertise": ["target_analysis", "pathway", "immunology"], "performance_score": 0.85, "availability": 0.8, "current_load": 1},
                {"node_id": "zhuguxia", "role": "工具链专家", "expertise": ["visualization", "pipeline", "dashboard"], "performance_score": 0.93, "availability": 0.7, "current_load": 3},
                {"node_id": "xiaowei", "role": "免疫疗法专家", "expertise": ["oit", "clinical", "safety"], "performance_score": 0.82, "availability": 0.95, "current_load": 1},
                {"node_id": "zhugebin", "role": "临床设计专家", "expertise": ["trial_design", "protocol", "coordination"], "performance_score": 1.0, "availability": 0.6, "current_load": 2}
            ]
            for n in default_nodes:
                self.nodes[n["node_id"]] = NodeProfile(**n)
            self._save_config()
            
    def _save_config(self):
        """保存节点配置"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump({"nodes": [n.to_dict() for n in self.nodes.values()]}, f, ensure_ascii=False, indent=2)
            
    def select_team(self, requirement: TaskRequirement) -> List[NodeProfile]:
        """根据任务需求选择最优团队"""
        candidates = []
        for node in self.nodes.values():
            # 计算匹配度
            expertise_match = len(set(node.expertise) & set(requirement.required_expertise))
            score = (expertise_match * 0.4 + 
                     node.performance_score * 0.3 + 
                     node.availability * 0.2 + 
                     (1.0 - node.current_load / 10.0) * 0.1)
            candidates.append((node, score))
            
        # 按分数排序
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        # 选择 top N
        team_size = min(requirement.max_nodes, len(candidates))
        team = [c[0] for c in candidates[:team_size]]
        
        # 记录选择历史
        self.history.append({
            "task_id": requirement.task_id,
            "timestamp": datetime.now().isoformat(),
            "selected": [n.node_id for n in team],
            "scores": {n.node_id: s for n, s in candidates[:team_size]}
        })
        
        print(f"🎯 任务 {requirement.task_id} 团队选择完成: {[n.node_id for n in team]}")
        return team
        
    def update_node_load(self, node_id: str, delta: int):
        """更新节点负载"""
        if node_id in self.nodes:
            self.nodes[node_id].current_load = max(0, self.nodes[node_id].current_load + delta)
            self._save_config()
            
    def get_team_report(self) -> Dict[str, Any]:
        """生成团队状态报告"""
        return {
            "nodes": {nid: n.to_dict() for nid, n in self.nodes.items()},
            "recent_selections": self.history[-5:]
        }

# 示例用法
if __name__ == "__main__":
    selector = TeamSelector()
    
    # 定义任务需求
    task = TaskRequirement(
        task_id="TASK_BAVI_001",
        title="台风巴威威胁分析",
        required_expertise=["pathway", "screening", "clinical"],
        min_nodes=2,
        max_nodes=3,
        priority="high"
    )
    
    # 选择团队
    team = selector.select_team(task)
    print("\n📊 选中团队详情:")
    for node in team:
        print(f"  - {node.node_id} ({node.role}): 专业={node.expertise}, 评分={node.performance_score}")
        
    # 更新负载
    for node in team:
        selector.update_node_load(node.node_id, 1)
        
    print("\n✅ 团队选择器测试完成")
