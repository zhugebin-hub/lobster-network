#!/usr/bin/env python3
"""
🦞 MCP 双向通道 - 消息中继服务器 v7
使用自定义 ASGI 应用，直接路由到 SSE transport
"""

import os
import json
import time
import uuid
import sqlite3
import secrets
import logging
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import TextContent, Tool

from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import PlainTextResponse, JSONResponse
from starlette.requests import Request
import uvicorn

logger = logging.getLogger("mcp-relay")

# === 配置 ===
DB_PATH = os.environ.get("MCP_RELAY_DB", "/home/admin/.openclaw/workspace/mcp-relay-server/relay.db")
HOST = os.environ.get("MCP_RELAY_HOST", "0.0.0.0")
PORT = int(os.environ.get("MCP_RELAY_PORT", "8721"))
API_TOKEN = os.environ.get("MCP_RELAY_TOKEN", "")

if not API_TOKEN:
    API_TOKEN = secrets.token_urlsafe(32)
    print(f"⚠️  未设置 MCP_RELAY_TOKEN，自动生成: {API_TOKEN}")

# === 数据库 ===
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS agents (
            agent_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            registered_at TEXT NOT NULL,
            last_seen TEXT NOT NULL,
            metadata TEXT DEFAULT '{}'
        );
        CREATE TABLE IF NOT EXISTS messages (
            msg_id TEXT PRIMARY KEY,
            from_agent TEXT NOT NULL,
            to_agent TEXT NOT NULL,
            content TEXT NOT NULL,
            msg_type TEXT DEFAULT 'text',
            timestamp TEXT NOT NULL,
            read INTEGER DEFAULT 0
        );
        CREATE INDEX IF NOT EXISTS idx_messages_to ON messages(to_agent, read);
        CREATE INDEX IF NOT EXISTS idx_messages_from ON messages(from_agent);
    """)
    conn.commit()
    conn.close()

# === MCP Server ===
server = Server("mcp-relay")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="send_message",
            description="发送消息给指定的 Agent。消息会被中继存储，对方通过 get_messages 获取。",
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "目标 Agent ID，如 xiaochen、xiasher"
                    },
                    "content": {
                        "type": "string",
                        "description": "消息内容（文本）"
                    },
                    "msg_type": {
                        "type": "string",
                        "description": "消息类型：text / command / file / system",
                        "enum": ["text", "command", "file", "system"],
                        "default": "text"
                    }
                },
                "required": ["to", "content"]
            }
        ),
        Tool(
            name="get_messages",
            description="获取自己收到的未读消息。可选是否标记为已读。",
            inputSchema={
                "type": "object",
                "properties": {
                    "mark_read": {
                        "type": "boolean",
                        "description": "获取后是否标记为已读",
                        "default": True
                    },
                    "limit": {
                        "type": "integer",
                        "description": "最多返回消息数量",
                        "default": 50
                    }
                }
            }
        ),
        Tool(
            name="register_agent",
            description="注册或更新自己的 Agent 信息。首次连接时必须调用。",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {
                        "type": "string",
                        "description": "Agent 唯一 ID，如 xiaochen、xiasher"
                    },
                    "name": {
                        "type": "string",
                        "description": "Agent 显示名称，如 小陈、虾尔"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "额外信息（可选），如平台、版本等"
                    }
                },
                "required": ["agent_id", "name"]
            }
        ),
        Tool(
            name="list_agents",
            description="列出所有已注册的 Agent 及其状态。",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="agent_status",
            description="查询指定 Agent 的在线状态和最后活跃时间。",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {
                        "type": "string",
                        "description": "要查询的 Agent ID"
                    }
                },
                "required": ["agent_id"]
            }
        ),
        Tool(
            name="ping",
            description="心跳检测，返回服务器当前时间和版本信息。",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="delete_message",
            description="删除指定消息（按 msg_id）。",
            inputSchema={
                "type": "object",
                "properties": {
                    "msg_id": {
                        "type": "string",
                        "description": "要删除的消息 ID"
                    }
                },
                "required": ["msg_id"]
            }
        ),
        Tool(
            name="clear_messages",
            description="清空自己收到的所有消息。",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    now = datetime.now(timezone.utc).isoformat()

    # 不需要认证的 tool
    if name == "ping":
        return [TextContent(
            type="text",
            text=json.dumps({
                "status": "ok",
                "server_time": now,
                "version": "7.0.0",
                "message": "🦞 MCP 双向通道中继服务器运行中"
            }, ensure_ascii=False, indent=2)
        )]
    
    if name == "register_agent":
        agent_id = arguments.get("agent_id", "")
        agent_name = arguments.get("name", "")
        metadata = arguments.get("metadata", {})
        if not agent_id or not agent_name:
            return [TextContent(type="text", text=json.dumps({
                "error": "agent_id 和 name 是必填参数"
            }, ensure_ascii=False))]
        
        conn = get_db()
        conn.execute(
            """INSERT INTO agents (agent_id, name, registered_at, last_seen, metadata)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(agent_id) DO UPDATE SET
                   name=excluded.name,
                   last_seen=excluded.last_seen,
                   metadata=excluded.metadata""",
            (agent_id, agent_name, now, now, json.dumps(metadata, ensure_ascii=False))
        )
        conn.commit()
        conn.close()
        return [TextContent(type="text", text=json.dumps({
            "status": "registered",
            "agent_id": agent_id,
            "name": agent_name,
            "message": f"✅ {agent_name} ({agent_id}) 注册成功"
        }, ensure_ascii=False, indent=2))]

    if name == "list_agents":
        conn = get_db()
        rows = conn.execute("SELECT * FROM agents ORDER BY last_seen DESC").fetchall()
        conn.close()
        agents = [dict(r) for r in rows]
        for a in agents:
            try:
                a["metadata"] = json.loads(a.get("metadata", "{}"))
            except:
                a["metadata"] = {}
        return [TextContent(type="text", text=json.dumps({
            "agents": agents,
            "count": len(agents)
        }, ensure_ascii=False, indent=2))]

    if name == "agent_status":
        agent_id = arguments.get("agent_id", "")
        conn = get_db()
        row = conn.execute("SELECT * FROM agents WHERE agent_id = ?", (agent_id,)).fetchone()
        conn.close()
        if not row:
            return [TextContent(type="text", text=json.dumps({
                "error": f"Agent '{agent_id}' 未注册"
            }, ensure_ascii=False))]
        info = dict(row)
        try:
            info["metadata"] = json.loads(info.get("metadata", "{}"))
        except:
            info["metadata"] = {}
        return [TextContent(type="text", text=json.dumps(info, ensure_ascii=False, indent=2))]

    # 以下 tool 需要知道 caller（从 arguments 中获取 _agent_id）
    caller = arguments.get("_agent_id", "")

    if name == "send_message":
        if not caller:
            return [TextContent(type="text", text=json.dumps({
                "error": "无法识别发送者身份。请在参数中传入 _agent_id。"
            }, ensure_ascii=False))]
        
        to_agent = arguments.get("to", "")
        content = arguments.get("content", "")
        msg_type = arguments.get("msg_type", "text")
        
        if not to_agent or not content:
            return [TextContent(type="text", text=json.dumps({
                "error": "to 和 content 是必填参数"
            }, ensure_ascii=False))]
        
        msg_id = f"{int(time.time()*1000)}-{uuid.uuid4().hex[:8]}"
        conn = get_db()
        conn.execute(
            """INSERT INTO messages (msg_id, from_agent, to_agent, content, msg_type, timestamp)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (msg_id, caller, to_agent, content, msg_type, now)
        )
        conn.execute(
            "UPDATE agents SET last_seen = ? WHERE agent_id = ?",
            (now, caller)
        )
        conn.commit()
        conn.close()
        
        return [TextContent(type="text", text=json.dumps({
            "status": "sent",
            "msg_id": msg_id,
            "from": caller,
            "to": to_agent,
            "message": f"✅ 消息已发送给 {to_agent}"
        }, ensure_ascii=False, indent=2))]

    if name == "get_messages":
        if not caller:
            return [TextContent(type="text", text=json.dumps({
                "error": "无法识别接收者身份。请在参数中传入 _agent_id。"
            }, ensure_ascii=False))]
        
        mark_read = arguments.get("mark_read", True)
        limit = min(arguments.get("limit", 50), 200)
        
        conn = get_db()
        rows = conn.execute(
            """SELECT * FROM messages 
               WHERE to_agent = ? AND read = 0 
               ORDER BY timestamp ASC LIMIT ?""",
            (caller, limit)
        ).fetchall()
        
        messages = [dict(r) for r in rows]
        
        if mark_read and messages:
            msg_ids = [m["msg_id"] for m in messages]
            placeholders = ",".join("?" * len(msg_ids))
            conn.execute(
                f"UPDATE messages SET read = 1 WHERE msg_id IN ({placeholders})",
                msg_ids
            )
            conn.execute(
                "UPDATE agents SET last_seen = ? WHERE agent_id = ?",
                (now, caller)
            )
            conn.commit()
        
        conn.close()
        
        return [TextContent(type="text", text=json.dumps({
            "agent_id": caller,
            "unread_count": len(messages),
            "messages": messages
        }, ensure_ascii=False, indent=2))]

    if name == "delete_message":
        if not caller:
            return [TextContent(type="text", text=json.dumps({
                "error": "无法识别身份"
            }, ensure_ascii=False))]
        
        msg_id = arguments.get("msg_id", "")
        conn = get_db()
        row = conn.execute(
            "SELECT * FROM messages WHERE msg_id = ? AND to_agent = ?",
            (msg_id, caller)
        ).fetchone()
        if not row:
            conn.close()
            return [TextContent(type="text", text=json.dumps({
                "error": f"消息 {msg_id} 不存在或不属于你"
            }, ensure_ascii=False))]
        
        conn.execute("DELETE FROM messages WHERE msg_id = ?", (msg_id,))
        conn.commit()
        conn.close()
        return [TextContent(type="text", text=json.dumps({
            "status": "deleted",
            "msg_id": msg_id
        }, ensure_ascii=False))]

    if name == "clear_messages":
        if not caller:
            return [TextContent(type="text", text=json.dumps({
                "error": "无法识别身份"
            }, ensure_ascii=False))]
        
        conn = get_db()
        result = conn.execute(
            "DELETE FROM messages WHERE to_agent = ?",
            (caller,)
        )
        conn.commit()
        deleted = result.rowcount
        conn.close()
        return [TextContent(type="text", text=json.dumps({
            "status": "cleared",
            "deleted_count": deleted
        }, ensure_ascii=False))]

    return [TextContent(type="text", text=json.dumps({
        "error": f"未知工具: {name}"
    }, ensure_ascii=False))]


