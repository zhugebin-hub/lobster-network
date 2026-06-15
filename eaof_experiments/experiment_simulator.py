# -*- coding: utf-8 -*-
"""
EAOF 实验模拟器
模拟生成实验数据并进行统计分析
"""

import numpy as np
from scipy import stats
from typing import Dict, List, Tuple
from dataclasses import dataclass
import json

@dataclass
class ExperimentResult:
    """实验结果数据结构"""
    metric_name: str
    mean: float
    std: float
    n: int
    values: np.ndarray  # 原始数据用于统计检验

class ExperimentSimulator:
    """实验模拟器"""
    
    def __init__(self, seed: int = 42):
        np.random.seed(seed)
        self.results = {}
    
    def simulate_latency(self, base: float, std: float, n: int = 50) -> np.ndarray:
        """
        模拟延迟数据（截断正态分布，延迟不能为负）
        """
        data = np.random.normal(base, std, n)
        data = np.maximum(data, 100)  # 最小延迟 100ms
        return data
    
    def simulate_success_rate(self, rate: float, std: float, n: int = 50) -> np.ndarray:
        """
        模拟成功率数据（截断到 [0, 1] 区间）
        """
        data = np.random.normal(rate, std, n)
        data = np.clip(data, 0, 1)
        return data
    
    def simulate_throughput(self, base: float, std: float, n: int = 50) -> np.ndarray:
        """
        模拟吞吐量数据（截断正态分布，吞吐量不能为负）
        """
        data = np.random.normal(base, std, n)
        data = np.maximum(data, 1)  # 最小吞吐量 1 req/s
        return data
    
    def run_baseline_experiment(self, config: Dict, n_runs: int = 50) -> Dict[str, ExperimentResult]:
        """
        运行基线对比实验
        """
        results = {}
        for framework_id, framework_config in config.items():
            latency_data = self.simulate_latency(
                framework_config['base_latency'],
                framework_config['latency_std'],
                n_runs
            )
            success_data = self.simulate_success_rate(
                framework_config['success_rate'],
                framework_config['success_rate_std'],
                n_runs
            )
            throughput_data = self.simulate_throughput(
                framework_config['throughput'],
                framework_config['throughput_std'],
                n_runs
            )
            
            results[framework_id] = {
                'latency': ExperimentResult(
                    '平均延迟 (ms)',
                    np.mean(latency_data),
                    np.std(latency_data),
                    n_runs,
                    latency_data
                ),
                'p95_latency': ExperimentResult(
                    'P95 延迟 (ms)',
                    np.percentile(latency_data, 95),
                    np.std(latency_data) * 1.5,
                    n_runs,
                    latency_data
                ),
                'success_rate': ExperimentResult(
                    '任务成功率',
                    np.mean(success_data),
                    np.std(success_data),
                    n_runs,
                    success_data
                ),
                'throughput': ExperimentResult(
                    '吞吐量 (req/s)',
                    np.mean(throughput_data),
                    np.std(throughput_data),
                    n_runs,
                    throughput_data
                ),
            }
        return results
    
    def run_ablation_experiment(self, config: Dict, n_runs: int = 50) -> Dict[str, Dict]:
        """
        运行消融实验
        """
        results = {}
        for exp_id, exp_config in config.items():
            latency_data = self.simulate_latency(
                exp_config['base_latency'],
                exp_config['latency_std'],
                n_runs
            )
            success_data = self.simulate_success_rate(
                exp_config['success_rate'],
                exp_config['success_rate_std'],
                n_runs
            )
            
            results[exp_id] = {
                'config': exp_config,
                'latency': ExperimentResult(
                    '平均延迟 (ms)',
                    np.mean(latency_data),
                    np.std(latency_data),
                    n_runs,
                    latency_data
                ),
                'p95_latency': ExperimentResult(
                    'P95 延迟 (ms)',
                    np.percentile(latency_data, 95),
                    np.std(latency_data) * 1.5,
                    n_runs,
                    latency_data
                ),
                'success_rate': ExperimentResult(
                    '任务成功率',
                    np.mean(success_data),
                    np.std(success_data),
                    n_runs,
                    success_data
                ),
            }
        return results
    
    def run_optimization_experiment(self, config: Dict, n_runs: int = 50) -> Dict[str, Dict]:
        """
        运行优化策略验证实验
        """
        results = {}
        for opt_id, opt_config in config.items():
            latency_data = self.simulate_latency(
                opt_config['base_latency'],
                opt_config['latency_std'],
                n_runs
            )
            success_data = self.simulate_success_rate(
                opt_config['success_rate'],
                opt_config['success_rate_std'],
                n_runs
            )
            
            results[opt_id] = {
                'config': opt_config,
                'latency': ExperimentResult(
                    '平均延迟 (ms)',
                    np.mean(latency_data),
                    np.std(latency_data),
                    n_runs,
                    latency_data
                ),
                'p95_latency': ExperimentResult(
                    'P95 延迟 (ms)',
                    np.percentile(latency_data, 95),
                    np.std(latency_data) * 1.5,
                    n_runs,
                    latency_data
                ),
                'success_rate': ExperimentResult(
                    '任务成功率',
                    np.mean(success_data),
                    np.std(success_data),
                    n_runs,
                    success_data
                ),
            }
        return results
    
    def run_stress_test(self, stress_data: Dict) -> Dict:
        """
        运行极限压力测试（使用论文中的数据点）
        """
        results = {}
        for concurrency, data in stress_data.items():
            results[concurrency] = {
                'eaof': {
                    'latency': data['eaof_latency'],
                    'success_rate': data['eaof_success'],
                    'throughput': data['eaof_throughput'],
                },
                'langchain': {
                    'success_rate': data['langchain_success'],
                },
                'autogpt': {
                    'success_rate': data['autogpt_success'],
                },
                'metagpt': {
                    'success_rate': data['metagpt_success'],
                },
            }
        return results


