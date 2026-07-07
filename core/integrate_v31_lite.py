#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V3.1 训练管线集成脚本 - 轻量版
直接测试各组件，避免触发完整的 SSH 网络初始化

使用方式:
    python3 core/integrate_v31_lite.py [--test] [--activate] [--status]
"""

import json
import sys
import logging
from pathlib import Path
from datetime import datetime

# 添加路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

logger = logging.getLogger(__name__)


class V31LiteActivator:
    """V3.1 轻量级集成激活器"""

    def __init__(self):
        # 延迟导入，避免循环依赖
        from lobster_network.circuit_breaker import get_breaker
        from lobster_network.cache_manager import get_cache
        from lobster_network.model_router import get_router
        from lobster_network.lobster_coin import main_economy, init_student_accounts

        self.circuit_breaker = get_breaker("training")
        self.cache = get_cache("training")
        self.router = get_router("default")
        self.economy = main_economy

        # 初始化龙虾币账户
        init_student_accounts(self.economy)
        self.economy.set_pricing("training_reward", 50.0)
        self.economy.set_pricing("api_call", 5.0)
        self.economy.set_pricing("bonus_perfect", 20.0)
        self.economy.set_pricing("penalty_fail", 10.0)

        logger.info("[V3.1 轻量集成] 初始化完成")

    def test_components(self) -> dict:
        """测试所有 V3.1 组件"""
        results = {}

        # 1. 熔断器测试
        try:
            status = self.circuit_breaker.get_status()
            results["circuit_breaker"] = {"status": "ok", "details": status}
        except Exception as e:
            results["circuit_breaker"] = {"status": "error", "error": str(e)}

        # 2. 缓存管理器测试
        try:
            stats = self.cache.get_stats()
            results["cache"] = {"status": "ok", "details": stats}
        except Exception as e:
            results["cache"] = {"status": "error", "error": str(e)}

        # 3. 模型路由测试
        try:
            stats = self.router.get_stats()
            results["router"] = {"status": "ok", "details": stats}
        except Exception as e:
            results["router"] = {"status": "error", "error": str(e)}

        # 4. 龙虾币经济系统测试
        try:
            stats = self.economy.get_economy_stats()
            results["economy"] = {"status": "ok", "details": stats}
        except Exception as e:
            results["economy"] = {"status": "error", "error": str(e)}

        return results

    def activate(self) -> dict:
        """激活 V3.1 组件"""
        result = {
            "activated_at": datetime.now().isoformat(),
            "components": {},
            "status": "activated"
        }

        # 1. 重置熔断器
        self.circuit_breaker.reset()
        result["components"]["circuit_breaker"] = "reset"

        # 2. 清空缓存
        self.cache.clear()
        result["components"]["cache"] = "cleared"

        # 3. 初始化龙虾币
        from lobster_network.lobster_coin import init_student_accounts
        init_student_accounts(self.economy)
        result["components"]["economy"] = "initialized"

        logger.info("[V3.1 轻量集成] 所有组件已激活")
        return result

    def get_status(self) -> dict:
        """获取组件状态"""
        return {
            "circuit_breaker": self.circuit_breaker.get_status(),
            "cache": self.cache.get_stats(),
            "router": self.router.get_stats(),
            "economy": self.economy.get_economy_stats(),
        }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="V3.1 训练管线集成激活（轻量版）")
    parser.add_argument("--test", action="store_true", help="运行测试")
    parser.add_argument("--activate", action="store_true", help="激活集成")
    parser.add_argument("--status", action="store_true", help="查看状态")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    activator = V31LiteActivator()

    if args.activate:
        print("🔄 激活 V3.1 组件...")
        result = activator.activate()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    if args.test:
        print("\n🧪 运行组件测试...")
        test_results = activator.test_components()
        print(json.dumps(test_results, ensure_ascii=False, indent=2))

    if args.status or (not args.test and not args.activate):
        print("\n📊 V3.1 组件状态:")
        status = activator.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
