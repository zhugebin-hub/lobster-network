"""
小龙虾网络示例：因陀罗网拓扑
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.lobster_network.network.indra_net import IndraNet, IndraNetNode


def main():
    """主函数"""
    # 创建因陀罗网
    network = IndraNet()
    
    # 添加节点
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
    
    network.add_node(node_a)
    network.add_node(node_b)
    network.add_node(node_c)
    
    print("=== 因陀罗网示例 ===\n")
    print(f"节点数量: {len(network.nodes)}")
    print(f"网络拓扑:\n{network.export_topology()}\n")
    
    # 触发对话
    print("=== 触发对话 ===\n")
    
    result1 = network.dialogue("xiaochen", "zhuguma", trigger="训练计划讨论")
    print(f"对话1: {result1['participants']}")
    print(f"涌现值: {result1['emergence_score']:.2f}")
    print(f"新见解: {result1['new_insight']}")
    print(f"解锁宝藏: {result1['treasure_unlocked']}\n")
    
    result2 = network.dialogue("xiaochen", "zhuguxia", trigger="解题策略交流")
    print(f"对话2: {result2['participants']}")
    print(f"涌现值: {result2['emergence_score']:.2f}")
    print(f"新见解: {result2['new_insight']}")
    print(f"解锁宝藏: {result2['treasure_unlocked']}\n")
    
    result3 = network.dialogue("zhuguma", "zhuguxia", trigger="训练效果评估")
    print(f"对话3: {result3['participants']}")
    print(f"涌现值: {result3['emergence_score']:.2f}")
    print(f"新见解: {result3['new_insight']}")
    print(f"解锁宝藏: {result3['treasure_unlocked']}\n")
    
    # 统计信息
    print("=== 网络统计 ===\n")
    stats = network.get_statistics()
    print(f"总节点数: {stats['total_nodes']}")
    print(f"总连接数: {stats['total_connections']}")
    print(f"最大可能连接数: {stats['max_possible_connections']}")
    print(f"连通率: {stats['connectivity_ratio']:.2f}")
    print(f"涌现统计: {stats['emergence_statistics']}\n")
    
    # 导出网络状态
    print("=== 网络状态 ===\n")
    print(network.export_topology())


if __name__ == "__main__":
    main()
