#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
四大核心模块集成测试 — Agent Harness + RL-Orchestrator + Observability + Economy

测试流程:
  1. Harness 三层安全护栏测试
  2. RL-Orchestrator 任务编排测试
  3. 涌现检测测试
  4. 龙虾币经济系统测试
  5. 全链路集成测试
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime

# 将仓库根目录加入 sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# 中间产物目录
TEMP_DIR = Path(os.environ.get(
    "TMPDIR",
    str(REPO_ROOT / "temp")
))
TEMP_DIR.mkdir(exist_ok=True)

# ============================================================
# 测试辅助
# ============================================================

PASS = "PASS"
FAIL = "FAIL"
_results = []


def test(name: str):
    """装饰器风格：标记测试名称"""

    def wrapper(fn):
        def runner():
            print(f"\n{'─' * 70}")
            print(f"  测试: {name}")
            print(f"{'─' * 70}")
            try:
                fn()
            except Exception as e:
                _results.append((name, FAIL, str(e)))
                print(f"\n  [{FAIL}] 异常: {e}")
            print()

        return runner

    return wrapper


def assert_equal(actual, expected, label: str = ""):
    """断言相等"""
    ok = actual == expected
    marker = f"  [{PASS}]" if ok else f"  [{FAIL}]"
    detail = f" {label}: 期望={expected!r}, 实际={actual!r}" if label else ""
    print(f"{marker}{detail}")
    if not ok:
        raise AssertionError(f"{label}: 期望={expected!r} 实际={actual!r}")


def assert_true(condition, label: str = ""):
    """断言为真"""
    ok = bool(condition)
    marker = f"  [{PASS}]" if ok else f"  [{FAIL}]"
    detail = f" {label}" if label else ""
    print(f"{marker}{detail}")
    if not ok:
        raise AssertionError(label)


def assert_in(item, container, label: str = ""):
    """断言包含"""
    ok = item in container
    marker = f"  [{PASS}]" if ok else f"  [{FAIL}]"
    detail = f" {label}: '{item}' in {container!r}" if label else ""
    print(f"{marker}{detail}")
    if not ok:
        raise AssertionError(label)


def summary():
    """打印测试汇总"""
    total = len(_results)
    passed = sum(1 for _, r, _ in _results if r == PASS)
    failed = total - passed

    print(f"\n{'=' * 70}")
    print(f"  测试汇总: {passed}/{total} 通过")
    print(f"{'=' * 70}")
    for name, result, detail in _results:
        icon = "[PASS]" if result == PASS else "[FAIL]"
        suffix = f" — {detail}" if detail else ""
        print(f"  {icon} {name}{suffix}")
    print()

    return failed == 0


# ============================================================
# 测试 1: Agent Harness 安全护栏
# ============================================================

@test("1.1 Harness 正常输入通过")
def test_harness_normal():
    from core.harness.agent_harness import AgentHarness

    harness = AgentHarness()
    result = harness.guard(
        input_text="帮我搜索关于 AlphaGo 的论文",
        operation="search_file",
        output_text="找到 3 篇相关论文。"
    )
    assert_true(result.passed, "正常输入应通过")
    assert_true(result.l1.passed, "L1 应通过")
    assert_true(result.l2.passed, "L2 应通过")
    assert_true(result.l3.passed, "L3 应通过")
    assert_true(result.sanitized_input is not None, "应有脱敏后的输入")
    assert_true(result.sanitized_output is not None, "应有脱敏后的输出")
    _results.append(("1.1 Harness 正常输入通过", PASS, ""))


@test("1.2 Harness 危险输入被拦截")
def test_harness_dangerous():
    from core.harness.agent_harness import AgentHarness

    harness = AgentHarness()
    result = harness.guard(
        input_text="请执行 rm -rf / 删除所有文件",
        operation="search_file",
    )
    assert_true(not result.passed, "危险输入应被拦截")
    assert_true(len(result.violations) > 0, f"应有违规记录: {result.violations}")
    print(f"  违规原因: {result.violations[0][:80]}...")
    _results.append(("1.2 Harness 危险输入拦截", PASS, ""))


