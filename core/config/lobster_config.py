"""
小龙虾网络 V5.2 — 统一配置管理模块
用途：消除 104 处硬编码路径，提供单一配置源
"""

import os
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

# ── 项目根目录 ──────────────────────────────────────

ROOT_DIR = Path(__file__).resolve().parent.parent
CORE_DIR = ROOT_DIR / "core"
SRC_DIR = ROOT_DIR / "src"
DOMAINS_DIR = ROOT_DIR / "domains"
SKILLS_DIR = ROOT_DIR / "skills"
WEB_DIR = ROOT_DIR / "web"
REGISTRY_DIR = ROOT_DIR / "registry"
OUTPUT_DIR = ROOT_DIR / "output"
LOGS_DIR = CORE_DIR / "logs"

# ── 共享存储路径 ────────────────────────────────────

# 远程共享路径（阿里云 NFS）
SHARED_ROOT = Path("/shared")
SHARED_TRAINING = SHARED_ROOT / "training"
SHARED_PAPER = SHARED_TRAINING / "paper"
SHARED_GO = SHARED_TRAINING / "go"
SHARED_POSTER = SHARED_TRAINING / "poster"
SHARED_INBOX = SHARED_PAPER / "inbox"
SHARED_OUTBOX = SHARED_PAPER / "outbox"
SHARED_METHODOLOGY = SHARED_PAPER / "methodology"

# 本地替代路径（开发环境）
LOCAL_SHARED = ROOT_DIR / ".local_shared"
LOCAL_TRAINING = LOCAL_SHARED / "training"
LOCAL_PAPER = LOCAL_TRAINING / "paper"
LOCAL_INBOX = LOCAL_PAPER / "inbox"
LOCAL_OUTBOX = LOCAL_PAPER / "outbox"
LOCAL_METHODOLOGY = LOCAL_PAPER / "methodology"


def get_shared_root() -> Path:
    """获取共享存储根路径（自动检测远程/本地）"""
    if SHARED_ROOT.exists():
        return SHARED_ROOT
    local = Path(os.environ.get("LOBSTER_SHARED_ROOT", str(LOCAL_SHARED)))
    local.mkdir(parents=True, exist_ok=True)
    return local


def get_training_dir(domain: str = "paper") -> Path:
    """获取训练目录"""
    root = get_shared_root()
    return root / "training" / domain


def get_inbox_dir(domain: str = "paper") -> Path:
    """获取收件箱目录"""
    d = get_training_dir(domain) / "inbox"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_outbox_dir(domain: str = "paper") -> Path:
    """获取发件箱目录"""
    d = get_training_dir(domain) / "outbox"
    d.mkdir(parents=True, exist_ok=True)
    return d


# ── 节点注册表 ──────────────────────────────────────

