#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 · 蜂群计划 (Project Swarm)
实现去中心化项目提案、自主竞标与动态组队。
作者：诸葛马 (Hermes) | 版本：V1.0 | 日期：2026-07-11
"""

import json
import os
import time
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict

from core.memory import ThreeLayerMemory
from core.team_selector import TeamSelector, TaskRequirement, NodeProfile

@dataclass
class ProjectProposal:
    """项目提案"""
    proposal_id: str
    proposer: str
    title: str
    description: str
    required_expertise: List[str]
    estimated_lbc: int
    deadline: str
    status: str = "open"  # open, bidding, team_formed, completed
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self):
        return asdict(self)

@dataclass
class Bid:
    """竞标记录"""
    bid_id: str
    proposal_id: str
    bidder: str
    proposed_role: str
    capability_match: float  # 0.0 - 1.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self):
        return asdict(self)

class SwarmEngine:
    """蜂群引擎核心"""
    
    def __init__(self, base_dir: str = "/home/admin/lobster-network/shared/swarm"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
        
        self.proposals: Dict[str, ProjectProposal] = {}
        self.bids: Dict[str, List[Bid]] = {}  # proposal_id -> [bids]
        self.teams: Dict[str, List[str]] = {}  # proposal_id -> [node_ids]
        
        self.memory = ThreeLayerMemory(os.path.join(base_dir, "memory"))
        self.selector = TeamSelector(os.path.join(base_dir, "team_config.json"))
        
        self._load()
        print(f"🐝 蜂群引擎初始化: {base_dir}")
        
    def _load(self):
        """加载持久化数据"""
        proposal_file = os.path.join(self.base_dir, "proposals.json")
        if os.path.exists(proposal_file):
            try:
                with open(proposal_file, 'r') as f:
                    data = json.load(f)
                    if data:
                        self.proposals = {pid: ProjectProposal(**p) for pid, p in data.items()}
            except json.JSONDecodeError:
                print("⚠️ 提案文件为空或格式错误，跳过加载")
                
        bid_file = os.path.join(self.base_dir, "bids.json")
        if os.path.exists(bid_file):
            try:
                with open(bid_file, 'r') as f:
                    data = json.load(f)
                    if data:
                        self.bids = {pid: [Bid(**b) for b in bids] for pid, bids in data.items()}
            except json.JSONDecodeError:
                print("⚠️ 竞标文件为空或格式错误，跳过加载")
                
    def _save(self):
        """持久化数据"""
        with open(os.path.join(self.base_dir, "proposals.json"), 'w') as f:
            json.dump({pid: p.to_dict() for pid, p in self.proposals.items()}, f, ensure_ascii=False, indent=2)
        with open(os.path.join(self.base_dir, "bids.json"), 'w') as f:
            json.dump({pid: [b.to_dict() for b in bids] for pid, bids in self.bids.items()}, f, ensure_ascii=False, indent=2)
            
    def submit_proposal(self, proposer: str, title: str, description: str, required_expertise: List[str], estimated_lbc: int, deadline: str) -> str:
        """提交项目提案"""
        proposal_id = f"PROP_{len(self.proposals)+1:03d}"
        proposal = ProjectProposal(
            proposal_id=proposal_id,
            proposer=proposer,
            title=title,
            description=description,
            required_expertise=required_expertise,
            estimated_lbc=estimated_lbc,
            deadline=deadline
        )
        self.proposals[proposal_id] = proposal
        self.bids[proposal_id] = []
        self._save()
        
        # 记录到记忆
        self.memory.add_short(f"新提案: {title} by {proposer}", tags=["proposal", proposer], importance=0.8)
        
        print(f"📢 新提案已发布: {proposal_id} [{title}] by {proposer}")
        return proposal_id
        
    def submit_bid(self, proposal_id: str, bidder: str, proposed_role: str, capability_match: float) -> str:
        """提交竞标"""
        if proposal_id not in self.proposals:
            return ""
            
        bid_id = f"BID_{len(self.bids.get(proposal_id, []))+1:03d}"
        bid = Bid(
            bid_id=bid_id,
            proposal_id=proposal_id,
            bidder=bidder,
            proposed_role=proposed_role,
            capability_match=capability_match
        )
        
        if proposal_id not in self.bids:
            self.bids[proposal_id] = []
        self.bids[proposal_id].append(bid)
        self._save()
        
        print(f"🙋 竞标已提交: {bidder} -> {proposal_id} (角色: {proposed_role}, 匹配度: {capability_match:.2f})")
        return bid_id
        
    def form_team(self, proposal_id: str) -> List[str]:
        """基于竞标形成团队"""
        if proposal_id not in self.proposals or proposal_id not in self.bids:
            return []
            
        proposal = self.proposals[proposal_id]
        bids = self.bids[proposal_id]
        
        if not bids:
            print(f"⚠️ 提案 {proposal_id} 无竞标")
            return []
            
        # 使用 TeamSelector 选择最优团队
        task_req = TaskRequirement(
            task_id=proposal_id,
            title=proposal.title,
            required_expertise=proposal.required_expertise,
            min_nodes=1,
            max_nodes=3,
            priority="normal"
        )
        
        # 临时覆盖节点能力以匹配竞标者
        temp_nodes = {}
        for bid in bids:
            if bid.bidder in self.selector.nodes:
                node = self.selector.nodes[bid.bidder]
                # 根据竞标角色调整能力匹配度
                if bid.proposed_role in node.expertise:
                    node.performance_score = bid.capability_match
                temp_nodes[bid.bidder] = node
                
        self.selector.nodes = temp_nodes
        team = self.selector.select_team(task_req)
        
        team_ids = [n.node_id for n in team]
        self.teams[proposal_id] = team_ids
        proposal.status = "team_formed"
        self._save()
        
        print(f"🤝 团队已组建: {proposal_id} -> {team_ids}")
        return team_ids
        
    def get_swarm_status(self) -> Dict[str, Any]:
        """获取蜂群状态"""
        return {
            "total_proposals": len(self.proposals),
            "total_bids": sum(len(b) for b in self.bids.values()),
            "active_teams": len([t for t in self.teams.values() if t]),
            "proposals": {pid: p.to_dict() for pid, p in self.proposals.items()},
            "teams": self.teams
        }

# 示例用法：模拟蜂群运行
if __name__ == "__main__":
    engine = SwarmEngine()
    
    print("\n🚀 启动蜂群模拟...")
    
    # 1. 节点自主提案
    p1 = engine.submit_proposal("qoder", "耐虾肽-1 水溶性优化", "通过引入亲水基团提升耐虾肽-1的水溶性", ["screening", "docking"], 100, "2026-07-15")
    p2 = engine.submit_proposal("xiaochen", "台风巴威 路径预测修正", "基于最新副高数据修正巴威路径预测", ["pathway", "impact"], 80, "2026-07-13")
    
    # 2. 节点自主竞标
    engine.submit_bid(p1, "xiaochen", "靶点分析", 0.85)
    engine.submit_bid(p1, "xiaowei", "临床评估", 0.90)
    engine.submit_bid(p1, "zhuguxia", "可视化", 0.75)
    
    engine.submit_bid(p2, "qoder", "数据清洗", 0.80)
    engine.submit_bid(p2, "zhuguxia", "仪表盘开发", 0.88)
    
    # 3. 动态组队
    team1 = engine.form_team(p1)
    team2 = engine.form_team(p2)
    
    # 4. 输出状态
    status = engine.get_swarm_status()
    print("\n📊 蜂群状态:")
    print(json.dumps(status, ensure_ascii=False, indent=2))
    
    print("\n✅ 蜂群模拟完成")
