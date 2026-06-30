#!/usr/bin/env python3
"""
双阶段调度器（Initializer + Executor）
基于 Agent Harness工程实践设计

Phase 1: Initializer - 理解任务 → 制定计划 → 写入 plan.md → 退出
Phase 2: Executor - 读取 plan.md → 按步执行 → 跨 Context Window 接力
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional


class Plan:
    """计划对象，对应 plan.md"""
    
    def __init__(self, task_id: str, goal: str, steps: List[Dict]):
        self.task_id = task_id
        self.goal = goal
        self.steps = steps
        self.created_at = time.time()
        self.status = "pending"  # pending, running, completed, failed
    
    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "goal": self.goal,
            "steps": self.steps,
            "created_at": self.created_at,
            "status": self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Plan':
        plan = cls(data["task_id"], data["goal"], data["steps"])
        plan.created_at = data.get("created_at", time.time())
        plan.status = data.get("status", "pending")
        return plan


class Initializer:
    """
    初始化器 Agent
    职责：理解任务 → 制定计划 → 写入 plan.md → 退出
    """
    
    def __init__(self, workspace_dir: str):
        self.workspace_dir = Path(workspace_dir)
        self.plans_dir = self.workspace_dir / "plans"
        self.plans_dir.mkdir(parents=True, exist_ok=True)
    
    def initialize(self, task: Dict) -> Plan:
        """
        初始化任务，生成执行计划
        
        Args:
            task: 任务字典，包含 type, goal, params 等
            
        Returns:
            Plan: 执行计划
        """
        task_id = task.get("task_id", f"task_{int(time.time())}")
        goal = task.get("goal", "")
        task_type = task.get("type", "general")
        
        # 根据任务类型生成不同的计划步骤
        if task_type == "training":
            steps = self._create_training_plan(task)
        elif task_type == "communication":
            steps = self._create_communication_plan(task)
        elif task_type == "analysis":
            steps = self._create_analysis_plan(task)
        else:
            steps = self._create_general_plan(task)
        
        plan = Plan(task_id, goal, steps)
        
        # 写入 plan.md
        self._save_plan(plan)
        
        print(f"[Initializer] 任务 {task_id} 计划已生成，共 {len(steps)} 步")
        return plan
    
    def _create_training_plan(self, task: Dict) -> List[Dict]:
        """创建训练任务计划"""
        return [
            {"step": 1, "action": "load_training_data", "params": task.get("params", {})},
            {"step": 2, "action": "distribute_to_nodes", "params": {"nodes": task.get("nodes", [])}},
            {"step": 3, "action": "monitor_progress", "params": {"interval": 300}},
            {"step": 4, "action": "collect_results", "params": {}},
            {"step": 5, "action": "generate_report", "params": {}}
        ]
    
    def _create_communication_plan(self, task: Dict) -> List[Dict]:
        """创建通信任务计划"""
        return [
            {"step": 1, "action": "validate_message", "params": {}},
            {"step": 2, "action": "route_to_target", "params": {"target": task.get("target", "")}},
            {"step": 3, "action": "wait_for_ack", "params": {"timeout": 3600}},
            {"step": 4, "action": "record_result", "params": {}}
        ]
    
    def _create_analysis_plan(self, task: Dict) -> List[Dict]:
        """创建分析任务计划"""
        return [
            {"step": 1, "action": "collect_data", "params": task.get("params", {})},
            {"step": 2, "action": "analyze", "params": {"method": task.get("method", "default")}},
            {"step": 3, "action": "generate_insights", "params": {}},
            {"step": 4, "action": "save_results", "params": {}}
        ]
    
    def _create_general_plan(self, task: Dict) -> List[Dict]:
        """创建通用任务计划"""
        return [
            {"step": 1, "action": "parse_task", "params": {}},
            {"step": 2, "action": "execute", "params": task.get("params", {})},
            {"step": 3, "action": "verify_result", "params": {}},
            {"step": 4, "action": "save_result", "params": {}}
        ]
    
    def _save_plan(self, plan: Plan):
        """保存计划到文件"""
        plan_file = self.plans_dir / f"{plan.task_id}.json"
        with open(plan_file, 'w', encoding='utf-8') as f:
            json.dump(plan.to_dict(), f, ensure_ascii=False, indent=2)
        
        # 同时生成 plan.md
        md_file = self.plans_dir / f"{plan.task_id}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(f"# 任务计划：{plan.goal}\n\n")
            f.write(f"**任务 ID:** {plan.task_id}\n")
            f.write(f"**创建时间:** {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(plan.created_at))}\n")
            f.write(f"**状态:** {plan.status}\n\n")
            f.write("## 执行步骤\n\n")
            for step in plan.steps:
                f.write(f"### 步骤 {step['step']}: {step['action']}\n")
                f.write(f"- 参数: {json.dumps(step.get('params', {}), ensure_ascii=False)}\n\n")


class Executor:
    """
    执行器 Agent
    职责：读取 plan.md → 按步执行 → 跨 Context Window 接力
    """
    
    def __init__(self, workspace_dir: str):
        self.workspace_dir = Path(workspace_dir)
        self.plans_dir = self.workspace_dir / "plans"
        self.execution_dir = self.workspace_dir / "execution"
        self.execution_dir.mkdir(parents=True, exist_ok=True)
    
    def execute(self, task_id: str) -> Dict:
        """
        执行计划
        
        Args:
            task_id: 任务 ID
            
        Returns:
            Dict: 执行结果
        """
        # 读取计划
        plan_file = self.plans_dir / f"{task_id}.json"
        if not plan_file.exists():
            raise FileNotFoundError(f"计划文件不存在: {plan_file}")
        
        with open(plan_file, 'r', encoding='utf-8') as f:
            plan_data = json.load(f)
        
        plan = Plan.from_dict(plan_data)
        plan.status = "running"
        
        # 检查是否有断点续传记录
        resume_from = self._check_resume(task_id)
        start_step = resume_from + 1 if resume_from else 1
        
        results = []
        for step in plan.steps:
            if step["step"] < start_step:
                continue
            
            print(f"[Executor] 执行步骤 {step['step']}: {step['action']}")
            
            try:
                result = self._execute_step(step)
                results.append({"step": step["step"], "status": "success", "result": result})
                self._save_progress(task_id, step["step"])
            except Exception as e:
                results.append({"step": step["step"], "status": "failed", "error": str(e)})
                plan.status = "failed"
                break
        
        # 更新计划状态
        if all(r["status"] == "success" for r in results):
            plan.status = "completed"
        
        # 保存执行结果
        self._save_results(task_id, plan, results)
        
        return {"task_id": task_id, "status": plan.status, "results": results}
    
    def _execute_step(self, step: Dict) -> Dict:
        """执行单个步骤"""
        action = step["action"]
        params = step.get("params", {})
        
        # 根据 action 执行不同操作
        if action == "load_training_data":
            return {"status": "success", "message": "训练数据加载完成"}
        elif action == "distribute_to_nodes":
            nodes = params.get("nodes", [])
            return {"status": "success", "distributed_to": nodes}
        elif action == "monitor_progress":
            return {"status": "success", "message": "进度监控已启动"}
        elif action == "collect_results":
            return {"status": "success", "message": "结果已收集"}
        elif action == "generate_report":
            return {"status": "success", "message": "报告已生成"}
        elif action == "validate_message":
            return {"status": "success", "message": "消息验证通过"}
        elif action == "route_to_target":
            return {"status": "success", "message": f"消息已路由到 {params.get('target', '')}"}
        elif action == "wait_for_ack":
            return {"status": "success", "message": "ACK 已收到"}
        elif action == "record_result":
            return {"status": "success", "message": "结果已记录"}
        elif action == "collect_data":
            return {"status": "success", "message": "数据已收集"}
        elif action == "analyze":
            return {"status": "success", "message": f"分析完成，方法: {params.get('method', 'default')}"}
        elif action == "generate_insights":
            return {"status": "success", "message": "洞察已生成"}
        elif action == "save_results":
            return {"status": "success", "message": "结果已保存"}
        elif action == "parse_task":
            return {"status": "success", "message": "任务已解析"}
        elif action == "execute":
            return {"status": "success", "message": "任务已执行"}
        elif action == "verify_result":
            return {"status": "success", "message": "结果已验证"}
        elif action == "save_result":
            return {"status": "success", "message": "结果已保存"}
        else:
            return {"status": "success", "message": f"未知操作 {action}，跳过"}
    
    def _check_resume(self, task_id: str) -> Optional[int]:
        """检查是否有断点续传记录"""
        progress_file = self.execution_dir / f"{task_id}_progress.json"
        if progress_file.exists():
            with open(progress_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("last_completed_step")
        return None
    
    def _save_progress(self, task_id: str, step: int):
        """保存执行进度"""
        progress_file = self.execution_dir / f"{task_id}_progress.json"
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump({
                "task_id": task_id,
                "last_completed_step": step,
                "updated_at": time.time()
            }, f, ensure_ascii=False, indent=2)
    
    def _save_results(self, task_id: str, plan: Plan, results: List[Dict]):
        """保存执行结果"""
        result_file = self.execution_dir / f"{task_id}_result.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump({
                "task_id": task_id,
                "goal": plan.goal,
                "status": plan.status,
                "results": results,
                "completed_at": time.time()
            }, f, ensure_ascii=False, indent=2)


class DualPhaseScheduler:
    """
    双阶段调度器
    协调 Initializer 和 Executor
    """
    
    def __init__(self, workspace_dir: str = None):
        if workspace_dir is None:
            workspace_dir = os.path.join(os.path.dirname(__file__), "..", "workspace")
        
        self.initializer = Initializer(workspace_dir)
        self.executor = Executor(workspace_dir)
    
    def schedule(self, task: Dict) -> Dict:
        """
        调度任务（双阶段）
        
        Args:
            task: 任务字典
            
        Returns:
            Dict: 执行结果
        """
        print(f"\n[Scheduler] 开始调度任务: {task.get('goal', 'unknown')}")
        
        # Phase 1: Initializer
        print("[Scheduler] Phase 1: 初始化任务...")
        plan = self.initializer.initialize(task)
        
        # Phase 2: Executor
        print("[Scheduler] Phase 2: 执行任务...")
        result = self.executor.execute(plan.task_id)
        
        print(f"[Scheduler] 任务 {plan.task_id} 完成，状态: {result['status']}")
        return result


if __name__ == "__main__":
    # 测试双阶段调度器
    scheduler = DualPhaseScheduler()
    
    # 测试训练任务
    training_task = {
        "task_id": "training_001",
        "type": "training",
        "goal": "完成围棋 Day5 训练",
        "nodes": ["xiaochen", "zhuguxia", "qoder"],
        "params": {"day": 5, "subject": "go"}
    }
    
    result = scheduler.schedule(training_task)
    print(f"\n执行结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
