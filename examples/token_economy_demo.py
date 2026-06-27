#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 Token 经济系统演示
参考比特币分布式货币机制
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.lobster_network.token_economy import (
    TokenEconomy,
    TX_TYPE_TRANSFER,
    TX_TYPE_TASK_REWARD,
)


def main():
    """主函数"""
    print("=" * 60)
    print("🦞 小龙虾网络 Token 经济系统演示")
    print("=" * 60)
    print()

    # ========== 1. 初始化 Token 经济系统 ==========
    token_economy = TokenEconomy(data_dir="/tmp/lobster-token-demo")
    token_economy.load_data()

    print("【步骤 1】初始化 Token 经济系统")
    print("-" * 40)
    print(f"  数据目录: {token_economy.data_dir}")
    print(f"  Token 总量: 21,000,000 {token_economy.TOKEN_UNIT if hasattr(token_economy, 'TOKEN_UNIT') else '🦞'}")
    print(f"  初始区块奖励: 50 {token_economy.TOKEN_UNIT if hasattr(token_economy, 'TOKEN_UNIT') else '🦞'}")
    print(f"  减半周期: 210,000 区块")
    print()

    # ========== 2. 创建钱包 ==========
    print("【步骤 2】创建钱包")
    print("-" * 40)

    nodes = ["xiaochen", "zhuguma", "zhuguxia", "qoder"]
    for node_id in nodes:
        ok, msg = token_economy.create_wallet(node_id)
        print(f"  创建钱包 {node_id}: {msg}")
    print()

    # ========== 3. 挖矿 ==========
    print("【步骤 3】挖矿（涌现共识）")
    print("-" * 40)

    # 小陈挖矿
    ok, msg = token_economy.mine_block("xiaochen", emergence_score=0.9)
    print(f"  小陈挖矿: {msg}")

    # 诸葛虾挖矿
    ok, msg = token_economy.mine_block("zhuguxia", emergence_score=0.7)
    print(f"  诸葛虾挖矿: {msg}")

    # Qoder 挖矿
    ok, msg = token_economy.mine_block("qoder", emergence_score=0.8)
    print(f"  Qoder 挖矿: {msg}")
    print()

    # ========== 4. 转账 ==========
    print("【步骤 4】转账")
    print("-" * 40)

    ok, msg = token_economy.transfer("xiaochen", "zhuguxia", 10.0)
    print(f"  小陈 → 诸葛虾: {msg}")

    ok, msg = token_economy.transfer("qoder", "xiaochen", 5.0)
    print(f"  Qoder → 小陈: {msg}")
    print()

    # ========== 5. 任务奖励 ==========
    print("【步骤 5】任务奖励")
    print("-" * 40)

    ok, msg = token_economy.reward_task("task-0001", "xiaochen", 20.0)
    print(f"  小陈完成任务: {msg}")

    ok, msg = token_economy.reward_task("task-0002", "zhuguxia", 15.0)
    print(f"  诸葛虾完成任务: {msg}")
    print()

    # ========== 6. 质押 ==========
    print("【步骤 6】质押")
    print("-" * 40)

    ok, msg = token_economy.stake("xiaochen", 30.0)
    print(f"  小陈质押: {msg}")

    ok, msg = token_economy.stake("qoder", 20.0)
    print(f"  Qoder 质押: {msg}")
    print()

    # ========== 7. 销毁 ==========
    print("【步骤 7】销毁")
    print("-" * 40)

    ok, msg = token_economy.burn("zhuguxia", 5.0)
    print(f"  诸葛虾销毁: {msg}")
    print()

    # ========== 8. 查看余额 ==========
    print("【步骤 8】余额查询")
    print("-" * 40)

    for node_id in nodes:
        wallet = token_economy.get_wallet(node_id)
        if wallet:
            print(f"  {node_id}: 余额={wallet.balance:.2f}, 质押={wallet.staked:.2f}")
    print()

    # ========== 9. 区块链信息 ==========
    print("【步骤 9】区块链信息")
    print("-" * 40)
    info = token_economy.get_blockchain_info()
    print(f"  链长度: {info['chain_length']}")
    print(f"  当前难度: {info['current_difficulty']}")
    print(f"  内存池大小: {info['mempool_size']}")
    print(f"  钱包数量: {info['total_wallets']}")
    print(f"  总供应量: {info['total_supply']:.2f}")
    print(f"  流通量: {info['circulating_supply']:.2f}")
    print()

    # ========== 10. 排行榜 ==========
    print("【步骤 10】排行榜")
    print("-" * 40)
    leaderboard = token_economy.get_leaderboard()
    for i, entry in enumerate(leaderboard, 1):
        print(f"  {i}. {entry['node_id']} - {entry['total']:.2f} 🦞 (余额: {entry['balance']:.2f}, 质押: {entry['staked']:.2f})")
    print()

    # ========== 11. 交易历史 ==========
    print("【步骤 11】交易历史（小陈）")
    print("-" * 40)
    txs = token_economy.get_transactions("xiaochen")
    for tx in txs[:5]:
        print(f"  {tx['tx_id']}: {tx['from']} → {tx['to']} | {tx['amount']:.2f} 🦞 | {tx['type']}")
    print()

    # ========== 12. 保存数据 ==========
    print("【步骤 12】保存数据")
    print("-" * 40)
    token_economy.save_data()
    print(f"  数据已保存到: {token_economy.data_dir}")
    print()

    print("=" * 60)
    print("🎉 演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
