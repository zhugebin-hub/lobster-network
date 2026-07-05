"""
Workspace — Agent 的持久化状态基座

铁律三: 状态要写文件，不要塞上下文。

Workspace = Agent 的 Git 仓库:
- 每一步操作都可回放
- 跨会话延续不依赖 Context Window
- 支持断点续传 (RPA Lock)
- 所有状态可审计

设计参考:
- 悟空 AI 招聘: /candidates/{id}/state.json + /rpa_lock/{batch_id}.json
- Anthropic Claude Code: Workspace 作为持久层
- Mitchell Hashimoto: 状态文件化

路径约定:
    .shared/workspace/{node_id}/
        state.json          — 节点当前状态
        plan.md            — 当前任务计划
        tasks/             — 任务状态
        rpa_lock/          — RPA 断点续传锁
        failures.jsonl     — 失败日志
"""

import json
import os
import fcntl
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from pathlib import Path
from enum import Enum


class TaskStatus(Enum):
    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class LockStatus(Enum):
    FREE = "free"
    ACQUIRED = "acquired"
    STALE = "stale"


@dataclass
class WorkspaceFile:
    """工作空间中的文件 — 每个文件都有来源和版本"""
    path: str                        # 相对路径
    content_type: str = "json"       # json/md/log/txt
    version: int = 1
    created_at: str = ""
    updated_at: str = ""
    size_bytes: int = 0

    def __post_init__(self):
        if not self.created_at:
            tz = timezone(timedelta(hours=8))
            self.created_at = datetime.now(tz).isoformat()


@dataclass
class RpaLock:
    """
    RPA 锁 — 事务边界保障。

    悟空 AI 血泪经验:
    "RPA + Agent 的接缝处最容易出事，必须做强制性的事务文件"

    用法:
        lock = RpaLock.acquire("batch-001", node_id="zhugema")
        try:
            # 执行 RPA 操作
            lock.update_progress(50, "已完成50%")
        finally:
            lock.release()
    """
    batch_id: str
    node_id: str
    status: LockStatus = LockStatus.ACQUIRED
    progress_pct: int = 0
    step: str = ""
    acquired_at: str = ""
    updated_at: str = ""
    released_at: str = ""

    def __post_init__(self):
        tz = timezone(timedelta(hours=8))
        now = datetime.now(tz).isoformat()
        if not self.acquired_at:
            self.acquired_at = now
        if not self.updated_at:
            self.updated_at = now

    @classmethod
    def acquire(cls, batch_id: str, node_id: str,
                workspace_dir: str) -> Optional['RpaLock']:
        """获取 RPA 锁"""
        lock_dir = Path(workspace_dir) / "rpa_lock"
        lock_dir.mkdir(parents=True, exist_ok=True)
        lock_file = lock_dir / f"{batch_id}.json"

        if lock_file.exists():
            # 检查是否过期 (超过24小时的锁视为stale)
            try:
                existing = json.loads(lock_file.read_text())
                acquired = datetime.fromisoformat(existing.get("acquired_at", "2000-01-01T00:00:00+08:00"))
                tz = timezone(timedelta(hours=8))
                if (datetime.now(tz) - acquired).total_seconds() > 86400:
                    lock_file.unlink()  # 释放过期锁
                else:
                    return None  # 锁被占用
            except Exception:
                lock_file.unlink()  # 损坏的锁文件

        lock = cls(batch_id=batch_id, node_id=node_id)
        lock_file.write_text(json.dumps(asdict(lock), ensure_ascii=False, indent=2))
        return lock

    def update_progress(self, pct: int, step: str = ""):
        """更新进度"""
        self.progress_pct = pct
        self.step = step
        tz = timezone(timedelta(hours=8))
        self.updated_at = datetime.now(tz).isoformat()

    def release(self, workspace_dir: str = ""):
        """释放锁"""
        self.status = LockStatus.FREE
        tz = timezone(timedelta(hours=8))
        self.released_at = datetime.now(tz).isoformat()

        if workspace_dir:
            lock_file = Path(workspace_dir) / "rpa_lock" / f"{self.batch_id}.json"
            if lock_file.exists():
                lock_file.unlink()


