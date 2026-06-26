"""
🦞 小龙虾网络 · AI/ML 训练引擎
支持：模型训练模拟、特征工程、超参数优化、模型评估
"""

import json
import os
import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class AIMLEngine:
    """AI/ML 训练引擎"""
    
    def __init__(self, problems_dir: str = None):
        """初始化引擎"""
        if problems_dir is None:
            problems_dir = os.path.join(
                os.path.dirname(__file__),
                '..', 'ai_ml', 'problems', 'problems'
            )
        self.problems_dir = problems_dir
        self.phases = {}
        self._load_problems()
        
    def _load_problems(self):
        """加载各阶段题库"""
        for phase in ['phase1', 'phase2', 'phase3']:
            phase_dir = os.path.join(self.problems_dir, phase)
            problems_file = os.path.join(phase_dir, 'problems.json')
            if os.path.exists(problems_file):
                with open(problems_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.phases[phase] = data
                    
    def get_problems(self, phase: str = None, problem_type: str = None, 
                     difficulty: str = None, limit: int = 10) -> List[Dict]:
        """获取题目"""
        problems = []
        phases_to_check = [phase] if phase else list(self.phases.keys())
        
        for p in phases_to_check:
            if p not in self.phases:
                continue
            for prob in self.phases[p]['problems']:
                if problem_type and prob.get('type') != problem_type:
                    continue
                if difficulty and prob.get('difficulty') != difficulty:
                    continue
                problems.append(prob)
                
        return problems[:limit]
    
    def simulate_training(self, model_type: str = 'linear_regression',
                         dataset_size: int = 1000,
                         epochs: int = 100) -> Dict:
        """
        模拟模型训练
        
        Args:
            model_type: 模型类型
            dataset_size: 数据集大小
            epochs: 训练轮数
            
        Returns:
            训练结果
        """
        # 模拟训练过程
        train_loss = []
        val_loss = []
        
        for epoch in range(epochs):
            # 模拟损失下降
            base_loss = 1.0 / (1 + epoch * 0.05)
            noise = random.uniform(-0.05, 0.05)
            train_loss.append(max(0.01, base_loss + noise))
            
            # 验证损失（可能过拟合）
            val_base = 1.0 / (1 + epoch * 0.04)
            val_noise = random.uniform(-0.08, 0.08)
            val_loss.append(max(0.02, val_base + val_noise + epoch * 0.001))
            
        # 找到最优epoch
        best_epoch = min(range(len(val_loss)), key=lambda i: val_loss[i])
        
        return {
            'model_type': model_type,
            'dataset_size': dataset_size,
            'epochs': epochs,
            'final_train_loss': round(train_loss[-1], 4),
            'final_val_loss': round(val_loss[-1], 4),
            'best_epoch': best_epoch + 1,
            'best_val_loss': round(val_loss[best_epoch], 4),
            'overfitting': val_loss[-1] > val_loss[best_epoch] * 1.2,
            'training_curve': {
                'train_loss': [round(l, 4) for l in train_loss[::10]],
                'val_loss': [round(l, 4) for l in val_loss[::10]]
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def feature_engineering(self, features: List[str],
                          target: str = 'label') -> Dict:
        """
        特征工程模拟
        
        Args:
            features: 特征列表
            target: 目标变量
            
        Returns:
            特征工程结果
        """
        # 模拟特征重要性
        importance = {}
        for f in features:
            importance[f] = round(random.uniform(0.01, 0.3), 3)
            
        # 归一化
        total = sum(importance.values())
        importance = {k: round(v/total, 3) for k, v in importance.items()}
        
        # 排序
        sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'features': features,
            'target': target,
            'feature_importance': dict(sorted_features),
            'top_features': [f for f, _ in sorted_features[:5]],
            'low_importance_features': [f for f, v in sorted_features if v < 0.05],
            'recommendations': [],
            'timestamp': datetime.now().isoformat()
        }
    
    def hyperparameter_tuning(self, model_type: str = 'random_forest',
                            param_space: Dict = None) -> Dict:
        """
        超参数调优模拟
        
        Args:
            model_type: 模型类型
            param_space: 参数空间
            
        Returns:
            调优结果
        """
        if param_space is None:
            param_space = {
                'n_estimators': [50, 100, 200],
                'max_depth': [3, 5, 7, 10],
                'learning_rate': [0.01, 0.05, 0.1]
            }
            
        # 模拟网格搜索
        best_score = 0
        best_params = {}
        results = []
        
        import itertools
        param_names = list(param_space.keys())
        param_values = list(param_space.values())
        
        for params in itertools.product(*param_values):
            param_dict = dict(zip(param_names, params))
            # 模拟得分
            score = random.uniform(0.7, 0.95)
            results.append({
                'params': param_dict,
                'score': round(score, 4)
            })
            if score > best_score:
                best_score = score
                best_params = param_dict
                
        # 排序
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'model_type': model_type,
            'param_space': param_space,
            'best_params': best_params,
            'best_score': round(best_score, 4),
            'top_results': results[:5],
            'total_combinations': len(results),
            'timestamp': datetime.now().isoformat()
        }
    
    def evaluate_model(self, model_type: str = 'classification',
                      metrics: List[str] = None) -> Dict:
        """
        模型评估
        
        Args:
            model_type: 模型类型
            metrics: 评估指标
            
        Returns:
            评估结果
        """
        if metrics is None:
            metrics = ['accuracy', 'precision', 'recall', 'f1']
            
        # 模拟评估结果
        results = {}
        for metric in metrics:
            if metric == 'accuracy':
                results[metric] = round(random.uniform(0.75, 0.95), 4)
            elif metric in ['precision', 'recall', 'f1']:
                results[metric] = round(random.uniform(0.70, 0.93), 4)
            else:
                results[metric] = round(random.uniform(0.60, 0.90), 4)
                
        return {
            'model_type': model_type,
            'metrics': results,
            'overall_score': round(sum(results.values()) / len(results), 4),
            'strengths': [],
            'weaknesses': [],
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_training_plan(self, student_type: str = 'xiaochen',
                               date: str = None) -> Dict:
        """
        生成每日训练计划
        
        Args:
            student_type: 学员类型
            date: 日期
            
        Returns:
            训练计划
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
            
        # 根据学员类型配置题量
        if student_type == 'zhuguxia':
            config = {
                'model_training': 4,
                'feature_engineering': 3,
                'hyperparameter_tuning': 2,
                'model_evaluation': 2
            }
        else:
            config = {
                'model_training': 3,
                'feature_engineering': 2,
                'hyperparameter_tuning': 1,
                'model_evaluation': 1
            }
            
        # 生成计划
        plan = {
            'date': date,
            'student': student_type,
            'type': 'ai-ml-training',
            'schedule': [],
            'total_problems': 0
        }
        
        time_slots = ['09:00', '14:00', '19:00', '21:00']
        slot_idx = 0
        
        type_names = {
            'model_training': '模型训练',
            'feature_engineering': '特征工程',
            'hyperparameter_tuning': '超参数调优',
            'model_evaluation': '模型评估'
        }
        
        for problem_type, count in config.items():
            if count == 0:
                continue
                
            problems = self.get_problems(problem_type=problem_type, limit=count)
            plan['schedule'].append({
                'time': time_slots[slot_idx % len(time_slots)],
                'type': type_names.get(problem_type, problem_type),
                'count': len(problems),
                'problems': problems
            })
            plan['total_problems'] += len(problems)
            slot_idx += 1
            
        return plan


# 演示
if __name__ == '__main__':
    engine = AIMLEngine()
    
    print("=" * 50)
    print("🦞 小龙虾网络 - AI/ML 训练引擎 V1.0")
    print("=" * 50)
    
    # 1. 模拟训练
    print("\n🔥 模拟模型训练:")
    training = engine.simulate_training('random_forest', 1000, 50)
    print(f"   模型: {training['model_type']}")
    print(f"   数据集: {training['dataset_size']}")
    print(f"   训练轮数: {training['epochs']}")
    print(f"   最终训练损失: {training['final_train_loss']:.4f}")
    print(f"   最终验证损失: {training['final_val_loss']:.4f}")
    print(f"   最优轮数: {training['best_epoch']}")
    print(f"   过拟合: {'⚠️ 是' if training['overfitting'] else '✅ 否'}")
    
    # 2. 特征工程
    print("\n🔧 特征工程:")
    features = ['age', 'income', 'education', 'experience', 'location', 'industry']
    fe = engine.feature_engineering(features)
    print(f"   特征数: {len(fe['features'])}")
    print(f"   Top 3 特征: {', '.join(fe['top_features'][:3])}")
    
    # 3. 超参数调优
    print("\n⚙️ 超参数调优:")
    tuning = engine.hyperparameter_tuning('random_forest')
    print(f"   模型: {tuning['model_type']}")
    print(f"   最优参数: {tuning['best_params']}")
    print(f"   最优得分: {tuning['best_score']:.4f}")
    print(f"   总组合数: {tuning['total_combinations']}")
    
    # 4. 模型评估
    print("\n📊 模型评估:")
    eval_result = engine.evaluate_model('classification')
    print(f"   模型: {eval_result['model_type']}")
    for metric, score in eval_result['metrics'].items():
        print(f"   {metric}: {score:.4f}")
    print(f"   综合得分: {eval_result['overall_score']:.4f}")
    
    # 5. 生成训练计划
    print("\n📋 训练计划:")
    plan = engine.generate_training_plan('xiaochen')
    print(f"   日期: {plan['date']}")
    print(f"   总题数: {plan['total_problems']}")
    for slot in plan['schedule']:
        print(f"   [{slot['time']}] {slot['type']}: {slot['count']}题")
        
    print("\n" + "=" * 50)
    print("✅ AI/ML 训练引擎测试完成！")
