#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 ARD 网关演示
Agentic Resource Discovery 协议网关集成
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.lobster_network.ard_protocol import ARDProtocol
from src.lobster_network.ard_gateway import ARDGateway, ARD_MSG_TYPE_DISCOVER, ARD_MSG_TYPE_REGISTER


def main():
    """主函数"""
    print("=" * 60)
    print("🦞 小龙虾网络 ARD 网关演示")
    print("=" * 60)
    print()

    # ========== 1. 初始化 ARD 协议和网关 ==========
    ard = ARDProtocol(data_dir="/tmp/lobster-ard-gateway-demo/ard")
    ard.load_data()

    gateway = ARDGateway(ard, data_dir="/tmp/lobster-ard-gateway-demo/gateway")
    gateway.load_data()

    print("【步骤 1】初始化 ARD 协议和网关")
    print("-" * 40)
    print(f"  ARD 数据目录: {ard.data_dir}")
    print(f"  网关数据目录: {gateway.data_dir}")
    print()

    # ========== 2. 注册 ARD 端点 ==========
    print("【步骤 2】注册 ARD 端点")
    print("-" * 40)

    # 注册谷歌端点
    ok, msg = gateway.register_endpoint(
        name="谷歌 Agent 平台",
        url="https://agent-platform.google.com",
        capabilities=["data-analysis", "machine-learning"],
        protocol="ard",
        metadata={"version": "1.0", "owner": "Google"},
    )
    print(f"  {msg}")

    # 注册微软端点
    ok, msg = gateway.register_endpoint(
        name="微软 Copilot",
        url="https://copilot.microsoft.com",
        capabilities=["writing", "coding", "analysis"],
        protocol="ard",
        metadata={"version": "2.0", "owner": "Microsoft"},
    )
    print(f"  {msg}")

    # 注册 Salesforce 端点
    ok, msg = gateway.register_endpoint(
        name="Salesforce Agent",
        url="https://agent.salesforce.com",
        capabilities=["crm", "sales", "marketing"],
        protocol="ard",
        metadata={"version": "1.5", "owner": "Salesforce"},
    )
    print(f"  {msg}")
    print()

    # ========== 3. 端点心跳 ==========
    print("【步骤 3】端点心跳")
    print("-" * 40)

    for endpoint_id in ["ard-endpoint-0001", "ard-endpoint-0002", "ard-endpoint-0003"]:
        ok, msg = gateway.heartbeat(endpoint_id)
        print(f"  {msg}")
    print()

    # ========== 4. 发送发现请求 ==========
    print("【步骤 4】发送发现请求")
    print("-" * 40)

    # 发送 Agent 发现请求
    ok, msg = gateway.send_message(
        msg_type=ARD_MSG_TYPE_DISCOVER,
        sender_id="xiaochen",
        receiver_id="gateway",
        payload={
            "criteria": {
                "capabilities": ["data-analysis"],
            },
        },
    )
    print(f"  {msg}")

    # 处理消息
    message = gateway.receive_message("ard-msg-000001")
    if message:
        ok, msg = gateway.process_message(message)
        print(f"  处理结果: {msg}")
    print()

    # ========== 5. 发送注册请求 ==========
    print("【步骤 5】发送注册请求")
    print("-" * 40)

    # 注册新 Agent
    ok, msg = gateway.send_message(
        msg_type=ARD_MSG_TYPE_REGISTER,
        sender_id="new-agent",
        receiver_id="gateway",
        payload={
            "type": "agent",
            "data": {
                "name": "新 Agent",
                "agent_type": "specialized",
                "capabilities": ["data-analysis", "report-generation"],
                "endpoint": "https://new-agent.lobster-network.ai",
                "metadata": {"version": "1.0"},
            },
        },
    )
    print(f"  {msg}")

    # 处理消息
    message = gateway.receive_message("ard-msg-000002")
    if message:
        ok, msg = gateway.process_message(message)
        print(f"  处理结果: {msg}")
    print()

    # ========== 6. 协议转换 ==========
    print("【步骤 6】协议转换")
    print("-" * 40)

    # 小龙虾消息转 ARD 消息
    lobster_message = {
        "msg_id": "msg-001",
        "from_node": "xiaochen",
        "to_node": "zhuguxia",
        "type": "discover",
        "payload": {
            "criteria": {"capabilities": ["data-analysis"]},
        },
        "timestamp": "2026-06-25T00:50:00",
    }

    ard_message = gateway.convert_to_ard(lobster_message)
    print(f"  小龙虾消息 → ARD 消息:")
    print(f"    消息 ID: {ard_message.message_id}")
    print(f"    类型: {ard_message.msg_type}")
    print(f"    发送方: {ard_message.sender_id}")
    print(f"    接收方: {ard_message.receiver_id}")
    print()

    # ARD 消息转小龙虾消息
    converted_message = gateway.convert_from_ard(ard_message)
    print(f"  ARD 消息 → 小龙虾消息:")
    print(f"    消息 ID: {converted_message['msg_id']}")
    print(f"    类型: {converted_message['type']}")
    print(f"    发送方: {converted_message['from_node']}")
    print(f"    接收方: {converted_message['to_node']}")
    print()

    # ========== 7. 统计信息 ==========
    print("【步骤 7】ARD 网关统计")
    print("-" * 40)
    stats = gateway.get_gateway_statistics()
    print(f"  总端点数: {stats['total_endpoints']}")
    print(f"  活跃端点: {stats['active_endpoints']}")
    print(f"  总消息数: {stats['total_messages']}")
    print(f"  ARD Agent 数: {stats['ard_statistics']['total_agents']}")
    print(f"  ARD 资源数: {stats['ard_statistics']['total_resources']}")
    print()

    # ========== 8. 保存数据 ==========
    print("【步骤 8】保存数据")
    print("-" * 40)
    gateway.save_data()
    ard.save_data()
    print(f"  数据已保存")
    print()

    print("=" * 60)
    print("🎉 ARD 网关演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()