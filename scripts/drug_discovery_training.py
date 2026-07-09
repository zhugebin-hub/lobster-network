#!/usr/bin/env python3
"""
小龙虾网络 - 新药创制科学智能体 CLI V1.0
食物过敏防治药物研制 · 6节点联合研究

用法:
  python3 scripts/drug_discovery_training.py --train <student>     # 训练指定学员
  python3 scripts/drug_discovery_training.py --train-all            # 全员训练
  python3 scripts/drug_discovery_training.py --target <allergen>    # 靶点识别
  python3 scripts/drug_discovery_training.py --screen <target>      # 先导化合物筛选
  python3 scripts/drug_discovery_training.py --dock <compound> <target>  # 分子对接
  python3 scripts/drug_discovery_training.py --admet <compound>     # ADMET预测
  python3 scripts/drug_discovery_training.py --safety <compound> <target>  # 安全评估
  python3 scripts/drug_discovery_training.py --trial <phase> <allergen>    # 临床试验设计
  python3 scripts/drug_discovery_training.py --pathway <allergen>   # 通路分析
  python3 scripts/drug_discovery_training.py --immuno <method> <allergen>  # 免疫疗法设计
  python3 scripts/drug_discovery_training.py --report               # 全员研究报告
  python3 scripts/drug_discovery_training.py --all                  # 完整流程
  python3 scripts/drug_discovery_training.py --join-network         # 加入联合研究
"""

import sys
import os
import json
import argparse

# 路径设置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
PROBLEMS_DIR = os.path.join(BASE_DIR, 'domains', 'learning', 'problems')
TRAINERS_DIR = os.path.join(BASE_DIR, 'domains', 'learning', 'trainers')

sys.path.insert(0, PROBLEMS_DIR)
sys.path.insert(0, TRAINERS_DIR)

from drug_discovery_engine import DrugDiscoveryEngine
from drug_discovery_trainer import DrugDiscoveryTrainer, STUDENT_CONFIG


def cmd_train(args):
    """训练指定学员"""
    trainer = DrugDiscoveryTrainer()
    if args.train not in STUDENT_CONFIG:
        print(f"❌ 未知学员: {args.train}")
        print(f"   可选: {', '.join(STUDENT_CONFIG.keys())}")
        return

    student = STUDENT_CONFIG[args.train]
    print("=" * 60)
    print(f"🦞 新药创制训练 - {student['name']}({student['type']})")
    print(f"   节点: {student['node']} | 重点: {', '.join(student['focus'])}")
    print("=" * 60)

    result = trainer.execute_research(args.train)

    print(f"\n📊 训练结果:")
    print(f"   答题: {result['correct']}/{result['total']} (正确率: {result['accuracy']:.1%})")
    print(f"   研究任务: {len(result['research_results'])}项")

    print(f"\n🔬 研究成果:")
    for r in result['research_results']:
        icon = "✅" if r['status'] == 'success' else "❌"
        print(f"   {icon} {r['task']}: {r.get('result_summary', r.get('error', ''))}")

    # 错题分析
    wrong = [p for p in result['problem_results'] if p['status'] == 'wrong']
    if wrong:
        print(f"\n❌ 错题分析 ({len(wrong)}题):")
        for p in wrong:
            print(f"   {p['id']} [{p['type']}] 难度:{p['difficulty']}")

    # 保存状态
    state_dir = os.path.join(TRAINERS_DIR, 'state')
    os.makedirs(state_dir, exist_ok=True)
    state_file = os.path.join(state_dir, f'{args.train}_drug_state.json')
    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n💾 状态已保存: {state_file}")


def cmd_train_all(args):
    """全员训练"""
    trainer = DrugDiscoveryTrainer()
    print("=" * 60)
    print("🦞 小龙虾网络 - 新药创制全员联合训练")
    print("=" * 60)

    for sid in STUDENT_CONFIG:
        print(f"\n{'─' * 40}")
        cmd_train(argparse.Namespace(train=sid))


