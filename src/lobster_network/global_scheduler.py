"""
龙虾网络全局调度协调器 - L3 调度层防护
支持：错峰调度、预算分配、批量合并、状态共享

用法：
    scheduler = GlobalScheduler(node_id="lobster-001")
    
    # 注册定时任务
    scheduler.register_task(
        name="stock_report",
        node_id="lobster-001",
        schedule="0 9 * * *",
        priority=1,
    )
    
    # 检查是否可以执行
    result = scheduler.can_execute("stock_report")
    if not result.allowed:
        print(f"调度限制: {result.reason}")
        exit(0)
    
    # 记录执行
    scheduler.record_execution("stock_report", tokens=3200)
    
    # 获取调度状态
    status = scheduler.get_status()
"""

import json
import os
import time
import threading
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from pathlib import Path

logger = None

def _get_logger():
    global logger
    if logger is None:
        try:
            from .utils.logger import get_logger
            logger = get_logger(__name__)
        except ImportError:
            import logging
            logger = logging.getLogger(__name__)
    return logger


# ========== 数据类 ==========

@dataclass
class ScheduledTask:
    """定时任务"""
    name: str
    node_id: str
    schedule: str           # cron 表达式
    priority: int           # 1=最高
    last_run: Optional[str] = None
    last_run_tokens: int = 0
    next_run: Optional[str] = None
    enabled: bool = True


@dataclass
class NodeBudget:
    """节点预算"""
    node_id: str
    daily_tokens: int
    max_requests_per_hour: int
    priority: str           # high | medium | low
    tokens_used_today: int = 0
    requests_this_hour: int = 0
    last_reset_date: str = ""


@dataclass
class ScheduleResult:
    """调度结果"""
    allowed: bool
    reason: str
    wait_seconds: int = 0


# ========== 默认配置 ==========

DEFAULT_SCHEDULE = [
    # 时间    节点          任务                    优先级
    ("09:00", "lobster-001", "stock_report",       1),  # 股票汇报（核心）
    ("09:05", "lobster-001", "lobster_daily_check", 2), # 龙虾日报
    ("09:10", "*",           "dorm_daily_report",   3),  # 宿舍日报
    ("15:00", "lobster-001", "stock_report",       1),
    ("15:05", "*",           "project_status",     3),
    ("20:00", "lobster-001", "stock_report",       1),
    ("20:05", "*",           "community_interaction", 4),
    ("21:30", "lobster-001", "heartbeat_check",    2),
    ("21:35", "hermes",      "night_sync",         3),
]

DEFAULT_BUDGETS = {
    "lobster-001": {
        "daily_tokens": 200000,
        "max_requests_per_hour": 30,
        "priority": "high",
    },
    "hermes": {
        "daily_tokens": 100000,
        "max_requests_per_hour": 15,
        "priority": "high",
    },
    "zhuguxia": {
        "daily_tokens": 80000,
        "max_requests_per_hour": 12,
        "priority": "medium",
    },
    "xiaochen": {
        "daily_tokens": 50000,
        "max_requests_per_hour": 8,
        "priority": "medium",
    },
    "qoder": {
        "daily_tokens": 40000,
        "max_requests_per_hour": 6,
        "priority": "low",
    },
    "lobster-museum-001": {
        "daily_tokens": 30000,
        "max_requests_per_hour": 5,
        "priority": "low",
    },
}


# ========== 全局调度器 ==========