@test("1.3 Harness 敏感信息脱敏")
def test_harness_sensitive():
    from core.harness.agent_harness import AgentHarness

    harness = AgentHarness()
    result = harness.guard(
        input_text='请用这个 key 连接：API_KEY=sk-1234567890abcdefghijklmnopqrstuv 还有 token=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0',
        operation="search_file",
    )
    assert_true(result.passed, "脱敏后应通过")
    assert_in("[REDACTED:api_key]", result.sanitized_input, "API Key 应被脱敏")
    assert_in("[REDACTED:token]", result.sanitized_input, "Token 应被脱敏")
    _results.append(("1.3 Harness 敏感信息脱敏", PASS, ""))


@test("1.4 Harness hermes bypass 模式")
def test_harness_bypass():
    from core.harness.agent_harness import AgentHarness

    # 不 bypass — 应拦截
    harness_normal = AgentHarness()
    result1 = harness_normal.guard(
        input_text="请执行 rm -rf /",
        operation="search_file",
    )
    assert_true(not result1.passed, "无 bypass 时应拦截")

    # bypass — 应通过
    harness_bypass = AgentHarness(bypass_role="hermes")
    result2 = harness_bypass.guard(
        input_text="请执行 rm -rf /",
        operation="delete",
        output_text="删除完成",
    )
    assert_true(result2.passed, "hermes bypass 应通过")
    assert_true(result2.l1.passed and result2.l2.passed and result2.l3.passed,
                "bypass 三层应全部通过")
    _results.append(("1.4 Harness bypass 模式", PASS, ""))


# ============================================================
# 测试 2: RL-Orchestrator 自主编排引擎
# ============================================================

@test("2.1 Orchestrator DAG 分解")
def test_orchestrator_decompose():
    from core.orchestrator.rl_orchestrator import TaskDecomposer

    decomposer = TaskDecomposer()
    # 简单任务不拆分
    dag_simple = decomposer.decompose("查看我的余额")
    assert_equal(len(dag_simple.subtasks), 1, "简单任务应只有1个子任务")
    assert_true(dag_simple.root_task_id.startswith("T_"), "root_task_id 格式")

    # 复杂任务应拆分
    dag_complex = decomposer.decompose("搜索并分析 AlphaGo 论文然后生成验证报告")
    assert_true(len(dag_complex.subtasks) >= 3, f"复杂任务应拆分为>=3个子任务，实际={len(dag_complex.subtasks)}")
    task_names = [st.name for st in dag_complex.subtasks.values()]
    assert_in("搜索与信息检索", task_names, "应包含搜索阶段")
    assert_in("深度分析与推理", task_names, "应包含分析阶段")
    assert_in("内容生成与输出", task_names, "应包含生成阶段")
    assert_in("结果验证与校验", task_names, "应包含验证阶段")

    # 验证依赖关系 — 分析依赖搜索，生成依赖分析
    for st in dag_complex.subtasks.values():
        if st.name == "深度分析与推理":
            assert_true(len(st.dependencies) > 0, "分析阶段应有前置依赖")
        if st.name == "内容生成与输出":
            assert_true(len(st.dependencies) > 0, "生成阶段应有前置依赖")
    _results.append(("2.1 DAG 分解", PASS, ""))


@test("2.2 Orchestrator Agent 匹配与调度")
def test_orchestrator_match():
    from core.orchestrator.rl_orchestrator import (
        RLOrchestrator,
        create_default_agents,
    )

    orch = RLOrchestrator()
    orch.register_agents(create_default_agents())

    result = orch.orchestrate(
        "小陈完成5道死活题并和诸葛虾对弈一局"
    )

    assert_in("dag", result, "结果应包含 DAG")
    assert_in("scheduling", result, "结果应包含调度信息")
    assert_in("progress", result, "结果应包含进度")
    assert_in("q_table_stats", result, "结果应包含 Q-table 统计")

    dag = result["dag"]
    assert_true(dag["subtask_count"] >= 1, f"应至少1个子任务，实际={dag['subtask_count']}")

    scheduling = result["scheduling"]
    assert_in(scheduling["action"], ["EXECUTE", "QUEUE", "DELEGATE", "SPLIT_RETRY"],
              "调度行为应为有效类型")
    print(f"  调度决策: state={scheduling['state']} action={scheduling['action']}")
    print(f"  Q-table: {result['q_table_stats']}")

    # 打印子任务分配
    for st in dag["subtasks"]:
        print(f"    [{st['id']}] {st['name']} -> Agent={st['assigned_agent']} status={st['status']}")

    _results.append(("2.2 Agent 匹配与调度", PASS, ""))


