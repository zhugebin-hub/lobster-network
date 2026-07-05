#!/usr/bin/env python3
"""
🦞 小龙虾网络节点注册脚本
注册用户：诸葛斌（zhugebin）
版本：v0.4.1
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, '/tmp/lobster-network-clone')

from src.lobster_network.integration import LobsterNetworkWithRegistry
from src.lobster_network.registry import TransportConfig, TransportType


def register_zhugebin_node():
    """注册诸葛斌的节点到小龙虾网络"""
    
    print("🦞 正在注册节点到小龙虾网络...")
    
    # 创建带注册中心的网络实例
    storage_dir = os.path.expanduser("~/.lobster-network")
    network = LobsterNetworkWithRegistry(storage_dir=storage_dir)
    
    # 注册节点
    node_id = "zhugebin-001"
    node_name = "诸葛斌"
    
    print(f"\n📝 节点信息:")
    print(f"  节点ID: {node_id}")
    print(f"  节点名称: {node_name}")
    print(f"  存储目录: {storage_dir}")
    
    # 配置传输通道（使用 File 通道作为本地开发环境）
    pending_dir = os.path.join(storage_dir, "pending")
    os.makedirs(pending_dir, exist_ok=True)
    
    transports = [
        TransportConfig(
            transport_type=TransportType.FILE,
            endpoint=pending_dir,
            priority=99,  # File 通道优先级最低，作为降级选项
        ),
    ]
    
    # 注册节点
    try:
        network.register_node(
            node_id=node_id,
            name=node_name,
            node_type="agent",
            perspective="高等教育、测试验证",
            knowledge_base="项目管理、自动化部署",
            value_orientation="工程实践、教育创新",
            capabilities=["deployment", "testing", "verification"],
            transports=transports,
        )
        print(f"\n✅ 节点注册成功！")
        
        # 验证节点状态
        is_alive = network.is_alive(node_id)
        print(f"  节点状态: {'在线' if is_alive else '离线'}")
        
        # 健康检查
        health = network.health_check()
        print(f"\n📊 网络健康状态:")
        print(f"  总节点数: {health['total_nodes']}")
        print(f"  在线节点: {health['online']}")
        print(f"  离线节点: {health['offline']}")
        
        # 列出所有节点
        registry = network.registry
        nodes = registry.get_all_nodes() if hasattr(registry, 'get_all_nodes') else []
        print(f"\n🌐 网络中的节点:")
        if nodes:
            for node in nodes:
                status = "🟢 在线" if node.status == "online" else "🔴 离线"
                print(f"  - {node.name} ({node.node_id}) [{status}]")
                if hasattr(node, 'capabilities') and node.capabilities:
                    print(f"    能力: {', '.join(node.capabilities)}")
        else:
            print(f"  当前只有你的节点在线")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 节点注册失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = register_zhugebin_node()
    sys.exit(0 if success else 1)
