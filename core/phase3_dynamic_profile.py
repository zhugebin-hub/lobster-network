#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 Phase 3 - 动态能力画像系统
功能：
1. 基于真实训练数据动态更新8维度得分
2. 自动识别学员短板并生成改进建议
3. 生成能力画像报告（雷达图数据）
4. 追踪能力变化趋势

作者：诸葛马 (Hermes)
日期：2026-06-30
版本：v1.0
"""

import json
import os
import math
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# ============================================================
# 配置
# ============================================================

class Config:
    """动态能力画像配置"""
    
    # 8维度定义
    DIMENSIONS = {
        "understanding": {"name": "理解力", "weight": 0.15},
        "execution": {"name": "执行力", "weight": 0.15},
        "retrieval": {"name": "检索力", "weight": 0.10},
        "reasoning": {"name": "推理力", "weight": 0.20},
        "reflection": {"name": "反思力", "weight": 0.15},
        "tooling": {"name": "工具力", "weight": 0.10},
        "eq": {"name": "情商", "weight": 0.08},
        "memory": {"name": "记忆力", "weight": 0.07},
    }
    
    # 学员配置
    STUDENTS = {
        "xiaochen": {
            "name": "小陈",
            "type": "稳健型",
            "current_level": "30级",
            "initial_profile": {
                "understanding": 0.72,
                "execution": 0.85,
                "retrieval": 0.78,
                "reasoning": 0.35,
                "reflection": 0.55,
                "tooling": 0.70,
                "eq": 0.68,
                "memory": 0.75,
            },
        },
        "zhuguxia": {
            "name": "诸葛虾",
            "type": "加速型",
            "current_level": "25级",
            "initial_profile": {
                "understanding": 0.88,
                "execution": 0.80,
                "retrieval": 0.82,
                "reasoning": 0.70,
                "reflection": 0.58,
                "tooling": 0.85,
                "eq": 0.75,
                "memory": 0.82,
            },
        },
        "qoder": {
            "name": "qoder",
            "type": "实战型",
            "current_level": "25级",
            "initial_profile": {
                "understanding": 0.78,
                "execution": 0.20,
                "retrieval": 0.65,
                "reasoning": 0.75,
                "reflection": 0.70,
                "tooling": 0.80,
                "eq": 0.72,
                "memory": 0.68,
            },
        },
    }
    
    # 共享目录
    SHARED_DIR = "/home/admin/go-training/shared/"
    RESULTS_DIR = f"{SHARED_DIR}results/"
    PROFILE_DIR = f"{SHARED_DIR}profiles/"
    HISTORY_DIR = f"{SHARED_DIR}profile_history/"
    
    # 更新参数
    LEARNING_RATE = 0.1  # 学习率（每次更新幅度）
    MIN_SAMPLES = 3      # 最少样本数
    DECAY_FACTOR = 0.9   # 历史数据衰减因子


# ============================================================
# 动态能力画像引擎
# ============================================================

class DynamicProfileEngine:
    """动态能力画像引擎"""
    
    def __init__(self):
        self.config = Config()
        self._init_dirs()
    
    def _init_dirs(self):
        os.makedirs(self.config.PROFILE_DIR, exist_ok=True)
        os.makedirs(self.config.HISTORY_DIR, exist_ok=True)
    
    # --- 核心：从训练数据计算能力得分 ---
    
    def calculate_profile_from_training(self, student_id: str, training_records: List[Dict]) -> Dict[str, float]:
        """
        从训练记录计算8维度能力得分
        
        计算逻辑：
        - 理解力：题目类型识别准确率
        - 执行力：任务完成率、提交及时性
        - 检索力：相似题命中率、知识检索速度
        - 推理力：高级题准确率、分步推理正确率
        - 反思力：反思日志质量、错题改进率
        - 工具力：工具使用熟练度、脚本执行成功率
        - 情商：协作表现、对抗赛态度
        - 记忆力：错题重复率、间隔重复效果
        """
        student = self.config.STUDENTS[student_id]
        initial = student["initial_profile"]
        
        # 初始化得分为基础分
        scores = dict(initial)
        
        if len(training_records) < self.config.MIN_SAMPLES:
            return scores  # 样本不足，返回初始值
        
        # 1. 理解力：基于题目类型识别
        understanding_score = self._calc_understanding(training_records)
        scores["understanding"] = self._blend_score(
            initial["understanding"], understanding_score
        )
        
        # 2. 执行力：基于任务完成率和提交及时性
        execution_score = self._calc_execution(training_records)
        scores["execution"] = self._blend_score(
            initial["execution"], execution_score
        )
        
        # 3. 检索力：基于相似题命中率和检索速度
        retrieval_score = self._calc_retrieval(training_records)
        scores["retrieval"] = self._blend_score(
            initial["retrieval"], retrieval_score
        )
        
        # 4. 推理力：基于高级题准确率和分步推理正确率
        reasoning_score = self._calc_reasoning(training_records)
        scores["reasoning"] = self._blend_score(
            initial["reasoning"], reasoning_score
        )
        
        # 5. 反思力：基于反思日志质量和错题改进率
        reflection_score = self._calc_reflection(training_records)
        scores["reflection"] = self._blend_score(
            initial["reflection"], reflection_score
        )
        
        # 6. 工具力：基于工具使用熟练度
        tooling_score = self._calc_tooling(training_records)
        scores["tooling"] = self._blend_score(
            initial["tooling"], tooling_score
        )
        
        # 7. 情商：基于协作表现
        eq_score = self._calc_eq(training_records)
        scores["eq"] = self._blend_score(
            initial["eq"], eq_score
        )
        
        # 8. 记忆力：基于错题重复率
        memory_score = self._calc_memory(training_records)
        scores["memory"] = self._blend_score(
            initial["memory"], memory_score
        )
        
        # 确保得分在0-1范围内
        return {k: round(max(0.0, min(1.0, v)), 2) for k, v in scores.items()}
    
    def _calc_understanding(self, records: List[Dict]) -> float:
        """计算理解力得分"""
        total = 0
        correct = 0
        
        for record in records:
            problems = record.get("problems", [])
            for problem in problems:
                total += 1
                if problem.get("is_correct", False):
                    correct += 1
        
        return correct / total if total > 0 else 0.5
    
    def _calc_execution(self, records: List[Dict]) -> float:
        """计算执行力得分"""
        total_tasks = len(records)
        completed_tasks = sum(1 for r in records if r.get("status") == "completed")
        
        # 提交及时性（假设24小时内提交为及时）
        timely_submissions = 0
        for record in records:
            submitted_at = record.get("submitted_at")
            if submitted_at:
                try:
                    submit_time = datetime.strptime(submitted_at, "%Y-%m-%d %H:%M:%S")
                    task_time = datetime.strptime(record.get("task_assigned_at", submitted_at), "%Y-%m-%d %H:%M:%S")
                    if (submit_time - task_time).total_seconds() < 86400:
                        timely_submissions += 1
                except:
                    pass
        
        completion_rate = completed_tasks / total_tasks if total_tasks > 0 else 0
        timeliness = timely_submissions / total_tasks if total_tasks > 0 else 0
        
        return 0.6 * completion_rate + 0.4 * timeliness
    
    def _calc_retrieval(self, records: List[Dict]) -> float:
        """计算检索力得分"""
        # 基于解题速度（越快说明检索越熟练）
        times = []
        for record in records:
            problems = record.get("problems", [])
            for problem in problems:
                thinking_time = problem.get("thinking_time", 0)
                if thinking_time > 0:
                    times.append(thinking_time)
        
        if not times:
            return 0.5
        
        avg_time = sum(times) / len(times)
        # 假设30秒为基准，越快得分越高
        return max(0.0, min(1.0, 1.0 - (avg_time - 30) / 60))
    
    def _calc_reasoning(self, records: List[Dict]) -> float:
        """计算推理力得分"""
        # 基于高级题准确率和分步推理正确率
        advanced_correct = 0
        advanced_total = 0
        step_correct = 0
        step_total = 0
        
        for record in records:
            problems = record.get("problems", [])
            for problem in problems:
                difficulty = problem.get("difficulty", "入门")
                if difficulty in ["高级", "高级"]:
                    advanced_total += 1
                    if problem.get("is_correct", False):
                        advanced_correct += 1
                
                # 分步推理
                if problem.get("step_by_step", False):
                    step_total += 1
                    if problem.get("reasoning_correct", False):
                        step_correct += 1
        
        advanced_rate = advanced_correct / advanced_total if advanced_total > 0 else 0
        step_rate = step_correct / step_total if step_total > 0 else 0
        
        return 0.7 * advanced_rate + 0.3 * step_rate
    
    def _calc_reflection(self, records: List[Dict]) -> float:
        """计算反思力得分"""
        reflection_count = 0
        total_problems = 0
        improvement_count = 0
        
        for record in records:
            # 检查是否有反思日志
            if record.get("reflection_log"):
                reflection_count += 1
            
            problems = record.get("problems", [])
            total_problems += len(problems)
            
            # 检查错题改进
            for problem in problems:
                if problem.get("was_wrong_before", False) and problem.get("is_correct", False):
                    improvement_count += 1
        
        reflection_rate = reflection_count / len(records) if records else 0
        improvement_rate = improvement_count / total_problems if total_problems > 0 else 0
        
        return 0.5 * reflection_rate + 0.5 * improvement_rate
    
    def _calc_tooling(self, records: List[Dict]) -> float:
        """计算工具力得分"""
        # 基于脚本执行成功率和工具使用频率
        success_count = 0
        total_count = 0
        
        for record in records:
            tool_usage = record.get("tool_usage", {})
            if tool_usage:
                total_count += 1
                if tool_usage.get("success", False):
                    success_count += 1
        
        return success_count / total_count if total_count > 0 else 0.7  # 默认0.7
    
    def _calc_eq(self, records: List[Dict]) -> float:
        """计算情商得分"""
        # 基于协作表现和对抗赛态度
        collaboration_count = 0
        total_interactions = 0
        
        for record in records:
            interactions = record.get("interactions", [])
            total_interactions += len(interactions)
            for interaction in interactions:
                if interaction.get("collaborative", False):
                    collaboration_count += 1
        
        return collaboration_count / total_interactions if total_interactions > 0 else 0.7
    
    def _calc_memory(self, records: List[Dict]) -> float:
        """计算记忆力得分"""
        # 基于错题重复率（越低越好）
        wrong_repeat_count = 0
        total_wrong = 0
        
        for record in records:
            problems = record.get("problems", [])
            for problem in problems:
                if problem.get("was_wrong_before", False):
                    total_wrong += 1
                    if not problem.get("is_correct", False):
                        wrong_repeat_count += 1
        
        # 重复率越低，记忆力越好
        repeat_rate = wrong_repeat_count / total_wrong if total_wrong > 0 else 0
        return 1.0 - repeat_rate
    
    def _blend_score(self, initial: float, calculated: float) -> float:
        """混合初始得分和计算得分"""
        lr = self.config.LEARNING_RATE
        return initial * (1 - lr) + calculated * lr
    
    # --- 能力画像管理 ---
    
    def get_current_profile(self, student_id: str) -> Dict:
        """获取学员当前能力画像"""
        profile_file = os.path.join(self.config.PROFILE_DIR, f"{student_id}_profile.json")
        
        if os.path.exists(profile_file):
            with open(profile_file) as f:
                return json.load(f)
        
        # 返回初始画像
        student = self.config.STUDENTS[student_id]
        return {
            "student_id": student_id,
            "name": student["name"],
            "type": student["type"],
            "current_level": student["current_level"],
            "profile": student["initial_profile"],
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sample_count": 0,
        }
    
    def update_profile(self, student_id: str, training_records: List[Dict]) -> Dict:
        """更新学员能力画像"""
        # 计算新得分
        new_profile = self.calculate_profile_from_training(student_id, training_records)
        
        # 获取旧画像
        old_profile = self.get_current_profile(student_id)
        
        # 保存历史
        self._save_history(student_id, old_profile)
        
        # 更新画像
        student = self.config.STUDENTS[student_id]
        updated = {
            "student_id": student_id,
            "name": student["name"],
            "type": student["type"],
            "current_level": student["current_level"],
            "profile": new_profile,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sample_count": len(training_records),
            "changes": self._calculate_changes(old_profile.get("profile", {}), new_profile),
        }
        
        # 保存新画像
        profile_file = os.path.join(self.config.PROFILE_DIR, f"{student_id}_profile.json")
        with open(profile_file, "w") as f:
            json.dump(updated, f, ensure_ascii=False, indent=2)
        
        return updated
    
    def _calculate_changes(self, old: Dict, new: Dict) -> Dict[str, Dict]:
        """计算能力变化"""
        changes = {}
        for dim in self.config.DIMENSIONS:
            old_val = old.get(dim, 0)
            new_val = new.get(dim, 0)
            delta = new_val - old_val
            
            changes[dim] = {
                "old": old_val,
                "new": new_val,
                "delta": round(delta, 3),
                "trend": "↑" if delta > 0.01 else "↓" if delta < -0.01 else "→",
            }
        
        return changes
    
    def _save_history(self, student_id: str, profile: Dict):
        """保存历史画像"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        history_file = os.path.join(
            self.config.HISTORY_DIR,
            f"{student_id}_profile_{timestamp}.json"
        )
        with open(history_file, "w") as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)
    
    # --- 短板识别 ---
    
    def identify_weaknesses(self, student_id: str) -> List[Dict]:
        """识别学员短板"""
        profile = self.get_current_profile(student_id)
        weaknesses = []
        
        for dim, info in self.config.DIMENSIONS.items():
            score = profile.get("profile", {}).get(dim, 0)
            
            if score < 0.5:
                severity = "Critical"
                priority = "高"
            elif score < 0.65:
                severity = "Warning"
                priority = "中"
            else:
                continue
            
            weaknesses.append({
                "dimension": dim,
                "name": info["name"],
                "score": score,
                "severity": severity,
                "priority": priority,
                "target": 0.70,
                "gap": round(0.70 - score, 2),
            })
        
        # 按严重程度排序
        weaknesses.sort(key=lambda x: x["score"])
        return weaknesses
    
    # --- 趋势分析 ---
    
    def analyze_trend(self, student_id: str, days: int = 7) -> Dict:
        """分析能力变化趋势"""
        history_dir = self.config.HISTORY_DIR
        profiles = []
        
        # 读取历史画像
        for filename in sorted(os.listdir(history_dir)):
            if filename.startswith(f"{student_id}_profile_") and filename.endswith(".json"):
                filepath = os.path.join(history_dir, filename)
                try:
                    with open(filepath) as f:
                        profile = json.load(f)
                    profiles.append(profile)
                except:
                    continue
        
        if len(profiles) < 2:
            return {"message": "历史数据不足，无法分析趋势"}
        
        # 计算各维度变化趋势
        trends = {}
        for dim in self.config.DIMENSIONS:
            values = []
            for profile in profiles:
                score = profile.get("profile", {}).get(dim, 0)
                values.append(score)
            
            if len(values) >= 2:
                # 简单线性回归
                n = len(values)
                x_mean = (n - 1) / 2
                y_mean = sum(values) / n
                
                numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
                denominator = sum((i - x_mean) ** 2 for i in range(n))
                
                slope = numerator / denominator if denominator != 0 else 0
                
                trends[dim] = {
                    "values": values,
                    "slope": round(slope, 4),
                    "trend": "上升" if slope > 0.001 else "下降" if slope < -0.001 else "稳定",
                    "start": values[0],
                    "end": values[-1],
                    "change": round(values[-1] - values[0], 3),
                }
        
        return {
            "student_id": student_id,
            "days": days,
            "sample_count": len(profiles),
            "trends": trends,
        }
    
    # --- 报告生成 ---
    
    def generate_profile_report(self, student_id: str) -> str:
        """生成能力画像报告（Markdown）"""
        profile = self.get_current_profile(student_id)
        weaknesses = self.identify_weaknesses(student_id)
        trend = self.analyze_trend(student_id)
        
        md = []
        md.append(f"# 📊 {profile['name']} 能力画像报告")
        md.append(f"\n> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        md.append(f"> 学员类型：{profile['type']}")
        md.append(f"> 当前等级：{profile['current_level']}")
        md.append(f"> 样本数量：{profile.get('sample_count', 0)}")
        md.append("")
        
        # 8维度得分
        md.append("## 📈 8维度能力得分")
        md.append("")
        md.append("| 维度 | 得分 | 等级 | 趋势 |")
        md.append("|------|------|------|------|")
        
        for dim, info in self.config.DIMENSIONS.items():
            score = profile.get("profile", {}).get(dim, 0)
            grade = self._score_to_grade(score)
            
            trend_info = trend.get("trends", {}).get(dim, {})
            trend_str = trend_info.get("trend", "N/A")
            
            md.append(f"| {info['name']} | {score:.2f} | {grade} | {trend_str} |")
        
        md.append("")
        
        # 短板分析
        if weaknesses:
            md.append("## ⚠️ 短板分析")
            md.append("")
            md.append("| 维度 | 得分 | 严重程度 | 目标 | 差距 |")
            md.append("|------|------|----------|------|------|")
            
            for w in weaknesses:
                md.append(f"| {w['name']} | {w['score']:.2f} | {w['severity']} | {w['target']:.2f} | {w['gap']:.2f} |")
            
            md.append("")
            
            # 改进建议
            md.append("## 💡 改进建议")
            md.append("")
            for w in weaknesses:
                md.append(f"- **{w['name']}**（{w['severity']}）：从{w['score']:.2f}提升到{w['target']:.2f}，差距{w['gap']:.2f}")
            
            md.append("")
        
        # 雷达图数据（JSON格式，可用于前端渲染）
        md.append("## 📊 雷达图数据")
        md.append("")
        md.append("```json")
        radar_data = {
            dim: profile.get("profile", {}).get(dim, 0)
            for dim in self.config.DIMENSIONS
        }
        md.append(json.dumps(radar_data, ensure_ascii=False, indent=2))
        md.append("```")
        
        md.append("")
        md.append("---")
        md.append(f"*报告由诸葛马 (Hermes) 动态能力画像系统 v1.0 自动生成*")
        
        return "\n".join(md)
    
    def _score_to_grade(self, score: float) -> str:
        """分数转等级"""
        if score >= 0.90: return "S"
        if score >= 0.80: return "A"
        if score >= 0.70: return "B"
        if score >= 0.60: return "C"
        if score >= 0.50: return "D"
        return "E"


# ============================================================
# 命令行接口
# ============================================================

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="动态能力画像系统")
    parser.add_argument("action", choices=["profile", "update", "weakness", "trend", "report"],
                       help="操作: profile(查看画像) | update(更新画像) | weakness(短板) | trend(趋势) | report(报告)")
    parser.add_argument("--student", type=str, required=True, help="学员ID")
    parser.add_argument("--training-file", type=str, help="训练数据文件（用于update）")
    
    args = parser.parse_args()
    engine = DynamicProfileEngine()
    
    if args.action == "profile":
        profile = engine.get_current_profile(args.student)
        print(json.dumps(profile, ensure_ascii=False, indent=2))
    
    elif args.action == "update":
        if args.training_file and os.path.exists(args.training_file):
            with open(args.training_file) as f:
                records = json.load(f)
            if not isinstance(records, list):
                records = [records]
            updated = engine.update_profile(args.student, records)
            print(json.dumps(updated, ensure_ascii=False, indent=2))
        else:
            print("❌ 请提供有效的训练数据文件")
    
    elif args.action == "weakness":
        weaknesses = engine.identify_weaknesses(args.student)
        print(json.dumps(weaknesses, ensure_ascii=False, indent=2))
    
    elif args.action == "trend":
        trend = engine.analyze_trend(args.student)
        print(json.dumps(trend, ensure_ascii=False, indent=2))
    
    elif args.action == "report":
        report = engine.generate_profile_report(args.student)
        print(report)
        
        # 保存报告
        report_file = os.path.join(
            engine.config.PROFILE_DIR,
            f"{args.student}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )
        with open(report_file, "w") as f:
            f.write(report)
        print(f"\n📝 报告已保存: {report_file}")


if __name__ == "__main__":
    main()