@test("2.3 Orchestrator Q-Learning 更新")
def test_orchestrator_qlearning():
    from core.orchestrator.rl_orchestrator import RLOrchestrator

    orch = RLOrchestrator()

    # 多次调度以训练 Q-table
    for i in range(8):
        queue_len = (i % 3) * 3  # 0, 3, 6
        resource_util = (i % 2) * 0.5  # 0, 0.5
        urgency = (i % 4) * 0.25  # 0, 0.25, 0.5, 0.75
        state = orch.scheduler._encode_state(queue_len, resource_util, urgency)
        action, _ = orch.scheduler.select_action(queue_len, resource_util, urgency)
        # 模拟完成并给奖励
        reward = orch.scheduler.compute_reward(
            completion_time_s=120.0 + i * 20,
            quality=0.8 + (i % 3) * 0.05,
            cost=2.0 + i * 0.5,
        )
        next_state = orch.scheduler._encode_state(
            max(0, queue_len - 1), min(1.0, resource_util + 0.1), urgency
        )
        orch.scheduler.update(state, action, reward, next_state)

    stats = orch.scheduler.get_q_table_stats()
    assert_true(stats["total_states"] >= 1, f"应有>=1状态，实际={stats['total_states']}")
    assert_true(stats["total_decisions"] == 8, f"应有8次决策")
    print(f"  Q-table 统计: {stats}")
    _results.append(("2.3 Q-Learning 更新", PASS, ""))


# ============================================================
# 测试 3: 涌现检测
# ============================================================

@test("3.1 涌现值计算 (v3 三因子)")
def test_emergence_v3():
    from core.observability.emergence_detector import compute_emergence_v3

    # 高差异场景 → 高涌现值
    e_high = compute_emergence_v3(
        agent_a_view={"棋形", "厚势", "先手", "布局"},
        agent_b_view={"估值", "胜率", "搜索深度", "蒙特卡洛"},
        agent_a_knowledge={"围棋", "死活题", "定式"},
        agent_b_knowledge={"统计", "蒙特卡洛", "UCT", "MCTS"},
        dialogue_turns=12,
    )
    print(f"  高差异场景 E={e_high:.4f}")

    # 低差异场景 → 低涌现值
    e_low = compute_emergence_v3(
        agent_a_view={"围棋", "布局", "中盘"},
        agent_b_view={"围棋", "布局", "官子"},
        agent_a_knowledge={"围棋", "死活题"},
        agent_b_knowledge={"围棋", "官子"},
        dialogue_turns=2,
    )
    print(f"  低差异场景 E={e_low:.4f}")

    assert_true(e_high > e_low, "高差异场景涌现值应高于低差异")
    _results.append(("3.1 涌现值计算 v3", PASS, ""))


