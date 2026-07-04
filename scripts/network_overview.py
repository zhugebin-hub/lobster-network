#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 V5.0 — 网络状态总览

一键查看所有节点状态、训练进度、经济指标、模块健康度。

用法：
  python3 scripts/network_overview.py
"""

import json
import sys
import subprocess
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "core" / "config" / "runtime_config.json"


def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def ssh_exec(cmd, timeout=10):
    config = load_config()
    server = config.get("server", {})
    host = server.get("host", "121.43.80.231")
    user = server.get("user", "admin")
    ssh_key = str(Path.home() / ".ssh" / "id_rsa_hermes")
    full_cmd = f'ssh -i {ssh_key} -o ConnectTimeout=5 -o StrictHostKeyChecking=no {user}@{host} "{cmd}"'
    try:
        r = subprocess.run(full_cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None


def section(title):
    w = 60
    print(f"\n{'─' * w}")
    print(f"  {title}")
    print(f"{'─' * w}")


def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"{'=' * 60}")
    print(f"  小龙虾网络 V5.0 网络状态总览")
    print(f"  {now}")
    print(f"{'=' * 60}")

    # ── 节点注册表 ──
    section("节点注册表")
    raw = ssh_exec("cat /shared/registry/registry.json 2>/dev/null")
    if raw:
        try:
            registry = json.loads(raw)
            for nid, info in registry.items():
                status = info.get("status", "unknown")
                last_hb = info.get("last_heartbeat", "N/A")[:19]
                name = info.get("name", nid)
                version = info.get("version", "?")
                caps = len(info.get("capabilities", []))
                print(f"  [{status.upper():7}] {name} (v{version}, {caps}项能力)")
                print(f"           最后心跳: {last_hb}")
        except json.JSONDecodeError:
            print("  注册表解析失败")
    else:
        print("  无法连接服务器")

    # ── 训练进度 ──
    section("围棋训练进度")
    status_raw = ssh_exec("cat /shared/training/go/status.json 2>/dev/null")
    if status_raw:
        try:
            ts = json.loads(status_raw)
            print(f"  训练计划: V{ts.get('version', '?')} | Phase{ts.get('phase', '?')} Week{ts.get('week', '?')} Day{ts.get('day', '?')}")
            print(f"  当前主题: {ts.get('topic', 'N/A')}")
            print(f"  脚本版本: {ts.get('script_version', '?')}")
            print()
            for pid, pinfo in ts.get("players", {}).items():
                acc = pinfo.get("accuracy", 0)
                rating = pinfo.get("rating", "?")
                submitted = "已提交" if pinfo.get("day3_submitted") else "未提交"
                print(f"  {pid:12} | 正确率 {acc:.1f}% | 评级 {rating} | Day3 {submitted}")
        except json.JSONDecodeError:
            print("  训练状态解析失败")

    # 各学员档案
    for node_id in ["qoder", "xiaochen", "zhuguxia"]:
        raw = ssh_exec(f"cat /shared/training/go/{node_id}/profile.json 2>/dev/null")
        if raw:
            try:
                p = json.loads(raw)
                day = p.get("v5_plan", {}).get("days_completed", [0])
                last_day = day[-1] if day else p.get("current_day", 0)
                target = p.get("v5_plan", {}).get("target_day", "?")
                print(f"\n  [{node_id}]")
                print(f"    等级: {p.get('current_level', '?')} | Day {last_day}/{target}")
                print(f"    做题: {p.get('total_problems_solved', 0)} | 对局: {p.get('total_games_played', 0)} | 胜率: {p.get('win_rate', 0):.1%}")
                print(f"    最后训练: {p.get('last_training_date', 'N/A')}")
                strengths = p.get("strengths", [])[-3:]
                if strengths:
                    print(f"    近期突破: {', '.join(strengths)}")
            except json.JSONDecodeError:
                pass

    # ── 本地模块状态 ──
    section("核心模块状态")
    modules = {
        "Harness 安全护栏": "core.harness",
        "RL-Orchestrator": "core.orchestrator",
        "Observability": "core.observability",
        "LBC Economy": "core.economy",
        "CC Broadcast": "core.cc_broadcast",
    }
    sys.path.insert(0, str(REPO_ROOT))
    for name, mod_path in modules.items():
        try:
            __import__(mod_path)
            print(f"  [OK]     {name}")
        except Exception as e:
            print(f"  [FAIL]   {name} — {e}")

    # ── Git 状态 ──
    section("Git 状态")
    try:
        branch = subprocess.run("git branch --show-current", shell=True, capture_output=True, text=True, cwd=str(REPO_ROOT))
        log = subprocess.run("git log --oneline -5", shell=True, capture_output=True, text=True, cwd=str(REPO_ROOT))
        print(f"  当前分支: {branch.stdout.strip()}")
        print(f"  最近提交:")
        for line in log.stdout.strip().split("\n")[:5]:
            print(f"    {line}")
    except Exception:
        print("  无法获取 Git 状态")

    print(f"\n{'=' * 60}\n")


if __name__ == "__main__":
    main()
