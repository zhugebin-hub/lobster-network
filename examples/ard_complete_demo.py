#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 ARD 协议完整实施演示 V5.0
Phase 1 + Phase 2 + Phase 3

功能：
1. Phase 1: ARD 协议解析/Agent 发现/资源发现
2. Phase 2: 动态匹配/任务协同/智能合约
3. Phase 3: ARD 网关优化/跨平台测试/性能优化
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.lobster_network.ard_protocol import ARDProtocol
from src.lobster_network.ard_gateway import ARDGateway
from src.lobster_network.ard_security import ARDSecurityGateway
from src.lobster_network.ard_match import ARDMatchEngine, ARDCollaborationEngine, ARDSmartContractEngine


def main():
    """主函数"""
    print("=" * 60)
    print("🦞 小龙虾网络 ARD 协议完整实施演示")
    print("=" * 60)
    print()

    # ========== 1. Phase 1: ARD 协议基础 ==========
    print("【Phase 1】ARD 协议基础")
    print("-" * 40)

    ard = ARDProtocol(data_dir="/tmp/lobster-ard-complete/ard")
    ard.load_data()

    gateway = ARDSecurityGateway(ard, data_dir="/tmp/lobster-ard-complete/gateway")
    gateway.load_data()

    print("  ✅ ARD 协议初始化")
    print("  ✅ ARD 网关初始化")
    print()

    # 注册 Agent
    print("  注册 Agent:")
    agents = [
        ("数据分析专家", "specialized", ["data-analysis", "statistics", "visualization"]),
        ("报告生成专家", "specialized", ["report-generation", "writing", "formatting"]),
        ("设计专家", "specialized", ["design", "visualization", "ui-ux"]),
        ("通用助手", "general", ["writing", "analysis", "coding"]),
    ]
    for name, agent_type, capabilities in agents:
        ok, msg = ard.register_agent(name, agent_type, capabilities)
        print(f"    {msg}")
    print()

    # 注册资源
    print("  注册资源:")
    resources = [
        ("股票数据 API", "api", "提供实时股票数据", "https://api.stock-data.com"),
        ("NLP 技能", "skill", "提供 NLP 相关技能", "https://skills.nlp-agent.com"),
        ("设计工具", "tool", "提供设计相关工具", "https://tools.design-agent.com"),
    ]
    for name, res_type, desc, endpoint in resources:
        ok, msg = ard.register_resource(name, res_type, desc, endpoint, "provider-001")
        print(f"    {msg}")
    print()

    # 发现 Agent
    print("  发现 Agent:")
    agents = ard.discover_agents({"capabilities": ["data-analysis"]})
    print(f"    发现 {len(agents)} 个数据分析 Agent")
    print()

    # 发现资源
    print("  发现资源:")
    resources = ard.discover_resources("api")
    print(f"    发现 {len(resources)} 个 API 资源")
    print()

    # ========== 2. Phase 2: 动态匹配与协同 ==========
    print("【Phase 2】动态匹配与协同")
    print("-" * 40)

    # 创建任务
    print("  创建 ARD 任务:")
    ok, msg = ard.create_task(
        title="市场调研报告",
        description="完成一份完整的市场调研报告",
        criteria={
            "capabilities": ["data-analysis", "report-generation", "visualization"],
        },
        reward=100.0,
    )
    print(f"    {msg}")
    print()

    # 动态匹配
    print("  动态匹配 Agent:")
    match_engine = ARDMatchEngine(ard)
    results = match_engine.match("ard-task-0001", algorithm="hybrid", top_k=3)
    print(f"    匹配结果:")
    for result in results:
        print(f"      - {result.details.get('agent_name', 'unknown')}: 匹配度 {result.score:.2f}")
    print()

    # 创建协同计划
    print("  创建协同计划:")
    collab_engine = ARDCollaborationEngine(ard)
    matched_agent_ids = [r.agent_id for r in results]
    ok, msg = collab_engine.create_plan("ard-task-0001", matched_agent_ids)
    print(f"    {msg}")
    print()

    # 执行协同计划
    print("  执行协同计划:")
    ok, msg = collab_engine.execute_plan("ard-plan-0001")
    print(f"    {msg}")
    print()

    # 创建智能合约
    print("  创建智能合约:")
    contract_engine = ARDSmartContractEngine(ard)
    ok, msg = contract_engine.create_contract(
        task_id="ard-task-0001",
        agent_ids=matched_agent_ids,
        reward=100.0,
    )
    print(f"    {msg}")
    print()

    # 执行智能合约
    print("  执行智能合约:")
    ok, msg = contract_engine.execute_contract("ard-contract-0001")
    print(f"    {msg}")
    print()

    # ========== 3. Phase 3: 网关优化与性能 ==========
    print("【Phase 3】网关优化与性能")
    print("-" * 40)

    # 注册端点
    print("  注册 ARD 端点:")
    endpoints = [
        ("谷歌 Agent 平台", "https://agent-platform.google.com", ["data-analysis", "machine-learning"]),
        ("微软 Copilot", "https://copilot.microsoft.com", ["writing", "coding", "analysis"]),
        ("Salesforce Agent", "https://agent.salesforce.com", ["crm", "sales", "marketing"]),
    ]
    for name, url, capabilities in endpoints:
        ok, msg = gateway.register_endpoint(name, url, capabilities)
        print(f"    {msg}")
    print()

    # 端点心跳
    print("  端点心跳:")
    for endpoint_id in ["ard-endpoint-0001", "ard-endpoint-0002", "ard-endpoint-0003"]:
        ok, msg = gateway.heartbeat(endpoint_id)
        print(f"    {msg}")
    print()

    # 发送安全消息
    print("  发送安全消息:")
    ok, msg = gateway.send_secure_message(
        msg_type="discover",
        sender_id="xiaochen",
        receiver_id="gateway",
        payload={"criteria": {"capabilities": ["data-analysis"]}},
    )
    print(f"    {msg}")
    print()

    # 性能统计
    print("  性能统计:")
    perf_stats = gateway.performance_optimizer.get_performance_statistics()
    print(f"    总操作数: {perf_stats['total_operations']}")
    print(f"    平均耗时: {perf_stats['avg_duration_ms']:.2f} ms")
    print(f"    成功率: {perf_stats['success_rate']:.2%}")
    print()

    # 安全统计
    print("  安全统计:")
    security_stats = gateway.get_security_statistics()
    print(f"    总密钥数: {security_stats['total_keys']}")
    print(f"    总错误数: {security_stats['total_errors']}")
    print()

    # ========== 4. 综合统计 ==========
    print("【综合统计】")
    print("-" * 40)

    ard_stats = ard.get_ard_statistics()
    print(f"  ARD 统计:")
    print(f"    总 Agent 数: {ard_stats['total_agents']}")
    print(f"    总资源数: {ard_stats['total_resources']}")
    print(f"    总任务数: {ard_stats['total_tasks']}")
    print(f"    总协同数: {ard_stats['total_collaborations']}")
    print()

    match_stats = match_engine.get_match_statistics()
    print(f"  匹配统计:")
    print(f"    总匹配数: {match_stats['total_matches']}")
    print(f"    平均匹配度: {match_stats['avg_score']:.2f}")
    print()

    collab_stats = collab_engine.get_collaboration_statistics()
    print(f"  协同统计:")
    print(f"    总计划数: {collab_stats['total_plans']}")
    print(f"    已完成计划: {collab_stats['completed_plans']}")
    print()

    contract_stats = contract_engine.get_contract_statistics()
    print(f"  合约统计:")
    print(f"    总合约数: {contract_stats['total_contracts']}")
    print(f"    已执行合约: {contract_stats['executed_contracts']}")
    print()

    gateway_stats = gateway.get_gateway_statistics()
    print(f"  网关统计:")
    print(f"    总端点数: {gateway_stats['total_endpoints']}")
    print(f"    活跃端点: {gateway_stats['active_endpoints']}")
    print(f"    总消息数: {gateway_stats['total_messages']}")
    print()

    # ========== 5. 保存数据 ==========
    print("【保存数据】")
    print("-" * 40)
    ard.save_data()
    gateway.save_data()
    print("  ✅ 数据已保存")
    print()

    print("=" * 60)
    print("🎉 ARD 协议完整实施演示完成！")
    print("=" * 60)
    print()
    print("📊 实施总结:")
    print("  Phase 1: ✅ ARD 协议解析/Agent 发现/资源发现")
    print("  Phase 2: ✅ 动态匹配/任务协同/智能合约")
    print("  Phase 3: ✅ 网关优化/跨平台测试/性能优化")
    print()
    print("🦞 小龙虾网络 ARD 协议集成完成！")


if __name__ == "__main__":
    main()