def cmd_target(args):
    """靶点识别"""
    engine = DrugDiscoveryEngine()
    allergen = args.target or '花生'

    print("=" * 60)
    print(f"🎯 靶点识别 - 过敏原: {allergen}")
    print("=" * 60)

    # 分析所有通路
    pathways = ['IgE', 'IL-4Rα', 'TSLP', 'IL-33', 'FOXP3', 'FcεRI']
    print(f"\n{'通路':<12} {'靶点名':<20} {'综合评分':<10} {'新颖性':<8} {'可成药':<8} {'临床':<8} {'市场':<8} {'推荐':<10}")
    print("─" * 90)

    best = None
    best_score = 0
    for pw in pathways:
        result = engine.identify_drug_target(allergen=allergen, pathway=pw)
        s = result['scores']
        print(f"{pw:<12} {result['target_info']['name']:<20} {result['overall_score']:<10.3f} {s['靶点新颖性']:<8.3f} {s['可成药性']:<8.3f} {s['临床可行性']:<8.3f} {s['市场潜力']:<8.3f} {result['recommendation']:<10}")
        if result['overall_score'] > best_score:
            best_score = result['overall_score']
            best = result

    print(f"\n🏆 最佳靶点推荐: {best['target_info']['name']} (通路: {best['target']})")
    print(f"   综合评分: {best['overall_score']:.3f}")
    print(f"   机制: {best['target_info']['mechanism']}")
    print(f"   已有药物: {', '.join(best['target_info']['examples'])}")
    print(f"   临床阶段: {best['target_info']['clinical_stage']}")
    print(f"   策略: {best['strategy']}")


def cmd_screen(args):
    """先导化合物筛选"""
    engine = DrugDiscoveryEngine()
    target = args.screen or 'IgE'

    print("=" * 60)
    print(f"🔍 先导化合物虚拟筛选 - 靶点: {target}")
    print("=" * 60)

    result = engine.screen_lead_compounds(target=target, max_results=10)

    print(f"\n筛选标准: {result['screening_criteria']['rules']}")
    print(f"分子量范围: {result['screening_criteria']['mw_range']}")
    print(f"logP范围: {result['screening_criteria']['logp_range']}")
    print(f"\n筛选结果: {result['total_screened']}个 → {result['total_passed']}个通过 ({result['pass_rate']:.0%})")

    print(f"\n{'ID':<10} {'名称':<16} {'类药性':<8} {'MW':<8} {'logP':<6} {'HBD':<5} {'HBA':<5} {'TPSA':<8} {'类别':<20}")
    print("─" * 100)
    for c in result['top_compounds']:
        print(f"{c['compound_id']:<10} {c['name']:<16} {c['drug_likeness_score']:<8.3f} {c['mw']:<8.1f} {c['logp']:<6.1f} {c['hbd']:<5} {c['hba']:<5} {c['tpsa']:<8.1f} {c['class']:<20}")


def cmd_dock(args):
    """分子对接"""
    engine = DrugDiscoveryEngine()
    compound = args.dock[0] if isinstance(args.dock, list) else args.dock
    target = args.dock_target or 'IgE'

    print("=" * 60)
    print(f"🧬 分子对接评分 - {compound} → {target}")
    print("=" * 60)

    result = engine.molecular_docking_score(compound_name=compound, target=target)

    if 'error' in result:
        print(f"❌ {result['error']}")
        print(f"   可用化合物: {', '.join(c['name'] for c in engine.get_compound_library())}")
        return

    print(f"\n化合物: {result['compound']['name']} ({result['compound']['id']})")
    print(f"类别: {result['compound']['class']}")
    print(f"靶点: {result['target']['name']} ({result['target']['pathway']})")
    print(f"结合位点: {result['target']['binding_site']}")
    print(f"\n结合自由能: {result['binding_energy']} {result['binding_energy_unit']}")
    print(f"估算Ki: {result['estimated_ki']} {result['ki_unit']}")
    print(f"预测氢键数: {result['predicted_hbonds']}")
    print(f"疏水接触数: {result['hydrophobic_contacts']}")
    print(f"关键残基: {', '.join(result['key_residues'])}")
    print(f"评级: {result['grade']}")
    print(f"置信度: {result['confidence']:.1%}")