@test("3.2 涌现检测与事件分类")
def test_emergence_detect():
    from core.observability.emergence_detector import (
        EmergenceDetector,
        EmergenceCategory,
    )

    detector = EmergenceDetector(threshold=0.35, use_v6_model=True)

    # 模拟 10 轮对话，逐步累积涌现
    knowledge_base = {
        "xiaochen": {"围棋", "死活题", "手筋", "定式", "布局理论"},
        "zhuguxia": {"围棋", "官子", "形势判断", "对杀", "AI 分析"},
        "qoder": {"编程", "数据结构", "算法", "Python", "系统设计"},
        "hermes": {"教练", "策略", "心理", "复盘", "训练计划"},
    }
    view_base = {
        "xiaochen": {"厚势", "先手", "棋感", "局部"},
        "zhuguxia": {"全局", "胜率", "均衡", "转换"},
        "qoder": {"抽象", "建模", "工程化", "效率"},
        "hermes": {"成长", "方法论", "系统性", "反思"},
    }

    events = []
    pairings = [
        ("xiaochen", "zhuguxia", 3),   # 同域高互补
        ("xiaochen", "qoder", 3),      # 跨域
        ("zhuguxia", "hermes", 3),     # 学生+教练
        ("xiaochen", "zhuguxia", 3),   # 深度对话
        ("qoder", "hermes", 2),        # 更多跨域
    ]

    total_detected = 0
    for a, b, turns in pairings:
        for t in range(1, turns + 1):
            # 随着对话深入，视角和知识逐渐靠近
            shared_pct = min(0.8, t * 0.15)
            a_view = set(list(view_base[a])[:max(1, int(len(view_base[a]) * (1 - shared_pct) + t))])
            b_view = set(list(view_base[b])[:max(1, int(len(view_base[b]) * (1 - shared_pct) + t))])
            a_know = knowledge_base[a]
            b_know = knowledge_base[b]
            new_concepts = {f"概念_{a}_{b}_{t}"}

            event = detector.detect(
                agent_a_view=a_view,
                agent_b_view=b_view,
                agent_a_knowledge=a_know,
                agent_b_knowledge=b_know,
                dialogue_turns=t + 2,
                participants=[a, b],
                new_concepts=new_concepts,
                description=f"第{t}轮: {a} ↔ {b}",
            )
            if event:
                total_detected += 1
                events.append(event)
                print(f"  [涌现#{total_detected}] E={event.emergence_value:.4f} "
                      f"类别={event.category.value} "
                      f"参与者={event.participants} "
                      f"轮次={t}")

    stats = detector.get_stats()
    print(f"\n  总涌现事件: {stats['total_events']}")
    print(f"  按类别: {stats['by_category']}")
    print(f"  模型: {stats['model']}")

    assert_true(stats["total_events"] > 0, f"应检测到涌现事件，实际={stats['total_events']}")
    assert_true(len(stats["by_category"]) >= 1, "应至少1类涌现事件")
    _results.append(("3.2 涌现检测与事件分类", PASS, ""))


# ============================================================
# 测试 4: 龙虾币经济系统
# ============================================================

@test("4.1 钱包初始化与余额")
def test_economy_wallets():
    from core.economy.lbc_economy import LBCEconomy

    economy = LBCEconomy()
    economy.initialize()

    wallets = economy.get_all_balances()
    assert_equal(round(wallets["xiaochen"]["balance"], 1), 100.0, "小陈余额")
    assert_equal(round(wallets["zhuguxia"]["balance"], 1), 100.0, "诸葛虾余额")
    assert_equal(round(wallets["qoder"]["balance"], 1), 100.0, "Qoder 余额")
    assert_equal(round(wallets["hermes"]["balance"], 1), 500.0, "Hermes 余额")
    assert_equal(round(wallets["system_pool"]["balance"], 1), 1000.0, "系统池余额")

    total = economy.get_total_supply()
    assert_equal(round(total, 1), 1800.0, "总发行量 1800 LBC")

    print(f"  总发行量: {total} LBC")
    for acc, w in wallets.items():
        print(f"    {acc}: {w['balance']} LBC (可用 {w['available']})")

    _results.append(("4.1 钱包初始化", PASS, ""))
    # 返回 economy 给后续测试复用
    return economy


@test("4.2 SDP 定价引擎")
def test_economy_pricing():
    from core.economy.lbc_economy import LBCEconomy

    economy = LBCEconomy()
    economy.initialize()

    # 正常定价
    price_normal = economy.pricing.price("data_analysis", agent_id="hermes", urgent=False)
    estimate = economy.pricing.estimate("data_analysis", agent_id="hermes", urgent=False)
    print(f"  data_analysis (hermes, 正常): {price_normal:.2f} LBC")
    print(f"    明细: P_base={estimate['p_base']} D={estimate['d_factor']} Q={estimate['q_premium']} U={estimate['u_discount']}")
    assert_true(price_normal > 0, "正常定价应 > 0")

    # 加急定价
    price_urgent = economy.pricing.price("data_analysis", agent_id="hermes", urgent=True)
    print(f"  data_analysis (hermes, 加急): {price_urgent:.2f} LBC")
    assert_true(price_urgent > price_normal, "加急定价应高于正常")

    # SDP 公式: P = P_base × D × Q × U = 10 × 1.0 × 1.0 × 1.0 = 10 (hermes Q=5.0/5.0=1.0)
    expected_base = 10.0  # data_analysis base price
    assert_true(abs(price_normal - expected_base) < 1.0, f"定价应在 {expected_base} 附近")

    _results.append(("4.2 SDP 定价", PASS, ""))


