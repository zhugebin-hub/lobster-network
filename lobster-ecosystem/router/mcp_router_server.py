#!/usr/bin/env python3
"""
🦞 MCP Router Server - 小龙虾生态路由中枢 v1.0
==============================================
核心功能：
  - 服务注册与发现（各小龙虾注册自身能力）
  - 消息路由分发（按任务类型/用户/优先级）
  - 消息持久化（SQLite）
  - 心跳检测（在线状态管理）
  - SSE 实时推送

架构：
  用户入口 → 虾尔(Client) → MCP Router(Server) → 诸葛马/诸葛虾(Client) → 返回结果
"""

import sqlite3
import json
import uuid
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from contextlib import asynccontextmanager

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.types import (
    Tool, TextContent, Prompt, Resource,
    PromptMessage, PromptArgument,
    ResourceTemplate, EmbeddedResource, ImageContent
)
import mcp.server.stdio
import mcp.types as types

# ============ 日志配置 ============
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [Router] %(levelname)s: %(message)s'
)
logger = logging.getLogger("mcp-router")

# ============ 数据库初始化 ============
DB_PATH = "/home/admin/.openclaw/workspace/lobster-ecosystem/router/router.db"

def init_db():
    """初始化路由数据库"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 服务注册表
    c.execute('''CREATE TABLE IF NOT EXISTS services (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        role TEXT NOT NULL,
        capabilities TEXT,
        status TEXT DEFAULT 'offline',
        last_heartbeat TEXT,
        registered_at TEXT,
        endpoint TEXT,
        metadata TEXT
    )''')

    # 消息队列
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY,
        from_service TEXT NOT NULL,
        to_service TEXT NOT NULL,
        type TEXT NOT NULL,
        priority TEXT DEFAULT 'normal',
        payload TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        created_at TEXT,
        delivered_at TEXT,
        ack_at TEXT,
        error TEXT,
        route_log TEXT
    )''')

    # 路由规则
    c.execute('''CREATE TABLE IF NOT EXISTS route_rules (
        id TEXT PRIMARY KEY,
        pattern TEXT NOT NULL,
        target_service TEXT NOT NULL,
        priority INTEGER DEFAULT 0,
        active INTEGER DEFAULT 1,
        created_at TEXT
    )''')

    # 心跳记录
    c.execute('''CREATE TABLE IF NOT EXISTS heartbeats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_id TEXT NOT NULL,
        timestamp TEXT,
        FOREIGN KEY(service_id) REFERENCES services(id)
    )''')

    conn.commit()
    conn.close()
    logger.info("数据库初始化完成: %s", DB_PATH)

# ============ 数据库操作 ============
class RouterDB:
    def __init__(self):
        self.db_path = DB_PATH

    def _conn(self):
        return sqlite3.connect(self.db_path)

    # --- 服务管理 ---
    def register_service(self, service_id: str, name: str, role: str,
                         capabilities: list, endpoint: str = "",
                         metadata: dict = None) -> bool:
        now = datetime.now().isoformat()
        conn = self._conn()
        try:
            conn.execute('''INSERT OR REPLACE INTO services
                (id, name, role, capabilities, status, registered_at, endpoint, metadata)
                VALUES (?, ?, ?, ?, 'online', ?, ?, ?)''',
                (service_id, name, role, json.dumps(capabilities), now, endpoint,
                 json.dumps(metadata or {})))
            conn.commit()
            logger.info(f"服务注册: {name} ({service_id}) role={role}")
            return True
        except Exception as e:
            logger.error(f"服务注册失败: {e}")
            return False
        finally:
            conn.close()

    def update_heartbeat(self, service_id: str):
        now = datetime.now().isoformat()
        conn = self._conn()
        try:
            conn.execute('''UPDATE services SET status='online', last_heartbeat=?
                WHERE id=?''', (now, service_id))
            conn.execute('''INSERT INTO heartbeats (service_id, timestamp)
                VALUES (?, ?)''', (service_id, now))
            conn.commit()
        except Exception as e:
            logger.error(f"心跳更新失败: {e}")
        finally:
            conn.close()

    def get_service(self, service_id: str) -> Optional[dict]:
        conn = self._conn()
        conn.row_factory = sqlite3.Row
        try:
            row = conn.execute('SELECT * FROM services WHERE id=?', (service_id,)).fetchone()
            if row:
                return dict(row)
            return None
        finally:
            conn.close()

    def list_services(self, role: str = None, status: str = None) -> list:
        conn = self._conn()
        conn.row_factory = sqlite3.Row
        try:
            query = 'SELECT * FROM services WHERE 1=1'
            params = []
            if role:
                query += ' AND role=?'
                params.append(role)
            if status:
                query += ' AND status=?'
                params.append(status)
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    # --- 消息路由 ---
    def send_message(self, from_id: str, to_id: str, msg_type: str,
                     payload: dict, priority: str = "normal",
                     route_log: str = "") -> str:
        msg_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        conn = self._conn()
        try:
            conn.execute('''INSERT INTO messages
                (id, from_service, to_service, type, priority, payload, status, created_at, route_log)
                VALUES (?, ?, ?, ?, ?, ?, 'pending', ?, ?)''',
                (msg_id, from_id, to_id, msg_type, priority,
                 json.dumps(payload), now, route_log))
            conn.commit()
            logger.info(f"消息路由: {from_id} → {to_id} [{msg_type}] {msg_id}")
            return msg_id
        except Exception as e:
            logger.error(f"消息发送失败: {e}")
            return ""
        finally:
            conn.close()

    def get_pending_messages(self, service_id: str) -> list:
        conn = self._conn()
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute('''SELECT * FROM messages
                WHERE to_service=? AND status='pending'
                ORDER BY CASE priority
                    WHEN 'urgent' THEN 1
                    WHEN 'high' THEN 2
                    WHEN 'normal' THEN 3
                    WHEN 'low' THEN 4
                END, created_at''', (service_id,)).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def mark_delivered(self, msg_id: str):
        now = datetime.now().isoformat()
        conn = self._conn()
        try:
            conn.execute('''UPDATE messages SET status='delivered', delivered_at=?
                WHERE id=?''', (now, msg_id))
            conn.commit()
        finally:
            conn.close()

    def mark_acked(self, msg_id: str):
        now = datetime.now().isoformat()
        conn = self._conn()
        try:
            conn.execute('''UPDATE messages SET status='acked', ack_at=?
                WHERE id=?''', (now, msg_id))
            conn.commit()
        finally:
            conn.close()

    def get_message(self, msg_id: str) -> Optional[dict]:
        conn = self._conn()
        conn.row_factory = sqlite3.Row
        try:
            row = conn.execute('SELECT * FROM messages WHERE id=?', (msg_id,)).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def list_messages(self, service_id: str = None, status: str = None,
                      limit: int = 20) -> list:
        conn = self._conn()
        conn.row_factory = sqlite3.Row
        try:
            query = 'SELECT * FROM messages WHERE 1=1'
            params = []
            if service_id:
                query += ' AND (from_service=? OR to_service=?)'
                params.extend([service_id, service_id])
            if status:
                query += ' AND status=?'
                params.append(status)
            query += ' ORDER BY created_at DESC LIMIT ?'
            params.append(limit)
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    # --- 路由规则 ---
    def add_route_rule(self, pattern: str, target: str, priority: int = 0) -> str:
        rule_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        conn = self._conn()
        try:
            conn.execute('''INSERT INTO route_rules (id, pattern, target_service, priority, created_at)
                VALUES (?, ?, ?, ?, ?)''', (rule_id, pattern, target, priority, now))
            conn.commit()
            return rule_id
        finally:
            conn.close()

    def get_route_rules(self) -> list:
        conn = self._conn()
        conn.row_factory = sqlite3.Row
        try:
            rows = conn.execute(
                'SELECT * FROM route_rules WHERE active=1 ORDER BY priority DESC'
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def resolve_route(self, msg_type: str, payload: dict) -> Optional[str]:
        """根据消息类型和内容匹配路由规则"""
        rules = self.get_route_rules()
        for rule in rules:
            pattern = rule['pattern']
            # 简单模式匹配
            if pattern == msg_type or pattern == "*":
                return rule['target_service']
            # JSONPath 风格匹配
            if pattern.startswith('$'):
                keys = pattern.lstrip('$').split('.')
                val = payload
                for k in keys:
                    if isinstance(val, dict) and k in val:
                        val = val[k]
                    else:
                        val = None
                        break
                if val and str(val).lower() in rule['pattern'].lower():
                    return rule['target_service']
        return None

    # --- 统计 ---
    def get_stats(self) -> dict:
        conn = self._conn()
        try:
            stats = {}
            stats['total_services'] = conn.execute('SELECT COUNT(*) FROM services').fetchone()[0]
            stats['online_services'] = conn.execute(
                "SELECT COUNT(*) FROM services WHERE status='online'"
            ).fetchone()[0]
            stats['total_messages'] = conn.execute('SELECT COUNT(*) FROM messages').fetchone()[0]
            stats['pending_messages'] = conn.execute(
                "SELECT COUNT(*) FROM messages WHERE status='pending'"
            ).fetchone()[0]
            stats['delivered_messages'] = conn.execute(
                "SELECT COUNT(*) FROM messages WHERE status IN ('delivered','acked')"
            ).fetchone()[0]
            stats['route_rules'] = conn.execute(
                "SELECT COUNT(*) FROM route_rules WHERE active=1"
            ).fetchone()[0]
            return stats
        finally:
            conn.close()

# ============ MCP Router Server ============
router_db = RouterDB()

# 初始化默认路由规则（围棋学习路由）
DEFAULT_RULES = [
    ("go_training_task", "xiaochen", 10),       # 围棋训练任务 → 小陈
    ("go_training_result", "hermes", 10),        # 训练结果 → 诸葛马
    ("go_match_request", "hermes", 10),          # 对局请求 → 诸葛马
    ("go_match_move", "*", 5),                   # 落子 → 广播
    ("go_review", "hermes", 8),                  # 复盘 → 诸葛马
    ("review_request", "hermes", 10),            # 审核请求 → 诸葛马
    ("strategic_planning", "hermes", 10),        # 战略规划 → 诸葛马
    ("broadcast", "*", 1),                       # 广播 → 所有
    ("*", "hermes", 0),                          # 默认 → 诸葛马
]

def init_default_rules():
    """初始化默认路由规则"""
    conn = sqlite3.connect(DB_PATH)
    try:
        count = conn.execute("SELECT COUNT(*) FROM route_rules").fetchone()[0]
        if count == 0:
            now = datetime.now().isoformat()
            for pattern, target, priority in DEFAULT_RULES:
                conn.execute('''INSERT INTO route_rules
                    (id, pattern, target_service, priority, active, created_at)
                    VALUES (?, ?, ?, ?, 1, ?)''',
                    (str(uuid.uuid4()), pattern, target, priority, now))
            conn.commit()
            logger.info(f"初始化 {len(DEFAULT_RULES)} 条默认路由规则")
    finally:
        conn.close()

# ============ 创建 MCP Server ============
app = Server("mcp-router-server")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="register_service",
            description="注册小龙虾服务到路由中枢。需要提供服务ID、名称、角色和能力列表。",
            inputSchema={
                "type": "object",
                "properties": {
                    "service_id": {"type": "string", "description": "服务唯一ID，如 lobster-001"},
                    "name": {"type": "string", "description": "服务名称，如 虾尔"},
                    "role": {"type": "string", "description": "角色类型：gateway/router/worker"},
                    "capabilities": {"type": "array", "items": {"type": "string"},
                                   "description": "能力列表，如 ['go_training', 'review', 'match']"},
                    "endpoint": {"type": "string", "description": "服务端点（可选）"},
                    "metadata": {"type": "object", "description": "额外元数据（可选）"}
                },
                "required": ["service_id", "name", "role", "capabilities"]
            }
        ),
        Tool(
            name="heartbeat",
            description="发送心跳保持在线状态。服务应定期调用此工具。",
            inputSchema={
                "type": "object",
                "properties": {
                    "service_id": {"type": "string", "description": "服务ID"}
                },
                "required": ["service_id"]
            }
        ),
        Tool(
            name="send_message",
            description="通过路由中枢发送消息。自动匹配路由规则分发到目标服务。",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_service": {"type": "string", "description": "发送方服务ID"},
                    "to_service": {"type": "string", "description": "目标服务ID（*表示广播）"},
                    "type": {"type": "string", "description": "消息类型，如 go_training_task"},
                    "payload": {"type": "object", "description": "消息内容（JSON对象）"},
                    "priority": {"type": "string", "enum": ["urgent", "high", "normal", "low"],
                                "description": "优先级", "default": "normal"}
                },
                "required": ["from_service", "to_service", "type", "payload"]
            }
        ),
        Tool(
            name="receive_messages",
            description="获取发送给当前服务的待处理消息队列。",
            inputSchema={
                "type": "object",
                "properties": {
                    "service_id": {"type": "string", "description": "当前服务ID"},
                    "max_count": {"type": "integer", "description": "最大返回数量", "default": 10}
                },
                "required": ["service_id"]
            }
        ),
        Tool(
            name="ack_message",
            description="确认消息已处理。",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {"type": "string", "description": "消息ID"},
                    "service_id": {"type": "string", "description": "处理方服务ID"}
                },
                "required": ["message_id", "service_id"]
            }
        ),
        Tool(
            name="list_services",
            description="列出所有已注册的服务及其状态。",
            inputSchema={
                "type": "object",
                "properties": {
                    "role": {"type": "string", "description": "按角色过滤（可选）"},
                    "status": {"type": "string", "description": "按状态过滤（可选）"}
                }
            }
        ),
        Tool(
            name="get_stats",
            description="获取路由中枢统计信息。",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="add_route_rule",
            description="添加新的路由规则。",
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "匹配模式（消息类型）"},
                    "target": {"type": "string", "description": "目标服务ID"},
                    "priority": {"type": "integer", "description": "优先级（数字越大越优先）", "default": 0}
                },
                "required": ["pattern", "target"]
            }
        ),
        Tool(
            name="get_message",
            description="查询指定消息的详情和状态。",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {"type": "string", "description": "消息ID"}
                },
                "required": ["message_id"]
            }
        ),
        Tool(
            name="list_messages",
            description="列出消息历史。",
            inputSchema={
                "type": "object",
                "properties": {
                    "service_id": {"type": "string", "description": "按服务过滤（可选）"},
                    "status": {"type": "string", "description": "按状态过滤（可选）"},
                    "limit": {"type": "integer", "description": "返回数量", "default": 20}
                }
            }
        ),
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        if name == "register_service":
            success = router_db.register_service(
                arguments["service_id"], arguments["name"], arguments["role"],
                arguments.get("capabilities", []),
                arguments.get("endpoint", ""),
                arguments.get("metadata", {})
            )
            return [TextContent(type="text", text=json.dumps({
                "status": "success" if success else "error",
                "message": f"服务 {arguments['name']} 已注册" if success else "注册失败"
            }, ensure_ascii=False, indent=2))]

        elif name == "heartbeat":
            router_db.update_heartbeat(arguments["service_id"])
            return [TextContent(type="text", text=json.dumps({
                "status": "ok",
                "message": f"{arguments['service_id']} 心跳已更新",
                "timestamp": datetime.now().isoformat()
            }, ensure_ascii=False, indent=2))]

        elif name == "send_message":
            # 自动路由：如果 to_service 是 "*" 或未指定，尝试匹配路由规则
            to_svc = arguments.get("to_service", "*")
            if to_svc == "*":
                resolved = router_db.resolve_route(
                    arguments["type"], arguments.get("payload", {})
                )
                if resolved:
                    to_svc = resolved
                    logger.info(f"自动路由: {arguments['type']} → {resolved}")

            msg_id = router_db.send_message(
                arguments["from_service"], to_svc, arguments["type"],
                arguments["payload"], arguments.get("priority", "normal"),
                f"routed_by={to_svc}"
            )
            return [TextContent(type="text", text=json.dumps({
                "status": "success",
                "message_id": msg_id,
                "from": arguments["from_service"],
                "to": to_svc,
                "type": arguments["type"]
            }, ensure_ascii=False, indent=2))]

        elif name == "receive_messages":
            msgs = router_db.get_pending_messages(arguments["service_id"])
            max_count = arguments.get("max_count", 10)
            msgs = msgs[:max_count]
            # 标记为已投递
            for m in msgs:
                router_db.mark_delivered(m["id"])
            result = []
            for m in msgs:
                result.append({
                    "id": m["id"],
                    "from": m["from_service"],
                    "type": m["type"],
                    "priority": m["priority"],
                    "payload": json.loads(m["payload"]),
                    "created_at": m["created_at"]
                })
            return [TextContent(type="text", text=json.dumps({
                "service_id": arguments["service_id"],
                "count": len(result),
                "messages": result
            }, ensure_ascii=False, indent=2))]

        elif name == "ack_message":
            router_db.mark_acked(arguments["message_id"])
            return [TextContent(type="text", text=json.dumps({
                "status": "acked",
                "message_id": arguments["message_id"]
            }, ensure_ascii=False, indent=2))]

        elif name == "list_services":
            services = router_db.list_services(
                arguments.get("role"), arguments.get("status")
            )
            for s in services:
                s["capabilities"] = json.loads(s["capabilities"]) if s["capabilities"] else []
                s["metadata"] = json.loads(s["metadata"]) if s["metadata"] else {}
            return [TextContent(type="text", text=json.dumps({
                "count": len(services),
                "services": services
            }, ensure_ascii=False, indent=2))]

        elif name == "get_stats":
            stats = router_db.get_stats()
            return [TextContent(type="text", text=json.dumps(stats, ensure_ascii=False, indent=2))]

        elif name == "add_route_rule":
            rule_id = router_db.add_route_rule(
                arguments["pattern"], arguments["target"],
                arguments.get("priority", 0)
            )
            return [TextContent(type="text", text=json.dumps({
                "status": "success",
                "rule_id": rule_id,
                "pattern": arguments["pattern"],
                "target": arguments["target"]
            }, ensure_ascii=False, indent=2))]

        elif name == "get_message":
            msg = router_db.get_message(arguments["message_id"])
            if msg:
                msg["payload"] = json.loads(msg["payload"])
                msg["route_log"] = json.loads(msg["route_log"]) if msg.get("route_log") else {}
            return [TextContent(type="text", text=json.dumps({
                "found": msg is not None,
                "message": msg
            }, ensure_ascii=False, indent=2))]

        elif name == "list_messages":
            msgs = router_db.list_messages(
                arguments.get("service_id"),
                arguments.get("status"),
                arguments.get("limit", 20)
            )
            for m in msgs:
                m["payload"] = json.loads(m["payload"])
            return [TextContent(type="text", text=json.dumps({
                "count": len(msgs),
                "messages": msgs
            }, ensure_ascii=False, indent=2))]

        else:
            return [TextContent(type="text", text=f"未知工具: {name}")]

    except Exception as e:
        logger.error(f"工具执行错误: {name} - {e}", exc_info=True)
        return [TextContent(type="text", text=json.dumps({
            "status": "error",
            "error": str(e)
        }, ensure_ascii=False, indent=2))]

# ============ 启动 ============
async def main():
    init_db()
    init_default_rules()
    logger.info("🦞 MCP Router Server 启动中...")
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream, write_stream,
            InitializationOptions(
                server_name="mcp-router",
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
