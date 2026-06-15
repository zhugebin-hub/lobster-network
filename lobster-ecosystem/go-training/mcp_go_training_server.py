#!/usr/bin/env python3
"""
🦞 MCP Go Training Server - 围棋学习 MCP 化 v1.0
================================================
将原有 /shared/training/go/ 文件系统的围棋训练系统
迁移为 MCP Server，提供标准 Tool 接口供路由中枢调用。

核心能力：
  - get_training_status     - 获取训练状态
  - get_player_profile      - 获取学员档案
  - get_player_progress     - 获取学员进度
  - submit_training_result  - 提交训练结果
  - start_match             - 发起对局
  - submit_move             - 提交落子
  - get_match_status        - 获取对局状态
  - get_daily_log           - 获取训练日志
  - update_training_config  - 更新训练配置
"""

import json
import os
import sqlite3
import asyncio
import logging
from datetime import datetime
from typing import Optional

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent
import mcp.server.stdio
import mcp.types as types

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [GoTraining] %(levelname)s: %(message)s'
)
logger = logging.getLogger("go-training")

# ============ 路径配置 ============
BASE_DIR = "/shared/training/go"
XIAOCHEN_DIR = os.path.join(BASE_DIR, "xiaochen")
ZHUGUXIA_DIR = os.path.join(BASE_DIR, "zhuguxia")
MATCHES_DIR = os.path.join(BASE_DIR, "matches")
PROBLEM_BANK = os.path.join(BASE_DIR, "problem_bank")

def _read_json(path: str) -> Optional[dict]:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"读取文件失败 {path}: {e}")
        return None

def _write_json(path: str, data: dict):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

