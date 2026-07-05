#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 V5.0 统一运行时入口

将四大核心能力串联为完整的运行时管线：
  输入 → Harness 安全过滤 → Orchestrator 编排调度
       → Metrics 可观测采集 → Economy 经济结算
       → Emergence 涌现检测 → 输出

用法：
  python3 -m core.lobster_runtime                    # 启动完整运行时
  python3 -m core.lobster_runtime --mode status      # 查看网络状态
  python3 -m core.lobster_runtime --mode train       # 触发一轮训练
  python3 -m core.lobster_runtime --mode test        # 运行自检
"""

import json
import sys
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# ── 本模块 ──────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "core" / "config" / "runtime_config.json"
LOG_DIR = REPO_ROOT / "core" / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 日志
logger = logging.getLogger("lobster_runtime")
logger.setLevel(logging.INFO)
_fh = logging.FileHandler(LOG_DIR / "runtime.log", encoding="utf-8")
_fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
logger.addHandler(_fh)
_ch = logging.StreamHandler()
_ch.setFormatter(logging.Formatter("[Lobster] %(levelname)s - %(message)s"))
logger.addHandler(_ch)


# ── 加载配置 ────────────────────────────────────────

def load_config() -> Dict[str, Any]:
    """加载运行时配置，缺失则使用默认值"""
    default = {
        "version": "5.1.0",
        "node_id": "qoder",
        "modules": {
            "harness": {"enabled": True, "risk_threshold": "medium"},
            "orchestrator": {"enabled": True, "q_learning_rate": 0.1},
            "observability": {"enabled": True, "collect_interval_sec": 60},
            "economy": {"enabled": True, "currency": "LBC"},
            "emergence": {"enabled": True, "sensitivity": 0.7},
            "fault_tolerance": {"enabled": True},
            "resource_manager": {"enabled": True},
            "cost_optimizer": {"enabled": True},
            "mutual_learning": {"enabled": True},
        },
        "budget": {"daily_limit_lbc": 100.0, "alert_pct": 80.0},
        "nodes": ["qoder", "xiaochen", "zhuguxia", "hermes", "xiaowei"],
        "server": {"host": "121.43.80.231", "user": "admin", "shared_path": "/shared"},
        "training": {"plan_version": "V6", "auto_resume": True}
    }
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        # 合并（浅层）
        for k, v in default.items():
            cfg.setdefault(k, v)
        return cfg
    return default


# ── 运行时类 ────────────────────────────────────────

class LobsterRuntime:
    """小龙虾网络 V5 统一运行时"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or load_config()
        self.node_id = self.config["node_id"]
        self.started_at = None
        self.modules = {}
        self._init_modules()

    def _init_modules(self):
        """按依赖顺序初始化八大模块"""
        mods = self.config["modules"]

        # 1) Harness 安全护栏
        if mods.get("harness", {}).get("enabled", True):
            from core.harness import AgentHarness
            h = AgentHarness()
            self.modules["harness"] = h
            logger.info("[1/8] Harness 安全护栏已加载")

        # 2) Orchestrator 编排引擎
        if mods.get("orchestrator", {}).get("enabled", True):
            from core.orchestrator import RLOrchestrator
            orch = RLOrchestrator()
            self.modules["orchestrator"] = orch
            logger.info("[2/8] RL-Orchestrator 编排引擎已加载")

        # 3) Observability 可观测性
        if mods.get("observability", {}).get("enabled", True):
            from core.observability import MetricsCollector, EmergenceDetector
            mc = MetricsCollector()
            ed = EmergenceDetector()
            self.modules["metrics"] = mc
            self.modules["emergence"] = ed
            logger.info("[3/8] Observability 可观测性已加载（采集器+涌现检测）")

        # 4) Economy 经济系统
        if mods.get("economy", {}).get("enabled", True):
            from core.economy import LBCEconomy
            eco = LBCEconomy()
            eco.initialize()
            self.modules["economy"] = eco
            logger.info("[4/8] LBC 经济系统已加载")

        # 5) Fault Tolerance 故障容错 (V5.1)
        if mods.get("fault_tolerance", {}).get("enabled", True):
            from core.utils.fault_tolerance import get_fault_tolerance
            ft = get_fault_tolerance()
            self.modules["fault_tolerance"] = ft
            logger.info("[5/8] FaultTolerance 故障容错已加载")

        # 6) Resource Manager 资源管理 (V5.1)
        if mods.get("resource_manager", {}).get("enabled", True):
            from core.utils.resource_manager import get_resource_manager
            rm = get_resource_manager()
            self.modules["resource_manager"] = rm
            logger.info("[6/8] ResourceManager 资源管理已加载")

        # 7) Cost Optimizer 成本优化 (V5.1)
        if mods.get("cost_optimizer", {}).get("enabled", True):
            from core.utils.cost_optimizer import get_cost_optimizer
            co = get_cost_optimizer(
                budget_limit_lbc=self.config.get("budget", {}).get("daily_limit_lbc", 100.0),
                alert_threshold_pct=self.config.get("budget", {}).get("alert_pct", 80.0),
            )
            self.modules["cost_optimizer"] = co
            logger.info("[7/8] CostOptimizer 成本优化已加载")

        # 8) Mutual Learning 互相学习 (V5.1)
        if mods.get("mutual_learning", {}).get("enabled", True):
            from core.coach.paper_mutual_learning import MutualLearningEngine
            from core.coach.paper_mutual_learning import load_learners_from_profiles
            learners = load_learners_from_profiles()
            ml = MutualLearningEngine(learners)
            self.modules["mutual_learning"] = ml
            logger.info("[8/8] MutualLearning 互相学习引擎已加载")

    # ── 管线处理 ──────────────────────────────────

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        完整管线：输入 → Harness → Orchestrator → Metrics → Economy → 输出
        """
        result = {"input": input_data, "stages": {}, "timestamp": datetime.now().isoformat()}

        # Stage 1: Harness 输入过滤
        if "harness" in self.modules:
            h = self.modules["harness"]
            raw_msg = input_data.get("message", "")
            hr = h.guard_input(raw_msg)
            result["stages"]["harness_input"] = {
                "passed": hr.passed,
                "blocked_reason": hr.blocked_reason or None,
            }
            if not hr.passed:
                result["blocked"] = True
                result["reason"] = f"Harness L1 输入拦截: {hr.blocked_reason}"
                logger.warning(f"Harness L1 拦截: {hr.blocked_reason}")
                return result

        # Stage 2: Orchestrator 任务分解
        if "orchestrator" in self.modules:
            orch = self.modules["orchestrator"]
            task_desc = input_data.get("task", "default_task")
            try:
                dag_result = orch.orchestrate(task_desc)
                result["stages"]["orchestrator"] = {
                    "subtasks": len(dag_result.get("subtasks", [])),
                    "status": dag_result.get("status", "decomposed")
                }
            except Exception as e:
                result["stages"]["orchestrator"] = {"status": "skipped", "error": str(e)}

        # Stage 3: Metrics 指标采集
        if "metrics" in self.modules:
            mc = self.modules["metrics"]
            try:
                mc.record_agent_message(self.node_id, direction="out", latency_ms=0.0)
                mc.record_agent_task(self.node_id, success=True, response_time_ms=0.0)
                result["stages"]["metrics"] = {"status": "recorded"}
            except Exception as e:
                result["stages"]["metrics"] = {"status": "skipped", "error": str(e)}

        # Stage 4: Economy 结算
        if "economy" in self.modules:
            eco = self.modules["economy"]
            try:
                wallet = eco.get_or_create_wallet(self.node_id)
                amount = eco.reward_distributor.reward_contribution(
                    self.node_id, "task_completion", wallet
                )
                result["stages"]["economy"] = {"status": "rewarded", "amount": amount}
            except Exception as e:
                result["stages"]["economy"] = {"status": "skipped", "error": str(e)}

        # Stage 5: 涌现检测
        if "emergence" in self.modules:
            ed = self.modules["emergence"]
            try:
                events = ed.check(input_data)
                result["stages"]["emergence"] = {
                    "events_detected": len(events) if events else 0
                }
            except Exception as e:
                result["stages"]["emergence"] = {"status": "skipped", "error": str(e)}

        result["completed"] = True
        logger.info(f"管线完成: {len(result['stages'])} 阶段, 输入类型={input_data.get('type', 'unknown')}")
        return result

    # ── 状态查看 ──────────────────────────────────

    def status(self) -> Dict[str, Any]:
        """返回运行时状态摘要"""
        info = {
            "runtime": "Lobster Network V5.0",
            "node_id": self.node_id,
            "loaded_modules": list(self.modules.keys()),
            "config_version": self.config.get("version", "unknown"),
            "timestamp": datetime.now().isoformat(),
        }

        # 经济余额
        if "economy" in self.modules:
            eco = self.modules["economy"]
            try:
                all_balances = eco.get_all_balances()
                info["economy_balances"] = {
                    nid: data.get("balance", 0)
                    for nid, data in all_balances.items()
                }
            except Exception as e:
                info["economy_error"] = str(e)

        # 训练状态（从服务器读取）
        info["training_status"] = self._fetch_training_status()

        return info

    def _fetch_training_status(self) -> Dict:
        """通过SSH从服务器读取训练状态"""
        import subprocess
        server = self.config.get("server", {})
        host = server.get("host", "121.43.80.231")
        user = server.get("user", "admin")
        ssh_key = str(Path.home() / ".ssh" / "id_rsa_hermes")

        cmd = f'ssh -i {ssh_key} -o ConnectTimeout=5 -o StrictHostKeyChecking=no {user}@{host} "cat /shared/training/go/status.json 2>/dev/null"'
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout.strip():
                return json.loads(result.stdout)
        except Exception as e:
            logger.warning(f"无法连接训练服务器: {e}")
        return {"error": "无法获取训练状态"}

    # ── 自检 ──────────────────────────────────────

    def self_test(self) -> Dict[str, Any]:
        """运行模块自检"""
        results = {}
        for name, mod in self.modules.items():
            try:
                # 简单的存活检查
                _ = type(mod).__name__
                results[name] = "OK"
            except Exception as e:
                results[name] = f"ERROR: {e}"

        results["config"] = "OK" if self.config else "MISSING"
        results["pipeline"] = "OK"  # 如果走到这里说明初始化没问题

        # 尝试一次空管线
        try:
            test_result = self.process({"type": "self_test", "message": "hello", "task": "test"})
            results["pipeline"] = "OK" if test_result.get("completed") else "INCOMPLETE"
        except Exception as e:
            results["pipeline"] = f"ERROR: {e}"

        return results

    # ── 启动 ──────────────────────────────────────

    def start(self):
        """启动运行时（守护模式）"""
        self.started_at = datetime.now()
        logger.info(f"小龙虾网络 V5.0 运行时启动 — 节点: {self.node_id}")
        logger.info(f"已加载模块: {list(self.modules.keys())}")

        status = self.status()
        print(json.dumps(status, ensure_ascii=False, indent=2))

        return status


# ── CLI 入口 ────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="小龙虾网络 V5.0 统一运行时")
    parser.add_argument("--mode", choices=["start", "status", "train", "test"],
                        default="status", help="运行模式")
    parser.add_argument("--node", default=None, help="指定节点ID（覆盖配置）")
    args = parser.parse_args()

    config = load_config()
    if args.node:
        config["node_id"] = args.node

    rt = LobsterRuntime(config)

    if args.mode == "start":
        rt.start()
    elif args.mode == "status":
        print(json.dumps(rt.status(), ensure_ascii=False, indent=2))
    elif args.mode == "test":
        results = rt.self_test()
        print(json.dumps(results, ensure_ascii=False, indent=2))
        # 退出码：有任何 ERROR 则非零
        has_error = any("ERROR" in str(v) for v in results.values())
        sys.exit(1 if has_error else 0)
    elif args.mode == "train":
        print("训练恢复请使用 scripts/training_resume.py")


if __name__ == "__main__":
    main()


# ============================================================
# system_health() — 系统健康检查与降级策略
# ============================================================

def system_health(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    系统健康检查报告。

    论文 6.3.4 节：启动时打印系统健康报告。
    - 调用 HealthChecker 检查所有节点
    - 调用 GracefulDegradation 注册降级策略
    - 返回完整健康报告

    用法:
        report = system_health()
        print(json.dumps(report, indent=2))
    """
    from .utils.fault_tolerance import HealthChecker, GracefulDegradation

    # 加载配置
    config = load_config(config_path)

    report = {
        "timestamp": datetime.now().isoformat(),
        "version": "V5.0",
        "node_id": config.get("node_id", "unknown"),
        "components": {},
        "overall_status": "healthy",
    }

    # ── 1. 节点心跳检测 ──
    checker = HealthChecker(
        heartbeat_interval=config.get("heartbeat_interval", 30),
        heartbeat_timeout=config.get("heartbeat_timeout", 90),
    )

    node_health = checker.check_all_nodes()
    report["components"]["nodes"] = node_health

    # ── 2. 降级策略注册 ──
    degradation = GracefulDegradation()

    # 注册核心模块降级策略
    degradation.register(
        "rl_orchestrator",
        fallback=lambda task: {"status": "degraded", "method": "round_robin", "task": task},
        description="RL-Orchestrator 不可用时回退到轮询调度"
    )
    degradation.register(
        "cc_broadcast",
        fallback=lambda msg: {"status": "queued", "msg": msg},
        description="CC 消息总线不可用时消息入队等待恢复"
    )
    degradation.register(
        "emergence_detector",
        fallback=lambda data: {"emergence": False, "fallback": True},
        description="涌现检测器不可用时保守返回无涌现"
    )
    degradation.register(
        "agent_harness",
        fallback=lambda content: {"passed": False, "reason": "harness_unavailable"},
        description="Agent Harness 不可用时拒绝所有请求（安全优先）"
    )
    degradation.register(
        "paper_coach",
        fallback=lambda prompt: {"status": "offline", "message": "论文教练模块暂不可用"},
        description="论文教练不可用时返回离线占位"
    )

    report["components"]["degradation"] = {
        "strategies_registered": len(degradation.list_strategies()),
        "strategies": degradation.list_strategies(),
    }

    # ── 3. 综合状态判定 ──
    node_statuses = [n.get("status", "unknown") for n in node_health.get("nodes", [])]
    offline_count = node_statuses.count("offline")
    if offline_count > 0:
        report["overall_status"] = "degraded"
        report["warnings"] = [f"{offline_count} 个节点离线"]
    else:
        report["overall_status"] = "healthy"

    logger.info(
        f"[system_health] 健康报告: overall={report['overall_status']}, "
        f"nodes={len(node_statuses)}, degradations={len(degradation.list_strategies())}"
    )

    return report


def print_health_report():
    """启动时打印系统健康报告"""
    try:
        report = system_health()
        print("\n" + "=" * 60)
        print("  小龙虾网络 V5.0 — 系统健康报告")
        print("=" * 60)
        print(f"  节点 ID : {report['node_id']}")
        print(f"  整体状态: {report['overall_status'].upper()}")

        nodes_comp = report["components"]["nodes"]
        for node in nodes_comp.get("nodes", []):
            status_icon = "OK" if node["status"] == "online" else "!!"
            print(f"  [{status_icon}] {node['node_id']}: {node['status']}")

        deg_comp = report["components"]["degradation"]
        print(f"  降级策略: {deg_comp['strategies_registered']} 条已注册")
        print("=" * 60 + "\n")
    except Exception as e:
        logger.error(f"[print_health_report] 健康报告生成失败: {e}")
        print(f"[WARNING] 健康报告生成失败: {e}")
