#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V3.1 训练管线集成脚本
将 V3.1 组件（熔断器、缓存、模型路由、MCP 验证、龙虾币、向量记忆）集成到训练流程

使用方式:
    python3 core/integrate_v31.py [--test] [--activate]
"""

import json
import sys
import logging
from pathlib import Path
from datetime import datetime

# 添加路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

logger = logging.getLogger(__name__)


class V31IntegrationActivator:
    """V3.1 集成激活器"""

    def __init__(self):
        from lobster_network.v31_pipeline import get_pipeline
        self.pipeline = get_pipeline()
        logger.info("[V3.1 集成] 激活器初始化完成")

    def test_components(self) -> dict:
        """测试所有 V3.1 组件"""
        results = {}

        # 1. 熔断器测试
        try:
            status = self.pipeline.circuit_breaker.get_status()
            results["circuit_breaker"] = {"status": "ok", "details": status}
        except Exception as e:
            results["circuit_breaker"] = {"status": "error", "error": str(e)}

        # 2. 缓存管理器测试
        try:
            stats = self.pipeline.cache.get_stats()
            results["cache"] = {"status": "ok", "details": stats}
        except Exception as e:
            results["cache"] = {"status": "error", "error": str(e)}

        # 3. 模型路由测试
        try:
            stats = self.pipeline.router.get_stats()
            results["router"] = {"status": "ok", "details": stats}
        except Exception as e:
            results["router"] = {"status": "error", "error": str(e)}

        # 4. MCP 验证器测试
        try:
            stats = self.pipeline.validator.get_stats()
            results["validator"] = {"status": "ok", "details": stats}
        except Exception as e:
            results["validator"] = {"status": "error", "error": str(e)}

        # 5. 龙虾币经济系统测试
        try:
            stats = self.pipeline.economy.get_economy_stats()
            results["economy"] = {"status": "ok", "details": stats}
        except Exception as e:
            results["economy"] = {"status": "error", "error": str(e)}

        # 6. 向量记忆测试
        try:
            stats = {k: m.get_stats() for k, m in self.pipeline.memories.items()}
            results["memories"] = {"status": "ok", "details": stats}
        except Exception as e:
            results["memories"] = {"status": "error", "error": str(e)}

        return results

    def activate_training_integration(self) -> dict:
        """激活训练集成"""
        result = {
            "activated_at": datetime.now().isoformat(),
            "components": {},
            "status": "activated"
        }

        # 1. 激活熔断器
        self.pipeline.circuit_breaker.reset()
        result["components"]["circuit_breaker"] = "activated"

        # 2. 清空缓存（重新开始）
        self.pipeline.cache.clear()
        result["components"]["cache"] = "cleared"

        # 3. 初始化龙虾币账户
        from lobster_network.lobster_coin import init_student_accounts
        init_student_accounts(self.pipeline.economy)
        result["components"]["economy"] = "initialized"

        # 4. 配置价格表
        self.pipeline.economy.set_pricing("training_reward", 50.0)
        self.pipeline.economy.set_pricing("api_call", 5.0)
        self.pipeline.economy.set_pricing("bonus_perfect", 20.0)
        self.pipeline.economy.set_pricing("penalty_fail", 10.0)
        result["components"]["pricing"] = "configured"

        logger.info("[V3.1 集成] 所有组件已激活")
        return result

    def run_test_training(self, student_id: str = "xiaochen") -> dict:
        """运行测试训练"""
        test_questions = [
            {
                "question": "测试题目：黑先，如何吃子？",
                "options": ["A. 打吃", "B. 长", "C. 虎", "D. 跳"],
                "answer": "A",
                "difficulty": "初级",
                "metadata": {"category": "手筋"}
            }
        ]

        result = self.pipeline.run_training(student_id, "go", test_questions)
        return result

    def get_full_status(self) -> dict:
        """获取完整状态"""
        return {
            "system": self.pipeline.get_system_status(),
            "test_components": self.test_components(),
        }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="V3.1 训练管线集成激活")
    parser.add_argument("--test", action="store_true", help="运行测试")
    parser.add_argument("--activate", action="store_true", help="激活集成")
    parser.add_argument("--student", default="xiaochen", help="测试学员 ID")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    activator = V31IntegrationActivator()

    if args.activate:
        print("🔄 激活 V3.1 集成...")
        result = activator.activate_training_integration()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    if args.test:
        print("\n🧪 运行组件测试...")
        test_results = activator.test_components()
        print(json.dumps(test_results, ensure_ascii=False, indent=2))

        print("\n🎯 运行测试训练...")
        training_result = activator.run_test_training(args.student)
        print(json.dumps(training_result, ensure_ascii=False, indent=2))

    if not args.test and not args.activate:
        print("📊 V3.1 集成状态:")
        status = activator.get_full_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
