#!/usr/bin/env python3
"""
时间套利引擎演示 (Time Arbitrage Engine Demo)

演示小龙虾网络的五维时间套利模式：
1. 速率套利 - 利用不同Agent的学习速度差
2. 错峰套利 - 利用低谷时段的高收益
3. 反思套利 - 遗忘曲线的最佳复习时机
4. 复利套利 - 多轮对话的涌现指数增长
5. 时距套利 - 知识的时间锁增值
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from datetime import datetime, timedelta
from lobster_network import (
    Node, DialogueEngine,
    TimeArbitrageEngine, NodeSpeedProfile, ArbitrageType,
)


def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def print_opportunity(opp):
    print(f"  [{opp.arbitrage_type.value.upper()}] {opp.description}")
    print(f"    预期收益: {opp.expected_return:.2f}x | 置信度: {opp.confidence:.0%}")
    print()


def demo_speed_arbitrage(engine, nodes):
    """演示1：速率套利"""
    print_header("1. 速率套利 (Speed Arbitrage)")
    print("  原理：快速节点(诸葛虾)先生成原始洞见，")
    print("        慢速节点(信电大虾)深化验证，形成知识价差。\n")

    zhuguxia = nodes["zhuguxia"]
    xiaochen = nodes["xiaochen"]

    # 检测套利机会
    opp = engine.detect_speed_arbitrage(zhuguxia, xiaochen, "围棋死活题")
    if opp:
        print_opportunity(opp)

    # 执行套利
    print("  执行3轮速率套利...")
    result = engine.execute_speed_arbitrage(zhuguxia, xiaochen, rounds=3)
    print(f"  触发对话: {result.dialogues_triggered} 轮")
    print(f"  涌现总量: {result.emergence_generated:.2f}")
    print(f"  实际收益: {result.actual_return:.2f}x")
    print(f"  复利因子: {result.compound_factor:.2f}")
    print(f"  知识转移: {result.knowledge_transferred}")


def demo_off_peak_arbitrage(engine, nodes, hour=2):
    """演示2：错峰套利"""
    print_header("2. 错峰套利 (Off-Peak Arbitrage)")
    print(f"  模拟时间: 凌晨 {hour}:00 (北京时间)\n")

    node_list = list(nodes.values())
    opp = engine.detect_off_peak_arbitrage(node_list, current_hour=hour)
    if opp:
        print_opportunity(opp)

    # 获取最优调度方案
    schedule = engine.get_optimal_schedule(node_list)
    print("  最优调度方案:")
    for window, info in schedule.items():
        print(f"    {window}: {info['window']} ({info['multiplier']}x)")
        print(f"      推荐任务: {', '.join(info['recommended_tasks'][:2])}")
        print(f"      强度: {info['intensity']}")


def demo_reflection_arbitrage(engine, nodes):
    """演示3：反思套利"""
    print_header("3. 反思套利 (Reflection Arbitrage)")
    print("  原理：基于艾宾浩斯遗忘曲线，")
    print("        在记忆保留率降至最佳复习点时触发复习。\n")

    node_id = "xiaochen"

    # 模拟3天前学习的知识点
    now = datetime.now()
    three_days_ago = now - timedelta(days=3)
    five_days_ago = now - timedelta(days=5)
    one_day_ago = now - timedelta(days=1)

    # 添加知识点
    engine.add_knowledge(node_id, "死活-倒扑", three_days_ago)
    engine.add_knowledge(node_id, "手筋-征子", five_days_ago)
    engine.add_knowledge(node_id, "定式-小飞挂", one_day_ago)

    # 先复习一次"倒扑"，提升稳定性
    review_time = now - timedelta(days=1)
    curves = engine.forgetting_curves[node_id]
    for c in curves:
        if c.knowledge_id == "死活-倒扑":
            c.review(review_time)
            break

    # 检测套利机会
    opportunities = engine.detect_reflection_arbitrage(node_id, now=now)

    if opportunities:
        print(f"  检测到 {len(opportunities)} 个复习机会:\n")
        for opp in opportunities:
            print_opportunity(opp)
    else:
        print("  当前时刻无最佳复习窗口（知识点要么太强、要么已太弱）\n")

    # 展示各知识点状态
    print("  知识点记忆状态:")
    for curve in curves:
        retention = curve.retention_at(now)
        optimal = curve.optimal_review_time()
        print(f"    {curve.knowledge_id}: 保留率={retention:.0%}, "
              f"复习{curve.review_count}次, 稳定性={curve.stability:.1f}, "
              f"最佳复习={optimal.strftime('%m-%d %H:%M')}")

    # 执行反思套利
    result = engine.execute_reflection(node_id, "手筋-征子", now=now)
    if result:
        print(f"\n  执行复习「手筋-征子」:")
        print(f"    稳定性提升: {result.compound_factor:.2f}x")


def demo_compound_arbitrage(engine, nodes):
    """演示4：复利套利"""
    print_header("4. 复利套利 (Compound Arbitrage)")
    print("  原理：多轮对话的涌现呈指数增长——")
    print("        E_total = E_1 × (1 + r)^(N-1)\n")

    zhuguma = nodes["zhuguma"]
    xiaochen = nodes["xiaochen"]

    # 启动复利对话链
    chain_id = engine.start_compound_chain(zhuguma, xiaochen)
    print(f"  启动复利链: {chain_id}")
    print(f"  执行5轮复利对话...\n")

    triggers = [
        "围棋AI定式分析",
        "死活题解法讨论",
        "布局策略对比",
        "中盘战斗评估",
        "官子收束技巧",
    ]

    for trigger in triggers:
        result = engine.compound_dialogue(chain_id, zhuguma, xiaochen, trigger)
        round_num = len(engine.compound_dialogue_chains[chain_id])
        print(f"    R{round_num} [{trigger}]: 涌现值={result.emergence_score:.2f}")

    # 统计
    stats = engine.get_compound_statistics(chain_id)
    print(f"\n  复利统计:")
    print(f"    总轮数: {stats['rounds']}")
    print(f"    总涌现: {stats['total_emergence']:.2f}")
    print(f"    平均涌现: {stats['avg_emergence']:.2f}")
    print(f"    复利因子: {stats['compound_factor']:.2f}x")
    print(f"    增长率: {stats['growth_rate']:.0%}")


def demo_temporal_arbitrage(engine, nodes):
    """演示5：时距套利"""
    print_header("5. 时距套利 (Temporal Distance Arbitrage)")
    print("  原理：知识的时间价值呈倒U型曲线——")
    print("        今天的洞见在48-72小时后价值最高。\n")

    # 创建时间锁宝藏
    treasures = []
    scenarios = [
        ("xiaochen", "征子技巧的7种变体", 24),
        ("zhuguxia", "AI定式的创新性解读", 72),
        ("qoder", "实战中的心理博弈策略", 48),
    ]

    for source, content, hours in scenarios:
        treasure = engine.create_time_locked_treasure(
            source_node_id=source,
            knowledge_content=content,
            unlock_conditions={"requires": "network_version >= 2"},
            lock_duration_hours=hours,
        )
        treasures.append(treasure)
        appreciation = treasure["expected_appreciation"]
        print(f"  宝藏 [{source}]: \"{content}\"")
        print(f"    锁定: {hours}h | 预计增值: {appreciation:.2f}x")
        print(f"    解锁时间: {treasure['unlock_at']}")
        print()

    # 展示增值曲线
    print("  时间增值曲线 (倒U型):")
    for h in [6, 12, 24, 48, 72, 96, 120, 144]:
        v = engine._estimate_appreciation(h)
        bar = "█" * int(v * 20)
        print(f"    {h:3d}h: {v:.2f}x {bar}")


def demo_full_scan(engine, nodes):
    """综合扫描"""
    print_header("综合套利扫描")
    print("  扫描所有节点、所有维度的套利机会...\n")

    now = datetime(2026, 6, 23, 2, 0, 0)  # 模拟凌晨2点
    node_list = list(nodes.values())

    opportunities = engine.scan_all_opportunities(node_list, now=now)

    if opportunities:
        print(f"  发现 {len(opportunities)} 个套利机会（按收益排序）:\n")
        for opp in opportunities:
            print_opportunity(opp)
    else:
        print("  暂无套利机会。")


def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║           🦞 小龙虾网络 - 时间套利引擎 v0.3.0           ║
║           Time Arbitrage Engine Demo                     ║
╚══════════════════════════════════════════════════════════╝
    """)

    # 创建节点
    nodes = {
        "xiaochen": Node(
            "xiaochen", "信电大虾",
            perspective="技术栈",
            knowledge_base="编程与电子",
            learning_rate="medium",
        ),
        "zhuguxia": Node(
            "zhuguxia", "诸葛虾",
            perspective="加速型",
            knowledge_base="围棋理论",
            learning_rate="high",
        ),
        "zhuguma": Node(
            "zhuguma", "诸葛马",
            node_type="coach",
            perspective="教练型",
            knowledge_base="训练设计",
            learning_rate="medium",
        ),
        "qoder": Node(
            "qoder", "小龙虾",
            perspective="实战型",
            knowledge_base="围棋实战",
            learning_rate="medium",
        ),
    }

    # 创建套利引擎
    engine = TimeArbitrageEngine()

    # 注册节点速度档案
    engine.register_node("xiaochen", NodeSpeedProfile.STEADY)
    engine.register_node("zhuguxia", NodeSpeedProfile.FAST)
    engine.register_node("qoder", NodeSpeedProfile.PRACTICAL)

    # 五个维度的演示
    demo_speed_arbitrage(engine, nodes)
    demo_off_peak_arbitrage(engine, nodes, hour=2)
    demo_reflection_arbitrage(engine, nodes)
    demo_compound_arbitrage(engine, nodes)
    demo_temporal_arbitrage(engine, nodes)

    # 综合扫描
    demo_full_scan(engine, nodes)

    # 组合概览
    print_header("套利组合概览")
    summary = engine.get_portfolio_summary()
    print(f"  总机会数: {summary['total_opportunities']}")
    print(f"  已执行: {summary['total_executed']}")
    print(f"  组合收益: {summary['portfolio_return']:.2f}")
    print(f"  复利链: {summary['compound_chains']}")
    print(f"  追踪知识点: {summary['tracked_knowledge']}")
    print(f"\n  按类型:")
    for atype, stats in summary["by_type"].items():
        print(f"    {atype}: {stats['pending_opportunities']}个机会, "
              f"{stats['executed']}次执行, "
              f"总收益={stats['total_return']:.2f}")

    print(f"\n{'='*60}")
    print("  你不停对话，世界就不停扩展 🦞⚡️")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
