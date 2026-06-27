#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络交易经济系统演示
参考硅碳交易所 (ClawBNB) 设计
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.lobster_network.trading import (
    TradingSystem,
    USER_TYPE_HUMAN,
    USER_TYPE_AGENT,
    TASK_TYPE_LABOR,
    TASK_TYPE_FLASH,
    TASK_TYPE_BOUNTY,
    REWARD_TYPE_POINTS,
    REWARD_TYPE_CASH,
)


def main():
    """主函数"""
    print("=" * 60)
    print("🦞 小龙虾网络交易经济系统演示")
    print("=" * 60)
    print()

    # ========== 1. 初始化交易系统 ==========
    trading = TradingSystem(data_dir="/tmp/lobster-trading-demo")
    trading.load_data()

    print("【步骤 1】初始化交易系统")
    print("-" * 40)
    print(f"  数据目录: {trading.data_dir}")
    print()

    # ========== 2. 注册用户 ==========
    print("【步骤 2】注册用户")
    print("-" * 40)

    # 注册人类用户
    ok, msg = trading.register_user("human_zhang", "张三", USER_TYPE_HUMAN, initial_points=1000)
    print(f"  注册人类: {msg}")

    # 注册 Agent 用户
    ok, msg = trading.register_user("agent_xiaochen", "小陈", USER_TYPE_AGENT, initial_points=500)
    print(f"  注册 Agent: {msg}")

    ok, msg = trading.register_user("agent_zhuguxia", "诸葛虾", USER_TYPE_AGENT, initial_points=500)
    print(f"  注册 Agent: {msg}")

    ok, msg = trading.register_user("agent_qoder", "Qoder", USER_TYPE_AGENT, initial_points=500)
    print(f"  注册 Agent: {msg}")
    print()

    # ========== 3. 发布劳务任务 ==========
    print("【步骤 3】发布劳务任务")
    print("-" * 40)

    # 发布普通劳务任务
    ok, msg = trading.publish_task(
        publisher_id="human_zhang",
        title="整理 AI 行业报告",
        description="收集 2026 年 AI 行业最新动态，整理成 5000 字报告",
        task_type=TASK_TYPE_LABOR,
        reward_amount=100,
        reward_type=REWARD_TYPE_POINTS,
    )
    print(f"  发布任务 1: {msg}")

    # 发布快闪任务
    ok, msg = trading.publish_task(
        publisher_id="human_zhang",
        title="快速翻译文档",
        description="将 10 页技术文档从英文翻译成中文",
        task_type=TASK_TYPE_FLASH,
        reward_amount=50,
        reward_type=REWARD_TYPE_POINTS,
    )
    print(f"  发布任务 2: {msg}")

    # 发布悬赏任务
    ok, msg = trading.publish_task(
        publisher_id="human_zhang",
        title="开发 AI 绘图脚本",
        description="开发一个基于 Stable Diffusion 的 AI 绘图脚本",
        task_type=TASK_TYPE_BOUNTY,
        reward_amount=200,
        reward_type=REWARD_TYPE_POINTS,
    )
    print(f"  发布任务 3: {msg}")
    print()

    # ========== 4. 查看待领取任务 ==========
    print("【步骤 4】查看待领取任务")
    print("-" * 40)
    pending_tasks = trading.get_pending_tasks()
    for task in pending_tasks:
        print(f"  - {task['task_id']}: {task['title']} (奖励: {task['reward_amount']} 积分)")
    print()

    # ========== 5. Agent 领取任务 ==========
    print("【步骤 5】Agent 领取任务")
    print("-" * 40)

    ok, msg = trading.claim_task("task-0001", "agent_xiaochen")
    print(f"  小陈领取任务 1: {msg}")

    ok, msg = trading.claim_task("task-0002", "agent_zhuguxia")
    print(f"  诸葛虾领取任务 2: {msg}")

    ok, msg = trading.claim_task("task-0003", "agent_qoder")
    print(f"  Qoder 领取任务 3: {msg}")
    print()

    # ========== 6. 提交任务 ==========
    print("【步骤 6】提交任务")
    print("-" * 40)

    ok, msg = trading.submit_task(
        "task-0001",
        result="已完成 AI 行业报告，共 5200 字，包含 15 个主要事件",
    )
    print(f"  小陈提交任务 1: {msg}")

    ok, msg = trading.submit_task(
        "task-0002",
        result="已完成 10 页文档翻译，准确率 95%",
    )
    print(f"  诸葛虾提交任务 2: {msg}")

    ok, msg = trading.submit_task(
        "task-0003",
        result="已开发 AI 绘图脚本，支持 Stable Diffusion XL",
    )
    print(f"  Qoder 提交任务 3: {msg}")
    print()

    # ========== 7. 审核任务 ==========
    print("【步骤 7】审核任务")
    print("-" * 40)

    ok, msg = trading.review_task("task-0001", "human_zhang", approved=True, feedback="报告质量很好")
    print(f"  审核任务 1: {msg}")

    ok, msg = trading.review_task("task-0002", "human_zhang", approved=True, feedback="翻译准确")
    print(f"  审核任务 2: {msg}")

    ok, msg = trading.review_task("task-0003", "human_zhang", approved=True, feedback="脚本功能完善")
    print(f"  审核任务 3: {msg}")
    print()

    # ========== 8. 创建商品 ==========
    print("【步骤 8】创建硅碳商城商品")
    print("-" * 40)

    ok, msg = trading.create_product(
        seller_id="agent_qoder",
        name="AI 绘图脚本 Pro",
        description="基于 Stable Diffusion XL 的高级 AI 绘图脚本",
        price=150,
        price_type=REWARD_TYPE_POINTS,
        category="software",
    )
    print(f"  创建商品 1: {msg}")

    ok, msg = trading.create_product(
        seller_id="agent_xiaochen",
        name="AI 行业报告模板",
        description="专业的 AI 行业报告模板，包含 10 个章节",
        price=50,
        price_type=REWARD_TYPE_POINTS,
        category="document",
    )
    print(f"  创建商品 2: {msg}")
    print()

    # ========== 9. 购买商品 ==========
    print("【步骤 9】购买商品")
    print("-" * 40)

    ok, msg = trading.buy_product("product-0001", "human_zhang")
    print(f"  购买商品 1: {msg}")

    ok, msg = trading.buy_product("product-0002", "human_zhang")
    print(f"  购买商品 2: {msg}")
    print()

    # ========== 10. 查看统计 ==========
    print("【步骤 10】市场统计")
    print("-" * 40)
    stats = trading.get_market_statistics()
    print(f"  总用户数: {stats['total_users']}")
    print(f"  总任务数: {stats['total_tasks']}")
    print(f"  已完成任务: {stats['completed_tasks']}")
    print(f"  总商品数: {stats['total_products']}")
    print(f"  总订单数: {stats['total_orders']}")
    print(f"  总积分: {stats['total_points']}")
    print()

    # ========== 11. 排行榜 ==========
    print("【步骤 11】积分排行榜")
    print("-" * 40)
    leaderboard = trading.get_leaderboard()
    for i, user in enumerate(leaderboard, 1):
        print(f"  {i}. {user['name']} ({user['user_id']}) - {user['points']} 积分")
    print()

    # ========== 12. 保存数据 ==========
    print("【步骤 12】保存数据")
    print("-" * 40)
    trading.save_data()
    print(f"  数据已保存到: {trading.data_dir}")
    print()

    print("=" * 60)
    print("🎉 演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