def cmd_admet(args):
    """ADMET预测"""
    engine = DrugDiscoveryEngine()
    compound = args.admet

    print("=" * 60)
    print(f"💊 ADMET预测 - {compound}")
    print("=" * 60)

    result = engine.predict_admet(compound_name=compound)

    if 'error' in result:
        print(f"❌ {result['error']}")
        return

    print(f"\n分子参数: MW={result['parameters']['mw']}, logP={result['parameters']['logp']}, HBD={result['parameters']['hbd']}, HBA={result['parameters']['hba']}, TPSA={result['parameters']['tpsa']}")

    print(f"\n1️⃣ 吸收 (Absorption):")
    a = result['absorption']
    print(f"   口服生物利用度: {a['oral_bioavailability']:.1%} ({a['rating']})")
    print(f"   Caco-2渗透性: {a['caco2_permeability']} {a['caco2_unit']}")

    print(f"\n2️⃣ 分布 (Distribution):")
    d = result['distribution']
    print(f"   血浆蛋白结合率: {d['plasma_protein_binding']:.1%}")
    print(f"   血脑屏障穿透: {d['bbb_penetration']:.1%}")
    print(f"   表观分布容积: {d['vd']} {d['vd_unit']} ({d['rating']})")

    print(f"\n3️⃣ 代谢 (Metabolism):")
    m = result['metabolism']
    print(f"   CYP3A4底物: {m['cyp3a4_substr']:.1%}")
    print(f"   CYP2D6底物: {m['cyp2d6_substr']:.1%}")
    print(f"   代谢稳定性: {m['metabolic_stability']:.1%} ({m['rating']})")

    print(f"\n4️⃣ 排泄 (Excretion):")
    e = result['excretion']
    print(f"   清除率: {e['clearance']} {e['clearance_unit']}")
    print(f"   半衰期: {e['half_life']}h ({e['rating']})")

    print(f"\n5️⃣ 毒性 (Toxicity):")
    t = result['toxicity']
    print(f"   hERG抑制风险: {t['herg_inhibition_risk']:.1%}")
    print(f"   肝毒性风险: {t['hepatotoxicity_risk']:.1%}")
    print(f"   Ames致突变性: {t['ames_mutagenicity']:.1%}")
    print(f"   安全性评分: {t['safety_score']:.1%} ({t['rating']})")

    print(f"\n📊 ADMET综合评分: {result['overall_admet_score']:.3f}")


def cmd_safety(args):
    """药物安全评估"""
    engine = DrugDiscoveryEngine()
    parts = args.safety.split()
    compound = parts[0] if parts else '龙虾素-A'
    target = parts[1] if len(parts) > 1 else 'IgE'
    group = parts[2] if len(parts) > 2 else '儿童'

    print("=" * 60)
    print(f"🛡️ 药物安全评估 - {compound} / {target} / {group}")
    print("=" * 60)

    result = engine.evaluate_drug_safety(compound_name=compound, target=target, patient_group=group)

    print(f"\n靶点: {result['target_info']['name']} ({result['target_info']['drug_class']})")
    print(f"患者群体: {result['patient_group']} (风险等级: {result['group_specific_risk']['风险等级']})")
    print(f"特殊注意: {result['group_specific_risk']['特殊注意']}")

    print(f"\n⚠️ 不良事件:")
    for ae in result['adverse_events']:
        print(f"   • {ae}")

    print(f"\n🔗 药物相互作用:")
    for di in result['drug_interactions']:
        print(f"   • {di['drug']}: {di['risk']} (严重性: {di['severity']})")

    print(f"\n🚫 禁忌症:")
    for c in result['contraindications']:
        print(f"   • {c}")

    if result['boxed_warning']:
        print(f"\n⬛ 黑框警告: {result['boxed_warning']}")

    print(f"\n📋 监测计划:")
    for i, m in enumerate(result['monitoring_plan'], 1):
        print(f"   {i}. {m}")

    print(f"\n安全评分: {result['safety_score']:.3f} → {result['recommendation']}")