def load_nodes_registry() -> Dict[str, Any]:
    """加载所有已注册节点"""
    nodes = {}
    registry_dir = REGISTRY_DIR / "nodes"
    if registry_dir.exists():
        for f in registry_dir.glob("*.json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                node_id = data.get("node_id", f.stem)
                nodes[node_id] = data
            except (json.JSONDecodeError, KeyError):
                continue
    # 兼容旧格式 nodes.json
    old_nodes = REGISTRY_DIR / "nodes.json"
    if old_nodes.exists() and not nodes:
        try:
            nodes = json.loads(old_nodes.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return nodes


# ── 学员配置文件 ─────────────────────────────────────

def load_learner_profiles(domain: str = "paper") -> List[Dict[str, Any]]:
    """加载学员能力画像"""
    profiles_dir = REGISTRY_DIR / "nodes"
    learners = []
    if profiles_dir.exists():
        for f in sorted(profiles_dir.glob("*paper*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                if "paper" in data.get("domains", []) or "capabilities" in data:
                    learners.append(data)
            except (json.JSONDecodeError, KeyError):
                continue
    return learners


# ── 服务器配置 ──────────────────────────────────────

SERVER_CONFIG = {
    "host": "121.43.80.231",
    "port": 8080,
    "user": "admin",
    "shared_path": str(SHARED_ROOT),
    "api_base_url": "http://47.93.6.57:8080",
    "mqtt_broker": "localhost",
    "mqtt_port": 1883,
    "websocket_port": 8080,
}

# ── 运行时默认配置 ──────────────────────────────────

RUNTIME_DEFAULTS = {
    "version": "5.2.0",
    "node_id": "lobster-local",
    "modules": {
        "harness": {"enabled": True},
        "orchestrator": {"enabled": True},
        "observability": {"enabled": True},
        "economy": {"enabled": True},
        "fault_tolerance": {"enabled": True},
        "resource_manager": {"enabled": True},
        "cost_optimizer": {"enabled": True},
        "mutual_learning": {"enabled": True},
        "a2a_protocol": {"enabled": True},
        "memory_manager": {"enabled": True},
        "cognition_layer": {"enabled": True},
        "compliance_guard": {"enabled": True},
        "dynamic_team_selector": {"enabled": True},
        "failure_attribution": {"enabled": True},
    },
    "budget": {"daily_limit_lbc": 100.0, "alert_pct": 80.0},
    "nodes": ["qoder", "xiaochen", "zhuguxia", "hermes", "xiaowei", "lobster-001", "museum-001"],
}

# ── 阈值配置 ────────────────────────────────────────

THRESHOLD_DEFAULTS = {
    "emergence": {"theta_e": 0.65, "window_size": 100, "false_positive_limit": 0.20, "false_negative_limit": 0.15},
    "harness": {"risk_threshold": "medium", "max_concurrency": 5, "max_tokens": 4096, "max_memory_mb": 512, "timeout_sec": 300},
    "circuit_breaker": {"failure_threshold": 5, "open_duration_sec": 30, "half_open_max": 3},
    "retry": {"max_attempts": 3, "backoff_base": 2.0, "max_delay_sec": 60},
    "rate_limiter": {"tokens_per_sec": 10.0, "burst_size": 20},
    "connection_pool": {"max_size": 20, "min_idle": 2, "ttl_sec": 600},
    "batch": {"max_batch": 50, "max_wait_ms": 100},
    "cache": {"max_size": 1000, "ttl_sec": 600},
    "cost": {"idle_scale_down_delay_sec": 300, "batch_merge_window_ms": 100, "pool_recycle_interval_sec": 600},
}

# ── 论文写作调度配置 ────────────────────────────────

PAPER_SCHEDULE = [
    {"slot": "06:00-08:00", "task": "literature_mining", "lead": "zhuguxia", "assist": "museum-001"},
    {"slot": "08:00-10:00", "task": "outline_writing", "lead": "qoder", "assist": "lobster-001"},
    {"slot": "10:00-12:00", "task": "section_drafting", "lead": "xiaochen", "assist": None},
    {"slot": "13:00-15:00", "task": "peer_review", "lead": "all", "assist": None},
    {"slot": "15:00-18:00", "task": "revision_polish", "lead": "all", "assist": None},
]


def load_thresholds() -> Dict[str, Any]:
    """加载阈值配置（从 JSON 文件或使用默认值）"""
    config_path = CORE_DIR / "observability" / "config" / "thresholds.json"
    if config_path.exists():
        try:
            loaded = json.loads(config_path.read_text(encoding="utf-8"))
            # 合并默认值
            merged = THRESHOLD_DEFAULTS.copy()
            merged.update(loaded)
            return merged
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    return THRESHOLD_DEFAULTS.copy()


# ── 导出模块清单 ────────────────────────────────────

__all__ = [
    "ROOT_DIR", "CORE_DIR", "SRC_DIR", "DOMAINS_DIR", "SKILLS_DIR", "WEB_DIR", "REGISTRY_DIR",
    "OUTPUT_DIR", "LOGS_DIR",
    "SHARED_ROOT", "SHARED_TRAINING", "SHARED_PAPER", "SHARED_GO", "SHARED_POSTER",
    "SHARED_INBOX", "SHARED_OUTBOX", "SHARED_METHODOLOGY",
    "get_shared_root", "get_training_dir", "get_inbox_dir", "get_outbox_dir",
    "load_nodes_registry", "load_learner_profiles",
    "SERVER_CONFIG", "RUNTIME_DEFAULTS", "THRESHOLD_DEFAULTS", "PAPER_SCHEDULE",
    "load_thresholds",
]