# === SSE Transport & Starlette App ===
# 使用全局变量存储 SSE transport 实例和 agent_id 映射
sse_transport = None
agent_id_map = {}  # session_id -> agent_id

async def handle_sse(request: Request):
    """处理 SSE 连接"""
    global sse_transport, agent_id_map
    
    agent_id = request.query_params.get("agent_id", "")
    
    # 如果 query 中有 agent_id，自动注册
    if agent_id:
        name = request.query_params.get("name", agent_id)
        conn = get_db()
        now = datetime.now(timezone.utc).isoformat()
        conn.execute(
            """INSERT INTO agents (agent_id, name, registered_at, last_seen, metadata)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(agent_id) DO UPDATE SET
                   name=excluded.name,
                   last_seen=excluded.last_seen""",
            (agent_id, name, now, now, '{}')
        )
        conn.commit()
        conn.close()
    
    # 创建 SSE transport 实例（如果还没有）
    if sse_transport is None:
        sse_transport = SseServerTransport("/messages/")
    
    # 使用 SSE transport 处理连接
    async with sse_transport.connect_sse(
        request.scope, request.receive, request._send
    ) as (read_stream, write_stream):
        # 获取 session_id
        session_id = request.query_params.get("session_id", "")
        if session_id and agent_id:
            agent_id_map[session_id] = agent_id
        
        # 注入 _agent_id 到 call_tool 的 arguments 中
        original_call_tool = server.call_tool
        
        async def wrapped_call_tool(name, arguments):
            # 从 session_id 获取 agent_id
            current_agent_id = agent_id
            if not current_agent_id and session_id:
                current_agent_id = agent_id_map.get(session_id, "")
            
            if current_agent_id:
                arguments = dict(arguments)
                arguments["_agent_id"] = current_agent_id
            return await original_call_tool(name, arguments)
        
        server.call_tool = wrapped_call_tool
        
        try:
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
        finally:
            server.call_tool = original_call_tool
            # 清理 session_id 映射
            if session_id in agent_id_map:
                del agent_id_map[session_id]

