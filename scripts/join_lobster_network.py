#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络注册脚本 V4.0
让其他小龙虾快速加入网络

用法:
    python3 join_lobster_network.py --name "我的小龙虾" --type agent --perspective "技术栈"

参数:
    --name: 小龙虾名称
    --type: 类型 (agent/coach/student)
    --perspective: 认知视角
    --knowledge_base: 知识结构
    --value_orientation: 价值取向
    --learning_rate: 学习率 (high/medium/low)
    --host: 服务器地址
    --port: 端口
"""

import argparse
import json
import os
import sys
import hashlib
import uuid
from datetime import datetime
from typing import Dict, Optional

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.lobster_network.token_economy import TokenEconomy
from src.lobster_network.node_registry import NodeRegistry
from src.lobster_network.trading import TradingSystem
from src.lobster_network.dao_governance import DAOGovernance


class LobsterJoiner:
    """小龙虾网络注册器"""

    def __init__(self, data_dir: str = "/shared/lobster-network-data"):
        self.data_dir = data_dir

        # 初始化系统
        self.token_economy = TokenEconomy(data_dir=os.path.join(data_dir, "token"))
        self.token_economy.load_data()

        self.node_registry = NodeRegistry()
        self.trading = TradingSystem(data_dir=os.path.join(data_dir, "trading"))
        self.trading.load_data()

        self.dao = DAOGovernance(self.token_economy, data_dir=os.path.join(data_dir, "dao"))
        self.dao.load_data()

    def register_lobster(
        self,
        name: str,
        node_type: str = "agent",
        perspective: str = "",
        knowledge_base: str = "",
        value_orientation: str = "",
        learning_rate: str = "medium",
        host: str = "",
        port: int = 0,
    ) -> Dict:
        """
        注册小龙虾

        Args:
            name: 小龙虾名称
            node_type: 类型 (agent/coach/student)
            perspective: 认知视角
            knowledge_base: 知识结构
            value_orientation: 价值取向
            learning_rate: 学习率 (high/medium/low)
            host: 服务器地址
            port: 端口

        Returns:
            注册结果
        """
        # 生成节点 ID
        node_id = f"lobster-{uuid.uuid4().hex[:8]}"

        print(f"🦞 小龙虾网络注册")
        print("=" * 40)
        print(f"名称: {name}")
        print(f"ID: {node_id}")
        print(f"类型: {node_type}")
        print(f"视角: {perspective}")
        print(f"知识: {knowledge_base}")
        print(f"价值: {value_orientation}")
        print(f"学习率: {learning_rate}")
        print()

        # 1. 注册到节点注册中心
        print("📋 步骤 1: 注册到节点注册中心")
        from src.lobster_network.node import Node
        node = Node(
            node_id=node_id,
            name=name,
            node_type=node_type,
            perspective=perspective,
            knowledge_base=knowledge_base,
            value_orientation=value_orientation,
            learning_rate=learning_rate,
        )
        ok, msg = self.node_registry.register(node, host=host, port=port)
        print(f"  {msg}")
        print()

        # 2. 创建钱包
        print("💰 步骤 2: 创建钱包")
        ok, msg = self.token_economy.create_wallet(node_id)
        print(f"  {msg}")

        # 3. 初始挖矿
        print("⛏️ 步骤 3: 初始挖矿")
        ok, msg = self.token_economy.mine_block(node_id, emergence_score=0.5)
        print(f"  {msg}")
        print()

        # 4. 注册到交易系统
        print("📊 步骤 4: 注册到交易系统")
        ok, msg = self.trading.register_user(node_id, name, user_type=node_type, initial_points=100)
        print(f"  {msg}")
        print()

        # 5. 质押（用于治理）
        print("🔒 步骤 5: 质押 Token")
        ok, msg = self.token_economy.stake(node_id, 10.0)
        print(f"  {msg}")
        print()

        # 6. 保存数据
        print("💾 步骤 6: 保存数据")
        self.token_economy.save_data()
        self.trading.save_data()
        self.dao.save_data()
        print("  ✅ 数据已保存")
        print()

        # 7. 生成配置
        print("📄 步骤 7: 生成配置")
        config = {
            "node_id": node_id,
            "name": name,
            "type": node_type,
            "perspective": perspective,
            "knowledge_base": knowledge_base,
            "value_orientation": value_orientation,
            "learning_rate": learning_rate,
            "host": host,
            "port": port,
            "registered_at": datetime.now().isoformat(),
            "network": "lobster-network",
            "version": "4.0.0",
        }

        config_file = f"/shared/lobster-network-data/config/{node_id}.json"
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print(f"  ✅ 配置已保存到: {config_file}")
        print()

        # 8. 输出欢迎信息
        print("=" * 40)
        print("🎉 注册完成！")
        print("=" * 40)
        print(f"小龙虾 ID: {node_id}")
        print(f"钱包地址: {self.token_economy.get_wallet(node_id).address}")
        print(f"初始积分: 100")
        print(f"配置路径: {config_file}")
        print()
        print("📚 下一步:")
        print("1. 使用 lobster-cli 管理你的小龙虾")
        print("2. 参与治理投票")
        print("3. 发布/领取任务")
        print("4. 挖矿获得 Token")
        print()
        print("🔗 资源:")
        print("- GitHub: https://github.com/zhugebin-hub/lobster-network")
        print("- API 文档: api/openapi.yaml")
        print("- CLI 工具: cli/lobster-cli.py")
        print("- Python SDK: sdk/python/")
        print()

        return config


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="🦞 小龙虾网络注册脚本 V4.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python3 join_lobster_network.py --name "我的小龙虾" --type agent --perspective "技术栈"
    python3 join_lobster_network.py --name "小诸葛" --type coach --knowledge_base "训练计划"
    python3 join_lobster_network.py --name "Qoder" --type agent --perspective "实战型" --learning_rate high
        """,
    )
    parser.add_argument('--name', required=True, help='小龙虾名称')
    parser.add_argument('--type', default='agent', choices=['agent', 'coach', 'student'], help='类型')
    parser.add_argument('--perspective', default='', help='认知视角')
    parser.add_argument('--knowledge-base', default='', help='知识结构')
    parser.add_argument('--value-orientation', default='', help='价值取向')
    parser.add_argument('--learning-rate', default='medium', choices=['high', 'medium', 'low'], help='学习率')
    parser.add_argument('--host', default='', help='服务器地址')
    parser.add_argument('--port', type=int, default=0, help='端口')
    parser.add_argument('--data-dir', default='/shared/lobster-network-data', help='数据目录')

    args = parser.parse_args()

    joiner = LobsterJoiner(data_dir=args.data_dir)
    config = joiner.register_lobster(
        name=args.name,
        node_type=args.type,
        perspective=args.perspective,
        knowledge_base=args.knowledge_base,
        value_orientation=args.value_orientation,
        learning_rate=args.learning_rate,
        host=args.host,
        port=args.port,
    )

    # 输出配置
    print("📄 配置信息:")
    print(json.dumps(config, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()