def cmd_trial(args):
    """临床试验设计"""
    engine = DrugDiscoveryEngine()
    parts = args.trial.split()
    phase = parts[0] if parts else 'II'
    allergen = parts[1] if len(parts) > 1 else '花生'
    target = parts[2] if len(parts) > 2 else 'IgE'

    print("=" * 60)
    print(f"🏥 临床试验设计 - {phase}期 / {allergen} / {target}")
    print("=" * 60)

    patient_count = {'I': 40, 'II': 120, 'III': 500}.get(phase, 120)
    duration = {'I': 12, 'II': 24, 'III': 52}.get(phase, 24)

    result = engine.design_clinical_trial(target=target, phase=phase, allergen=allergen,
                                           patient_count=patient_count, duration_weeks=duration)

    print(f"\n试验ID: {result['trial_id']}")
    print(f"阶段: {result['phase_info']['name']} - {result['phase_info']['purpose']}")
    print(f"设计: {result['design']['type']}")
    print(f"随机化: {result['design']['randomization']}")
    print(f"盲法: {result['design']['blinding']}")

    print(f"\n分组:")
    for arm in result['design']['arms']:
        print(f"   {arm['name']}: {arm['size']}例")

    print(f"\n总样本量: {result['patient_count']}例 (每组≈{result['estimated_n_per_arm']}例)")
    print(f"试验周期: {result['duration_weeks']}周")
    print(f"样本量依据: {result['sample_size_justification']}")

    print(f"\n入组标准:")
    for inc in result['inclusion_criteria']:
        print(f"   ✅ {inc}")

    print(f"\n排除标准:")
    for exc in result['exclusion_criteria']:
        print(f"   ❌ {exc}")

    print(f"\n评估时间点: {' → '.join(result['timepoints'])}")

    print(f"\n主要终点:")
    for ep in result['endpoints']['primary']:
        print(f"   ★ {ep}")

    print(f"\n次要终点:")
    for ep in result['endpoints']['secondary']:
        print(f"   ○ {ep}")

    print(f"\n统计方法: {', '.join(result['statistical_methods'])}")

    print(f"\n安全监察:")
    for sm in result['safety_monitoring']:
        print(f"   🛡️ {sm}")

    print(f"\n监管路径: {result['regulatory_pathway']}")


def cmd_pathway(args):
    """通路分析"""
    engine = DrugDiscoveryEngine()
    allergen = args.pathway or '花生'

    print("=" * 60)
    print(f"🧠 食物过敏通路分析 - {allergen}")
    print("=" * 60)

    result = engine.food_allergy_pathway_analysis(allergen=allergen)

    ai = result['allergen_info']
    print(f"\n过敏原: {allergen} ({ai.get('scientific', '?')})")
    print(f"主要致敏蛋白: {', '.join(ai.get('major_allergens', []))}")
    print(f"患病率: {ai.get('prevalence', '?')}")
    print(f"严重性: {ai.get('severity', '?')}")
    print(f"自然耐受率: {ai.get('persistence', '?')}")
    print(f"交叉反应: {', '.join(ai.get('cross_reactivity', []))}")

    for pname, pdata in result['pathways'].items():
        print(f"\n{'─' * 40}")
        print(f"📋 {pname}")
        print(f"   描述: {pdata['description']}")
        print(f"   时间线: {pdata['timeline']}")
        print(f"   步骤:")
        for step in pdata['steps']:
            print(f"     {step}")
        print(f"   关键分子: {', '.join(pdata['key_molecules'])}")
        print(f"   干预位点: {', '.join(pdata['intervention_points'])}")

    print(f"\n{'─' * 40}")
    print(f"🤝 联合策略推荐:")
    for cs in result['combination_strategies']:
        print(f"\n   策略: {cs['strategy']}")
        print(f"   原理: {cs['rationale']}")
        print(f"   证据: {cs['evidence']}")
        print(f"   预期协同: {cs['expected_synergy']:.0%}")

    print(f"\n🏆 推荐方案: {result['recommended_approach']}")


