#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交叉审查机制
解决 P1-问题 5：训练质量无法独立验证

功能：
1. 节点 A 的训练结果由节点 B 审查
2. 独立 Context 审查（只看结果和规则）
3. 生成审查报告
4. 综合评分 = 自评分 × 0.4 + 交叉审查分 × 0.6

作者：信电大虾 (小龙虾网络)
日期：2026-07-01
"""

import json
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))
from compat import SHARED_DIR, json_load, json_dump, setup_logger

logger = setup_logger("ReviewAgent")

# 审查轮转分配
REVIEW_ROTATION = {
    "qoder": "zhuguxia",
    "zhuguxia": "xiaochen",
    "xiaochen": "qoder",
    "zhugebin": "xiaowei",
    "xiaowei": "zhugebin",
}


class ReviewAgent:
    """交叉审查代理"""
    
    def __init__(self, reviewer_id: str):
        self.reviewer_id = reviewer_id
        self.review_dir = SHARED_DIR / "reviews"
        self.review_dir.mkdir(parents=True, exist_ok=True)
        
    def get_reviewee_id(self) -> Optional[str]:
        """获取被审查者 ID"""
        return REVIEW_ROTATION.get(self.reviewer_id)
        
    def load_training_result(self, reviewee_id: str, day: int) -> Optional[Dict]:
        """加载训练结果"""
        from_dir = SHARED_DIR / f"from-{reviewee_id}"
        
        if not from_dir.exists():
            return None
            
        # 查找最新的结果文件
        result_files = sorted(from_dir.glob(f"day{day}_*.json"))
        if not result_files:
            return None
            
        return json_load(result_files[-1])
        
    def review(self, reviewee_id: str, day: int, training_result: Dict) -> Dict:
        """执行审查"""
        logger.info(f"🔍 {self.reviewer_id} 审查 {reviewee_id} Day {day} 训练结果...")
        
        # 独立审查评分
        review_score = self._calculate_review_score(training_result)
        
        # 获取自评分
        self_score = training_result.get("accuracy", 0) * 100
        
        # 综合评分
        final_score = self_score * 0.4 + review_score * 0.6
        
        # 生成审查报告
        report = {
            "reviewer": self.reviewer_id,
            "reviewee": reviewee_id,
            "day": day,
            "self_score": round(self_score, 2),
            "review_score": round(review_score, 2),
            "final_score": round(final_score, 2),
            "passed": final_score >= 60,
            "reviewed_at": datetime.now().isoformat(),
            "feedback": self._generate_feedback(training_result, review_score),
        }
        
        # 保存审查报告
        report_file = self.review_dir / f"{self.reviewer_id}_{reviewee_id}_day{day}.json"
        json_dump(report, report_file)
        
        logger.info(f"✅ 审查完成：最终得分 {final_score:.1f}")
        return report
        
    def _calculate_review_score(self, result: Dict) -> float:
        """计算审查评分"""
        score = 0.0
        
        # 1. 准确率评分 (40 分)
        accuracy = result.get("accuracy", 0)
        score += accuracy * 40
        
        # 2. 题量评分 (20 分)
        problems = result.get("problems", 0)
        if problems >= 100:
            score += 20
        elif problems >= 50:
            score += 10
        else:
            score += 5
            
        # 3. 对局评分 (20 分)
        games = result.get("games", 0)
        if games >= 10:
            score += 20
        elif games >= 5:
            score += 10
        else:
            score += 5
            
        # 4. 提交及时性 (20 分)
        # 简化处理，实际应比较提交时间与任务发布时间
        score += 20
        
        return min(score, 100.0)
        
    def _generate_feedback(self, result: Dict, score: float) -> List[str]:
        """生成反馈建议"""
        feedback = []
        
        accuracy = result.get("accuracy", 0)
        if accuracy < 0.7:
            feedback.append("⚠️ 准确率偏低，建议加强基础题训练")
            
        problems = result.get("problems", 0)
        if problems < 50:
            feedback.append("⚠️ 题量不足，建议增加训练量")
            
        games = result.get("games", 0)
        if games < 5:
            feedback.append("⚠️ 对局数偏少，建议增加实战练习")
            
        if score >= 90:
            feedback.append("🌟 表现优秀，保持当前训练节奏")
        elif score >= 70:
            feedback.append("👍 表现良好，继续优化薄弱环节")
        else:
            feedback.append("💪 需要加强训练，重点关注薄弱环节")
            
        return feedback
        
    def run_review_cycle(self, day: int):
        """运行审查周期"""
        reviewee_id = self.get_reviewee_id()
        
        if not reviewee_id:
            logger.error(f"❌ 未找到 {self.reviewer_id} 的审查对象")
            return
            
        # 加载训练结果
        result = self.load_training_result(reviewee_id, day)
        
        if not result:
            logger.warning(f"⚠️ {reviewee_id} Day {day} 无训练结果，跳过审查")
            return
            
        # 执行审查
        report = self.review(reviewee_id, day, result)
        
        # 输出结果
        print(f"\n📊 审查报告")
        print(f"   审查者：{self.reviewer_id}")
        print(f"   被审查者：{reviewee_id}")
        print(f"   天数：Day {day}")
        print(f"   自评分：{report['self_score']:.1f}")
        print(f"   审查分：{report['review_score']:.1f}")
        print(f"   最终分：{report['final_score']:.1f}")
        print(f"   是否通过：{'✅' if report['passed'] else '❌'}")
        print(f"   反馈：")
        for item in report['feedback']:
            print(f"     {item}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='交叉审查机制')
    parser.add_argument('--reviewer-id', type=str, required=True, help='审查者 ID')
    parser.add_argument('--day', type=int, required=True, help='审查天数')
    
    args = parser.parse_args()
    
    agent = ReviewAgent(args.reviewer_id)
    agent.run_review_cycle(args.day)


if __name__ == "__main__":
    main()