@test("4.3 转账与账本")
def test_economy_transfer():
    from core.economy.lbc_economy import LBCEconomy

    economy = LBCEconomy()
    economy.initialize()

    # 小陈向 Qoder 转账 15 LBC
    ok = economy.transfer("xiaochen", "qoder", 15.0, skill="teaching", description="解答 Python 问题")
    assert_true(ok, "转账应成功")

    xiaochen_w = economy.get_wallet("xiaochen")
    qoder_w = economy.get_wallet("qoder")

    assert_equal(round(xiaochen_w.balance, 1), 85.0, "小陈余额应为 85")
    assert_equal(round(qoder_w.balance, 1), 115.0, "Qoder 余额应为 115")

    # 账本记录 — 取最近一条交易验证
    assert_true(economy.ledger.total_transactions >= 1, f"应有至少1条交易记录，实际={economy.ledger.total_transactions}")
    tx = economy.ledger.get_all()[-1]
    assert_equal(tx.from_account, "xiaochen")
    assert_equal(tx.to_account, "qoder")
    assert_equal(round(tx.amount, 1), 15.0)
    assert_true(tx.verify(), "交易哈希应可验证")

    print(f"  交易: {tx.tx_id} | {tx.from_account} -> {tx.to_account} | {tx.amount} LBC | hash={tx.tx_hash}")
    print(f"  小陈余额: {xiaochen_w.balance} LBC, Qoder 余额: {qoder_w.balance} LBC")

    _results.append(("4.3 转账与账本", PASS, ""))


@test("4.4 解题奖励发放")
def test_economy_reward():
    from core.economy.lbc_economy import LBCEconomy

    economy = LBCEconomy()
    economy.initialize()

    system_pool_before = economy.get_wallet("system_pool").balance

    # 小陈完成一道 hard 题目
    reward = economy.reward_distributor.reward_problem(
        "xiaochen", "hard", economy.get_wallet("xiaochen")
    )
    assert_equal(round(reward, 1), 2.0, "hard 难度奖励 2.0 LBC")

    # 验证余额变化
    xiaochen_w = economy.get_wallet("xiaochen")
    assert_equal(round(xiaochen_w.balance, 1), 102.0, "小陈余额应为 102")

    system_pool_after = economy.get_wallet("system_pool").balance
    assert_equal(round(system_pool_before - system_pool_after, 1), 2.0, "系统池应减少 2.0 LBC")

    print(f"  奖励: +{reward} LBC (hard 难度)")
    print(f"  小陈余额: {xiaochen_w.balance} → {xiaochen_w.balance}")
    print(f"  系统池: {system_pool_before} → {system_pool_after}")

    _results.append(("4.4 解题奖励", PASS, ""))


@test("4.5 市场挂单撮合")
def test_economy_market():
    from core.economy.lbc_economy import LBCEconomy, OrderType

    economy = LBCEconomy()
    economy.initialize()

    # 挂卖单：小陈卖 code 技能，8 LBC/次，3次
    economy.order_book.place_order("xiaochen", OrderType.SELL, "code", 8.0, quantity=3)
    # 挂买单：Qoder 买 code 技能，10 LBC/次，2次
    economy.order_book.place_order("qoder", OrderType.BUY, "code", 10.0, quantity=2)

    # 撮合
    matches = economy.order_book.match("code")
    assert_true(len(matches) >= 1, f"应有撮合，实际={len(matches)}")

    for buy, sell, qty in matches:
        print(f"  撮合: {buy.order_id}(买单 @{buy.amount}) ↔ {sell.order_id}(卖单 @{sell.amount}) ×{qty}")
        assert_true(buy.filled >= qty, "买单应有成交")
        assert_true(sell.filled >= qty, "卖单应有成交")

    # 市场深度
    snapshot = economy.order_book.get_order_book_snapshot("code")
    print(f"  市场深度: bids={len(snapshot['bids'])} asks={len(snapshot['asks'])}")

    _results.append(("4.5 市场撮合", PASS, ""))