def cmd_immuno(args):
    """免疫疗法设计"""
    engine = DrugDiscoveryEngine()
    parts = args.immuno.split()
    method = parts[0] if parts else 'OIT'
    allergen = parts[1] if len(parts) > 1 else '花生'

    print("=" * 60)
    print(f"💉 免疫疗法设计 - {method} / {allergen}")
    print("=" * 60)

    result = engine.design_immunotherapy(allergen=allergen, method=method, patient_age=8, severity="中度")

    mi = result['method_info']
    print(f"\n方法: {mi['name']} ({mi['full_name']})")
    print(f"给药途径: {mi['route']}")
    print(f"机制: {mi['mechanism']}")
    print(f"批准状态: {mi.get('approved', '?')}")

    print(f"\n✅ 优势:")
    for adv in mi['advantages']:
        print(f"   • {adv}")

    print(f"\n⚠️ 劣势:")
    for dis in mi['disadvantages']:
        print(f"   • {dis}")

    print(f"\n📋 剂量方案:")
    for k, v in result['protocol'].items():
        print(f"   {k}: {v}")

    print(f"\n安全特征:")
    sp = result['safety_profile']
    print(f"   主要风险: {sp.get('主要风险', '?')}")
    print(f"   严重AE: {sp.get('严重AE', '?')}")
    print(f"   禁忌: {sp.get('禁忌', '?')}")

    print(f"\n年龄适配: {result['age_recommendation']}")
    print(f"严重程度匹配: {result['severity_match']}")
    print(f"预期疗效: {result['expected_efficacy']:.1%}")

    print(f"\n监测方案:")
    for m in result['monitoring']:
        print(f"   📊 {m}")

    print(f"\n成功标准:")
    for sc in result['success_criteria']:
        print(f"   ✓ {sc}")


def cmd_report(args):
    """全员研究报告"""
    trainer = DrugDiscoveryTrainer()

    print("=" * 60)
    print("🦞 小龙虾网络 - 新药创制科学智能体全员研究报告")
    print("   食物过敏防治药物研制 · 6节点联合研究")
    print("=" * 60)

    report = trainer.get_research_report()

    s = report['summary']
    print(f"\n📊 总览:")
    print(f"   参与节点: {s['total_students']}个 (覆盖{s['total_nodes']}台服务器)")
    print(f"   平均正确率: {s['avg_accuracy']:.1%}")
    print(f"   研究任务总数: {s['total_research_tasks']}项")
    print(f"   答题总数: {s['total_problems_solved']}题")
    print(f"   引擎方法: {s['engine_methods']}大科学方法")
    print(f"   题库总量: {s['total_problems']}题")

    print(f"\n{'学员':<12} {'类型':<8} {'节点':<18} {'正确率':<8} {'答题':<6} {'研究':<6} {'重点'}")
    print("─" * 100)
    for stu in report['students']:
        focus_str = '/'.join(stu['focus'][:3])
        print(f"{stu['name']:<12} {stu['type']:<8} {stu['node']:<18} {stu['accuracy']:<8.0%} {stu['problems_solved']:<6} {stu['research_tasks_done']:<6} {focus_str}")

    print(f"\n🔬 各节点研究成果:")
    for stu in report['students']:
        if stu['research_summaries']:
            print(f"\n   【{stu['name']}】({stu['node']}):")
            for summary in stu['research_summaries']:
                print(f"     • {summary}")


