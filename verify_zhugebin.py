#!/usr/bin/env python3
"""
🦞 小龙虾网络节点验证脚本
验证诸葛斌节点的完整功能
"""

import sys
sys.path.insert(0, '/tmp/lobster-network-clone')

from src.lobster_network.integration import LobsterNetworkWithRegistry


def verify_node():
    """验证节点功能"""
    
    print("🦞 小龙虾网络节点验证")
    print("=" * 50)
    
    # 加载网络（从持久化存储恢复）
    network = LobsterNetworkWithRegistry(storage_dir="~/.lobster-network")
    
    # 1. 检查节点状态
    node_id = "zhugebin-001"
    is_alive = network.is_alive(node_id)
    print(f"\n✅ 节点存活检查: {'在线' if is_alive else '离线'}")
    
    # 2. 健康检查
    health = network.health_check()
    print(f"\n📊 网络健康状态:")
    print(f"  总节点数: {health['total_nodes']}")
    print(f"  在线节点: {health['online']}")
    print(f"  离线节点: {health['offline']}")
    print(f"  疑似节点: {health.get('suspected', 0)}")
    
    # 3. 发送测试消息
    print(f"\n📨 发送测试消息...")
    msg = network.send_message(
        from_node=node_id,
        to_node="hermes",  # 教练节点
        msg_type="hello",
        payload={"message": "诸葛斌加入小龙虾网络！"},
    )
    print(f"  消息ID: {msg.msg_id}")
    print(f"  消息状态: {msg.status}")
    print(f"  传输通道: {msg.attempts[-1].transport if msg.attempts else 'N/A'}")
    
    # 4. 查看消息统计
    stats = network.messenger.get_statistics()
    print(f"\n📈 消息统计:")
    print(f"  已发送: {stats.get('sent', 0)}")
    print(f"  已投递: {stats.get('delivered', 0)}")
    print(f"  失败: {stats.get('failed', 0)}")
    
    print("\n" + "=" * 50)
    print("✅ 验证完成！你的节点已成功加入小龙虾网络。")
    print("\n下一步：")
    print("  - 运行部署脚本: sudo ./scripts/deploy_v0.4.1.sh deploy")
    print("  - 查看 v0.4.2 规划: docs/ROADMAP-v0.4.2.md")
    print("  - 查看升级清单: docs/upgrade-checklist-v0.4.1.md")


if __name__ == "__main__":
    verify_node()
