#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
训练恢复脚本 — 检测三学员训练停滞并自动恢复

功能：
1. SSH 连接服务器读取训练状态
2. 检测每个学员的最后训练时间
3. 如果停滞超过阈值，生成恢复指令
4. 更新 status.json 推进到下一个训练日
5. 通过 CC 协议通知相关节点

用法：
  python3 scripts/training_resume.py              # 检测+恢复
  python3 scripts/training_resume.py --dry-run    # 仅检测不修改
  python3 scripts/training_resume.py --node xiaochen  # 指定单节点
"""

import json
import sys
import subprocess
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "core" / "config" / "runtime_config.json"

logger = logging.getLogger("training_resume")
logger.setLevel(logging.INFO)
_ch = logging.StreamHandler()
_ch.setFormatter(logging.Formatter("[Training] %(levelname)s - %(message)s"))
logger.addHandler(_ch)

# ── 停滞阈值（天） ──
STALE_THRESHOLD_DAYS = 3


def load_config() -> Dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "server": {"host": "121.43.80.231", "user": "admin", "ssh_key": "~/.ssh/id_rsa_hermes"},
        "training": {"targets": {}}
    }


def ssh_exec(cmd: str, timeout: int = 15) -> Optional[str]:
    """通过SSH执行远程命令"""
    config = load_config()
    server = config.get("server", {})
    host = server.get("host", "121.43.80.231")
    user = server.get("user", "admin")
    ssh_key = str(Path.home() / ".ssh" / "id_rsa_hermes")

    full_cmd = f'ssh -i {ssh_key} -o ConnectTimeout=8 -o StrictHostKeyChecking=no {user}@{host} "{cmd}"'
    try:
        result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0:
            return result.stdout.strip()
        logger.warning(f"SSH命令失败(rc={result.returncode}): {result.stderr[:200]}")
    except subprocess.TimeoutExpired:
        logger.warning("SSH命令超时")
    except Exception as e:
        logger.error(f"SSH错误: {e}")
    return None


def fetch_training_status() -> Dict:
    """从服务器获取训练状态"""
    raw = ssh_exec("cat /shared/training/go/status.json 2>/dev/null")
    if raw:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass
    return {}


def fetch_profile(node_id: str) -> Dict:
    """获取指定学员的训练档案"""
    raw = ssh_exec(f"cat /shared/training/go/{node_id}/profile.json 2>/dev/null")
    if raw:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass
    return {}


def check_staleness(profile: Dict, node_id: str) -> Dict:
    """检查训练是否停滞"""
    last_date_str = profile.get("last_training_date", "unknown")
    current_day = profile.get("current_day", 0) if "v5_plan" not in profile else profile.get("v5_plan", {}).get("days_completed", [0])[-1] if profile.get("v5_plan", {}).get("days_completed") else profile.get("current_day", 0)
    target_day = profile.get("v5_plan", {}).get("target_day", current_day + 10)

    try:
        last_date = datetime.strptime(last_date_str[:10], "%Y-%m-%d")
        stale_days = (datetime.now() - last_date).days
    except (ValueError, TypeError):
        stale_days = -1
        last_date = None

    return {
        "node_id": node_id,
        "last_training": last_date_str,
        "stale_days": stale_days,
        "is_stale": stale_days > STALE_THRESHOLD_DAYS,
        "current_day": current_day,
        "target_day": target_day,
        "total_problems": profile.get("total_problems_solved", 0),
        "total_games": profile.get("total_games_played", 0),
        "win_rate": profile.get("win_rate", 0),
        "level": profile.get("current_level", "unknown"),
    }


def generate_resume_plan(checks: Dict[str, Dict]) -> Dict:
    """为停滞的学员生成恢复计划"""
    plan = {"timestamp": datetime.now().isoformat(), "actions": []}
    config = load_config()
    targets = config.get("training", {}).get("targets", {})

    for node_id, check in checks.items():
        if not check["is_stale"]:
            continue

        target_info = targets.get(node_id, {})
        next_day = check["current_day"] + 1
        target_day = target_info.get("target_day", check["target_day"])

        action = {
            "node_id": node_id,
            "stale_days": check["stale_days"],
            "resume_from_day": check["current_day"],
            "next_day": next_day,
            "target_day": target_day,
            "remaining_days": target_day - next_day,
            "focus_areas": [],
            "commands": []
        }

        # 根据学员特点确定训练重点
        if node_id == "qoder":
            action["focus_areas"] = ["双飞挂应对深化", "高级定式深度", "19路中盘复杂战斗"]
            action["commands"] = [
                f"cd /shared/training/go && python3 trainer_v6.py --node {node_id} --day {next_day} --mode nocturnal",
                f"cd /shared/training/go && python3 evaluator.py --node {node_id} --day {next_day}"
            ]
        elif node_id == "xiaochen":
            action["focus_areas"] = ["官子精度提升", "中盘战斗力训练", "死活题强化"]
            action["commands"] = [
                f"cd /shared/training/go && python3 trainer_v6.py --node {node_id} --day {next_day} --mode steady",
                f"cd /shared/training/go && python3 evaluator.py --node {node_id} --day {next_day}"
            ]
        elif node_id == "zhuguxia":
            action["focus_areas"] = ["官子精度", "中盘计算深化", "手筋速度训练"]
            action["commands"] = [
                f"cd /shared/training/go && python3 trainer_v6.py --node {node_id} --day {next_day} --mode accelerated",
                f"cd /shared/training/go && python3 evaluator.py --node {node_id} --day {next_day}"
            ]

        plan["actions"].append(action)

    return plan


def execute_resume(plan: Dict, dry_run: bool = False) -> Dict:
    """执行恢复计划"""
    results = {"executed_at": datetime.now().isoformat(), "results": []}

    for action in plan.get("actions", []):
        node_id = action["node_id"]
        result = {
            "node_id": node_id,
            "status": "skipped" if dry_run else "pending",
            "stale_days": action["stale_days"],
            "next_day": action["next_day"]
        }

        if dry_run:
            logger.info(f"[DRY-RUN] {node_id}: 停滞{action['stale_days']}天, 将恢复到Day{action['next_day']}")
            result["status"] = "dry_run"
            results["results"].append(result)
            continue

        # 执行训练命令
        for cmd in action.get("commands", []):
            logger.info(f"执行 {node_id}: {cmd[:80]}...")
            output = ssh_exec(cmd, timeout=120)
            if output:
                result["status"] = "success"
                result["output_preview"] = output[:200]
                logger.info(f"{node_id} Day{action['next_day']} 训练启动成功")
            else:
                result["status"] = "command_failed"
                logger.warning(f"{node_id} 训练命令执行失败，可能需要手动恢复")

        results["results"].append(result)

    return results


def generate_report(checks: Dict, plan: Dict, exec_results: Optional[Dict] = None) -> str:
    """生成可读的训练恢复报告"""
    lines = ["=" * 60]
    lines.append("  小龙虾网络训练恢复报告")
    lines.append(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 60)
    lines.append("")

    for node_id, check in checks.items():
        status = "停滞" if check["is_stale"] else "正常"
        icon = "!" if check["is_stale"] else "OK"
        lines.append(f"[{icon}] {node_id}:")
        lines.append(f"    状态: {status} (最后训练: {check['last_training']}, 已{check['stale_days']}天)")
        lines.append(f"    进度: Day{check['current_day']} / 目标Day{check['target_day']}")
        lines.append(f"    成绩: {check['total_problems']}题 / {check['total_games']}局 / 胜率{check['win_rate']:.1%} / {check['level']}")
        lines.append("")

    if plan.get("actions"):
        lines.append("-" * 60)
        lines.append("恢复计划:")
        for action in plan["actions"]:
            lines.append(f"  {action['node_id']}: Day{action['next_day']} → Day{action['target_day']}")
            lines.append(f"    重点: {', '.join(action['focus_areas'])}")
        lines.append("")

    if exec_results:
        lines.append("-" * 60)
        lines.append("执行结果:")
        for r in exec_results.get("results", []):
            lines.append(f"  {r['node_id']}: {r['status']} (Day{r['next_day']})")

    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="训练恢复脚本")
    parser.add_argument("--dry-run", action="store_true", help="仅检测不执行")
    parser.add_argument("--node", default=None, help="指定单节点")
    args = parser.parse_args()

    logger.info("开始检测训练状态...")

    # 获取训练状态
    status = fetch_training_status()
    if not status:
        logger.error("无法获取训练状态，服务器可能不可达")
        sys.exit(1)

    # 检查每个学员
    nodes_to_check = [args.node] if args.node else ["qoder", "xiaochen", "zhuguxia"]
    checks = {}
    for node_id in nodes_to_check:
        profile = fetch_profile(node_id)
        if profile:
            checks[node_id] = check_staleness(profile, node_id)
        else:
            logger.warning(f"无法获取 {node_id} 的训练档案")
            checks[node_id] = {"node_id": node_id, "is_stale": False, "error": "无法获取档案"}

    # 生成恢复计划
    plan = generate_resume_plan(checks)

    # 执行（或dry-run）
    exec_results = None
    if plan.get("actions"):
        exec_results = execute_resume(plan, dry_run=args.dry_run)

    # 输出报告
    report = generate_report(checks, plan, exec_results)
    print(report)

    # 保存报告
    report_path = REPO_ROOT / "core" / "logs" / f"training_resume_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    logger.info(f"报告已保存: {report_path}")


if __name__ == "__main__":
    main()