def cmd_join_network(args):
    """加入联合研究"""
    print("=" * 60)
    print("🦞 小龙虾网络 - 新药创制科学智能体联合研究")
    print("   食物过敏防治药物研制")
    print("=" * 60)

    print("\n📡 网络节点状态:")
    nodes = [
        ('诸葛马', '47.93.6.57', '教练型', '药物安全+监管+高级评审'),
        ('诸葛虾', '60.205.139.51', '加速型', '分子对接+ADMET+先导筛选'),
        ('小陈', '121.43.80.231', '稳健型', '靶点识别+过敏机制'),
        ('qoder', '192.168.1.161', '技术型', 'ADMET计算+虚拟筛选'),
        ('小薇', 'local', '实战型', '免疫疗法+临床执行'),
        ('诸葛斌', 'local', '研究型', '全流程+临床试验设计'),
    ]

    print(f"{'节点':<10} {'服务器':<18} {'类型':<8} {'研究方向'}")
    print("─" * 70)
    for name, server, ntype, focus in nodes:
        print(f"{name:<10} {server:<18} {ntype:<8} {focus}")

    print(f"\n🔬 8大科学方法:")
    methods = [
        ('1', '靶点识别', 'identify_drug_target', '基于过敏通路推荐药物靶点'),
        ('2', '先导化合物筛选', 'screen_lead_compounds', 'Lipinski五规则+类药性评估'),
        ('3', '分子对接评分', 'molecular_docking_score', '结合自由能+关键残基分析'),
        ('4', 'ADMET预测', 'predict_admet', '吸收/分布/代谢/排泄/毒性五维'),
        ('5', '药物安全评估', 'evaluate_drug_safety', '副作用/禁忌/相互作用'),
        ('6', '临床试验设计', 'design_clinical_trial', 'I/II/III期方案生成'),
        ('7', '通路分析', 'food_allergy_pathway_analysis', 'IgE/Th2/口服耐受全景'),
        ('8', '免疫疗法设计', 'design_immunotherapy', 'OIT/SLIT/EPIT/联合方案'),
    ]
    for num, name, method, desc in methods:
        print(f"   [{num}] {name}: {desc}")

    print(f"\n📚 题库体系:")
    print(f"   Phase 1: 药物发现基础与食物过敏机制 (20题)")
    print(f"   Phase 2: 先导化合物筛选与ADMET评估 (20题)")
    print(f"   Phase 3: 临床试验设计与免疫疗法实例验证 (20题)")
    print(f"   合计: 60题")

    print(f"\n🚀 快速开始:")
    print(f"   python3 scripts/drug_discovery_training.py --train zhugebin-001  # 训练")
    print(f"   python3 scripts/drug_discovery_training.py --target 花生          # 靶点识别")
    print(f"   python3 scripts/drug_discovery_training.py --screen IgE           # 化合物筛选")
    print(f"   python3 scripts/drug_discovery_training.py --dock 龙虾素-A IgE   # 分子对接")
    print(f"   python3 scripts/drug_discovery_training.py --admet 龙虾素-A      # ADMET")
    print(f"   python3 scripts/drug_discovery_training.py --trial II 花生       # 临床设计")
    print(f"   python3 scripts/drug_discovery_training.py --pathway 花生        # 通路分析")
    print(f"   python3 scripts/drug_discovery_training.py --immuno OIT 花生     # 免疫疗法")
    print(f"   python3 scripts/drug_discovery_training.py --report              # 全员报告")
    print(f"   python3 scripts/drug_discovery_training.py --all                 # 完整流程")