class StatisticalAnalyzer:
    """统计分析器"""
    
    @staticmethod
    def t_test(group1: np.ndarray, group2: np.ndarray) -> Dict:
        """
        独立样本 t 检验（双尾）
        """
        t_stat, p_value = stats.ttest_ind(group1, group2, equal_var=False)
        return {
            't_statistic': t_stat,
            'p_value': p_value,
            'significant': p_value < 0.05
        }
    
    @staticmethod
    def cohens_d(group1: np.ndarray, group2: np.ndarray) -> float:
        """
        计算 Cohen's d 效应量
        """
        n1, n2 = len(group1), len(group2)
        mean1, mean2 = np.mean(group1), np.mean(group2)
        var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
        
        pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
        d = (mean1 - mean2) / pooled_std
        return d
    
    @staticmethod
    def confidence_interval(data: np.ndarray, confidence: float = 0.95) -> Tuple:
        """
        计算置信区间
        """
        n = len(data)
        mean = np.mean(data)
        sem = stats.sem(data)
        ci = stats.t.interval(confidence, n - 1, loc=mean, scale=sem)
        return ci
    
    @staticmethod
    def bonferroni_correction(alpha: float, num_comparisons: int) -> float:
        """
        Bonferroni 校正
        """
        return alpha / num_comparisons
    
    @staticmethod
    def analyze_ablation_results(results: Dict, baseline_key: str = 'full') -> List[Dict]:
        """
        分析消融实验结果
        """
        analyses = []
        baseline = results[baseline_key]
        
        for exp_id, exp_data in results.items():
            if exp_id == baseline_key:
                continue
            
            # 成功率差异分析
            success_diff = baseline['success_rate'].mean - exp_data['success_rate'].mean
            success_ci = StatisticalAnalyzer.confidence_interval(
                baseline['success_rate'].values - exp_data['success_rate'].values
            )
            success_ttest = StatisticalAnalyzer.t_test(
                baseline['success_rate'].values,
                exp_data['success_rate'].values
            )
            
            # 延迟差异分析
            latency_ttest = StatisticalAnalyzer.t_test(
                baseline['latency'].values,
                exp_data['latency'].values
            )
            
            analyses.append({
                'comparison': f"{baseline['config']['name']} vs {exp_data['config']['name']}",
                'success_rate_diff': success_diff,
                'success_rate_ci': success_ci,
                'success_t_stat': success_ttest['t_statistic'],
                'success_p_value': success_ttest['p_value'],
                'latency_t_stat': latency_ttest['t_statistic'],
                'latency_p_value': latency_ttest['p_value'],
                'cohens_d': StatisticalAnalyzer.cohens_d(
                    baseline['success_rate'].values,
                    exp_data['success_rate'].values
                )
            })
        
        return analyses
