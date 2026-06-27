#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 v2.2 + v3.0 综合演示
DAO 治理 + DEX + 流动性挖矿 + Layer 2 + ZK 证明 + 跨链桥
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.lobster_network.token_economy import TokenEconomy
from src.lobster_network.dao_governance import DAOGovernance, PROPOSAL_TYPE_TREASURY
from src.lobster_network.dex import DEX
from src.lobster_network.liquidity_mining import LiquidityMining
from src.lobster_network.layer2 import Layer2System
from src.lobster_network.zk_proof import ZKProofSystem
from src.lobster_network.cross_chain_bridge import CrossChainBridge


def main():
    """主函数"""
    print("=" * 60)
    print("🦞 小龙虾网络 v2.2 + v3.0 综合演示")
    print("=" * 60)
    print()

    # ========== 1. 初始化系统 ==========
    print("【步骤 1】初始化系统")
    print("-" * 40)

    token_economy = TokenEconomy(data_dir="/tmp/lobster-v22-v30-demo/token")
    token_economy.load_data()

    dao = DAOGovernance(token_economy, data_dir="/tmp/lobster-v22-v30-demo/dao")
    dao.load_data()

    dex = DEX(token_economy, data_dir="/tmp/lobster-v22-v30-demo/dex")
    dex.load_data()

    mining = LiquidityMining(token_economy, data_dir="/tmp/lobster-v22-v30-demo/mining")
    mining.load_data()

    layer2 = Layer2System(token_economy, data_dir="/tmp/lobster-v22-v30-demo/layer2")
    layer2.load_data()

    zk_proof = ZKProofSystem(data_dir="/tmp/lobster-v22-v30-demo/zk-proof")
    zk_proof.load_data()

    bridge = CrossChainBridge(data_dir="/tmp/lobster-v22-v30-demo/bridge")
    bridge.load_data()

    print("  ✅ Token 经济系统初始化")
    print("  ✅ DAO 治理系统初始化")
    print("  ✅ DEX 系统初始化")
    print("  ✅ 流动性挖矿系统初始化")
    print("  ✅ Layer 2 系统初始化")
    print("  ✅ 零知识证明系统初始化")
    print("  ✅ 跨链桥系统初始化")
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

    # ========== 3. DAO 治理 ==========
    print("【步骤 3】DAO 治理")
    print("-" * 40)

    # 质押
    for node_id in nodes:
        ok, msg = token_economy.stake(node_id, 20.0)
        print(f"  {node_id} 质押: {msg}")

    # 创建提案
    ok, msg = dao.create_proposal(
        creator_id="xiaochen",
        title="降低交易手续费",
        description="将交易手续费从 0.3% 降低到 0.2%",
        proposal_type=PROPOSAL_TYPE_TREASURY,
    )
    print(f"  创建提案: {msg}")

    # 提交提案
    ok, msg = dao.submit_proposal("proposal-0001")
    print(f"  提交提案: {msg}")

    # 投票
    ok, msg = dao.vote("proposal-0001", "xiaochen", "for", reason="支持降低手续费")
    print(f"  小陈投票: {msg}")

    ok, msg = dao.vote("proposal-0001", "zhuguxia", "for", reason="同意")
    print(f"  诸葛虾投票: {msg}")

    ok, msg = dao.vote("proposal-0001", "qoder", "against", reason="手续费已很低")
    print(f"  Qoder 投票: {msg}")

    # 检查提案结果
    ok, msg = dao.check_proposal_result("proposal-0001")
    print(f"  提案结果: {msg}")
    print()

    # ========== 4. DEX ==========
    print("【步骤 4】DEX 交易")
    print("-" * 40)

    # 创建交易对
    ok, msg = dex.create_pair("🦞", "USDT", initial_a=1000, initial_b=100)
    print(f"  创建交易对: {msg}")

    # 添加流动性
    ok, msg = dex.add_liquidity("pair-0001", "xiaochen", 500, 50)
    print(f"  小陈添加流动性: {msg}")

    # 兑换
    ok, msg, amount_out = dex.swap("pair-0001", "zhuguxia", "🦞", "USDT", 100)
    print(f"  诸葛虾兑换: {msg}")
    print()

    # ========== 5. 流动性挖矿 ==========
    print("【步骤 5】流动性挖矿")
    print("-" * 40)

    # 创建挖矿池
    ok, msg = mining.create_pool("🦞/USDT 挖矿", "pair-0001", reward_rate=50.0)
    print(f"  创建挖矿池: {msg}")

    # 激活挖矿池
    ok, msg = mining.activate_pool("pool-0001")
    print(f"  激活挖矿池: {msg}")

    # 质押
    ok, msg = mining.stake("pool-0001", "xiaochen", 500)
    print(f"  小陈质押: {msg}")

    # 领取奖励
    ok, msg = mining.claim_rewards("pool-0001", "xiaochen")
    print(f"  小陈领取奖励: {msg}")
    print()

    # ========== 6. Layer 2 ==========
    print("【步骤 6】Layer 2 扩容")
    print("-" * 40)

    # 创建 L2 交易
    for i in range(5):
        ok, msg = layer2.create_l2_transaction("xiaochen", "zhuguxia", 10.0)
        print(f"  L2 交易 {i+1}: {msg}")

    # 提交批次
    ok, msg = layer2.submit_batch()
    print(f"  提交批次: {msg}")

    # 最终确定
    ok, msg = layer2.finalize_batch("batch-0001")
    print(f"  最终确定: {msg}")
    print()

    # ========== 7. 零知识证明 ==========
    print("【步骤 7】零知识证明")
    print("-" * 40)

    # 创建证明
    ok, msg = zk_proof.create_proof(
        proof_type="transfer",
        prover_id="xiaochen",
        verifier_id="zhuguxia",
        proof_data="zk-snark-proof-data-1234567890",
        public_inputs={"amount": 50.0},
    )
    print(f"  创建证明: {msg}")

    # 验证证明
    ok, msg = zk_proof.verify_proof("zk-proof-0001")
    print(f"  验证证明: {msg}")

    # 创建隐私交易
    ok, msg = zk_proof.create_privacy_transaction(
        from_commitment="commitment-123",
        to_commitment="commitment-456",
        amount=50.0,
        proof_id="zk-proof-0001",
    )
    print(f"  隐私交易: {msg}")

    # 创建 Merkle 树
    leaves = ["leaf1", "leaf2", "leaf3", "leaf4"]
    ok, msg = zk_proof.create_merkle_tree(leaves)
    print(f"  创建 Merkle 树: {msg}")
    print()

    # ========== 8. 跨链桥 ==========
    print("【步骤 8】跨链桥")
    print("-" * 40)

    # 注册资产
    ok, msg = bridge.register_asset("🦞", "Lobster", ["lobster", "ethereum", "solana"])
    print(f"  注册资产: {msg}")

    # 注册中继器
    ok, msg = bridge.register_relayer("Relayer-001", ["lobster", "ethereum", "solana"], stake=1000)
    print(f"  注册中继器: {msg}")

    # 创建跨链交易
    ok, msg = bridge.create_bridge_transaction(
        from_chain="lobster",
        to_chain="ethereum",
        from_address="0x1234",
        to_address="0x5678",
        asset="🦞",
        amount=100,
    )
    print(f"  创建跨链交易: {msg}")

    # 锁定资产
    ok, msg = bridge.lock_assets("bridge-tx-000001", "lock-tx-hash-123456")
    print(f"  锁定资产: {msg}")

    # 铸造资产
    ok, msg = bridge.mint_assets("bridge-tx-000001", "mint-tx-hash-789012", "relayer-0001")
    print(f"  铸造资产: {msg}")

    # 完成交易
    ok, msg = bridge.complete_transaction("bridge-tx-000001")
    print(f"  完成交易: {msg}")
    print()

    # ========== 9. 综合统计 ==========
    print("【步骤 9】综合统计")
    print("-" * 40)

    token_stats = token_economy.get_blockchain_info()
    print(f"  Token 经济:")
    print(f"    链长度: {token_stats['chain_length']}")
    print(f"    总供应量: {token_stats['total_supply']:.2f} 🦞")

    dao_stats = dao.get_governance_statistics()
    print(f"  DAO 治理:")
    print(f"    总提案数: {dao_stats['total_proposals']}")
    print(f"    已通过: {dao_stats['passed_proposals']}")

    dex_stats = dex.get_dex_statistics()
    print(f"  DEX:")
    print(f"    交易对: {dex_stats['total_pairs']}")
    print(f"    TVL: {dex_stats['total_tvl']:.2f}")

    mining_stats = mining.get_mining_statistics()
    print(f"  流动性挖矿:")
    print(f"    挖矿池: {mining_stats['total_pools']}")
    print(f"    总质押: {mining_stats['total_staked']:.2f}")

    layer2_stats = layer2.get_layer2_statistics()
    print(f"  Layer 2:")
    print(f"    批次: {layer2_stats['total_batches']}")
    print(f"    L2 交易: {layer2_stats['total_l2_transactions']}")

    zk_stats = zk_proof.get_zk_statistics()
    print(f"  零知识证明:")
    print(f"    证明数: {zk_stats['total_proofs']}")
    print(f"    有效证明: {zk_stats['valid_proofs']}")

    bridge_stats = bridge.get_bridge_statistics()
    print(f"  跨链桥:")
    print(f"    资产: {bridge_stats['total_assets']}")
    print(f"    交易: {bridge_stats['total_transactions']}")
    print()

    # ========== 10. 保存数据 ==========
    print("【步骤 10】保存数据")
    print("-" * 40)
    token_economy.save_data()
    dao.save_data()
    dex.save_data()
    mining.save_data()
    layer2.save_data()
    zk_proof.save_data()
    bridge.save_data()
    print("  ✅ 数据已保存")
    print()

    print("=" * 60)
    print("🎉 v2.2 + v3.0 演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