def cmd_all(args):
    """完整流程"""
    print("=" * 60)
    print("🦞 新药创制科学智能体 - 完整研究流程")
    print("   食物过敏防治药物研制 · 全流程实例验证")
    print("=" * 60)

    engine = DrugDiscoveryEngine()

    # Step 1: 通路分析
    print("\n" + "─" * 60)
    print("Step 1: 食物过敏通路分析")
    pathway = engine.food_allergy_pathway_analysis(allergen="花生")
    print(f"  过敏原: {pathway['allergen']} ({pathway['allergen_info']['severity']})")
    print(f"  三大通路: {', '.join(pathway['pathways'].keys())}")
    print(f"  推荐联合策略: {pathway['recommended_approach']}")

    # Step 2: 靶点识别
    print("\n" + "─" * 60)
    print("Step 2: 靶点识别")
    best_target = None
    best_score = 0
    for pw in ['IgE', 'IL-4Rα', 'TSLP', 'IL-33', 'FOXP3']:
        t = engine.identify_drug_target(allergen="花生", pathway=pw)
        print(f"  {pw}: {t['overall_score']:.3f} ({t['recommendation']})")
        if t['overall_score'] > best_score:
            best_score = t['overall_score']
            best_target = t
    print(f"  → 最佳靶点: {best_target['target_info']['name']} ({best_target['overall_score']:.3f})")

    # Step 3: 先导化合物筛选
    print("\n" + "─" * 60)
    print("Step 3: 先导化合物筛选")
    screening = engine.screen_lead_compounds(target=best_target['target'], max_results=3)
    print(f"  筛选: {screening['total_screened']} → {screening['total_passed']}通过 ({screening['pass_rate']:.0%})")
    best_compound = screening['top_compounds'][0]
    print(f"  → 最佳先导: {best_compound['name']} (类药性: {best_compound['drug_likeness_score']:.3f})")

    # Step 4: 分子对接
    print("\n" + "─" * 60)
    print("Step 4: 分子对接评分")
    docking = engine.molecular_docking_score(compound_name=best_compound['name'], target=best_target['target'])
    print(f"  {docking['compound']['name']} → {docking['target']['name']}")
    print(f"  结合自由能: {docking['binding_energy']} kcal/mol ({docking['grade']})")
    print(f"  估算Ki: {docking['estimated_ki']} μM")

    # Step 5: ADMET预测
    print("\n" + "─" * 60)
    print("Step 5: ADMET预测")
    admet = engine.predict_admet(compound_name=best_compound['name'])
    print(f"  口服生物利用度: {admet['absorption']['oral_bioavailability']:.1%}")
    print(f"  半衰期: {admet['excretion']['half_life']}h")
    print(f"  安全性: {admet['toxicity']['safety_score']:.1%} ({admet['toxicity']['rating']})")
    print(f"  ADMET综合: {admet['overall_admet_score']:.3f}")

    # Step 6: 安全评估
    print("\n" + "─" * 60)
    print("Step 6: 药物安全评估")
    safety = engine.evaluate_drug_safety(compound_name=best_compound['name'], target=best_target['target'], patient_group="儿童")
    print(f"  安全评分: {safety['safety_score']:.3f} → {safety['recommendation']}")
    print(f"  主要风险: {', '.join(safety['adverse_events'][:2])}")

    # Step 7: 临床试验设计
    print("\n" + "─" * 60)
    print("Step 7: 临床试验设计")
    trial = engine.design_clinical_trial(target=best_target['target'], phase="II", allergen="花生", patient_count=120, duration_weeks=24)
    print(f"  试验: {trial['trial_id']}")
    print(f"  设计: {trial['design']['type']}")
    print(f"  主要终点: {trial['endpoints']['primary'][0]}")
    print(f"  样本量: {trial['patient_count']}例")

    # Step 8: 免疫疗法
    print("\n" + "─" * 60)
    print("Step 8: 免疫疗法设计")
    immuno = engine.design_immunotherapy(allergen="花生", method="生物制剂联合")
    print(f"  方法: {immuno['method_info']['name']}")
    print(f"  预期疗效: {immuno['expected_efficacy']:.1%}")
    # 取第一个protocol项作为摘要
    first_protocol_key = list(immuno['protocol'].keys())[0] if immuno['protocol'] else 'N/A'
    print(f"  {first_protocol_key}: {immuno['protocol'].get(first_protocol_key, 'N/A')}")

    # 全员训练
    print("\n" + "─" * 60)
    print("Step 9: 全员联合训练")
    trainer = DrugDiscoveryTrainer()
    report = trainer.get_research_report()
    s = report['summary']
    print(f"  参与节点: {s['total_students']}个")
    print(f"  平均正确率: {s['avg_accuracy']:.1%}")
    print(f"  研究任务: {s['total_research_tasks']}项")
    print(f"  答题: {s['total_problems_solved']}题")

    print("\n" + "=" * 60)
    print("✅ 新药创制科学智能体完整流程验证完成！")
    print(f"   过敏原: 花生 | 靶点: {best_target['target_info']['name']} | 先导: {best_compound['name']}")
    print(f"   对接: {docking['binding_energy']} kcal/mol | ADMET: {admet['overall_admet_score']:.3f}")
    print(f"   安全: {safety['safety_score']:.3f} | 临床: {trial['trial_id']}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='🦞 小龙虾网络 - 新药创制科学智能体 (食物过敏防治药物研制)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --train zhugebin-001          # 训练诸葛斌
  %(prog)s --train-all                    # 全员训练
  %(prog)s --target 花生                   # 靶点识别
  %(prog)s --screen IgE                   # 先导化合物筛选
  %(prog)s --dock 龙虾素-A IgE            # 分子对接
  %(prog)s --admet 龙虾素-A               # ADMET预测
  %(prog)s --safety 龙虾素-A IgE 儿童     # 安全评估
  %(prog)s --trial II 花生 IgE            # 临床试验设计
  %(prog)s --pathway 花生                  # 通路分析
  %(prog)s --immuno OIT 花生              # 免疫疗法设计
  %(prog)s --report                       # 全员报告
  %(prog)s --all                          # 完整流程
  %(prog)s --join-network                 # 加入联合研究
"""
    )

    parser.add_argument('--train', metavar='STUDENT', help='训练指定学员')
    parser.add_argument('--train-all', action='store_true', help='全员训练')
    parser.add_argument('--target', metavar='ALLERGEN', help='靶点识别 (过敏原)')
    parser.add_argument('--screen', metavar='TARGET', help='先导化合物筛选 (靶点)')
    parser.add_argument('--dock', metavar='COMPOUND', help='分子对接 (化合物名)')
    parser.add_argument('--dock-target', metavar='TARGET', default='IgE', help='对接靶点 (默认IgE)')
    parser.add_argument('--admet', metavar='COMPOUND', help='ADMET预测 (化合物名)')
    parser.add_argument('--safety', metavar='ARGS', help='安全评估 (化合物 靶点 群体)')
    parser.add_argument('--trial', metavar='ARGS', help='临床试验设计 (期 过敏原 靶点)')
    parser.add_argument('--pathway', metavar='ALLERGEN', help='通路分析 (过敏原)')
    parser.add_argument('--immuno', metavar='ARGS', help='免疫疗法 (方法 过敏原)')
    parser.add_argument('--report', action='store_true', help='全员研究报告')
    parser.add_argument('--all', action='store_true', help='完整流程')
    parser.add_argument('--join-network', action='store_true', help='加入联合研究')

    args = parser.parse_args()

    if args.train:
        cmd_train(args)
    elif args.train_all:
        cmd_train_all(args)
    elif args.target:
        cmd_target(args)
    elif args.screen:
        cmd_screen(args)
    elif args.dock:
        cmd_dock(args)
    elif args.admet:
        cmd_admet(args)
    elif args.safety:
        cmd_safety(args)
    elif args.trial:
        cmd_trial(args)
    elif args.pathway:
        cmd_pathway(args)
    elif args.immuno:
        cmd_immuno(args)
    elif args.report:
        cmd_report(args)
    elif args.all:
        cmd_all(args)
    elif args.join_network:
        cmd_join_network(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
