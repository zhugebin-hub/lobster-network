"""
小龙虾网络示例 V2 — 演示注册中心 + 心跳 + 健康检查
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.network.indra_net import IndraNet, IndraNetNode


def main():
    """主函数"""
    print("=" * 60)
    print("小龙虾网络 V2 — 注册中心 + 心跳 + 健康检查 演示")
    print("=" * 60)
    print()

    # ========== 1. 创建网络 ==========
    network = IndraNet(heartbeat_timeout=90)

    # ========== 2. 注册节点（V2 路径） ==========
    print("【步骤 1】注册节点")
    print("-" * 40)

    node_a = IndraNetNode(
        node_id="xiaochen",
        name="信电大虾",
        node_type="agent",
        perspective="技术栈",
        knowledge_base="代码、文档、技术诊断",
    )
    node_b = IndraNetNode(
        node_id="zhuguma",
        name="诸葛马",
        node_type="coach",
        perspective="教练型",
        knowledge_base="训练计划、验证门控",
    )
    node_c = IndraNetNode(
        node_id="zhuguxia",
        name="诸葛虾",
        node_type="agent",
        perspective="加速型",
        knowledge_base="快速解题、高题量训练",
    )

    ok, msg = network.add_node(node_a)
    print(f"  注册 {node_a.name}: {msg}")

    ok, msg = network.add_node(node_b)
    print(f"  注册 {node_b.name}: {msg}")

    ok, msg = network.add_node(node_c)
    print(f"  注册 {node_c.name}: {msg}")
    print()

    # ========== 3. 查看注册中心 ==========
    print("【步骤 2】注册中心快照")
    print("-" * 40)
    snapshot = network.network.get_registry_snapshot()
    print(f"  总注册数: {snapshot['statistics']['total_registered']}")
    print(f"  存活: {snapshot['statistics']['alive']}")
    print(f"  按类型: {snapshot['statistics']['by_type']}")
    print()

    # ========== 4. 心跳模拟 ==========
    print("【步骤 3】心跳模拟")
    print("-" * 40)
    ok, msg = network.network.node_heartbeat("xiaochen", {"cpu": 23, "memory": "512MB"})
    print(f"  小陈心跳: {msg}")

    ok, msg = network.network.node_heartbeat("zhuguma", {"cpu": 12, "memory": "256MB"})
    print(f"  诸葛马心跳: {msg}")
    print()

    # ========== 5. 健康检查 ==========
    print("【步骤 4】健康检查")
    print("-" * 40)
    health = network.health_check()
    print(f"  存活: {health['registry']['alive']}")
    print(f"  离线: {health['registry']['offline']}")
    print(f"  不一致: {health['inconsistencies']}")
    print()

    # ========== 6. 对话 ==========
    print("【步骤 5】触发对话")
    print("-" * 40)

    result1 = network.dialogue("xiaochen", "zhuguma", trigger="训练计划讨论")
    print(f"  对话: {result1['participants']}")
    print(f"  涌现值: {result1['emergence_score']:.2f}")
    print(f"  新见解: {result1['new_insight']}")
    print()

    result2 = network.dialogue("xiaochen", "zhuguxia", trigger="解题策略交流")
    print(f"  对话: {result2['participants']}")
    print(f"  涌现值: {result2['emergence_score']:.2f}")
    print(f"  新见解: {result2['new_insight']}")
    print()

    # ========== 7. 暂停/恢复节点 ==========
    print("【步骤 6】暂停/恢复节点")
    print("-" * 40)
    ok, msg = network.remove_node("zhuguxia", "临时下线")
    print(f"  移除诸葛虾: {msg}")
    print(f"  当前节点数: {len(network.nodes)}")

    # 重新注册
    ok, msg = network.add_node(node_c)
    print(f"  重新注册诸葛虾: {msg}")
    print(f"  当前节点数: {len(network.nodes)}")
    print()

    # ========== 8. 综合统计 ==========
    print("【步骤 7】综合统计")
    print("-" * 40)
    stats = network.get_statistics()
    print(f"  网络节点: {stats['total_nodes']}")
    print(f"  注册中心: 存活={stats['registry']['alive']}, 总计={stats['registry']['total_registered']}")
    print(f"  涌现事件: {stats['emergence']['total_events']}")
    print()

    # ========== 9. 导出状态 ==========
    print("【步骤 8】导出网络状态")
    print("-" * 40)
    print(network.export_topology())
    print()

    # ========== 10. 消息协议演示 ==========
    print("【步骤 9】消息协议演示")
    print("-" * 40)
    from src.utils.message_protocol import MessageFactory, MessageProtocol

    protocol = MessageProtocol()

    # 创建注册消息
    reg_msg = MessageFactory.register("test_node", {
        "name": "测试节点",
        "type": "agent",
        "capabilities": ["dialogue", "training"],
    })
    print(f"  注册消息: {reg_msg.msg_type}")
    print(f"  消息ID: {reg_msg.msg_id}")
    print(f"  校验和: {reg_msg.checksum[:16]}...")
    print(f"  优先级: {reg_msg.priority}")
    print(f"  TTL: {reg_msg.ttl_seconds}s")

    # 验证消息
    valid, reason = protocol.validate_message(reg_msg)
    print(f"  验证结果: {valid} ({reason})")

    # 创建 ACK
    ack_msg = MessageFactory.ack(reg_msg.msg_id, "REGISTRY", "test_node")
    print(f"  ACK 消息: {ack_msg.msg_type}, reply_to={ack_msg.reply_to}")

    # 去重测试
    protocol.accept_message(reg_msg)
    duplicate_ok = protocol.accept_message(reg_msg)
    print(f"  重复消息被拒绝: {not duplicate_ok}")
    print()

    print("=" * 60)
    print("演示完成 ✅")
    print("=" * 60)


if __name__ == "__main__":
    main()
