# -*- coding: utf-8 -*-
"""
EAOF 三层架构实验配置文件
基于论文《基于形式化建模的大模型多智能体协同架构与性能分析》
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Tuple

# 设置随机种子以确保实验可复现
np.random.seed(42)

@dataclass
class ExperimentConfig:
    """实验配置参数"""
    # 基础配置
    num_runs: int = 50  # 每个实验重复运行次数
    significance_level: float = 0.05  # 显著性水平α
    
    # 负载配置
    concurrency_levels: List[int] = None  # 并发用户数级别
    
    # 任务类型分布
    task_distribution: Dict[str, float] = None  # 任务类型比例
    
    def __post_init__(self):
        if self.concurrency_levels is None:
            self.concurrency_levels = [10, 50, 100, 200, 500, 1000]
        if self.task_distribution is None:
            self.task_distribution = {
                'text_qa': 0.6,      # 文本问答 60%
                'knowledge_retrieval': 0.3,  # 知识检索 30%
                'tool_invocation': 0.1  # 工具调用 10%
            }

# 基线框架配置
BASELINE_FRAMEWORKS = {
    'pure_api': {
        'name': '纯 API 调用',
        'base_latency': 1159,
        'latency_std': 166,
        'success_rate': 0.851,
        'success_rate_std': 0.030,
        'throughput': 24.9,
        'throughput_std': 3.0,
        'error_rate': 0.001,
    },
    'react': {
        'name': 'ReAct (学术基线)',
        'base_latency': 2450,
        'latency_std': 410,
        'success_rate': 0.895,
        'success_rate_std': 0.035,
        'throughput': 12.5,
        'throughput_std': 2.0,
        'error_rate': 0.015,
    },
    'toolformer': {
        'name': 'Toolformer 变体',
        'base_latency': 1950,
        'latency_std': 280,
        'success_rate': 0.912,
        'success_rate_std': 0.028,
        'throughput': 15.8,
        'throughput_std': 2.2,
        'error_rate': 0.008,
    },
    'langchain': {
        'name': 'LangChain',
        'base_latency': 2183,
        'latency_std': 371,
        'success_rate': 0.877,
        'success_rate_std': 0.042,
        'throughput': 13.2,
        'throughput_std': 2.7,
        'error_rate': 0.012,
    },
    'autogpt': {
        'name': 'AutoGPT',
        'base_latency': 3519,
        'latency_std': 665,
        'success_rate': 0.781,
        'success_rate_std': 0.061,
        'throughput': 7.7,
        'throughput_std': 1.9,
        'error_rate': 0.035,
    },
    'metagpt': {
        'name': 'MetaGPT',
        'base_latency': 2849,
        'latency_std': 366,
        'success_rate': 0.837,
        'success_rate_std': 0.047,
        'throughput': 11.1,
        'throughput_std': 2.4,
        'error_rate': 0.020,
    },
    'eaof': {
        'name': 'EAOF (本文)',
        'base_latency': 1823,
        'latency_std': 162,
        'success_rate': 0.984,
        'success_rate_std': 0.012,
        'throughput': 18.1,
        'throughput_std': 1.5,
        'error_rate': 0.005,
    },
}

# 消融实验配置
ABLATION_CONFIGS = {
    'full': {
        'name': '完整架构',
        'memory_retrieval': True,
        'tool_invocation': True,
        'protocol_adaptation': True,
        'base_latency': 1839,
        'latency_std': 113,
        'success_rate': 0.985,
        'success_rate_std': 0.009,
    },
    'no_memory': {
        'name': '去除记忆检索模块',
        'memory_retrieval': False,
        'tool_invocation': True,
        'protocol_adaptation': True,
        'base_latency': 1546,
        'latency_std': 116,
        'success_rate': 0.821,
        'success_rate_std': 0.035,
    },
    'no_tool': {
        'name': '去除工具调用引擎',
        'memory_retrieval': True,
        'tool_invocation': False,
        'protocol_adaptation': True,
        'base_latency': 1596,
        'latency_std': 97,
        'success_rate': 0.749,
        'success_rate_std': 0.042,
    },
    'no_protocol': {
        'name': '去除协议适配层',
        'memory_retrieval': True,
        'tool_invocation': True,
        'protocol_adaptation': False,
        'base_latency': 1783,
        'latency_std': 124,
        'success_rate': 0.950,
        'success_rate_std': 0.021,
    },
}

# 优化策略验证配置
OPTIMIZATION_CONFIGS = {
    'base': {
        'name': '基础架构 (无优化)',
        'async_streaming': False,
        'multi_level_cache': False,
        'base_latency': 2226,
        'latency_std': 169,
        'success_rate': 0.929,
        'success_rate_std': 0.026,
    },
    '+async': {
        'name': '+ 异步流式协议适配',
        'async_streaming': True,
        'multi_level_cache': False,
        'base_latency': 1910,
        'latency_std': 147,
        'success_rate': 0.946,
        'success_rate_std': 0.022,
    },
    '+cache': {
        'name': '+ 多级缓存记忆检索',
        'async_streaming': True,
        'multi_level_cache': True,
        'base_latency': 1825,
        'latency_std': 144,
        'success_rate': 0.969,
        'success_rate_std': 0.013,
    },
    'full_opt': {
        'name': '全部优化 (完整架构)',
        'async_streaming': True,
        'multi_level_cache': True,
        'base_latency': 1791,
        'latency_std': 127,
        'success_rate': 0.986,
        'success_rate_std': 0.009,
    },
}

# 压力测试数据点
STRESS_TEST_DATA = {
    10: {'eaof_latency': 1200, 'eaof_success': 0.995, 'eaof_throughput': 10,
         'langchain_success': 0.92, 'autogpt_success': 0.85, 'metagpt_success': 0.88},
    50: {'eaof_latency': 1800, 'eaof_success': 0.985, 'eaof_throughput': 25,
         'langchain_success': 0.88, 'autogpt_success': 0.78, 'metagpt_success': 0.82},
    100: {'eaof_latency': 2200, 'eaof_success': 0.97, 'eaof_throughput': 30,
          'langchain_success': 0.83, 'autogpt_success': 0.70, 'metagpt_success': 0.76},
    200: {'eaof_latency': 2800, 'eaof_success': 0.945, 'eaof_throughput': 32,
          'langchain_success': 0.75, 'autogpt_success': 0.58, 'metagpt_success': 0.66},
    500: {'eaof_latency': 4200, 'eaof_success': 0.88, 'eaof_throughput': 28,
          'langchain_success': 0.60, 'autogpt_success': 0.40, 'metagpt_success': 0.50},
    1000: {'eaof_latency': 8500, 'eaof_success': 0.65, 'eaof_throughput': 15,
           'langchain_success': 0.28, 'autogpt_success': 0.15, 'metagpt_success': 0.22},
}
