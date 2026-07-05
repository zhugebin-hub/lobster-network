#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 ARD 协议演示
Agentic Resource Discovery 协议集成
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.lobster_network.ard_protocol import ARDProtocol


def main():
    """主函数"""
    print("=" * 60)
    print("🦞 小龙虾网络 ARD 协议演示")
    print("=" * 60)
    print()

    # ========== 1. 初始化 ARD 协议 ==========
    ard = ARDProtocol(data_dir="/tmp/lobster-ard-demo")
    ard.load_data()

    print("【步骤 1】初始化 ARD 协议")
    print("-" * 40)
    print(f"  数据目录: {ard.data_dir}")
    print(f"  协议版本: {ard.data_dir}")
    print()

    # ========== 2. 注册 Agent ==========
    print("【步骤 2】注册 Agent")
    print("-" * 40)

    # 注册数据分析 Agent
    ok, msg = ard.register_agent(
        name="数据分析专家",
        agent_type="specialized",
        capabilities=["data-analysis", "statistics", "visualization"],
        endpoint="https://data-agent.lobster-network.ai",
        metadata={"version": "1.0", "language": "Python"},
    )
    print(f"  {msg}")

    # 注册报告生成 Agent
    ok, msg = ard.register_agent(
        name="报告生成专家",
        agent_type="specialized",
        capabilities=["report-generation", "writing", "formatting"],
        endpoint="https://report-agent.lobster-network.ai",
        metadata={"version": "1.0", "language": "Python"},
    )
    print(f"  {msg}")

    # 注册设计 Agent
    ok, msg = ard.register_agent(
        name="设计专家",
        agent_type="specialized",
        capabilities=["design", "visualization", "ui-ux"],
        endpoint="https://design-agent.lobster-network.ai",
        metadata={"version": "1.0", "language": "Python"},
    )
    print(f"  {msg}")
    print()

    # ========== 3. 注册资源 ==========
    print("【步骤 3】注册资源")
    print("-" * 40)

    # 注册 API 资源
    ok, msg = ard.register_resource(
        name="股票数据 API",
        resource_type="api",
        description="提供实时股票数据",
        endpoint="https://api.stock-data.com/v1",
        provider_id="provider-001",
        metadata={"rate_limit": "100/min", "cost": "0.01/call"},
    )
    print(f"  {msg}")

    # 注册技能资源
    ok, msg = ard.register_resource(
        name="自然语言处理技能",
        resource_type="skill",
        description="提供 NLP 相关技能",
        endpoint="https://skills.nlp-agent.com",
        provider_id="provider-002",
        metadata={"version": "2.0", "models": ["BERT", "GPT"]},
    )
    print(f"  {msg}")
    print()

    # ========== 4. 发现 Agent ==========
    print("【步骤 4】发现 Agent")
    print("-" * 40)

    # 发现具有数据分析能力的 Agent
    agents = ard.discover_agents({"capabilities": ["data-analysis"]})
    print(f"  发现 {len(agents)} 个数据分析 Agent:")
    for agent in agents:
        print(f"    - {agent.name} ({agent.agent_id})")
    print()

    # ========== 5. 发现资源 ==========
    print("【步骤 5】发现资源")
    print("-" * 40)

    # 发现 API 资源
    resources = ard.discover_resources("api")
    print(f"  发现 {len(resources)} 个 API 资源:")
    for resource in resources:
        print(f"    - {resource.name} ({resource.resource_id})")
    print()

    # ========== 6. 创建任务 ==========
    print("【步骤 6】创建 ARD 任务")
    print("-" * 40)

    # 创建市场调研任务
    ok, msg = ard.create_task(
        title="市场调研报告",
        description="完成一份完整的市场调研报告",
        criteria={
            "capabilities": ["data-analysis", "report-generation", "visualization"],
        },
        reward=100.0,
    )
    print(f"  {msg}")
    print()

    # ========== 7. 动态匹配 ==========
    print("【步骤 7】动态匹配 Agent")
    print("-" * 40)

    ok, msg, matched_agents = ard.match_agents("ard-task-0001")
    print(f"  {msg}")
    print(f"  匹配的 Agent:")
    for agent_id in matched_agents:
        agent = ard.get_agent(agent_id)
        if agent:
            print(f"    - {agent['name']} (匹配度: 高)")
    print()

    # ========== 8. 创建协同 ==========
    print("【步骤 8】创建协同任务")
    print("-" * 40)

    ok, msg = ard.create_collaboration("ard-task-0001", matched_agents)
    print(f"  {msg}")
    print()

    # ========== 9. 更新进度 ==========
    print("【步骤 9】更新协同进度")
    print("-" * 40)

    # 模拟进度更新
    for progress in [0.25, 0.5, 0.75, 1.0]:
        ok, msg = ard.update_collaboration_progress(
            "ard-collab-0001",
            progress=progress,
            emergence_score=0.8,
        )
        print(f"  进度 {progress:.0%}: {msg}")
    print()

    # ========== 10. 统计信息 ==========
    print("【步骤 10】ARD 统计信息")
    print("-" * 40)
    stats = ard.get_ard_statistics()
    print(f"  总 Agent 数: {stats['total_agents']}")
    print(f"  总资源数: {stats['total_resources']}")
    print(f"  总任务数: {stats['total_tasks']}")
    print(f"  总协同数: {stats['total_collaborations']}")
    print(f"  已完成协同: {stats['completed_collaborations']}")
    print()

    # ========== 11. 保存数据 ==========
    print("【步骤 11】保存数据")
    print("-" * 40)
    ard.save_data()
    print(f"  数据已保存到: {ard.data_dir}")
    print()

    print("=" * 60)
    print("🎉 ARD 协议演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()