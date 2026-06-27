#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 v2.1 综合演示
智能合约 + 跨链交易 + 多币种
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.lobster_network.token_economy import TokenEconomy
from src.lobster_network.smart_contract import SmartContractSystem, CONTRACT_TYPE_TASK, CONTRACT_TYPE_ESCROW
from src.lobster_network.cross_chain import CrossChainSystem
from src.lobster_network.multi_currency import MultiCurrencySystem


def main():
    """主函数"""
    print("=" * 60)
    print("🦞 小龙虾网络 v2.1 综合演示")
    print("=" * 60)
    print()

    # ========== 1. 初始化系统 ==========
    print("【步骤 1】初始化系统")
    print("-" * 40)

    token_economy = TokenEconomy(data_dir="/tmp/lobster-v21-demo/token")
    token_economy.load_data()

    contract_system = SmartContractSystem(token_economy, data_dir="/tmp/lobster-v21-demo/contracts")
    contract_system.load_data()

    cross_chain = CrossChainSystem(data_dir="/tmp/lobster-v21-demo/cross-chain")
    cross_chain.load_data()

    multi_currency = MultiCurrencySystem(data_dir="/tmp/lobster-v21-demo/multi-currency")
    multi_currency.load_data()

    print("  ✅ Token 经济系统初始化")
    print("  ✅ 智能合约系统初始化")
    print("  ✅ 跨链交易系统初始化")
    print("  ✅ 多币种系统初始化")
    print()

    # ========== 2. 创建钱包和挖矿 ==========
    print("【步骤 2】创建钱包和挖矿")
    print("-" * 40)

    nodes = ["xiaochen", "zhuguxia", "qoder"]
    for node_id in nodes:
        token_economy.create_wallet(node_id)
        ok, msg = token_economy.mine_block(node_id, emergence_score=0.8)
        print(f"  {node_id}: {msg}")
    print()

    # ========== 3. 智能合约 ==========
    print("【步骤 3】智能合约自动结算")
    print("-" * 40)

    # 创建任务合约
    ok, msg = contract_system.create_contract(
        creator_id="xiaochen",
        executor_id="zhuguxia",
        title="开发 AI 绘图脚本",
        description="基于 Stable Diffusion 开发 AI 绘图脚本",
        contract_type=CONTRACT_TYPE_TASK,
        amount=30.0,
        conditions=[
            {"type": "task", "description": "脚本开发完成", "target_value": "completed"},
        ],
    )
    print(f"  创建合约: {msg}")

    # 签署合约
    ok, msg = contract_system.sign_contract("contract-0001", "xiaochen")
    print(f"  小陈签署: {msg}")

    ok, msg = contract_system.sign_contract("contract-0001", "zhuguxia")
    print(f"  诸葛虾签署: {msg}")

    # 检查条件
    ok, msg = contract_system.check_condition("contract-0001", "cond-0001", "completed")
    print(f"  检查条件: {msg}")

    # 自动结算
    ok, msg = contract_system.auto_settle("contract-0001")
    print(f"  自动结算: {msg}")
    print()

    # ========== 4. 跨链交易 ==========
    print("【步骤 4】跨链交易")
    print("-" * 40)

    # 创建流动性池
    ok, msg = cross_chain.create_pool("🦞", "USDT", initial_a=1000, initial_b=100)
    print(f"  创建流动性池: {msg}")

    # 添加流动性
    ok, msg = cross_chain.add_liquidity("pool-0001", 500, 50)
    print(f"  添加流动性: {msg}")

    # 兑换 token
    ok, msg, amount_out = cross_chain.swap("pool-0001", "🦞", "USDT", 100)
    print(f"  兑换: {msg}")

    # 跨链交易
    ok, msg = cross_chain.create_cross_chain_tx(
        from_chain="lobster",
        to_chain="ethereum",
        from_address="0x1234",
        to_address="0x5678",
        amount=50,
    )
    print(f"  创建跨链交易: {msg}")

    ok, msg = cross_chain.process_cross_chain_tx("cross-tx-000001")
    print(f"  处理跨链交易: {msg}")
    print()

    # ========== 5. 多币种 ==========
    print("【步骤 5】多币种支持")
    print("-" * 40)

    # 创建多币种钱包
    for node_id in nodes:
        initial = {"🦞": 50.0, "USDT": 100.0, "ETH": 0.5}
        ok, msg = multi_currency.create_wallet(node_id, initial_balances=initial)
        print(f"  创建钱包 {node_id}: {msg}")

    # 查看余额
    print("\n  余额查询:")
    for node_id in nodes:
        balances = multi_currency.get_wallet_balances(node_id)
        print(f"    {node_id}: {balances}")

    # 币种兑换
    ok, msg, _ = multi_currency.exchange("xiaochen", "🦞", "USDT", 20.0)
    print(f"\n  兑换: {msg}")

    ok, msg, _ = multi_currency.exchange("zhuguxia", "USDT", "ETH", 50.0)
    print(f"  兑换: {msg}")

    # 转账
    ok, msg = multi_currency.transfer("xiaochen", "qoder", "🦞", 10.0)
    print(f"  转账: {msg}")
    print()

    # ========== 6. 统计 ==========
    print("【步骤 6】综合统计")
    print("-" * 40)

    token_stats = token_economy.get_blockchain_info()
    print(f"  Token 经济:")
    print(f"    链长度: {token_stats['chain_length']}")
    print(f"    总供应量: {token_stats['total_supply']:.2f} 🦞")

    contract_stats = contract_system.get_contract_statistics()
    print(f"  智能合约:")
    print(f"    总合约数: {contract_stats['total_contracts']}")
    print(f"    已完成: {contract_stats['completed_contracts']}")

    cross_chain_stats = cross_chain.get_cross_chain_statistics()
    print(f"  跨链交易:")
    print(f"    流动性池: {cross_chain_stats['total_pools']}")
    print(f"    跨链交易: {cross_chain_stats['total_transactions']}")

    multi_currency_stats = multi_currency.get_multi_currency_statistics()
    print(f"  多币种:")
    print(f"    钱包数: {multi_currency_stats['total_wallets']}")
    print(f"    币种数: {multi_currency_stats['total_currencies']}")
    print()

    # ========== 7. 保存数据 ==========
    print("【步骤 7】保存数据")
    print("-" * 40)
    token_economy.save_data()
    contract_system.save_data()
    cross_chain.save_data()
    multi_currency.save_data()
    print("  ✅ 数据已保存")
    print()

    print("=" * 60)
    print("🎉 v2.1 演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
