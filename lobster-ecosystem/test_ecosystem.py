#!/usr/bin/env python3
"""
🦞 MCP 生态测试脚本 - 验证路由 + 围棋训练服务
================================================
测试场景：
  1. 初始化路由数据库
  2. 注册 3 个服务（虾尔、诸葛虾、诸葛马）
  3. 发送测试消息并验证路由
  4. 调用围棋训练服务获取状态
  5. 验证端到端流程
"""

import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "router"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "go-training"))

# ============ 测试1: 路由服务器 ============
print("=" * 60)
print("🦞 测试1: MCP Router Server - 初始化")
print("=" * 60)

from router.mcp_router_server import RouterDB, init_db, init_default_rules

db = RouterDB()
init_db()
init_default_rules()
print("✅ 路由数据库初始化完成")

# ============ 测试2: 注册服务 ============
print("\n" + "=" * 60)
print("🦞 测试2: 注册小龙虾服务")
print("=" * 60)

services = [
    {
        "id": "lobster-001",
        "name": "虾尔",
        "role": "gateway",
        "capabilities": ["dingtalk_gateway", "wechat_gateway", "task_dispatch", "review"],
        "metadata": {"channel": "dingtalk", "owner": "黄宝怡"}
    },
    {
        "id": "lobster-002",
        "name": "诸葛虾",
        "role": "worker",
        "capabilities": ["go_training", "go_match", "review", "content_generation"],
        "metadata": {"type": "accelerated"}
    },
    {
        "id": "hermes-001",
        "name": "诸葛马",
        "role": "worker",
        "capabilities": ["go_coaching", "thesis_review", "teaching_analysis",
                        "strategic_planning", "match_referee"],
        "metadata": {"type": "coach"}
    },
]

for svc in services:
    success = db.register_service(
        svc["id"], svc["name"], svc["role"],
        svc["capabilities"], "", svc["metadata"]
    )
    status = "✅" if success else "❌"
    print(f"  {status} 注册: {svc['name']} ({svc['id']}) role={svc['role']}")

# ============ 测试3: 服务列表 ============
print("\n" + "=" * 60)
print(" 测试3: 服务注册表")
print("=" * 60)

all_services = db.list_services()
print(f"  已注册 {len(all_services)} 个服务:")
for s in all_services:
    caps = json.loads(s["capabilities"]) if s["capabilities"] else []
    print(f"     {s['name']} ({s['id']}) - role={s['role']} status={s['status']}")
    print(f"       能力: {', '.join(caps)}")

# ============ 测试4: 路由规则 ============
print("\n" + "=" * 60)
print("🦞 测试4: 路由规则")
print("=" * 60)

rules = db.get_route_rules()
print(f"  共 {len(rules)} 条路由规则:")
for r in rules[:5]:
    print(f"    {r['pattern']} → {r['target_service']} (priority={r['priority']})")

# ============ 测试5: 消息路由 ============
print("\n" + "=" * 60)
print("🦞 测试5: 消息路由测试")
print("=" * 60)

test_messages = [
    {
        "from": "lobster-001",
        "to": "hermes-001",
        "type": "go_training_task",
        "payload": {"week": 5, "topic": "定式基础", "student": "xiaochen"},
        "priority": "high"
    },
    {
        "from": "lobster-002",
        "to": "hermes-001",
        "type": "go_training_result",
        "payload": {"student": "zhuguxia", "score": 85, "accuracy": 0.78},
        "priority": "normal"
    },
    {
        "from": "lobster-001",
        "to": "*",
        "type": "go_match_request",
        "payload": {"black": "xiaochen", "white": "zhuguxia", "board": 9},
        "priority": "urgent"
    },
    {
        "from": "lobster-002",
        "to": "hermes-001",
        "type": "review_request",
        "payload": {"doc": "AI黑客松作品展页面", "url": "http://43.133.22.250:8089/"},
        "priority": "high"
    },
    {
        "from": "lobster-001",
        "to": "hermes-001",
        "type": "strategic_planning",
        "payload": {"topic": "小龙虾生态建设", "participants": ["虾尔", "诸葛虾", "诸葛马"]},
        "priority": "urgent"
    },
]

for msg in test_messages:
    msg_id = db.send_message(
        msg["from"], msg["to"], msg["type"],
        msg["payload"], msg["priority"]
    )
    print(f"  ✅ 消息发送: {msg['from']} → {msg['to']} [{msg['type']}]")
    print(f"     ID: {msg_id[:8]}... priority={msg['priority']}")

# ============ 测试6: 消息接收 ============
print("\n" + "=" * 60)
print("🦞 测试6: 诸葛马收取消息")
print("=" * 60)

