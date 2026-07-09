#!/usr/bin/env python3
"""
食物过敏防治药物研制科学智能体 · 融合集成入口
====================================================
将学习模块(engine/trainer/problems) + 项目文档(README/research-plan/quick-start/protocol)
+ 仪表盘(dashboard) + 研究数据(data) + 研究报告(reports) 融合为统一系统

用法:
  python3 domains/drug-discovery/fusion.py --full        # 全流程融合运行
  python3 domains/drug-discovery/fusion.py --research     # 仅研究流程
  python3 domains/drug-discovery/fusion.py --train        # 仅学习训练
  python3 domains/drug-discovery/fusion.py --report       # 生成报告
  python3 domains/drug-discovery/fusion.py --status       # 查看项目状态
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DOMAIN_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / 'domains' / 'learning' / 'problems'))
sys.path.insert(0, str(PROJECT_ROOT / 'domains' / 'learning' / 'trainers'))


class DrugDiscoveryFusion:
    """药物发现项目融合管理器"""

    def __init__(self):
        self.engine = None
        self.trainer = None
        self.domain_dir = DOMAIN_DIR
        self.data_dir = DOMAIN_DIR / 'data'
        self.reports_dir = DOMAIN_DIR / 'reports'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def load_engine(self):
        """加载科学智能体引擎"""
        from drug_discovery_engine import DrugDiscoveryEngine
        self.engine = DrugDiscoveryEngine()
        print("  [OK] 引擎已加载: drug_discovery_engine.py")
        return self.engine

    def load_trainer(self):
        """加载训练器"""
        from drug_discovery_trainer import DrugDiscoveryTrainer
        self.trainer = DrugDiscoveryTrainer()
        print("  [OK] 训练器已加载: drug_discovery_trainer.py")
        return self.trainer

    # ========== 研究流程 ==========

    def run_research(self):
        """运行完整研究流程"""
        print("\n" + "=" * 60)
        print("  食物过敏防治药物研制 · 全流程研究")
        print("=" * 60)

        engine = self.load_engine()
        allergens = list(engine.allergens.keys())
        target_pathways = list(engine.targets.keys())

        # Phase 1: 通路分析 + 靶点评分
        print("\n  [Phase 1] 知识构建")
        print(f"  - 过敏原: {len(allergens)}种")
        print(f"  - 靶点: {len(target_pathways)}个")

        pathway_results = {}
        for allergen in allergens:
            pathway = engine.food_allergy_pathway_analysis(allergen)
            pathway_results[allergen] = {
                'severity': pathway['allergen_info'].get('severity', ''),
                'recommended': pathway['recommended_approach'],
                'strategies': [s['strategy'] for s in pathway['combination_strategies']]
            }

        target_scores = {}
        for tp in target_pathways:
            result = engine.identify_drug_target(allergen='花生', pathway=tp)
            target_scores[tp] = {
                'name': result['target_info']['name'],
                'overall': result['overall_score'],
                'recommendation': result['recommendation'],
                'clinical_stage': result['target_info']['clinical_stage']
            }

        # Phase 2: 虚拟筛选 + 对接 + ADMET
        print("\n  [Phase 2] 计算筛选")
        screening = engine.screen_lead_compounds(target='IgE', max_results=10)
        print(f"  - 筛选: {screening['total_screened']} → {screening['total_passed']} 通过")

        dockings = []
        for lead in screening['top_compounds']:
            best_dock = None
            best_target = None
            for tp in target_pathways:
                dock = engine.molecular_docking_score(compound_name=lead['name'], target=tp)
                if best_dock is None or dock['binding_energy'] < best_dock['binding_energy']:
                    best_dock = dock
                    best_target = tp

            admet = engine.predict_admet(compound_name=lead['name'])
            safety = engine.evaluate_drug_safety(compound_name=lead['name'], target=best_target)

            dockings.append({
                'compound': lead['name'],
                'best_target': best_target,
                'binding_energy': best_dock['binding_energy'],
                'grade': best_dock['grade'],
                'ki': best_dock['estimated_ki'],
                'admet_score': admet['overall_admet_score'],
                'safety_score': safety['safety_score'],
                'drug_likeness': lead['drug_likeness_score']
            })

        dockings.sort(key=lambda x: x['binding_energy'])

        # Phase 3: 临床设计 + 免疫疗法
        print("\n  [Phase 3] 评估与临床设计")
        trials = {}
        for allergen in allergens:
            trial = engine.design_clinical_trial(
                target='IL-4Rα', phase='II', allergen=allergen,
                patient_count=120, duration_weeks=24
            )
            trials[allergen] = {
                'trial_id': trial['trial_id'],
                'design': trial['design']['type'],
                'sample': trial['patient_count']
            }

        immuno_methods = ['OIT', 'SLIT', 'EPIT', '生物制剂联合']
        immuno_results = {}
        for method in immuno_methods:
            immuno = engine.design_immunotherapy(
                allergen='花生', method=method, patient_age=8, severity='中度'
            )
            immuno_results[method] = {
                'name': immuno['method_info']['name'],
                'efficacy': immuno['expected_efficacy'],
                'protocol': immuno['protocol']
            }

        # 保存数据
        full_data = {
            'project': '食物过敏防治药物研制科学智能体',
            'version': 'V1.0',
            'node': 'zhugebin-001',
            'timestamp': datetime.now().isoformat(),
            'phase1': {
                'allergens': pathway_results,
                'targets': target_scores
            },
            'phase2': {
                'screening': {
                    'total': screening['total_screened'],
                    'passed': screening['total_passed'],
                    'rate': screening['pass_rate']
                },
                'candidates': dockings
            },
            'phase3': {
                'trials': trials,
                'immunotherapy': immuno_results
            },
            'summary': {
                'allergens': len(allergens),
                'targets': len(target_scores),
                'compounds_passed': screening['total_passed'],
                'best_candidate': dockings[0]['compound'] if dockings else 'N/A',
                'best_binding': dockings[0]['binding_energy'] if dockings else 0,
                'best_immuno': max(immuno_results.items(), key=lambda x: x[1]['efficacy'])[0],
                'best_immuno_efficacy': max(r['efficacy'] for r in immuno_results.values())
            }
        }

        data_file = self.data_dir / 'full_research_results.json'
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(full_data, f, ensure_ascii=False, indent=2)

        print(f"\n  [OK] 研究数据已保存: {data_file}")
        print(f"  - 最佳候选: {full_data['summary']['best_candidate']}")
        print(f"  - 结合能: {full_data['summary']['best_binding']} kcal/mol")
        print(f"  - 最佳疗法: {full_data['summary']['best_immuno']} ({full_data['summary']['best_immuno_efficacy']:.0%})")

        return full_data

    # ========== 学习训练 ==========

    def run_training(self):
        """运行全员联合训练"""
        print("\n" + "=" * 60)
        print("  全员联合学习训练")
        print("=" * 60)

        trainer = self.load_trainer()
        results = trainer.train_all()

        # 保存训练状态
        state_file = self.data_dir / 'training_results.json'
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)

        print(f"\n  [OK] 训练结果已保存: {state_file}")
        return results

    # ========== 生成报告 ==========

    def generate_report(self):
        """生成综合研究报告"""
        print("\n" + "=" * 60)
        print("  生成综合研究报告")
        print("=" * 60)

        data_file = self.data_dir / 'full_research_results.json'
        if not data_file.exists():
            print("  [!] 无研究数据，先运行 --research")
            self.run_research()

        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        report_file = self.reports_dir / 'comprehensive_report.md'
        # 报告已在之前生成，此处检查是否存在
        if report_file.exists():
            print(f"  [OK] 报告已存在: {report_file}")
        else:
            print(f"  [!] 报告文件不存在，请运行 fusion.py --full")
            return None

        print(f"  [OK] 报告路径: {report_file}")
        return report_file

    # ========== 项目状态 ==========

    def show_status(self):
        """显示项目状态"""
        print("\n" + "=" * 60)
        print("  食物过敏防治药物研制科学智能体 · 项目状态")
        print("=" * 60)

        # 文件检查
        files = {
            '核心引擎': PROJECT_ROOT / 'domains/learning/problems/drug_discovery_engine.py',
            '训练器': PROJECT_ROOT / 'domains/learning/trainers/drug_discovery_trainer.py',
            'CLI工具': PROJECT_ROOT / 'scripts/drug_discovery_training.py',
            '题库P1': PROJECT_ROOT / 'domains/learning/problems/problems/drug-discovery/phase1/problems.json',
            '题库P2': PROJECT_ROOT / 'domains/learning/problems/problems/drug-discovery/phase2/problems.json',
            '题库P3': PROJECT_ROOT / 'domains/learning/problems/problems/drug-discovery/phase3/problems.json',
            '项目总览': DOMAIN_DIR / 'README.md',
            '研究计划': DOMAIN_DIR / 'research-plan.md',
            '快速启动': DOMAIN_DIR / 'quick-start.md',
            '协作协议': DOMAIN_DIR / 'collab/protocol.md',
            '仪表盘': DOMAIN_DIR / 'drug_discovery_dashboard.html',
            '研究数据': DOMAIN_DIR / 'data/full_research_results.json',
            '综合报告': DOMAIN_DIR / 'reports/comprehensive_report.md',
            '训练结果': DOMAIN_DIR / 'data/training_results.json',
        }

        print("\n  文件状态:")
        for name, path in files.items():
            exists = "OK" if path.exists() else "MISSING"
            size = f"{path.stat().st_size/1024:.1f}KB" if path.exists() else "-"
            print(f"  [{'+' if path.exists() else '-'}] {name:12s} | {size:>8s} | {path.name}")

        # 研究数据摘要
        data_file = DOMAIN_DIR / 'data/full_research_results.json'
        if data_file.exists():
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            summary = data.get('summary', {})
            print(f"\n  研究摘要:")
            print(f"  - 过敏原: {summary.get('allergens', '?')}种")
            print(f"  - 靶点: {summary.get('targets', '?')}个")
            print(f"  - 候选化合物: {summary.get('compounds_passed', '?')}个")
            print(f"  - 最佳候选: {summary.get('best_candidate', '?')}")
            print(f"  - 结合能: {summary.get('best_binding', '?')} kcal/mol")
            print(f"  - 最佳疗法: {summary.get('best_immuno', '?')} ({summary.get('best_immuno_efficacy', 0):.0%})")

        # CC消息
        cc_dir = PROJECT_ROOT / '.shared/messages/queue'
        if cc_dir.exists():
            nodes = list(cc_dir.iterdir())
            total_msgs = 0
            for node in nodes:
                inbox = node / 'inbox'
                if inbox.exists():
                    total_msgs += len(list(inbox.glob('*.json')))
            print(f"\n  CC消息: {total_msgs}条待处理 (跨{len(nodes)}个节点)")

        print("\n" + "=" * 60)

    # ========== 全流程 ==========

    def run_full(self):
        """运行全流程融合"""
        print("\n" + "=" * 60)
        print("  食物过敏防治药物研制 · 融合全流程")
        print("  小龙虾网络 · 多智能体协作")
        print("=" * 60)

        # 1. 研究流程
        data = self.run_research()

        # 2. 学习训练
        training = self.run_training()

        # 3. 生成报告
        report = self.generate_report()

        # 4. 状态汇总
        self.show_status()

        print("\n" + "=" * 60)
        print("  [DONE] 融合全流程完成！")
        print(f"  - 研究数据: {self.data_dir / 'full_research_results.json'}")
        print(f"  - 训练结果: {self.data_dir / 'training_results.json'}")
        print(f"  - 综合报告: {self.reports_dir / 'comprehensive_report.md'}")
        print(f"  - 仪表盘: {DOMAIN_DIR / 'drug_discovery_dashboard.html'}")
        print("=" * 60)

        return {
            'research': data,
            'training': training,
            'report': report
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description='食物过敏防治药物研制科学智能体 · 融合入口')
    parser.add_argument('--full', action='store_true', help='全流程融合运行')
    parser.add_argument('--research', action='store_true', help='仅研究流程')
    parser.add_argument('--train', action='store_true', help='仅学习训练')
    parser.add_argument('--report', action='store_true', help='生成报告')
    parser.add_argument('--status', action='store_true', help='查看项目状态')

    args = parser.parse_args()

    fusion = DrugDiscoveryFusion()

    if args.full:
        fusion.run_full()
    elif args.research:
        fusion.run_research()
    elif args.train:
        fusion.run_training()
    elif args.report:
        fusion.generate_report()
    elif args.status:
        fusion.show_status()
    else:
        parser.print_help()
        print("\n  示例:")
        print("  python3 domains/drug-discovery/fusion.py --full      # 全流程")
        print("  python3 domains/drug-discovery/fusion.py --research   # 研究")
        print("  python3 domains/drug-discovery/fusion.py --status     # 状态")


if __name__ == '__main__':
    main()
