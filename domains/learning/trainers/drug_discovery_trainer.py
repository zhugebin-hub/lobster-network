"""
新药创制科学智能体训练器 V1.0
支持6个节点联合研究，覆盖食物过敏防治药物研制全流程

学员配置：
- xiaochen (小陈) - 稳健型：靶点识别+基础概念
- zhuguxia (诸葛虾) - 加速型：分子对接+ADMET评估
- zhugebin-001 (诸葛斌) - 研究型：全流程+临床试验设计
- zhugema (诸葛马) - 教练型：药物安全+监管+高级评审
- xiaowei (小薇) - 实战型：免疫疗法+临床执行
- qoder - 技术型：ADMET计算+虚拟筛选
"""

import json
import os
from typing import Dict, List
from datetime import datetime

try:
    from .drug_discovery_engine import DrugDiscoveryEngine
except ImportError:
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'problems'))
    from drug_discovery_engine import DrugDiscoveryEngine


STUDENT_CONFIG = {
    'xiaochen': {
        'name': '小陈',
        'node': '121.43.80.231',
        'type': '稳健型',
        'focus': ['靶点识别', '过敏机制', '基础概念'],
        'phases': ['phase1'],
        'daily_target': 8,
        'accuracy_goal': 0.85,
    },
    'zhuguxia': {
        'name': '诸葛虾',
        'node': '60.205.139.51',
        'type': '加速型',
        'focus': ['分子对接', 'ADMET评估', '先导化合物筛选'],
        'phases': ['phase1', 'phase2'],
        'daily_target': 12,
        'accuracy_goal': 0.80,
    },
    'zhugebin-001': {
        'name': '诸葛斌',
        'node': 'local',
        'type': '研究型',
        'focus': ['全流程', '临床试验设计', '免疫疗法'],
        'phases': ['phase1', 'phase2', 'phase3'],
        'daily_target': 15,
        'accuracy_goal': 0.90,
    },
    'zhugema': {
        'name': '诸葛马',
        'node': '47.93.6.57',
        'type': '教练型',
        'focus': ['药物安全', '监管审批', '高级评审'],
        'phases': ['phase2', 'phase3'],
        'daily_target': 10,
        'accuracy_goal': 0.88,
        'role': 'AI教练(主节点)',
    },
    'xiaowei': {
        'name': '小薇',
        'node': 'local',
        'type': '实战型',
        'focus': ['免疫疗法', '临床执行', '患者管理'],
        'phases': ['phase3'],
        'daily_target': 8,
        'accuracy_goal': 0.82,
    },
    'qoder': {
        'name': 'qoder',
        'node': '192.168.1.161',
        'type': '技术型',
        'focus': ['ADMET计算', '虚拟筛选', '分子对接'],
        'phases': ['phase2'],
        'daily_target': 10,
        'accuracy_goal': 0.85,
    },
}