class Workspace:
    """
    Agent 工作空间 — 持久化状态基座。

    这是铁律三的落地实现:
    "状态写在文件里，不在脑子里"

    原则:
    1. Context 是工位，Workspace 才是档案室
    2. 每次操作都可回放 (通过版本号追踪)
    3. 跨会话延续不依赖 Context Window
    4. 所有状态变更有审计记录
    """

    # 标准目录结构
    DIRS = ["state", "tasks", "rpa_lock", "plans", "logs"]

    def __init__(self, node_id: str, base_dir: str = ""):
        """
        初始化工作空间。

        参数:
            node_id: 节点ID (如 'zhugebin-001')
            base_dir: 基础目录 (默认 .shared/workspace/)
        """
        self.node_id = node_id
        self.base_dir = Path(base_dir) if base_dir else Path(".shared/workspace")
        self.ws_dir = self.base_dir / node_id
        self._ensure_dirs()
        self._operations: List[Dict] = []  # 操作审计日志

    def _ensure_dirs(self):
        """确保目录结构存在"""
        for d in self.DIRS:
            (self.ws_dir / d).mkdir(parents=True, exist_ok=True)

    def get_state(self) -> Dict:
        """读取节点状态"""
        state_file = self.ws_dir / "state" / "node_state.json"
        if state_file.exists():
            return json.loads(state_file.read_text())
        return {"node_id": self.node_id, "status": "new"}

    def save_state(self, state: Dict):
        """保存节点状态"""
        state_file = self.ws_dir / "state" / "node_state.json"
        state["updated_at"] = datetime.now(timezone(timedelta(hours=8))).isoformat()
        state["version"] = state.get("version", 0) + 1

        # 原子写入
        tmp = str(state_file) + ".tmp"
        with open(tmp, 'w') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        os.replace(tmp, str(state_file))

        self._log_operation("save_state", {"version": state["version"]})

    def get_plan(self, task_id: str = "current") -> Optional[str]:
        """读取任务计划 (Init Stage 输出)"""
        plan_file = self.ws_dir / "plans" / f"{task_id}.md"
        if plan_file.exists():
            return plan_file.read_text(encoding='utf-8')
        return None

    def save_plan(self, task_id: str, plan_content: str):
        """保存任务计划"""
        plan_file = self.ws_dir / "plans" / f"{task_id}.md"
        plan_file.parent.mkdir(parents=True, exist_ok=True)

        # 加版本头
        header = f"# plan: {task_id}\n"
        header += f"# node: {self.node_id}\n"
        header += f"# created: {datetime.now(timezone(timedelta(hours=8))).isoformat()}\n\n"
        plan_file.write_text(header + plan_content, encoding='utf-8')

        self._log_operation("save_plan", {"task_id": task_id})

    def get_task_status(self, task_id: str) -> Dict:
        """读取任务状态"""
        task_file = self.ws_dir / "tasks" / f"{task_id}.json"
        if task_file.exists():
            return json.loads(task_file.read_text())
        return {"task_id": task_id, "status": TaskStatus.PENDING.value}

    def save_task_status(self, task_id: str, status: TaskStatus, details: Dict = None):
        """保存任务状态"""
        task_file = self.ws_dir / "tasks" / f"{task_id}.json"
        state = {
            "task_id": task_id,
            "status": status.value,
            "node_id": self.node_id,
            "updated_at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
            "details": details or {},
        }
        task_file.write_text(json.dumps(state, ensure_ascii=False, indent=2))
        self._log_operation("save_task_status", {"task_id": task_id, "status": status.value})

    def acquire_lock(self, batch_id: str) -> Optional[RpaLock]:
        """获取 RPA 锁"""
        lock = RpaLock.acquire(batch_id, self.node_id, str(self.ws_dir))
        if lock:
            self._log_operation("acquire_lock", {"batch_id": batch_id})
        return lock

    def release_lock(self, batch_id: str):
        """释放 RPA 锁"""
        lock = RpaLock(batch_id=batch_id, node_id=self.node_id)
        lock.release(str(self.ws_dir))
        self._log_operation("release_lock", {"batch_id": batch_id})

    def record_failure(self, error: str, context: str = ""):
        """记录失败事件"""
        fail_file = self.ws_dir / "logs" / "failures.jsonl"
        record = {
            "node_id": self.node_id,
            "timestamp": datetime.now(timezone(timedelta(hours=8))).isoformat(),
            "error": error,
            "context": context[:500] if context else "",
        }
        with open(fail_file, 'a') as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        self._log_operation("record_failure", {"error": error[:100]})

    def checkpoint(self, label: str = "") -> str:
        """
        创建检查点 — 保存当前完整状态的快照。

        返回: checkpoint_id
        """
        cid = f"cp-{self.node_id}-{datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d_%H%M%S')}"
        if label:
            cid += f"-{label}"

        state = self.get_state()
        cp_file = self.ws_dir / "state" / "checkpoints" / f"{cid}.json"
        cp_file.parent.mkdir(parents=True, exist_ok=True)
        cp_file.write_text(json.dumps(state, ensure_ascii=False, indent=2))

        self._log_operation("checkpoint", {"id": cid})
        return cid

    def list_files(self) -> List[WorkspaceFile]:
        """列出所有工作空间文件"""
        files = []
        for fpath in self.ws_dir.rglob("*"):
            if fpath.is_file():
                stat = fpath.stat()
                files.append(WorkspaceFile(
                    path=str(fpath.relative_to(self.ws_dir)),
                    size_bytes=stat.st_size,
                    updated_at=datetime.fromtimestamp(stat.st_mtime, tz=timezone(timedelta(hours=8))).isoformat(),
                ))
        return files

    def get_audit_log(self) -> List[Dict]:
        """获取审计日志"""
        return self._operations

    def _log_operation(self, op: str, details: Dict = None):
        """记录操作到审计日志"""
        self._operations.append({
            "op": op,
            "node_id": self.node_id,
            "timestamp": datetime.now(timezone(timedelta(hours=8))).isoformat(),
            "details": details or {},
        })

    def __repr__(self):
        return f"Workspace({self.node_id}, {self.ws_dir})"
