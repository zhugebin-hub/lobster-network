#!/usr/bin/env python3
"""
V3.1 训练调度集成 - 小龙虾网络
将 V3.1 集成引擎集成到 V4/V6 训练调度器

功能:
- 训练前: 熔断器检查 + 缓存命中检查
- 训练中: 模型路由 + MCP 验证
- 训练后: 龙虾币结算 + 向量记忆索引
"""

import json
import sys
import logging
from datetime import datetime
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

logger = logging.getLogger(__name__)


class V31TrainingIntegration:
    """V3.1 训练调度集成"""

    def __init__(self):
        from lobster_network.v31_pipeline import get_pipeline
        self.pipeline = get_pipeline()
        logger.info("[V3.1集成] 初始化完成")

    def pre_training_check(self, student_id: str, module: str) -> dict:
        """训练前检查"""
        result = {
            "student": student_id,
            "module": module,
            "can_train": True,
            "reason": "",
        }

        # 熔断器检查
        if not self.pipeline.circuit_breaker.can_execute():
            result["can_train"] = False
            result["reason"] = "熔断器打开，拒绝训练请求"
            return result

        # 缓存检查
        cache_key = f"{module}_{student_id}_{datetime.now().strftime('%Y%m%d')}"
        cached = self.pipeline.cache.get(cache_key)
        if cached:
            result["can_train"] = False
            result["reason"] = "今日训练已完成"
            result["cached"] = True
            return result

        return result

    def run_training(self, student_id: str, module: str, questions: list) -> dict:
        """执行训练"""
        return self.pipeline.run_training(student_id, module, questions)

    def post_training_process(self, student_id: str, module: str, result: dict) -> dict:
        """训练后处理"""
        # 龙虾币结算
        economy_result = self.pipeline.get_student_economy(student_id)
        result["economy"] = economy_result

        # 向量记忆统计
        memory_stats = self.pipeline.memories.get(module, {}).get("total_entries", 0)
        result["memory_entries"] = memory_stats

        return result

    def get_training_report(self, student_id: str) -> dict:
        """获取学员训练报告"""
        report = {
            "student": student_id,
            "economy": self.pipeline.get_student_economy(student_id),
            "system_status": self.pipeline.get_system_status(),
        }
        return report


# 便捷函数
def integrate_with_scheduler():
    """集成到调度器"""
    integration = V31TrainingIntegration()
    return integration


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    integration = integrate_with_scheduler()

    # 测试
    result = integration.pre_training_check("xiaochen", "go")
    print(json.dumps(result, ensure_ascii=False, indent=2))