app = Server("mcp-go-training")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_training_status",
            description="获取围棋训练系统整体状态，包括当前阶段、周次、主题等。",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="get_player_profile",
            description="获取指定学员的档案信息（姓名、等级、优势、弱点等）。",
            inputSchema={
                "type": "object",
                "properties": {
                    "player_id": {"type": "string", "enum": ["xiaochen", "zhuguxia"],
                                 "description": "学员ID"}
                },
                "required": ["player_id"]
            }
        ),
        Tool(
            name="get_player_progress",
            description="获取指定学员的训练进度（做题统计、正确率、阶段历史等）。",
            inputSchema={
                "type": "object",
                "properties": {
                    "player_id": {"type": "string", "enum": ["xiaochen", "zhuguxia"],
                                 "description": "学员ID"}
                },
                "required": ["player_id"]
            }
        ),
        Tool(
            name="get_daily_log",
            description="获取指定学员的最新训练日志。",
            inputSchema={
                "type": "object",
                "properties": {
                    "player_id": {"type": "string", "enum": ["xiaochen", "zhuguxia"],
                                 "description": "学员ID"},
                    "log_file": {"type": "string", "description": "指定日志文件名（可选）"}
                },
                "required": ["player_id"]
            }
        ),
        Tool(
            name="submit_training_result",
            description="提交学员训练结果（做题成绩、学习总结等）。",
            inputSchema={
                "type": "object",
                "properties": {
                    "player_id": {"type": "string", "enum": ["xiaochen", "zhuguxia"]},
                    "date": {"type": "string", "description": "日期 YYYY-MM-DD"},
                    "problems_solved": {"type": "integer", "description": "完成题数"},
                    "problems_correct": {"type": "integer", "description": "正确题数"},
                    "time_minutes": {"type": "integer", "description": "用时（分钟）"},
                    "summary": {"type": "string", "description": "学习总结"},
                    "next_focus": {"type": "string", "description": "下一步重点"}
                },
                "required": ["player_id", "date", "problems_solved", "problems_correct"]
            }
        ),
        Tool(
            name="start_match",
            description="发起新的围棋对局。",
            inputSchema={
                "type": "object",
                "properties": {
                    "black": {"type": "string", "description": "黑方学员ID"},
                    "white": {"type": "string", "description": "白方学员ID"},
                    "board_size": {"type": "integer", "description": "棋盘尺寸", "default": 9},
                    "rule": {"type": "string", "description": "规则", "default": "中国规则"},
                    "komi": {"type": "number", "description": "贴目", "default": 7.5}
                },
                "required": ["black", "white"]
            }
        ),
        Tool(
            name="submit_move",
            description="提交围棋落子。",
            inputSchema={
                "type": "object",
                "properties": {
                    "match_id": {"type": "string", "description": "对局ID"},
                    "player": {"type": "string", "description": "落子方"},
                    "coord": {"type": "string", "description": "坐标，如 Q16"},
                    "reason": {"type": "string", "description": "落子理由"}
                },
                "required": ["match_id", "player", "coord"]
            }
        ),
        Tool(
            name="get_match_status",
            description="获取指定对局的状态。",
            inputSchema={
                "type": "object",
                "properties": {
                    "match_id": {"type": "string", "description": "对局ID"}
                },
                "required": ["match_id"]
            }
        ),
        Tool(
            name="list_matches",
            description="列出所有对局记录。",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {"type": "string", "description": "按状态过滤（可选）"}
                }
            }
        ),
        Tool(
            name="get_problem_bank_stats",
            description="获取题库统计信息。",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="update_training_config",
            description="更新训练配置（当前阶段、周次、主题等）。",
            inputSchema={
                "type": "object",
                "properties": {
                    "phase": {"type": "integer", "description": "阶段号"},
                    "week": {"type": "integer", "description": "周次"},
                    "day": {"type": "integer", "description": "第几天"},
                    "topic": {"type": "string", "description": "训练主题"}
                }
            }
        ),
        Tool(
            name="get_ecosystem_training_overview",
            description="获取生态视角的训练总览（两位学员对比、系统状态等）。",
            inputSchema={"type": "object", "properties": {}}
        ),
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        if name == "get_training_status":
            status = _read_json(os.path.join(BASE_DIR, "status.json"))
            return [TextContent(type="text", text=json.dumps(status, ensure_ascii=False, indent=2))]

        elif name == "get_player_profile":
            pid = arguments["player_id"]
            profile = _read_json(os.path.join(BASE_DIR, pid, "profile.json"))
            return [TextContent(type="text", text=json.dumps(profile, ensure_ascii=False, indent=2))]

        elif name == "get_player_progress":
            pid = arguments["player_id"]
            progress = _read_json(os.path.join(BASE_DIR, pid, "progress.json"))
            return [TextContent(type="text", text=json.dumps(progress, ensure_ascii=False, indent=2))]

        elif name == "get_daily_log":
            pid = arguments["player_id"]
            log_dir = os.path.join(BASE_DIR, pid, "daily_log")
            if arguments.get("log_file"):
                log_file = arguments["log_file"]
            else:
                files = sorted(os.listdir(log_dir)) if os.path.exists(log_dir) else []
                log_file = files[-1] if files else None
            if log_file:
                log_data = _read_json(os.path.join(log_dir, log_file))
                return [TextContent(type="text", text=json.dumps({
                    "player": pid,
                    "file": log_file,
                    "data": log_data
                }, ensure_ascii=False, indent=2))]
            return [TextContent(type="text", text=json.dumps({"error": "no logs found"}))]

        elif name == "submit_training_result":
            pid = arguments["player_id"]
            date = arguments["date"]
            solved = arguments["problems_solved"]
            correct = arguments["problems_correct"]
            time_min = arguments.get("time_minutes", 0)
            summary = arguments.get("summary", "")
            next_focus = arguments.get("next_focus", "")

            accuracy = correct / solved if solved > 0 else 0

            # 更新进度
            progress_path = os.path.join(BASE_DIR, pid, "progress.json")
            progress = _read_json(progress_path) or {}

            # 更新 sprint
            progress["sprint_day1"] = {
                "date": date,
                "problems": solved,
                "correct": correct,
                "accuracy": round(accuracy, 3),
                "time_minutes": time_min
            }
            progress["total_solved"] = solved
            progress["total_correct"] = correct
            progress["overall_accuracy"] = round(accuracy, 3)
            progress["last_analysis"] = datetime.now().isoformat()

            _write_json(progress_path, progress)

            # 写入日志
            log_dir = os.path.join(BASE_DIR, pid, "daily_log")
            os.makedirs(log_dir, exist_ok=True)
            log_entry = {
                "date": date,
                "problems_solved": solved,
                "problems_correct": correct,
                "accuracy": round(accuracy, 3),
                "time_minutes": time_min,
                "summary": summary,
                "next_focus": next_focus,
                "submitted_via": "mcp_go_training_server",
                "timestamp": datetime.now().isoformat()
            }
            log_file = f"mcp_result_{date.replace('-', '')}.json"
            _write_json(os.path.join(log_dir, log_file), log_entry)

            return [TextContent(type="text", text=json.dumps({
                "status": "success",
                "player": pid,
                "date": date,
                "solved": solved,
                "correct": correct,
                "accuracy": round(accuracy, 3),
                "log_file": log_file
            }, ensure_ascii=False, indent=2))]

        elif name == "start_match":
            import uuid
            match_id = f"go-match-{int(datetime.now().timestamp())}"
            match_data = {
                "game_id": match_id,
                "status": "pending",
                "black": arguments.get("black", "xiaochen"),
                "white": arguments.get("white", "zhuguxia"),
                "board_size": arguments.get("board_size", 9),
                "moves": [],
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "rule": arguments.get("rule", "中国规则"),
                "komi": arguments.get("komi", 7.5),
                "next_turn": "black",
                "notes": "MCP 发起的对局"
            }
            _write_json(os.path.join(MATCHES_DIR, f"{match_id}.json"), match_data)
            return [TextContent(type="text", text=json.dumps({
                "status": "success",
                "match_id": match_id,
                "data": match_data
            }, ensure_ascii=False, indent=2))]

        elif name == "submit_move":
            match_id = arguments["match_id"]
            match_path = os.path.join(MATCHES_DIR, f"{match_id}.json")
            match = _read_json(match_path)
            if not match:
                return [TextContent(type="text", text=json.dumps({"error": "match not found"}))]

            move_num = len(match.get("moves", [])) + 1
            move = {
                "move": move_num,
                "player": arguments["player"],
                "color": "black" if match["black"] == arguments["player"] else "white",
                "coord": arguments["coord"],
                "reason": arguments.get("reason", ""),
                "timestamp": datetime.now().isoformat()
            }
            match.setdefault("moves", []).append(move)
            # 切换回合
            match["next_turn"] = "white" if match["next_turn"] == "black" else "black"
            _write_json(match_path, match)

            return [TextContent(type="text", text=json.dumps({
                "status": "success",
                "move": move
            }, ensure_ascii=False, indent=2))]

        elif name == "get_match_status":
            match_id = arguments["match_id"]
            match = _read_json(os.path.join(MATCHES_DIR, f"{match_id}.json"))
            return [TextContent(type="text", text=json.dumps(match, ensure_ascii=False, indent=2))]

        elif name == "list_matches":
            matches = []
            if os.path.exists(MATCHES_DIR):
                for f in sorted(os.listdir(MATCHES_DIR)):
                    if f.endswith('.json') and f.startswith('go-match'):
                        data = _read_json(os.path.join(MATCHES_DIR, f))
                        if data:
                            if arguments.get("status") and data.get("status") != arguments["status"]:
                                continue
                            matches.append(data)
            return [TextContent(type="text", text=json.dumps({
                "count": len(matches),
                "matches": matches
            }, ensure_ascii=False, indent=2))]

        elif name == "get_problem_bank_stats":
            stats = {}
            categories = ["life", "tesuji", "joseki", "endgame", "fuseki"]
            for cat in categories:
                cat_dir = os.path.join(PROBLEM_BANK, cat)
                if os.path.exists(cat_dir):
                    files = [f for f in os.listdir(cat_dir) if f.endswith('.json')]
                    stats[cat] = len(files)
                else:
                    stats[cat] = 0
            return [TextContent(type="text", text=json.dumps({
                "problem_bank_path": PROBLEM_BANK,
                "categories": stats,
                "total": sum(stats.values())
            }, ensure_ascii=False, indent=2))]

        elif name == "update_training_config":
            status_path = os.path.join(BASE_DIR, "status.json")
            status = _read_json(status_path) or {}
            if "phase" in arguments:
                status["phase"] = arguments["phase"]
            if "week" in arguments:
                status["week"] = arguments["week"]
            if "day" in arguments:
                status["day"] = arguments["day"]
            if "topic" in arguments:
                status["topic"] = arguments["topic"]
            status["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            _write_json(status_path, status)
            return [TextContent(type="text", text=json.dumps({
                "status": "success",
                "updated": status
            }, ensure_ascii=False, indent=2))]

        elif name == "get_ecosystem_training_overview":
            status = _read_json(os.path.join(BASE_DIR, "status.json")) or {}
            xiaochen_profile = _read_json(os.path.join(XIAOCHEN_DIR, "profile.json")) or {}
            xiaochen_progress = _read_json(os.path.join(XIAOCHEN_DIR, "progress.json")) or {}
            zhuguxia_profile = _read_json(os.path.join(ZHUGUXIA_DIR, "profile.json")) or {}
            zhuguxia_progress = _read_json(os.path.join(ZHUGUXIA_DIR, "progress.json")) or {}

            overview = {
                "system": {
                    "version": status.get("version", "3.0"),
                    "phase": status.get("phase"),
                    "week": status.get("week"),
                    "topic": status.get("topic"),
                    "last_updated": status.get("last_updated")
                },
                "xiaochen": {
                    "name": xiaochen_profile.get("name"),
                    "level": xiaochen_profile.get("current_level"),
                    "type": xiaochen_profile.get("type"),
                    "total_solved": xiaochen_progress.get("total_solved", 0),
                    "total_correct": xiaochen_progress.get("total_correct", 0),
                    "accuracy": xiaochen_progress.get("overall_accuracy", 0),
                    "strengths": xiaochen_profile.get("strengths", []),
                    "weaknesses": xiaochen_profile.get("weaknesses", [])
                },
                "zhuguxia": {
                    "name": zhuguxia_profile.get("name"),
                    "level": zhuguxia_profile.get("current_level"),
                    "type": zhuguxia_profile.get("type"),
                    "total_solved": zhuguxia_progress.get("total_solved", 0),
                    "total_correct": zhuguxia_progress.get("total_correct", 0),
                    "accuracy": zhuguxia_progress.get("overall_accuracy", 0),
                    "strengths": zhuguxia_profile.get("strengths", []),
                    "weaknesses": zhuguxia_profile.get("weaknesses", [])
                }
            }
            return [TextContent(type="text", text=json.dumps(overview, ensure_ascii=False, indent=2))]

        else:
            return [TextContent(type="text", text=f"未知工具: {name}")]

    except Exception as e:
        logger.error(f"工具执行错误: {name} - {e}", exc_info=True)
        return [TextContent(type="text", text=json.dumps({
            "status": "error",
            "error": str(e)
        }, ensure_ascii=False, indent=2))]

async def main():
    logger.info("🦞 MCP Go Training Server 启动中...")
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream, write_stream,
            InitializationOptions(
                server_name="mcp-go-training",
                server_version="1.0.0",
                capabilities=app.get_capabilities()
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
