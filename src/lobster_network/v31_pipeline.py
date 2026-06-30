#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V3.1优化层集成引擎 - 小龙虾网络
统一调度熔断器、缓存、模型路由、MCP验证、龙虾币、向量记忆

使用方式:
    from lobster_network.v31_pipeline import V31Pipeline
    pipeline = V31Pipeline()
    result = pipeline.run_training("xiaochen", "go", questions)
"""

import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class V31Pipeline:
    """V3.1 训练管线集成引擎"""

    def __init__(self, storage_dir: str = "/shared/training/go"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # 延迟导入，避免循环依赖
        from .circuit_breaker import get_breaker
        from .cache_manager import get_cache
        from .model_router import get_router
        from .mcp_validator import training_validator
        from .lobster_coin import main_economy, init_student_accounts, student_earn, api_cost
        from .vector_memory_expander import get_memory, add_wrong_answer

        # 初始化组件
        self.circuit_breaker = get_breaker("training")
        self.cache = get_cache("training")
        self.router = get_router("default")
        self.validator = training_validator
        self.economy = main_economy
        self.memories = {
            "go": get_memory("go", storage_path=f"{storage_dir}/vector_memory_go.json"),
            "networking": get_memory("networking", storage_path=f"{storage_dir}/vector_memory_networking.json"),
        }

        # 初始化龙虾币账户
        init_student_accounts(self.economy)
        # 配置价格表
        self.economy.set_pricing("training_reward", 50.0)
        self.economy.set_pricing("api_call", 5.0)
        self.economy.set_pricing("bonus_perfect", 20.0)
        self.economy.set_pricing("penalty_fail", 10.0)

        logger.info("[V3.1管线] 初始化完成")

    def run_training(self, student_id: str, module: str, questions: List[Dict]) -> Dict:
        """
        执行训练流程（集成V3.1组件）

        Args:
            student_id: 学员ID
            module: 模块名称 (go/networking/poster...)
            questions: 题目列表 [{"question": "...", "options": [...], "answer": "...", "difficulty": "medium"}]

        Returns:
            训练结果字典
        """
        result = {
            "student": student_id,
            "module": module,
            "questions_total": len(questions),
            "status": "pending",
            "started_at": datetime.now().isoformat(),
        }

        try:
            # 1. 熔断器保护
            if not self.circuit_breaker.can_execute():
                raise RuntimeError("熔断器打开，拒绝训练请求")

            # 2. 缓存检查（同模块同日不重复训练）
            cache_key = f"{module}_{student_id}_{datetime.now().strftime('%Y%m%d')}"
            cached = self.cache.get(cache_key)
            if cached:
                result["status"] = "cached"
                result["message"] = "今日训练已完成，跳过"
                return result

            # 3. 模型路由（按首题难度选择模型）
            if questions:
                routing = self.router.route(
                    questions[0].get("question", ""),
                    questions[0].get("metadata", {})
                )
                result["selected_model"] = routing.selected_model
                result["difficulty"] = routing.difficulty

            # 4. 执行训练（占位：实际由训练引擎执行）
            start_time = time.time()
            # ... 实际训练逻辑 ...
            elapsed = time.time() - start_time
            result["elapsed_seconds"] = round(elapsed, 2)

            # 5. MCP 验证
            validation = self.validator.validate(result)
            result["validation"] = validation.to_dict()

            # 6. 龙虾币结算
            if validation.overall.value == "pass":
                self.economy.earn(student_id, 50, "earn_training", "训练完成奖励")
                if validation.total_score >= 0.9:
                    self.economy.earn(student_id, 20, "earn_bonus", "满分奖励")
            else:
                self.economy.spend(student_id, 10, "spend_penalty", "训练失败惩罚")

            # 7. 向量记忆（错题索引）
            for q in questions:
                if not q.get("correct", True):
                    add_wrong_answer(
                        module,
                        q.get("question", ""),
                        q.get("answer", ""),
                        q.get("correct_answer", "")
                    )

            # 8. 缓存结果
            self.cache.set(cache_key, result, ttl=3600)
            self.circuit_breaker.record_success()
            result["status"] = "completed"

            logger.info(f"[V3.1管线] {student_id} {module} 训练完成: {validation.overall.value}")

        except Exception as e:
            self.circuit_breaker.record_failure(e)
            result["status"] = "failed"
            result["error"] = str(e)
            logger.error(f"[V3.1管线] {student_id} {module} 训练失败: {e}")

        result["finished_at"] = datetime.now().isoformat()
        return result

    def search_wrong_answers(self, module: str, query: str, top_k: int = 3) -> List[Dict]:
        """搜索相似错题"""
        mem = self.memories.get(module)
        if not mem:
            return []
        results = mem.search(query, top_k=top_k)
        return [(entry.to_dict(), score) for entry, score in results]

    def get_student_economy(self, student_id: str) -> Optional[Dict]:
        """获取学员经济状态"""
        account = self.economy.get_account(student_id)
        return account.to_dict() if account else None

    def get_system_status(self) -> Dict:
        """获取V3.1系统状态"""
        return {
            "circuit_breaker": self.circuit_breaker.get_status(),
            "cache": self.cache.get_stats(),
            "router": self.router.get_stats(),
            "validator": self.validator.get_stats(),
            "economy": self.economy.get_economy_stats(),
            "memories": {k: m.get_stats() for k, m in self.memories.items()},
        }


# 全局单例
_pipeline: Optional[V31Pipeline] = None

def get_pipeline() -> V31Pipeline:
    """获取V3.1管线实例"""
    global _pipeline
    if _pipeline is None:
        _pipeline = V31Pipeline()
    return _pipeline