class DrugDiscoveryTrainer:
    """新药创制科学智能体训练器"""

    def __init__(self, engine: DrugDiscoveryEngine = None):
        self.engine = engine or DrugDiscoveryEngine()
        self.students = STUDENT_CONFIG

    def generate_daily_plan(self, student_id: str, date: str = None) -> Dict:
        """生成每日研究计划"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        student = self.students.get(student_id)
        if not student:
            return {"error": f"未知学员: {student_id}"}

        # 按学员阶段分配题目
        plan = {
            'date': date,
            'student_id': student_id,
            'student_name': student['name'],
            'student_type': student['type'],
            'node': student['node'],
            'focus': student['focus'],
            'module': 'drug-discovery',
            'schedule': [],
            'total_problems': 0,
        }

        time_slots = ['09:00', '14:00', '19:00']
        slot_idx = 0
        daily_target = student['daily_target']
        problems_per_slot = max(2, daily_target // len(student['phases']))

        for phase in student['phases']:
            problems = self.engine.get_problems(phase=phase, limit=problems_per_slot)
            if problems:
                plan['schedule'].append({
                    'time': time_slots[slot_idx % len(time_slots)],
                    'phase': phase,
                    'count': len(problems),
                    'problems': problems,
                })
                plan['total_problems'] += len(problems)
                slot_idx += 1

        # 研究任务（引擎功能调用）
        research_tasks = []
        if '靶点识别' in student['focus']:
            research_tasks.append({'task': '靶点识别', 'method': 'identify_drug_target', 'params': {'allergen': '花生', 'pathway': 'IgE'}})
        if '分子对接' in student['focus']:
            research_tasks.append({'task': '分子对接评分', 'method': 'molecular_docking_score', 'params': {'compound_name': '龙虾素-A', 'target': 'IgE'}})
        if 'ADMET评估' in student['focus'] or 'ADMET计算' in student['focus']:
            research_tasks.append({'task': 'ADMET预测', 'method': 'predict_admet', 'params': {'compound_name': '龙虾素-A'}})
        if '先导化合物筛选' in student['focus'] or '虚拟筛选' in student['focus']:
            research_tasks.append({'task': '先导化合物筛选', 'method': 'screen_lead_compounds', 'params': {'target': 'IgE'}})
        if '临床试验设计' in student['focus']:
            research_tasks.append({'task': '临床试验设计', 'method': 'design_clinical_trial', 'params': {'target': 'IgE', 'phase': 'II', 'allergen': '花生'}})
        if '免疫疗法' in student['focus']:
            research_tasks.append({'task': '免疫疗法设计', 'method': 'design_immunotherapy', 'params': {'allergen': '花生', 'method': 'OIT'}})
        if '药物安全' in student['focus']:
            research_tasks.append({'task': '药物安全评估', 'method': 'evaluate_drug_safety', 'params': {'compound_name': '龙虾素-A', 'target': 'IgE', 'patient_group': '儿童'}})

        plan['research_tasks'] = research_tasks

        return plan

    def execute_research(self, student_id: str) -> Dict:
        """执行研究任务（调用引擎方法）"""
        student = self.students.get(student_id)
        if not student:
            return {"error": f"未知学员: {student_id}"}

        plan = self.generate_daily_plan(student_id)
        results = {
            'student_id': student_id,
            'student_name': student['name'],
            'node': student['node'],
            'date': plan['date'],
            'research_results': [],
            'problem_results': [],
            'accuracy': 0.0,
        }

        # 执行研究任务
        for task in plan.get('research_tasks', []):
            method_name = task['method']
            params = task['params']
            method = getattr(self.engine, method_name, None)
            if method:
                try:
                    result = method(**params)
                    results['research_results'].append({
                        'task': task['task'],
                        'method': method_name,
                        'status': 'success',
                        'result_summary': self._summarize_result(method_name, result),
                    })
                except Exception as e:
                    results['research_results'].append({
                        'task': task['task'],
                        'method': method_name,
                        'status': 'error',
                        'error': str(e),
                    })

        # 模拟答题
        correct_count = 0
        total_count = 0
        for slot in plan['schedule']:
            for prob in slot['problems']:
                total_count += 1
                # 模拟答题（基于学员能力）
                import random
                accuracy = student['accuracy_goal']
                if random.random() < accuracy:
                    correct_count += 1
                    status = 'correct'
                else:
                    status = 'wrong'
                results['problem_results'].append({
                    'id': prob['id'],
                    'type': prob['type'],
                    'status': status,
                    'difficulty': prob.get('difficulty', '未知'),
                })

        results['accuracy'] = round(correct_count / total_count, 3) if total_count > 0 else 0
        results['correct'] = correct_count
        results['total'] = total_count
        results['timestamp'] = datetime.now().isoformat()

        return results

    def _summarize_result(self, method_name: str, result: Dict) -> str:
        """摘要研究结果"""
        if method_name == 'identify_drug_target':
            return f"靶点: {result.get('target_info', {}).get('name', '?')}, 综合评分: {result.get('overall_score', 0):.3f}, 推荐: {result.get('recommendation', '?')}"
        elif method_name == 'screen_lead_compounds':
            return f"筛选: {result.get('total_screened', 0)}个化合物 → {result.get('total_passed', 0)}个通过 ({result.get('pass_rate', 0):.0%})"
        elif method_name == 'molecular_docking_score':
            return f"结合自由能: {result.get('binding_energy', 0)} kcal/mol, 评级: {result.get('grade', '?')}, Ki: {result.get('estimated_ki', 0)} μM"
        elif method_name == 'predict_admet':
            return f"ADMET综合: {result.get('overall_admet_score', 0):.3f}, 安全性: {result.get('toxicity', {}).get('safety_score', 0):.3f}"
        elif method_name == 'evaluate_drug_safety':
            return f"安全评分: {result.get('safety_score', 0):.3f}, 推荐: {result.get('recommendation', '?')}"
        elif method_name == 'design_clinical_trial':
            return f"试验: {result.get('trial_id', '?')}, 阶段: {result.get('phase', '?')}, 样本: {result.get('patient_count', 0)}例"
        elif method_name == 'design_immunotherapy':
            return f"方法: {result.get('method_info', {}).get('name', '?')}, 预期疗效: {result.get('expected_efficacy', 0):.1%}"
        elif method_name == 'food_allergy_pathway_analysis':
            return f"过敏原: {result.get('allergen', '?')}, 推荐策略: {result.get('recommended_approach', '?')}"
        return str(result)[:100]

    def get_research_report(self) -> Dict:
        """生成全员研究报告"""
        report = {
            'module': '新药创制科学智能体',
            'focus': '食物过敏防治药物研制',
            'version': 'V1.0',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'students': [],
            'summary': {},
        }

        all_accuracy = []
        all_research = 0
        all_problems = 0

        for student_id, student in self.students.items():
            result = self.execute_research(student_id)
            report['students'].append({
                'student_id': student_id,
                'name': student['name'],
                'node': student['node'],
                'type': student['type'],
                'focus': student['focus'],
                'accuracy': result['accuracy'],
                'problems_solved': result['total'],
                'research_tasks_done': len(result['research_results']),
                'research_summaries': [r.get('result_summary', '') for r in result['research_results']],
            })
            all_accuracy.append(result['accuracy'])
            all_research += len(result['research_results'])
            all_problems += result['total']

        report['summary'] = {
            'total_students': len(self.students),
            'total_nodes': len(set(s['node'] for s in self.students.values())),
            'avg_accuracy': round(sum(all_accuracy) / len(all_accuracy), 3) if all_accuracy else 0,
            'total_research_tasks': all_research,
            'total_problems_solved': all_problems,
            'engine_methods': 8,
            'total_problems': sum(len(p.get('problems', [])) for p in self.engine.phases.values()),
        }

        return report


# 演示
if __name__ == '__main__':
    trainer = DrugDiscoveryTrainer()

    print("=" * 60)
    print("🦞 小龙虾网络 - 新药创制科学智能体训练器 V1.0")
    print("   食物过敏防治药物研制 · 6节点联合研究")
    print("=" * 60)

    print(f"\n📊 学员配置 ({len(trainer.students)} 节点):")
    print(f"{'学员':<12} {'类型':<8} {'节点':<20} {'重点':<30} {'日题量':<6} {'目标':<6}")
    print("-" * 90)
    for sid, s in trainer.students.items():
        focus_str = '/'.join(s['focus'][:3])
        print(f"{s['name']:<12} {s['type']:<8} {s['node']:<20} {focus_str:<30} {s['daily_target']:<6} {s['accuracy_goal']:.0%}")

    # 单个学员演示
    print("\n" + "=" * 60)
    print("📋 诸葛斌(研究型)每日研究计划:")
    plan = trainer.generate_daily_plan('zhugebin-001')
    print(f"   日期: {plan['date']}")
    print(f"   总题数: {plan['total_problems']}")
    print(f"   研究任务: {len(plan['research_tasks'])}项")
    for slot in plan['schedule']:
        print(f"   [{slot['time']}] {slot['phase']}: {slot['count']}题")
    for task in plan['research_tasks']:
        print(f"   🔬 {task['task']} → {task['method']}")

    # 执行研究
    print("\n" + "=" * 60)
    print("🧪 执行研究任务:")
    result = trainer.execute_research('zhugebin-001')
    print(f"   学员: {result['student_name']}")
    print(f"   答题: {result['correct']}/{result['total']} (正确率: {result['accuracy']:.1%})")
    print(f"   研究任务完成: {len(result['research_results'])}项")
    for r in result['research_results']:
        status_icon = "✅" if r['status'] == 'success' else "❌"
        print(f"   {status_icon} {r['task']}: {r.get('result_summary', r.get('error', ''))}")

    # 全员报告
    print("\n" + "=" * 60)
    print("📊 全员联合研究报告:")
    report = trainer.get_research_report()
    s = report['summary']
    print(f"   参与节点: {s['total_students']}个 (覆盖{s['total_nodes']}台服务器)")
    print(f"   平均正确率: {s['avg_accuracy']:.1%}")
    print(f"   研究任务总数: {s['total_research_tasks']}项")
    print(f"   答题总数: {s['total_problems_solved']}题")
    print(f"   引擎方法: {s['engine_methods']}大科学方法")
    print(f"   题库总量: {s['total_problems']}题")

    for stu in report['students']:
        print(f"   {stu['name']:<12} 正确率:{stu['accuracy']:.0%}  答题:{stu['problems_solved']}  研究:{stu['research_tasks_done']}项")

    print("\n" + "=" * 60)
    print("✅ 新药创制科学智能体训练器测试完成！")