async def handle_messages(request: Request):
    """处理 POST 到 /messages/ 的消息"""
    global sse_transport
    if sse_transport:
        # SSE transport's handle_post_message is an ASGI callable
        # It directly calls send() with the response
        await sse_transport.handle_post_message(
            request.scope, request.receive, request._send
        )
        return None  # The SSE transport handles the response directly
    return JSONResponse({"error": "SSE transport not initialized"}, status_code=503)

@asynccontextmanager
async def lifespan(app):
    init_db()
    logger.info(f"✅ MCP 中继服务器数据库已初始化: {DB_PATH}")
    try:
        yield
    finally:
        pass

app = Starlette(
    debug=True,
    lifespan=lifespan,
    routes=[
        Route("/sse/", endpoint=handle_sse),
        Route("/messages/", endpoint=handle_messages, methods=["POST"]),
        Route("/health", endpoint=lambda r: PlainTextResponse("ok")),
        Route("/auth", endpoint=lambda r: JSONResponse(
            {"authenticated": True, "token_valid": True}
            if r.query_params.get("token") == API_TOKEN
            else {"authenticated": False}
        )),
    ],
)

if __name__ == "__main__":
    print(f"🦞 MCP 双向通道中继服务器 v7.0")
    print(f"   监听地址: http://{HOST}:{PORT}")
    print(f"   SSE 端点: http://{HOST}:{PORT}/sse/")
    print(f"   数据库: {DB_PATH}")
    print(f"   API Token: {API_TOKEN[:12]}...")
    print(f"")
    print(f"📡 连接信息（发给对方配置用）:")
    print(f"   URL: http://60.205.139.51:{PORT}/sse/")
    print(f"   Token: {API_TOKEN}")
    
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level="info"
    )