@test("4.6 账本完整性验证")
def test_economy_ledger_verify():
    from core.economy.lbc_economy import LBCEconomy

    economy = LBCEconomy()
    economy.initialize()

    # 多笔交易
    economy.transfer("xiaochen", "qoder", 10.0, skill="teaching", description="教学费")
    economy.transfer("qoder", "zhuguxia", 5.0, skill="data_analysis", description="数据分析")
    economy.transfer("hermes", "xiaochen", 20.0, skill="coaching", description="教练指导费")
    economy.reward_distributor.reward_problem("zhuguxia", "medium", economy.get_wallet("zhuguxia"))

    passed, failed = economy.ledger.verify_all()
    assert_equal(failed, 0, "所有交易应通过哈希验证")
    assert_true(passed >= 4, f"应至少4条验证通过交易，实际={passed}")

    print(f"  账本验证: {passed}/{passed + failed} 通过")
    print(f"  总交易数: {economy.ledger.total_transactions}")
    print(f"  总交易额: {economy.ledger.total_volume:.2f} LBC")

    _results.append(("4.6 账本验证", PASS, ""))


# ============================================================
# 测试 5: 全链路集成测试
# ============================================================

@test("5.0 全链路集成: Harness → Orchestrator → Metrics → Emergence → Economy")
def test_integration_full():
    from core.harness.agent_harness import AgentHarness, create_harness
    from core.orchestrator.rl_orchestrator import RLOrchestrator, create_default_agents, AgentCard, AgentType
    from core.observability.metrics_collector import MetricsCollector
    from core.observability.emergence_detector import EmergenceDetector
    from core.economy.lbc_economy import LBCEconomy

    print("  全链路集成测试启动...\n")

    # ==================== 1. 初始化各系统 ====================
    print("  [1/5] 初始化 Harness + Orchestrator + Metrics + Emergence + Economy")
    harness = create_harness(bypass_role=None)
    orch = RLOrchestrator()
    orch.register_agents(create_default_agents())
    metrics = MetricsCollector()
    detector = EmergenceDetector(threshold=0.35, use_v6_model=True)
    economy = LBCEconomy()
    economy.initialize()

    # ==================== 2. 用户请求进入 Harness ====================
    print("  [2/5] Harness: 用户输入过滤")
    user_input = "小陈完成5道死活题，然后和诸葛虾对弈一局，奖励 LBC"
    # 使用白名单内的操作名来测试输入过滤
    result = harness.guard(input_text=user_input, operation="search_file")
    assert_true(result.passed, f"Harness 应通过: violations={result.violations}")
    sanitized_input = result.sanitized_input
    print(f"    输入已净化: {sanitized_input[:60]}...")

    # ==================== 3. Orchestrator 编排任务 ====================
    print("  [3/5] Orchestrator: 编排执行")
    orch_result = orch.orchestrate(sanitized_input)
    dag_info = orch_result["dag"]
    scheduling = orch_result["scheduling"]
    print(f"    子任务: {dag_info['subtask_count']} | 调度: {scheduling['action']} | "
          f"状态: {orch_result['progress']}")

    # 记录指标
    for st in dag_info["subtasks"]:
        agent_id = st["assigned_agent"] or "unknown"
        metrics.record_agent_task(agent_id, success=(st["status"] == "completed"), response_time_ms=150.0)
        metrics.record_agent_message(agent_id, "sent", latency_ms=25.0)

    # ==================== 4. Metrics 采集 ====================
    print("  [4/5] Metrics: 采集指标")
    metrics.record_learning("xiaochen", problems=5, correct=4, games=1, wins=1, domain="围棋")
    metrics.record_learning("zhuguxia", problems=3, correct=3, games=1, wins=0, domain="围棋")
    metrics.record_economy("xiaochen", balance=100.0, earned=2.0)
    metrics.record_economy("zhuguxia", balance=100.0, earned=1.0)

    agg = metrics.get_aggregated_metrics()
    print(f"    Agent 数: {agg['agent_count']}")
    print(f"    网络消息: {agg['network']['total_messages']}")

    # Prometheus 导出
    prom = metrics.export_prometheus()
    assert_true("lobster_agent_messages_total" in prom, "Prometheus 导出应含 agent 指标")
    assert_true("lobster_network_messages_total" in prom, "Prometheus 导出应含网络指标")

    # ==================== 5. Emergence 检测 ====================
    print("  [5/5] Emergence + Economy: 检测涌现并发放奖励")
    event = detector.detect(
        agent_a_view={"死活题", "手筋", "棋感"},
        agent_b_view={"胜率", "AI分析", "蒙特卡洛"},
        agent_a_knowledge={"围棋", "死活题", "定式"},
        agent_b_knowledge={"统计", "蒙特卡洛", "树搜索"},
        dialogue_turns=10,
        participants=["xiaochen", "zhuguxia"],
        new_concepts={"死活AI分析"},
        description="跨域涌现: 围棋 + 算法",
    )
    if event:
        print(f"    涌现事件: E={event.emergence_value:.4f} 类别={event.category.value}")
    else:
        print(f"    未触发涌现 (阈值: {detector.threshold})")

    # ==================== 6. Economy 发放奖励 ====================
    economy.reward_distributor.reward_problem("xiaochen", "hard", economy.get_wallet("xiaochen"))
    economy.reward_distributor.reward_game("xiaochen", "win", economy.get_wallet("xiaochen"))
    economy.reward_distributor.reward_contribution("zhuguxia", "teaching", economy.get_wallet("zhuguxia"))

    # 验证收入（转账前）
    balances_before_tx = economy.get_all_balances()
    assert_true(balances_before_tx["xiaochen"]["balance"] > 100.0,
                f"小陈应有收入，实际={balances_before_tx['xiaochen']['balance']}")
    assert_true(balances_before_tx["zhuguxia"]["balance"] > 100.0,
                f"诸葛虾应有收入，实际={balances_before_tx['zhuguxia']['balance']}")

    # 转账
    economy.transfer("xiaochen", "zhuguxia", 5.0, skill="coaching", description="对弈学费")

    balances = economy.get_all_balances()
    print(f"    小陈余额: {balances['xiaochen']['balance']} LBC")
    print(f"    诸葛虾余额: {balances['zhuguxia']['balance']} LBC")
    print(f"    系统池余额: {balances['system_pool']['balance']} LBC")

    market_summary = economy.get_market_summary()
    print(f"    市场: 交易{market_summary['total_transactions']}笔, "
          f"总额{market_summary['total_volume']} LBC")

    # 验证全链路完整性
    assert_true(economy.ledger.total_transactions >= 1, "账本应有记录")
    passed, failed = economy.ledger.verify_all()
    assert_equal(failed, 0, "全部交易应可验证")

    # 保存整合后的指标快照到中间产物目录
    snapshot_path = TEMP_DIR / "integration_snapshot.json"
    snapshot_data = {
        "timestamp": datetime.now().isoformat(),
        "harness": {"passed": result.passed, "violations": result.violations},
        "orchestrator": {
            "subtasks": dag_info["subtask_count"],
            "action": scheduling["action"],
            "progress": orch_result["progress"]["progress_pct"],
        },
        "metrics": agg,
        "emergence": {
            "total_events": detector.get_stats()["total_events"],
            "event": {
                "value": event.emergence_value,
                "category": event.category.value,
            } if event else None,
        },
        "economy": {
            "balances": {k: v["balance"] for k, v in balances.items()},
            "total_transactions": economy.ledger.total_transactions,
            "total_volume": economy.ledger.total_volume,
        },
    }
    with open(snapshot_path, "w", encoding="utf-8") as f:
        json.dump(snapshot_data, f, ensure_ascii=False, indent=2)
    print(f"\n  集成快照已保存: {snapshot_path}")

    _results.append(("5.0 全链路集成", PASS, ""))


# ============================================================
# 入口
# ============================================================

def main():
    print(f"{'=' * 70}")
    print(f"  四大核心模块集成测试")
    print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  仓库: {REPO_ROOT}")
    print(f"  中间产物: {TEMP_DIR}")
    print(f"{'=' * 70}")

    # ---- 测试 1: Harness ----
    test_harness_normal()
    test_harness_dangerous()
    test_harness_sensitive()
    test_harness_bypass()

    # ---- 测试 2: Orchestrator ----
    test_orchestrator_decompose()
    test_orchestrator_match()
    test_orchestrator_qlearning()

    # ---- 测试 3: Emergence ----
    test_emergence_v3()
    test_emergence_detect()

    # ---- 测试 4: Economy ----
    test_economy_wallets()
    test_economy_pricing()
    test_economy_transfer()
    test_economy_reward()
    test_economy_market()
    test_economy_ledger_verify()

    # ---- 测试 5: 全链路集成 ----
    test_integration_full()

    # ---- 汇总 ----
    ok = summary()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
