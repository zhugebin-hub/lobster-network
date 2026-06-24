#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 CLI 工具 V4.0
命令行界面管理小龙虾网络

用法:
    lobster-cli <command> [options]

命令:
    wallet      钱包管理
    node        节点管理
    task        任务管理
    proposal    治理提案
    mine        挖矿
    stats       网络统计
"""

import argparse
import json
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.lobster_network.token_economy import TokenEconomy
from src.lobster_network.node_registry import NodeRegistry
from src.lobster_network.trading import TradingSystem
from src.lobster_network.dao_governance import DAOGovernance


class LobsterCLI:
    """小龙虾网络 CLI"""

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

    # ========== 钱包命令 ==========

    def wallet_create(self, args):
        """创建钱包"""
        ok, msg = self.token_economy.create_wallet(args.node_id)
        print(msg)

    def wallet_balance(self, args):
        """查询余额"""
        balance = self.token_economy.get_balance(args.node_id)
        wallet = self.token_economy.get_wallet(args.node_id)
        if wallet:
            print(f"节点: {args.node_id}")
            print(f"地址: {wallet.address}")
            print(f"余额: {balance:.2f} 🦞")
            print(f"质押: {wallet.staked:.2f} 🦞")
        else:
            print(f"钱包不存在: {args.node_id}")

    def wallet_transfer(self, args):
        """转账"""
        ok, msg = self.token_economy.transfer(args.from_node, args.to_node, args.amount)
        print(msg)

    def wallet_stake(self, args):
        """质押"""
        ok, msg = self.token_economy.stake(args.node_id, args.amount)
        print(msg)

    def wallet_unstake(self, args):
        """解除质押"""
        ok, msg = self.token_economy.unstake(args.node_id, args.amount)
        print(msg)

    # ========== 节点命令 ==========

    def node_list(self, args):
        """列出节点"""
        # 从 trading 系统获取用户
        users = self.trading.users
        for node_id, user in users.items():
            print(f"{node_id}: {user.name} ({user.user_type}) - 积分: {user.points}")

    def node_register(self, args):
        """注册节点"""
        ok, msg = self.trading.register_user(
            args.node_id,
            args.name,
            user_type=args.type,
            initial_points=args.points,
        )
        print(msg)

    # ========== 任务命令 ==========

    def task_list(self, args):
        """列出任务"""
        tasks = self.trading.get_pending_tasks(limit=args.limit)
        for task in tasks:
            print(f"{task['task_id']}: {task['title']} (奖励: {task['reward_amount']} 积分)")

    def task_create(self, args):
        """创建任务"""
        ok, msg = self.trading.publish_task(
            publisher_id=args.publisher_id,
            title=args.title,
            description=args.description,
            task_type=args.type,
            reward_amount=args.reward,
        )
        print(msg)

    def task_claim(self, args):
        """领取任务"""
        ok, msg = self.trading.claim_task(args.task_id, args.node_id)
        print(msg)

    def task_submit(self, args):
        """提交任务"""
        ok, msg = self.trading.submit_task(args.task_id, args.result)
        print(msg)

    def task_review(self, args):
        """审核任务"""
        approved = args.approve.lower() in ['true', 'yes', '1']
        ok, msg = self.trading.review_task(args.task_id, args.reviewer_id, approved, args.feedback)
        print(msg)

    # ========== 治理命令 ==========

    def proposal_list(self, args):
        """列出提案"""
        proposals = self.dao.get_active_proposals(limit=args.limit)
        for proposal in proposals:
            print(f"{proposal['proposal_id']}: {proposal['title']} ({proposal['status']})")

    def proposal_create(self, args):
        """创建提案"""
        ok, msg = self.dao.create_proposal(
            creator_id=args.creator_id,
            title=args.title,
            description=args.description,
            proposal_type=args.type,
        )
        print(msg)

    def proposal_vote(self, args):
        """投票"""
        ok, msg = self.dao.vote(args.proposal_id, args.voter_id, args.option, args.reason)
        print(msg)

    # ========== 挖矿命令 ==========

    def mine(self, args):
        """挖矿"""
        ok, msg = self.token_economy.mine_block(args.node_id, args.emergence)
        print(msg)

    # ========== 统计命令 ==========

    def stats(self, args):
        """网络统计"""
        token_stats = self.token_economy.get_blockchain_info()
        trading_stats = self.trading.get_market_statistics()
        dao_stats = self.dao.get_governance_statistics()

        print("=" * 40)
        print("🦞 小龙虾网络统计")
        print("=" * 40)
        print(f"Token 经济:")
        print(f"  链长度: {token_stats['chain_length']}")
        print(f"  总供应量: {token_stats['total_supply']:.2f} 🦞")
        print(f"  流通量: {token_stats['circulating_supply']:.2f} 🦞")
        print(f"  钱包数: {token_stats['total_wallets']}")
        print()
        print(f"交易市场:")
        print(f"  用户数: {trading_stats['total_users']}")
        print(f"  任务数: {trading_stats['total_tasks']}")
        print(f"  已完成: {trading_stats['completed_tasks']}")
        print()
        print(f"DAO 治理:")
        print(f"  提案数: {dao_stats['total_proposals']}")
        print(f"  活跃: {dao_stats['active_proposals']}")
        print(f"  已通过: {dao_stats['passed_proposals']}")
        print()

    # ========== 保存数据 ==========

    def save(self, args):
        """保存数据"""
        self.token_economy.save_data()
        self.trading.save_data()
        self.dao.save_data()
        print("✅ 数据已保存")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="🦞 小龙虾网络 CLI 工具 V4.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--data-dir', default='/shared/lobster-network-data', help='数据目录')

    subparsers = parser.add_subparsers(dest='command', help='命令')

    # 钱包命令
    wallet_parser = subparsers.add_parser('wallet', help='钱包管理')
    wallet_subparsers = wallet_parser.add_subparsers(dest='wallet_command')

    # wallet create
    wallet_create_parser = wallet_subparsers.add_parser('create', help='创建钱包')
    wallet_create_parser.add_argument('node_id', help='节点 ID')

    # wallet balance
    wallet_balance_parser = wallet_subparsers.add_parser('balance', help='查询余额')
    wallet_balance_parser.add_argument('node_id', help='节点 ID')

    # wallet transfer
    wallet_transfer_parser = wallet_subparsers.add_parser('transfer', help='转账')
    wallet_transfer_parser.add_argument('from_node', help='发送方节点 ID')
    wallet_transfer_parser.add_argument('to_node', help='接收方节点 ID')
    wallet_transfer_parser.add_argument('amount', type=float, help='金额')

    # wallet stake
    wallet_stake_parser = wallet_subparsers.add_parser('stake', help='质押')
    wallet_stake_parser.add_argument('node_id', help='节点 ID')
    wallet_stake_parser.add_argument('amount', type=float, help='金额')

    # wallet unstake
    wallet_unstake_parser = wallet_subparsers.add_parser('unstake', help='解除质押')
    wallet_unstake_parser.add_argument('node_id', help='节点 ID')
    wallet_unstake_parser.add_argument('amount', type=float, help='金额')

    # 节点命令
    node_parser = subparsers.add_parser('node', help='节点管理')
    node_subparsers = node_parser.add_subparsers(dest='node_command')

    # node list
    node_list_parser = node_subparsers.add_parser('list', help='列出节点')

    # node register
    node_register_parser = node_subparsers.add_parser('register', help='注册节点')
    node_register_parser.add_argument('node_id', help='节点 ID')
    node_register_parser.add_argument('name', help='节点名称')
    node_register_parser.add_argument('--type', default='agent', help='节点类型')
    node_register_parser.add_argument('--points', type=int, default=100, help='初始积分')

    # 任务命令
    task_parser = subparsers.add_parser('task', help='任务管理')
    task_subparsers = task_parser.add_subparsers(dest='task_command')

    # task list
    task_list_parser = task_subparsers.add_parser('list', help='列出任务')
    task_list_parser.add_argument('--limit', type=int, default=20, help='数量限制')

    # task create
    task_create_parser = task_subparsers.add_parser('create', help='创建任务')
    task_create_parser.add_argument('publisher_id', help='发布者节点 ID')
    task_create_parser.add_argument('title', help='任务标题')
    task_create_parser.add_argument('description', help='任务描述')
    task_create_parser.add_argument('--type', default='labor', help='任务类型')
    task_create_parser.add_argument('--reward', type=float, default=10.0, help='奖励')

    # task claim
    task_claim_parser = task_subparsers.add_parser('claim', help='领取任务')
    task_claim_parser.add_argument('task_id', help='任务 ID')
    task_claim_parser.add_argument('node_id', help='节点 ID')

    # task submit
    task_submit_parser = task_subparsers.add_parser('submit', help='提交任务')
    task_submit_parser.add_argument('task_id', help='任务 ID')
    task_submit_parser.add_argument('result', help='结果')

    # task review
    task_review_parser = task_subparsers.add_parser('review', help='审核任务')
    task_review_parser.add_argument('task_id', help='任务 ID')
    task_review_parser.add_argument('reviewer_id', help='审核者节点 ID')
    task_review_parser.add_argument('approve', help='是否通过')
    task_review_parser.add_argument('--feedback', default='', help='反馈')

    # 治理命令
    proposal_parser = subparsers.add_parser('proposal', help='治理提案')
    proposal_subparsers = proposal_parser.add_subparsers(dest='proposal_command')

    # proposal list
    proposal_list_parser = proposal_subparsers.add_parser('list', help='列出提案')
    proposal_list_parser.add_argument('--limit', type=int, default=20, help='数量限制')

    # proposal create
    proposal_create_parser = proposal_subparsers.add_parser('create', help='创建提案')
    proposal_create_parser.add_argument('creator_id', help='创建者节点 ID')
    proposal_create_parser.add_argument('title', help='提案标题')
    proposal_create_parser.add_argument('description', help='提案描述')
    proposal_create_parser.add_argument('--type', default='generic', help='提案类型')

    # proposal vote
    proposal_vote_parser = proposal_subparsers.add_parser('vote', help='投票')
    proposal_vote_parser.add_argument('proposal_id', help='提案 ID')
    proposal_vote_parser.add_argument('voter_id', help='投票者节点 ID')
    proposal_vote_parser.add_argument('option', help='投票选项 (for/against/abstain)')
    proposal_vote_parser.add_argument('--reason', default='', help='理由')

    # 挖矿命令
    mine_parser = subparsers.add_parser('mine', help='挖矿')
    mine_parser.add_argument('node_id', help='节点 ID')
    mine_parser.add_argument('--emergence', type=float, default=0.5, help='涌现值')

    # 统计命令
    stats_parser = subparsers.add_parser('stats', help='网络统计')

    # 保存命令
    save_parser = subparsers.add_parser('save', help='保存数据')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    cli = LobsterCLI(data_dir=args.data_dir)

    # 钱包命令
    if args.command == 'wallet':
        if args.wallet_command == 'create':
            cli.wallet_create(args)
        elif args.wallet_command == 'balance':
            cli.wallet_balance(args)
        elif args.wallet_command == 'transfer':
            cli.wallet_transfer(args)
        elif args.wallet_command == 'stake':
            cli.wallet_stake(args)
        elif args.wallet_command == 'unstake':
            cli.wallet_unstake(args)
        else:
            wallet_parser.print_help()

    # 节点命令
    elif args.command == 'node':
        if args.node_command == 'list':
            cli.node_list(args)
        elif args.node_command == 'register':
            cli.node_register(args)
        else:
            node_parser.print_help()

    # 任务命令
    elif args.command == 'task':
        if args.task_command == 'list':
            cli.task_list(args)
        elif args.task_command == 'create':
            cli.task_create(args)
        elif args.task_command == 'claim':
            cli.task_claim(args)
        elif args.task_command == 'submit':
            cli.task_submit(args)
        elif args.task_command == 'review':
            cli.task_review(args)
        else:
            task_parser.print_help()

    # 治理命令
    elif args.command == 'proposal':
        if args.proposal_command == 'list':
            cli.proposal_list(args)
        elif args.proposal_command == 'create':
            cli.proposal_create(args)
        elif args.proposal_command == 'vote':
            cli.proposal_vote(args)
        else:
            proposal_parser.print_help()

    # 挖矿命令
    elif args.command == 'mine':
        cli.mine(args)

    # 统计命令
    elif args.command == 'stats':
        cli.stats(args)

    # 保存命令
    elif args.command == 'save':
        cli.save(args)


if __name__ == '__main__':
    main()