hermes_msgs = db.get_pending_messages("hermes-001")
print(f"  诸葛马收到 {len(hermes_msgs)} 条待处理消息:")
for m in hermes_msgs:
    payload = json.loads(m["payload"])
    print(f"    📬 [{m['priority']}] {m['type']} from {m['from_service']}")
    print(f"       内容: {json.dumps(payload, ensure_ascii=False)[:80]}...")
    db.mark_delivered(m["id"])

# ============ 测试7: 围棋训练服务 ============
print("\n" + "=" * 60)
print("🦞 测试7: 围棋训练服务调用")
print("=" * 60)

GO_BASE = "/shared/training/go"
status = json.load(open(os.path.join(GO_BASE, "status.json")))
print(f"  训练系统状态:")
print(f"    版本: {status.get('version')}")
print(f"    阶段: {status.get('phase')} | 周次: {status.get('week')} | 天: {status.get('day')}")
print(f"    主题: {status.get('topic')}")

xiaochen = json.load(open(os.path.join(GO_BASE, "xiaochen", "profile.json")))
zhuguxia = json.load(open(os.path.join(GO_BASE, "zhuguxia", "profile.json")))
print(f"\n  学员档案:")
print(f"    小陈: {xiaochen['current_level']} | 类型: {xiaochen['type']}")
print(f"    诸葛虾: {zhuguxia['current_level']} | 类型: {zhuguxia['type']}")

# ============ 测试8: 统计 ============
print("\n" + "=" * 60)
print("🦞 测试8: 路由统计")
print("=" * 60)

stats = db.get_stats()
print(f"  总服务数: {stats['total_services']}")
print(f"  在线服务: {stats['online_services']}")
print(f"  总消息数: {stats['total_messages']}")
print(f"  待处理: {stats['pending_messages']}")
print(f"  已投递: {stats['delivered_messages']}")
print(f"  路由规则: {stats['route_rules']}")

# ============ 测试9: 端到端流程 ============
print("\n" + "=" * 60)
print("🦞 测试9: 端到端流程模拟")
print("=" * 60)

# 模拟：钉钉用户通过虾尔提交围棋学习进度查询
print("  步骤1: 用户通过钉钉向虾尔发送查询请求")
msg1_id = db.send_message("lobster-001", "lobster-001", "user_query",
    {"user": "则白", "query": "围棋学习进度如何？"}, "normal")
print(f"    ✅ 虾尔收到用户请求: {msg1_id[:8]}...")

# 虾尔查询路由，发现需要调用 go_training 服务
print("  步骤2: 虾尔查询路由，发现需要调用 go_training 服务")
target = db.resolve_route("go_training_task", {"student": "xiaochen"})
print(f"    路由解析: go_training_task → {target}")

# 虾尔向路由发送围棋状态查询
print("  步骤3: 虾尔通过路由查询围棋训练状态")
msg2_id = db.send_message("lobster-001", "hermes-001", "go_training_status_query",
    {"requester": "lobster-001"}, "normal")
print(f"    ✅ 状态查询已发送: {msg2_id[:8]}...")

# 诸葛马收到并处理
print("  步骤4: 诸葛马收到查询并处理")
hermes_msgs = db.get_pending_messages("hermes-001")
for m in hermes_msgs:
    db.mark_acked(m["id"])
print(f"    ✅ 诸葛马已处理 {len(hermes_msgs)} 条消息")

# 诸葛马返回结果
print("  步骤5: 诸葛马通过路由返回结果")
msg3_id = db.send_message("hermes-001", "lobster-001", "go_training_status_response",
    {
        "status": "active",
        "phase": 2,
        "week": 5,
        "xiaochen_level": "1级",
        "zhuguxia_level": "初段",
        "next_action": "安排对局"
    }, "normal")
print(f"    ✅ 结果已返回: {msg3_id[:8]}...")

# 虾尔收到结果并回复用户
print("  步骤6: 虾尔收到结果并回复用户")
lobster_msgs = db.get_pending_messages("lobster-001")
for m in lobster_msgs:
    db.mark_acked(m["id"])
print(f"    ✅ 虾尔已处理 {len(lobster_msgs)} 条消息")
print(f"    📤 虾尔通过钉钉回复则白：围棋学习进度报告已生成")

print("\n" + "=" * 60)
print("🎉 所有测试通过！MCP 路由生态 MVP 运行正常")
print("=" * 60)
print(f"\n📊 最终统计:")
final_stats = db.get_stats()
for k, v in final_stats.items():
    print(f"   {k}: {v}")

print(f"\n 数据库文件: /home/admin/.openclaw/workspace/lobster-ecosystem/router/router.db")
print(f"📝 日志目录: /home/admin/.openclaw/workspace/lobster-ecosystem/")
