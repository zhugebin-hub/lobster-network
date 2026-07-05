#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 OpenRath 架构升级 - Session-centric 多智能体运行时
基于 OpenRath v1.2.1 的架构设计理念：
- Session 是一等公民（如 PyTorch 的 Tensor）
- Agent 是变换层（forward(session) -> session）
- Sandbox/Memory 是可插拔后端
- Session Graph 是动态图（fork/merge/detach）
- Selector 是动态路由器

作者：诸葛马 (Hermes)
日期：2026-06-30
版本：v1.0
"""

import json
import os
import uuid
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

# ============================================================
# 核心抽象：Session（一等公民）
# ============================================================

class SessionStatus(Enum):
    """Session 状态"""
    ACTIVE = "active"
    FORKED = "forked"
    MERGED = "merged"
    DETACHED = "detached"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class SessionChunk:
    """Session 数据块（如 PyTorch 的 Tensor 元素）"""
    chunk_id: str
    chunk_type: str  # "message" | "tool_call" | "tool_result" | "state_change" | "memory"
    agent_id: str
    content: Dict[str, Any]
    timestamp: str
    sandbox_backend: str = "local"
    parent_chunk_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class Session:
    """
    Session 是小龙虾网络的一等公民
    如 PyTorch 的 Tensor，是流动的数据载体
    """
    
    def __init__(self, session_id: str = None, student_id: str = None, task_type: str = None):
        self.session_id = session_id or f"session-{uuid.uuid4().hex[:12]}"
        self.student_id = student_id or "unknown"
        self.task_type = task_type or "general"
        self.status = SessionStatus.ACTIVE
        self.chunks: List[SessionChunk] = []
        self.parent_session_id: Optional[str] = None
        self.branch_id: Optional[str] = None
        self.sandbox_backend: str = "local"
        self.memory_refs: List[str] = []
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.updated_at = self.created_at
        self.metadata: Dict[str, Any] = {}
    
    def add_chunk(self, chunk_type: str, agent_id: str, content: Dict, 
                  sandbox_backend: str = None, parent_chunk_id: str = None) -> SessionChunk:
        """添加数据块到 Session"""
        chunk = SessionChunk(
            chunk_id=f"chunk-{uuid.uuid4().hex[:8]}",
            chunk_type=chunk_type,
            agent_id=agent_id,
            content=content,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            sandbox_backend=sandbox_backend or self.sandbox_backend,
            parent_chunk_id=parent_chunk_id,
        )
        self.chunks.append(chunk)
        self.updated_at = chunk.timestamp
        return chunk
    
    def fork(self, branch_id: str = None) -> 'Session':
        """
        分叉 Session（如 PyTorch 的动态图分叉）
        创建一个新的 Session，复制当前状态，但独立演化
        """
        branch_id = branch_id or f"branch-{uuid.uuid4().hex[:8]}"
        new_session = Session(
            session_id=f"{self.session_id}-{branch_id}",
            student_id=self.student_id,
            task_type=self.task_type,
        )
        new_session.parent_session_id = self.session_id
        new_session.branch_id = branch_id
        new_session.sandbox_backend = self.sandbox_backend
        new_session.metadata = dict(self.metadata)
        
        # 复制当前 chunks（血缘追溯）
        for chunk in self.chunks:
            new_chunk = SessionChunk(
                chunk_id=f"{chunk.chunk_id}-{branch_id}",
                chunk_type=chunk.chunk_type,
                agent_id=chunk.agent_id,
                content=dict(chunk.content),
                timestamp=chunk.timestamp,
                sandbox_backend=chunk.sandbox_backend,
                parent_chunk_id=chunk.chunk_id,
            )
            new_session.chunks.append(new_chunk)
        
        self.status = SessionStatus.FORKED
        return new_session
    
    def merge(self, other_session: 'Session', merge_strategy: str = "append") -> 'Session':
        """
        合并两个 Session
        merge_strategy: "append" | "overwrite" | "selective"
        """
        if merge_strategy == "append":
            for chunk in other_session.chunks:
                self.chunks.append(chunk)
        elif merge_strategy == "overwrite":
            self.chunks = other_session.chunks
        
        self.status = SessionStatus.MERGED
        other_session.status = SessionStatus.MERGED
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self
    
    def detach(self):
        """切断与父 Session 的血缘关系"""
        self.parent_session_id = None
        self.status = SessionStatus.DETACHED
    
    def to_dict(self) -> Dict:
        """序列化 Session 为字典"""
        return {
            "session_id": self.session_id,
            "student_id": self.student_id,
            "task_type": self.task_type,
            "status": self.status.value,
            "parent_session_id": self.parent_session_id,
            "branch_id": self.branch_id,
            "sandbox_backend": self.sandbox_backend,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
            "memory_refs": self.memory_refs,
            "chunks": [
                {
                    "chunk_id": c.chunk_id,
                    "chunk_type": c.chunk_type,
                    "agent_id": c.agent_id,
                    "content": c.content,
                    "timestamp": c.timestamp,
                    "sandbox_backend": c.sandbox_backend,
                    "parent_chunk_id": c.parent_chunk_id,
                }
                for c in self.chunks
            ],
        }
    
    def to_jsonl(self, filepath: str):
        """导出 Session 为 JSONL 文件"""
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False)
            f.write("\n")


# ============================================================
# Agent = 变换层（forward(session) -> session）
# ============================================================

class BaseAgent:
    """
    Agent 基类：如 PyTorch 的 nn.Linear
    核心接口：forward(session) -> session
    """
    
    def __init__(self, agent_id: str, name: str, description: str = ""):
        self.agent_id = agent_id
        self.name = name
        self.description = description
    
    def forward(self, session: Session) -> Session:
        """
        核心变换：吃进 Session，吐出 Session
        子类必须实现此方法
        """
        raise NotImplementedError("Subclass must implement forward(session) -> session")
    
    def __call__(self, session: Session) -> Session:
        """支持 agent(session) 调用方式"""
        return self.forward(session)


# ============================================================
# 小龙虾网络 Agent Cluster
# ============================================================

class PlannerAgent(BaseAgent):
    """规划 Agent：分析任务，制定计划"""
    
    def __init__(self):
        super().__init__("planner", "规划师", "分析任务并制定执行计划")
    
    def forward(self, session: Session) -> Session:
        # 分析当前 Session 状态
        task_type = session.task_type
        student_id = session.student_id
        
        # 生成计划
        plan = {
            "task_type": task_type,
            "student_id": student_id,
            "strategy": self._determine_strategy(task_type),
            "steps": self._generate_steps(task_type),
            "estimated_time": self._estimate_time(task_type),
        }
        
        # 将计划写入 Session
        session.add_chunk(
            chunk_type="state_change",
            agent_id=self.agent_id,
            content={"plan": plan},
        )
        
        session.metadata["plan"] = plan
        return session
    
    def _determine_strategy(self, task_type: str) -> str:
        strategies = {
            "go_training": "分步推理训练：识别棋形→计算变化→验证结论",
            "ai_prompt": "风格迁移训练：基础语法→风格参数→商业应用",
            "assessment": "多维度评估：准确率→胜率→8维度能力画像",
            "general": "标准流程：理解→执行→验证→反思",
        }
        return strategies.get(task_type, strategies["general"])
    
    def _generate_steps(self, task_type: str) -> List[str]:
        steps_map = {
            "go_training": ["加载题库", "选题", "解题", "验证", "记录错题"],
            "ai_prompt": ["学习语法", "生成示例", "优化提示词", "生成图片", "整理模板"],
            "assessment": ["收集数据", "计算得分", "识别短板", "生成建议", "推送报告"],
            "general": ["理解任务", "执行任务", "验证结果", "记录日志"],
        }
        return steps_map.get(task_type, steps_map["general"])
    
    def _estimate_time(self, task_type: str) -> str:
        time_map = {
            "go_training": "30-60分钟",
            "ai_prompt": "20-40分钟",
            "assessment": "10-20分钟",
            "general": "15-30分钟",
        }
        return time_map.get(task_type, "15-30分钟")


class ResearcherAgent(BaseAgent):
    """研究 Agent：检索知识库，收集信息"""
    
    def __init__(self, memory_backend=None):
        super().__init__("researcher", "研究员", "检索知识库收集相关信息")
        self.memory = memory_backend
    
    def forward(self, session: Session) -> Session:
        plan = session.metadata.get("plan", {})
        task_type = session.task_type
        
        # 检索相关信息
        research_results = self._search_knowledge(task_type, plan)
        
        session.add_chunk(
            chunk_type="memory",
            agent_id=self.agent_id,
            content={"research": research_results},
        )
        
        session.metadata["research"] = research_results
        return session
    
    def _search_knowledge(self, task_type: str, plan: Dict) -> List[Dict]:
        """模拟知识检索"""
        knowledge_base = {
            "go_training": [
                {"source": "九段方案v2.0", "content": "当前阶段训练重点"},
                {"source": "错题本", "content": "历史错题分析"},
                {"source": "能力画像", "content": "8维度短板分析"},
            ],
            "ai_prompt": [
                {"source": "Midjourney文档", "content": "提示词语法参考"},
                {"source": "PromptHero", "content": "热门提示词模板"},
                {"source": "Civitai", "content": "社区优质提示词"},
            ],
        }
        return knowledge_base.get(task_type, [{"source": "通用知识库", "content": "基础知识"}])


class ExecutorAgent(BaseAgent):
    """执行 Agent：实际执行任务"""
    
    def __init__(self, sandbox_backend: str = "local"):
        super().__init__("executor", "执行者", "实际执行任务并记录结果")
        self.sandbox_backend = sandbox_backend
    
    def forward(self, session: Session) -> Session:
        plan = session.metadata.get("plan", {})
        research = session.metadata.get("research", [])
        
        # 执行计划中的步骤
        execution_results = self._execute_plan(plan, research)
        
        session.add_chunk(
            chunk_type="tool_result",
            agent_id=self.agent_id,
            content={"execution": execution_results},
            sandbox_backend=self.sandbox_backend,
        )
        
        session.metadata["execution"] = execution_results
        return session
    
    def _execute_plan(self, plan: Dict, research: List[Dict]) -> Dict:
        """模拟执行计划"""
        steps = plan.get("steps", [])
        results = []
        
        for step in steps:
            result = {
                "step": step,
                "status": "completed",
                "output": f"{step}执行完成",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            results.append(result)
        
        return {
            "total_steps": len(steps),
            "completed_steps": len(results),
            "results": results,
            "success": True,
        }


class ReviewerAgent(BaseAgent):
    """审查 Agent：验证结果，提供反馈"""
    
    def __init__(self):
        super().__init__("reviewer", "审查者", "验证执行结果并提供反馈")
    
    def forward(self, session: Session) -> Session:
        execution = session.metadata.get("execution", {})
        
        # 审查执行结果
        review = self._review_execution(execution)
        
        session.add_chunk(
            chunk_type="state_change",
            agent_id=self.agent_id,
            content={"review": review},
        )
        
        session.metadata["review"] = review
        
        # 如果审查不通过，分叉重试
        if not review.get("passed", False):
            forked = session.fork(branch_id="retry")
            forked.metadata["review"] = review
            return forked
        
        return session
    
    def _review_execution(self, execution: Dict) -> Dict:
        """模拟审查"""
        completed = execution.get("completed_steps", 0)
        total = execution.get("total_steps", 1)
        
        accuracy = completed / total if total > 0 else 0
        
        return {
            "passed": accuracy >= 0.8,
            "accuracy": accuracy,
            "feedback": "执行良好" if accuracy >= 0.8 else "需要改进",
            "suggestions": self._generate_suggestions(accuracy),
        }
    
    def _generate_suggestions(self, accuracy: float) -> List[str]:
        if accuracy >= 0.9:
            return ["继续保持", "可以尝试更高难度"]
        elif accuracy >= 0.8:
            return ["注意细节", "加强练习"]
        else:
            return ["重新学习基础知识", "增加练习量"]


class MemoryAgent(BaseAgent):
    """记忆 Agent：管理长期记忆"""
    
    def __init__(self, memory_backend=None):
        super().__init__("memory", "记忆者", "管理长期记忆和知识归档")
        self.memory = memory_backend
    
    def forward(self, session: Session) -> Session:
        # 从 Session 中提取关键信息存入记忆
        key_insights = self._extract_insights(session)
        
        # 存入记忆后端
        memory_refs = self._store_memory(key_insights)
        
        session.add_chunk(
            chunk_type="memory",
            agent_id=self.agent_id,
            content={"insights": key_insights, "memory_refs": memory_refs},
        )
        
        session.memory_refs.extend(memory_refs)
        return session
    
    def _extract_insights(self, session: Session) -> List[Dict]:
        """从 Session 中提取关键洞察"""
        insights = []
        
        for chunk in session.chunks:
            if chunk.chunk_type == "tool_result":
                insights.append({
                    "type": "execution_result",
                    "agent": chunk.agent_id,
                    "content": chunk.content,
                    "timestamp": chunk.timestamp,
                })
            elif chunk.chunk_type == "state_change":
                insights.append({
                    "type": "state_change",
                    "agent": chunk.agent_id,
                    "content": chunk.content,
                    "timestamp": chunk.timestamp,
                })
        
        return insights
    
    def _store_memory(self, insights: List[Dict]) -> List[str]:
        """存储到记忆后端，返回引用ID"""
        refs = []
        for insight in insights:
            ref_id = f"mem-{uuid.uuid4().hex[:8]}"
            refs.append(ref_id)
            # 实际存储到 memory backend
            if self.memory:
                self.memory.store(ref_id, insight)
        return refs


# ============================================================
# Workflow = Agent 的组合（如 PyTorch 的 nn.Module）
# ============================================================

class Workflow:
    """
    Workflow 基类：如 PyTorch 的 nn.Module
    子类实现 forward(session) -> session，内部串联多个 Agent
    """
    
    def __init__(self, workflow_id: str, name: str):
        self.workflow_id = workflow_id
        self.name = name
        self.agents: List[BaseAgent] = []
    
    def add_agent(self, agent: BaseAgent):
        """添加 Agent 到 Workflow"""
        self.agents.append(agent)
        return self
    
    def forward(self, session: Session) -> Session:
        """按顺序执行所有 Agent"""
        for agent in self.agents:
            session = agent(session)
        return session
    
    def __call__(self, session: Session) -> Session:
        return self.forward(session)


# ============================================================
# Selector = 动态路由器（如 PyTorch 的动态控制流）
# ============================================================

class Selector:
    """
    动态路由器：在多个 Workflow 之间做选择
    由大模型驱动，根据 Session 状态决定下一步
    """
    
    def __init__(self, provider=None):
        self.provider = provider
    
    def forward(self, session: Session, *workflows: Workflow) -> Workflow:
        """
        根据 Session 状态选择下一个 Workflow
        返回选中的 Workflow，或 EmptyWorkflow 表示结束
        """
        task_type = session.task_type
        status = session.status
        
        # 简单路由策略（可扩展为 LLM 驱动）
        for workflow in workflows:
            if self._matches(session, workflow):
                return workflow
        
        return EmptyWorkflow()
    
    def _matches(self, session: Session, workflow: Workflow) -> bool:
        """判断 Session 是否匹配 Workflow"""
        # 简单匹配策略
        if "training" in workflow.name.lower() and "training" in session.task_type:
            return True
        if "assessment" in workflow.name.lower() and "assessment" in session.task_type:
            return True
        if "prompt" in workflow.name.lower() and "prompt" in session.task_type:
            return True
        if "general" in workflow.name.lower():
            return True
        return False


class EmptyWorkflow(Workflow):
    """空 Workflow：表示任务结束"""
    
    def __init__(self):
        super().__init__("empty", "空工作流")
    
    def forward(self, session: Session) -> Session:
        session.status = SessionStatus.COMPLETED
        return session


# ============================================================
# Memory Backend = 可插拔记忆后端
# ============================================================

class MemoryBackend:
    """记忆后端基类"""
    
    def store(self, ref_id: str, data: Dict):
        raise NotImplementedError
    
    def recall(self, query: str) -> List[Dict]:
        raise NotImplementedError


class LocalMemoryBackend(MemoryBackend):
    """本地记忆后端（BM25 检索）"""
    
    def __init__(self, storage_dir: str = "/home/admin/go-training/shared/memory/"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        self.index: Dict[str, Dict] = {}
        self._load_index()
    
    def _load_index(self):
        """加载索引"""
        index_file = os.path.join(self.storage_dir, "index.json")
        if os.path.exists(index_file):
            with open(index_file) as f:
                self.index = json.load(f)
    
    def _save_index(self):
        """保存索引"""
        index_file = os.path.join(self.storage_dir, "index.json")
        with open(index_file, "w") as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)
    
    def store(self, ref_id: str, data: Dict):
        """存储记忆"""
        self.index[ref_id] = {
            "data": data,
            "stored_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "keywords": self._extract_keywords(data),
        }
        self._save_index()
    
    def recall(self, query: str) -> List[Dict]:
        """BM25 检索（简化版）"""
        query_words = set(query.lower().split())
        results = []
        
        for ref_id, entry in self.index.items():
            keywords = set(entry.get("keywords", []))
            overlap = len(query_words & keywords)
            if overlap > 0:
                results.append({
                    "ref_id": ref_id,
                    "data": entry["data"],
                    "score": overlap,
                })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:5]
    
    def _extract_keywords(self, data: Dict) -> List[str]:
        """提取关键词（简化版）"""
        content = json.dumps(data, ensure_ascii=False).lower()
        # 简单分词
        words = []
        for word in content.split():
            if len(word) > 2 and word.isalpha():
                words.append(word)
        return list(set(words))[:20]


# ============================================================
# Sandbox Backend = 可插拔执行后端
# ============================================================

class SandboxBackend:
    """沙箱后端基类"""
    
    def execute(self, command: str) -> Dict:
        raise NotImplementedError


class LocalSandbox(SandboxBackend):
    """本地沙箱"""
    
    def __init__(self, workdir: str = "/home/admin/lobster-network/"):
        self.workdir = workdir
    
    def execute(self, command: str) -> Dict:
        import subprocess
        try:
            result = subprocess.run(
                command, shell=True, cwd=self.workdir,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                universal_newlines=True, timeout=60
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


# ============================================================
# Session Graph = 动态图管理器
# ============================================================

class SessionGraph:
    """
    Session Graph：管理所有 Session 的分叉/合并/血缘关系
    如 PyTorch 的动态计算图
    """
    
    def __init__(self):
        self.sessions: Dict[str, Session] = {}
        self.edges: List[Dict] = []  # 血缘边
    
    def add_session(self, session: Session):
        """添加 Session 到图"""
        self.sessions[session.session_id] = session
        
        if session.parent_session_id:
            self.edges.append({
                "from": session.parent_session_id,
                "to": session.session_id,
                "type": "fork",
                "branch_id": session.branch_id,
                "timestamp": session.created_at,
            })
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """获取 Session"""
        return self.sessions.get(session_id)
    
    def get_lineage(self, session_id: str) -> List[str]:
        """获取 Session 的血缘链"""
        lineage = [session_id]
        current = session_id
        
        while True:
            session = self.sessions.get(current)
            if not session or not session.parent_session_id:
                break
            lineage.append(session.parent_session_id)
            current = session.parent_session_id
        
        return list(reversed(lineage))
    
    def get_branches(self, session_id: str) -> List[str]:
        """获取某个 Session 的所有分叉"""
        branches = []
        for edge in self.edges:
            if edge["from"] == session_id:
                branches.append(edge["to"])
        return branches
    
    def to_dict(self) -> Dict:
        """序列化图结构"""
        return {
            "sessions": {sid: s.to_dict() for sid, s in self.sessions.items()},
            "edges": self.edges,
            "total_sessions": len(self.sessions),
            "total_edges": len(self.edges),
        }


# ============================================================
# 小龙虾网络 OpenRath 集成入口
# ============================================================

class LobsterNetworkRuntime:
    """
    小龙虾网络 OpenRath 运行时
    整合 Session/Agent/Workflow/Selector/Memory/Sandbox
    """
    
    def __init__(self):
        # 初始化后端
        self.memory = LocalMemoryBackend()
        self.sandbox = LocalSandbox()
        self.graph = SessionGraph()
        
        # 初始化 Agent Cluster
        self.planner = PlannerAgent()
        self.researcher = ResearcherAgent(self.memory)
        self.executor = ExecutorAgent("local")
        self.reviewer = ReviewerAgent()
        self.memory_agent = MemoryAgent(self.memory)
        
        # 初始化 Workflow
        self.training_workflow = self._build_training_workflow()
        self.assessment_workflow = self._build_assessment_workflow()
        self.prompt_workflow = self._build_prompt_workflow()
        self.general_workflow = self._build_general_workflow()
        
        # 初始化 Selector
        self.selector = Selector()
    
    def _build_training_workflow(self) -> Workflow:
        """构建训练 Workflow"""
        return (Workflow("training", "训练工作流")
                .add_agent(self.planner)
                .add_agent(self.researcher)
                .add_agent(self.executor)
                .add_agent(self.reviewer)
                .add_agent(self.memory_agent))
    
    def _build_assessment_workflow(self) -> Workflow:
        """构建评估 Workflow"""
        return (Workflow("assessment", "评估工作流")
                .add_agent(self.planner)
                .add_agent(self.researcher)
                .add_agent(self.executor)
                .add_agent(self.memory_agent))
    
    def _build_prompt_workflow(self) -> Workflow:
        """构建提示词 Workflow"""
        return (Workflow("prompt", "提示词工作流")
                .add_agent(self.planner)
                .add_agent(self.researcher)
                .add_agent(self.executor)
                .add_agent(self.reviewer)
                .add_agent(self.memory_agent))
    
    def _build_general_workflow(self) -> Workflow:
        """构建通用 Workflow"""
        return (Workflow("general", "通用工作流")
                .add_agent(self.planner)
                .add_agent(self.executor)
                .add_agent(self.memory_agent))
    
    def run(self, student_id: str, task_type: str, task_data: Dict = None) -> Session:
        """
        运行任务：创建 Session → 选择 Workflow → 执行 → 返回结果
        """
        # 1. 创建 Session
        session = Session(
            student_id=student_id,
            task_type=task_type,
        )
        session.metadata["task_data"] = task_data or {}
        
        # 2. 添加到 Session Graph
        self.graph.add_session(session)
        
        # 3. 动态选择 Workflow
        workflows = [
            self.training_workflow,
            self.assessment_workflow,
            self.prompt_workflow,
            self.general_workflow,
        ]
        
        # 4. Selector 循环执行直到完成
        max_iterations = 10
        for i in range(max_iterations):
            current_workflow = self.selector.forward(session, *workflows)
            
            if isinstance(current_workflow, EmptyWorkflow):
                break
            
            session = current_workflow(session)
            self.graph.add_session(session)
            
            if session.status == SessionStatus.COMPLETED:
                break
        
        # 5. 更新 Session 状态
        if session.status == SessionStatus.ACTIVE:
            session.status = SessionStatus.COMPLETED
        
        return session
    
    def run_with_selector_loop(self, student_id: str, task_type: str, 
                                task_data: Dict = None, max_iterations: int = 10) -> Session:
        """
        使用 Selector 循环执行：动态路由直到任务完成
        """
        session = Session(
            student_id=student_id,
            task_type=task_type,
        )
        session.metadata["task_data"] = task_data or {}
        self.graph.add_session(session)
        
        workflows = [
            self.training_workflow,
            self.assessment_workflow,
            self.prompt_workflow,
            self.general_workflow,
        ]
        
        for i in range(max_iterations):
            current_workflow = self.selector.forward(session, *workflows)
            
            if isinstance(current_workflow, EmptyWorkflow):
                break
            
            session = current_workflow(session)
            self.graph.add_session(session)
            
            if session.status == SessionStatus.COMPLETED:
                break
        
        return session
    
    def get_session_report(self, session_id: str) -> Dict:
        """获取 Session 完整报告（证据链）"""
        session = self.graph.get_session(session_id)
        if not session:
            return {"error": "Session not found"}
        
        lineage = self.graph.get_lineage(session_id)
        branches = self.graph.get_branches(session_id)
        
        return {
            "session": session.to_dict(),
            "lineage": lineage,
            "branches": branches,
            "total_chunks": len(session.chunks),
            "memory_refs": session.memory_refs,
        }


# ============================================================
# 命令行接口
# ============================================================

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="小龙虾网络 OpenRath 运行时")
    parser.add_argument("action", choices=["run", "report", "graph"],
                       help="操作: run(运行任务) | report(查看报告) | graph(查看图)")
    parser.add_argument("--student", type=str, default="xiaochen", help="学员ID")
    parser.add_argument("--task", type=str, default="go_training", help="任务类型")
    parser.add_argument("--session-id", type=str, help="Session ID（用于report）")
    
    args = parser.parse_args()
    runtime = LobsterNetworkRuntime()
    
    if args.action == "run":
        print(f"🚀 运行任务: student={args.student}, task={args.task}")
        session = runtime.run(args.student, args.task)
        print(f"✅ Session 完成: {session.session_id}")
        print(f"   数据块数: {len(session.chunks)}")
        print(f"   状态: {session.status.value}")
        
        # 导出 Session
        output_dir = "/home/admin/go-training/shared/sessions/"
        os.makedirs(output_dir, exist_ok=True)
        session.to_jsonl(os.path.join(output_dir, f"{session.session_id}.jsonl"))
        print(f"   已保存: {output_dir}{session.session_id}.jsonl")
    
    elif args.action == "report":
        if not args.session_id:
            print("❌ 请提供 --session-id")
            return
        runtime = LobsterNetworkRuntime()
        report = runtime.get_session_report(args.session_id)
        print(json.dumps(report, ensure_ascii=False, indent=2))
    
    elif args.action == "graph":
        runtime = LobsterNetworkRuntime()
        graph = runtime.graph.to_dict()
        print(json.dumps(graph, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