class GlobalScheduler:
    """龙虾网络全局调度协调器"""
    
    def __init__(
        self,
        node_id: str = "lobster-001",
        state_dir: Optional[str] = None,
        config: Optional[dict] = None,
    ):
        if state_dir is None:
            state_dir = os.path.expanduser("~/.openclaw/workspace")
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        self.node_id = node_id
        self.schedule_file = self.state_dir / "global-schedule.json"
        self.budget_file = self.state_dir / "node-budgets.json"
        
        self.config = config or {}
        
        self._lock = threading.Lock()
        self._load_state()
    
    def _load_state(self):
        """加载状态"""
        # 先初始化默认值
        self.tasks = []
        self.budgets = {}
        
        # 加载调度表
        if self.schedule_file.exists():
            try:
                with open(self.schedule_file, "r") as f:
                    data = json.load(f)
                self.tasks = data.get("tasks", [])
            except Exception as e:
                _get_logger().warning(f"加载调度表失败: {e}")
        
        # 如果任务为空，初始化默认调度表
        if not self.tasks:
            for time_str, node_id, name, priority in DEFAULT_SCHEDULE:
                self.tasks.append({
                    "name": name,
                    "node_id": node_id,
                    "schedule": time_str,
                    "priority": priority,
                    "last_run": None,
                    "last_run_tokens": 0,
                    "next_run": None,
                    "enabled": True,
                })
        
        # 加载预算
        if self.budget_file.exists():
            try:
                with open(self.budget_file, "r") as f:
                    data = json.load(f)
                self.budgets = data.get("budgets", {})
            except Exception as e:
                _get_logger().warning(f"加载预算失败: {e}")
        
        # 如果预算为空，初始化默认预算
        if not self.budgets:
            for nid, bcfg in DEFAULT_BUDGETS.items():
                self.budgets[nid] = {
                    "node_id": nid,
                    "daily_tokens": bcfg["daily_tokens"],
                    "max_requests_per_hour": bcfg["max_requests_per_hour"],
                    "priority": bcfg["priority"],
                    "tokens_used_today": 0,
                    "requests_this_hour": 0,
                    "last_reset_date": datetime.utcnow().strftime("%Y-%m-%d"),
                }
        
        # 统一保存一次
        self._save_state()
    
    def _save_state(self):
        """保存状态"""
        with open(self.schedule_file, "w") as f:
            json.dump({"tasks": self.tasks}, f, ensure_ascii=False, indent=2)
        
        with open(self.budget_file, "w") as f:
            json.dump({"budgets": self.budgets}, f, ensure_ascii=False, indent=2)
    
    # ========== 公开 API ==========
    
    def register_task(
        self,
        name: str,
        node_id: str,
        schedule: str,
        priority: int = 3,
    ) -> bool:
        """
        注册定时任务
        
        Args:
            name: 任务名称
            node_id: 执行节点（* 表示任意节点）
            schedule: cron 表达式或 HH:MM
            priority: 优先级（1=最高）
        
        Returns:
            是否注册成功
        """
        with self._lock:
            # 检查是否已存在
            for task in self.tasks:
                if task["name"] == name:
                    _get_logger().warning(f"任务 {name} 已存在，跳过")
                    return False
            
            self.tasks.append({
                "name": name,
                "node_id": node_id,
                "schedule": schedule,
                "priority": priority,
                "last_run": None,
                "last_run_tokens": 0,
                "next_run": None,
                "enabled": True,
            })
            
            # 按优先级排序
            self.tasks.sort(key=lambda t: t["priority"])
            
            self._save_state()
            _get_logger().info(f"注册任务: {name} (node={node_id}, priority={priority})")
            return True
    
    def can_execute(self, task_name: str) -> ScheduleResult:
        """
        检查任务是否可以执行
        
        Args:
            task_name: 任务名称
        
        Returns:
            ScheduleResult(allowed, reason, wait_seconds)
        """
        with self._lock:
            now = datetime.utcnow()
            
            # 1. 查找任务
            task = None
            for t in self.tasks:
                if t["name"] == task_name:
                    task = t
                    break
            
            if not task:
                return ScheduleResult(allowed=False, reason=f"任务 {task_name} 未注册")
            
            if not task.get("enabled", True):
                return ScheduleResult(allowed=False, reason=f"任务 {task_name} 已禁用")
            
            # 2. 检查节点预算
            node_id = task["node_id"]
            if node_id != "*" and node_id in self.budgets:
                budget = self.budgets[node_id]
                
                # 检查每日重置
                today = now.strftime("%Y-%m-%d")
                if budget["last_reset_date"] != today:
                    budget["tokens_used_today"] = 0
                    budget["requests_this_hour"] = 0
                    budget["last_reset_date"] = today
                
                # 检查 token 预算
                if budget["tokens_used_today"] >= budget["daily_tokens"]:
                    return ScheduleResult(
                        allowed=False,
                        reason=f"节点 {node_id} 每日 token 预算已用完",
                    )
                
                # 检查每小时请求数
                if budget["requests_this_hour"] >= budget["max_requests_per_hour"]:
                    return ScheduleResult(
                        allowed=False,
                        reason=f"节点 {node_id} 每小时请求数已达上限",
                    )
            
            # 3. 检查错峰冲突
            # 如果任务在 5 分钟内有其他同优先级任务执行过，延迟执行
            if task.get("last_run"):
                last_run = self._parse_time(task["last_run"])
                if (now - last_run).total_seconds() < 300:  # 5 分钟间隔
                    wait = 300 - int((now - last_run).total_seconds())
                    return ScheduleResult(
                        allowed=False,
                        reason=f"任务 {task_name} 上次执行不足 5 分钟",
                        wait_seconds=wait,
                    )
            
            return ScheduleResult(allowed=True, reason="允许执行")
    
    def record_execution(self, task_name: str, tokens: int = 0):
        """
        记录任务执行
        
        Args:
            task_name: 任务名称
            tokens: 消耗 token 数
        """
        with self._lock:
            now = datetime.utcnow()
            today = now.strftime("%Y-%m-%d")
            
            # 更新任务记录
            for task in self.tasks:
                if task["name"] == task_name:
                    task["last_run"] = now.isoformat() + "Z"
                    task["last_run_tokens"] = tokens
                    break
            
            # 更新节点预算
            node_id = self.node_id
            if node_id in self.budgets:
                budget = self.budgets[node_id]
                budget["tokens_used_today"] += tokens
                budget["requests_this_hour"] += 1
                budget["last_reset_date"] = today
            
            self._save_state()
    
    def get_schedule(self) -> List[dict]:
        """获取调度表"""
        with self._lock:
            return list(self.tasks)
    
    def get_budget_status(self) -> Dict[str, dict]:
        """获取预算状态"""
        with self._lock:
            now = datetime.utcnow()
            today = now.strftime("%Y-%m-%d")
            
            status = {}
            for nid, budget in self.budgets.items():
                # 检查是否需要重置
                if budget["last_reset_date"] != today:
                    budget["tokens_used_today"] = 0
                    budget["requests_this_hour"] = 0
                    budget["last_reset_date"] = today
                
                usage_pct = budget["tokens_used_today"] / budget["daily_tokens"] if budget["daily_tokens"] > 0 else 0
                
                status[nid] = {
                    "daily_tokens": budget["daily_tokens"],
                    "tokens_used": budget["tokens_used_today"],
                    "usage_pct": round(usage_pct, 4),
                    "max_rph": budget["max_requests_per_hour"],
                    "current_rph": budget["requests_this_hour"],
                    "priority": budget["priority"],
                }
            
            return status
    
    def get_conflicts(self) -> List[dict]:
        """
        检查调度冲突
        
        Returns:
            冲突列表
        """
        with self._lock:
            conflicts = []
            
            # 按时间分组
            time_groups: Dict[str, List[dict]] = {}
            for task in self.tasks:
                schedule = task.get("schedule", "")
                if schedule not in time_groups:
                    time_groups[schedule] = []
                time_groups[schedule].append(task)
            
            # 检查冲突（同一时间有多个高优先级任务）
            for schedule, tasks in time_groups.items():
                if len(tasks) > 1:
                    high_priority = [t for t in tasks if t["priority"] <= 2]
                    if len(high_priority) > 1:
                        conflicts.append({
                            "time": schedule,
                            "tasks": [t["name"] for t in high_priority],
                            "count": len(high_priority),
                            "suggestion": f"建议将 {high_priority[1]['name']} 错开 5 分钟",
                        })
            
            return conflicts
    
    def borrow_budget(
        self,
        from_node: str,
        to_node: str,
        amount: int,
    ) -> bool:
        """
        预算借用（高优先级节点可用完后可借用低优先级节点的剩余额度）
        
        Args:
            from_node: 借出节点
            to_node: 借入节点
            amount: 借用 token 数
        
        Returns:
            是否成功
        """
        with self._lock:
            if from_node not in self.budgets or to_node not in self.budgets:
                return False
            
            from_budget = self.budgets[from_node]
            to_budget = self.budgets[to_node]
            
            # 检查借出节点是否有剩余
            remaining = from_budget["daily_tokens"] - from_budget["tokens_used_today"]
            if remaining < amount:
                _get_logger().warning(
                    f"节点 {from_node} 剩余预算不足: {remaining} < {amount}"
                )
                return False
            
            # 执行借用
            from_budget["tokens_used_today"] += amount
            to_budget["daily_tokens"] += amount
            
            _get_logger().info(
                f"预算借用: {from_node} → {to_node}, {amount} tokens"
            )
            
            self._save_state()
            return True
    
    def disable_task(self, task_name: str) -> bool:
        """禁用任务"""
        with self._lock:
            for task in self.tasks:
                if task["name"] == task_name:
                    task["enabled"] = False
                    self._save_state()
                    _get_logger().info(f"禁用任务: {task_name}")
                    return True
            return False
    
    def enable_task(self, task_name: str) -> bool:
        """启用任务"""
        with self._lock:
            for task in self.tasks:
                if task["name"] == task_name:
                    task["enabled"] = True
                    self._save_state()
                    _get_logger().info(f"启用任务: {task_name}")
                    return True
            return False
    
    def get_status(self) -> dict:
        """获取调度器状态"""
        with self._lock:
            now = datetime.utcnow()
            today = now.strftime("%Y-%m-%d")
            
            return {
                "node_id": self.node_id,
                "updated_at": now.isoformat() + "Z",
                "total_tasks": len(self.tasks),
                "enabled_tasks": sum(1 for t in self.tasks if t.get("enabled", True)),
                "budgets": self.get_budget_status(),
                "conflicts": self.get_conflicts(),
            }
    
    # ========== 内部方法 ==========
    
    @staticmethod
    def _parse_time(s: str) -> datetime:
        """解析 ISO 时间字符串"""
        s = s.replace("Z", "").split("+")[0]
        fmt = "%Y-%m-%dT%H:%M:%S.%f" if "." in s else "%Y-%m-%dT%H:%M:%S"
        return datetime.strptime(s, fmt)
