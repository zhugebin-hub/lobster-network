#!/usr/bin/env python3
"""
🦞 小龙虾网络 · 大小模型路由
版本: V1.0 | 日期: 2026-06-28
功能: 根据题目难度自动分配算力，降本增效
"""
class ModelRouter:
    def __init__(self):
        self.small_model = "qwen-turbo"   # 低成本，快
        self.large_model = "qwen-max"     # 高成本，强推理
    
    def route(self, problem: dict) -> str:
        difficulty = problem.get("difficulty", "初级")
        module = problem.get("module", "")
        
        # 路由策略
        if difficulty in ["入门", "初级"] or module in ["概念选择", "基础计算"]:
            return self.small_model
        elif difficulty in ["中级", "高级"] or module in ["逻辑推理", "代码生成", "围棋死活"]:
            return self.large_model
        return self.small_model # 默认小模型

    def estimate_cost(self, model: str, tokens: int) -> float:
        rate = 0.002 if model == self.small_model else 0.02 # 假设费率
        return tokens * rate

if __name__ == "__main__":
    router = ModelRouter()
    probs = [
        {"difficulty": "入门", "module": "概念选择"},
        {"difficulty": "高级", "module": "围棋死活"},
        {"difficulty": "中级", "module": "逻辑推理"}
    ]
    for p in probs:
        m = router.route(p)
        cost = router.estimate_cost(m, 1000)
        print(f"📤 路由: {p['difficulty']} -> {m} (预估成本: ¥{cost:.4f})")
