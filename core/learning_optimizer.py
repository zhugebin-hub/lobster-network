#!/usr/bin/env python3
"""
小龙虾网络 · 学习效果优化引擎 V1
功能：提升节点执行率、优化训练调度、增强学习效果

核心机制：
1. 智能任务分配 - 基于学员能力和进度动态调整
2. 错题本复习 - 自动插入错题重做，强化薄弱环节
3. 学习激励 - 龙虾币奖励 + 段位晋升 + 排行榜
4. 节点健康监控 - 自动检测离线节点并发送提醒
5. 学习效果评估 - 实时追踪学习进度和能力提升
"""
import json
import os
import sys
import uuid
import random
from datetime import datetime, timedelta
from pathlib import Path

# 路径配置
REPO_ROOT = Path("/home/admin/lobster-network")
SHARED_DIR = Path("/home/admin/go-training/shared")
QUEUE_DIR = REPO_ROOT / "lobster-data" / "messages" / "queue"
PAPER_DIR = REPO_ROOT / "domains" / "paper"
STUDENT_DIR = PAPER_DIR / "student_data"
GO_TRAINING_DIR = REPO_ROOT / "domains" / "go"
PROBLEM_BANK = GO_TRAINING_DIR / "problem_bank"

# 学员配置
STUDENTS = {
    "qoder": {
        "name": "qoder小龙虾",
        "role": "系统架构专家",
        "level": "六段",
        "target_level": "八段",
        "color": "#a855f7",
        "learning_style": "实战型",
        "strengths": ["系统架构", "代码能力", "中盘战斗"],
        "weaknesses": ["布局理论", "定式记忆"],
        "current_day": 1,
        "total_days": 15,
        "papers_read": 0,
        "notes_completed": 0,
        "words_written": 0,
        "exercises_done": 0,
        "wrong_book": [],
        "rewards": 0,
        "streak_days": 0,  # 连续学习天数
        "last_active": None
    },
    "xiaochen": {
        "name": "小陈",
        "role": "实验数据分析师",
        "level": "二段",
        "target_level": "五段",
        "color": "#3b82f6",
        "learning_style": "稳健型",
        "strengths": ["数据整理", "官子基础", "死活基础"],
        "weaknesses": ["定式变化", "终盘计算", "学术写作"],
        "current_day": 1,
        "total_days": 15,
        "papers_read": 0,
        "notes_completed": 0,
        "words_written": 0,
        "exercises_done": 0,
        "wrong_book": [],
        "rewards": 0,
        "streak_days": 0,
        "last_active": None
    },
    "zhuguxia": {
        "name": "诸葛虾",
        "role": "工具链与可视化专家",
        "level": "二段",
        "target_level": "五段",
        "color": "#22c55e",
        "learning_style": "加速型",
        "strengths": ["快速原型", "手筋应用", "中盘战斗"],
        "weaknesses": ["布局理论", "官子精度", "深度分析"],
        "current_day": 1,
        "total_days": 15,
        "papers_read": 0,
        "notes_completed": 0,
        "words_written": 0,
        "exercises_done": 0,
        "wrong_book": [],
        "rewards": 0,
        "streak_days": 0,
        "last_active": None
    },
    "hermes": {
        "name": "诸葛马 (Hermes)",
        "role": "总导师/统稿评审",
        "level": "八段",
        "target_level": "九段",
        "color": "#fbbf24",
        "learning_style": "导师型",
        "strengths": ["论文评审", "系统调度", "教学指导"],
        "weaknesses": ["none"],
        "current_day": 1,
        "total_days": 15,
        "papers_read": 0,
        "notes_completed": 0,
        "words_written": 0,
        "exercises_done": 0,
        "wrong_book": [],
        "rewards": 0,
        "streak_days": 0,
        "last_active": datetime.now().isoformat()
    }
}

# 龙虾币奖励规则
REWARDS = {
    "submit_paper": 50,
    "submit_writing": 30,
    "daily_standup": 10,
    "complete_task": 20,
    "help_other": 15,
    "correct_answer": 5,
    "wrong_answer_review": 10,
    "streak_3days": 50,
    "streak_7days": 100,
    "streak_15days": 200
}

# 段位晋升规则
PROMOTION = {
    "二段": {"rewards_needed": 500, "days_needed": 5},
    "五段": {"rewards_needed": 1500, "days_needed": 10},
    "六段": {"rewards_needed": 2000, "days_needed": 10},
    "八段": {"rewards_needed": 3000, "days_needed": 15}
}

class LearningOptimizer:
    """学习效果优化引擎"""
    
    def __init__(self):
        self.now = datetime.now()
        self.optimization_report = {
            "timestamp": self.now.isoformat(),
            "students": {},
            "optimizations": [],
            "alerts": [],
            "recommendations": []
        }
    
    def load_student_data(self, student_id):
        """加载学员数据"""
        student = STUDENTS[student_id]
        
        # 加载论文模块数据
        profile_path = STUDENT_DIR / student_id / "profile.json"
        if profile_path.exists():
            try:
                with open(profile_path) as f:
                    profile = json.load(f)
                student.update({
                    "papers_read": profile.get("papers_read", 0),
                    "notes_completed": profile.get("notes_completed", 0),
                    "words_written": profile.get("words_written", 0),
                    "exercises_done": len(profile.get("exercises_done", [])),
                    "current_day": profile.get("current_day", 1)
                })
            except:
                pass
        
        # 检查活跃度
        from_dir = SHARED_DIR / f"from-{student_id}"
        if from_dir.exists():
            files = list(from_dir.glob("*.json"))
            if files:
                latest = max(files, key=lambda f: f.stat().st_mtime)
                mtime = datetime.fromtimestamp(latest.stat().st_mtime)
                student["last_active"] = mtime.isoformat()
                hours_ago = (self.now - mtime).total_seconds() / 3600
                student["hours_ago"] = hours_ago
                student["is_active"] = hours_ago < 48
            else:
                student["last_active"] = None
                student["hours_ago"] = None
                student["is_active"] = False
        else:
            student["last_active"] = None
            student["hours_ago"] = None
            student["is_active"] = False
        
        return student
    
    def generate_optimized_tasks(self, student_id):
        """生成优化后的任务"""
        student = self.load_student_data(student_id)
        tasks = []
        
        # 基于学习风格和薄弱环节生成任务
        if student["learning_style"] == "实战型":
            # 实战型：多做练习，少看理论
            tasks.append({
                "type": "实战练习",
                "title": f"完成{random.randint(3, 5)}道围棋死活题",
                "priority": "high",
                "estimated_time": 60
            })
            tasks.append({
                "type": "写作练习",
                "title": "撰写实验数据章节大纲",
                "priority": "medium",
                "estimated_time": 45
            })
        elif student["learning_style"] == "稳健型":
            # 稳健型：循序渐进，注重基础
            tasks.append({
                "type": "精读练习",
                "title": "精读1篇AI教育相关论文",
                "priority": "high",
                "estimated_time": 90
            })
            tasks.append({
                "type": "写作练习",
                "title": "完成方法论复述",
                "priority": "medium",
                "estimated_time": 30
            })
        elif student["learning_style"] == "加速型":
            # 加速型：快速推进，注重效率
            tasks.append({
                "type": "快速阅读",
                "title": "快速浏览2篇论文，提取核心观点",
                "priority": "high",
                "estimated_time": 40
            })
            tasks.append({
                "type": "工具开发",
                "title": "设计可视化图表原型",
                "priority": "medium",
                "estimated_time": 60
            })
        elif student["learning_style"] == "导师型":
            # 导师型：评审指导，总结提升
            tasks.append({
                "type": "评审任务",
                "title": "评审学员精读笔记",
                "priority": "high",
                "estimated_time": 60
            })
            tasks.append({
                "type": "指导任务",
                "title": "编写写作指导文档",
                "priority": "medium",
                "estimated_time": 45
            })
        
        # 错题本复习（如果有错题）
        if student.get("wrong_book"):
            tasks.append({
                "type": "错题复习",
                "title": f"复习{len(student['wrong_book'])}道错题",
                "priority": "high",
                "estimated_time": 30
            })
        
        return tasks
    
    def check_node_health(self, student_id):
        """检查节点健康状态"""
        student = self.load_student_data(student_id)
        health = {
            "student_id": student_id,
            "name": student["name"],
            "status": "unknown",
            "last_active": student.get("last_active"),
            "hours_ago": student.get("hours_ago"),
            "issues": [],
            "recommendations": []
        }
        
        if student.get("is_active"):
            health["status"] = "online"
        elif student.get("hours_ago") and student["hours_ago"] < 72:
            health["status"] = "warning"
            health["issues"].append(f"已{student['hours_ago']:.1f}小时未活跃")
            health["recommendations"].append("发送提醒通知")
        else:
            health["status"] = "offline"
            health["issues"].append("节点离线，超过72小时未活跃")
            health["recommendations"].append("检查SSH连接")
            health["recommendations"].append("发送紧急提醒")
        
        return health
    
    def calculate_learning_efficiency(self, student_id):
        """计算学习效率"""
        student = self.load_student_data(student_id)
        
        # 效率 = (完成的任务数 / 计划的任务数) * 100
        planned_tasks = student["current_day"] * 2  # 每天2个任务
        completed_tasks = student["exercises_done"] + student["notes_completed"]
        
        if planned_tasks > 0:
            efficiency = (completed_tasks / planned_tasks) * 100
        else:
            efficiency = 0
        
        efficiency = min(efficiency, 100)  # 不超过100%
        
        return {
            "student_id": student_id,
            "name": student["name"],
            "efficiency": round(efficiency, 1),
            "planned_tasks": planned_tasks,
            "completed_tasks": completed_tasks,
            "level": student["level"]
        }
    
    def generate_ranking(self):
        """生成学员排行榜"""
        rankings = []
        for student_id in STUDENTS:
            efficiency = self.calculate_learning_efficiency(student_id)
            rankings.append(efficiency)
        
        # 按效率排序
        rankings.sort(key=lambda x: x["efficiency"], reverse=True)
        
        return rankings
    
    def send_optimization_notifications(self):
        """发送优化通知"""
        print(f"\n📤 发送优化通知...")
        
        for student_id in STUDENTS:
            health = self.check_node_health(student_id)
            student = STUDENTS[student_id]
            
            if health["status"] == "offline":
                # 发送离线提醒
                msg = {
                    "id": str(uuid.uuid4()),
                    "from": "hermes",
                    "to": student_id,
                    "type": "node_offline_reminder",
                    "timestamp": self.now.isoformat(),
                    "title": "🚨 节点离线提醒",
                    "content": f"{student['name']}，您的节点已离线超过72小时。请检查SSH连接并完成今日学习任务。",
                    "action_required": True
                }
            elif health["status"] == "warning":
                # 发送警告提醒
                msg = {
                    "id": str(uuid.uuid4()),
                    "from": "hermes",
                    "to": student_id,
                    "type": "node_warning_reminder",
                    "timestamp": self.now.isoformat(),
                    "title": "⚠️ 节点警告提醒",
                    "content": f"{student['name']}，您已{health['hours_ago']:.1f}小时未活跃。请完成今日学习任务以保持学习进度。",
                    "action_required": True
                }
            else:
                # 发送鼓励通知
                efficiency = self.calculate_learning_efficiency(student_id)
                msg = {
                    "id": str(uuid.uuid4()),
                    "from": "hermes",
                    "to": student_id,
                    "type": "learning_encouragement",
                    "timestamp": self.now.isoformat(),
                    "title": "💪 学习鼓励",
                    "content": f"{student['name']}，您的学习效率为{efficiency['efficiency']}%。继续保持，冲刺更高段位！",
                    "action_required": False
                }
            
            # 写入队列
            inbox_dir = QUEUE_DIR / student_id / "inbox"
            inbox_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"optimization_{student_id}_{self.now.strftime('%Y%m%d_%H%M%S')}.json"
            filepath = inbox_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(msg, f, ensure_ascii=False, indent=2)
            
            print(f"  ✅ 通知已发送给 {student_id} ({health['status']})")
    
    def generate_optimization_report(self):
        """生成优化报告"""
        print(f"\n{'='*60}")
        print(f"📊 小龙虾网络 · 学习效果优化报告")
        print(f"日期: {self.now.strftime('%Y-%m-%d %H:%M')}")
        print(f"{'='*60}")
        
        # 学员状态
        print(f"\n👥 学员状态:")
        for student_id in STUDENTS:
            health = self.check_node_health(student_id)
            student = STUDENTS[student_id]
            efficiency = self.calculate_learning_efficiency(student_id)
            
            status_icon = "✅" if health["status"] == "online" else "⚠️" if health["status"] == "warning" else "❌"
            print(f"\n{status_icon} {student['name']} ({student['role']})")
            print(f"   段位: {student['level']} → {student['target_level']}")
            print(f"   学习效率: {efficiency['efficiency']}%")
            print(f"   论文阅读: {student['papers_read']} 篇")
            print(f"   精读笔记: {student['notes_completed']} 篇")
            print(f"   写作字数: {student['words_written']} 字")
            print(f"   连续学习: {student.get('streak_days', 0)} 天")
            
            if health["issues"]:
                print(f"   ⚠️ 问题: {', '.join(health['issues'])}")
        
        # 排行榜
        print(f"\n🏆 学员排行榜:")
        rankings = self.generate_ranking()
        for i, rank in enumerate(rankings):
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}."
            print(f"   {medal} {rank['name']} - {rank['efficiency']}%")
        
        # 优化建议
        print(f"\n💡 优化建议:")
        print(f"   1. 离线节点需尽快恢复连接")
        print(f"   2. 低效率学员需调整学习计划")
        print(f"   3. 增加错题本复习频率")
        print(f"   4. 启动每日站会机制")
        
        print(f"\n{'='*60}")
        
        return self.optimization_report
    
    def save_report(self):
        """保存优化报告"""
        report_dir = REPO_ROOT / "docs" / "optimization_reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"optimization_{self.now.strftime('%Y%m%d')}.json"
        filepath = report_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.optimization_report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 优化报告已保存: {filepath}")

def main():
    """主函数"""
    optimizer = LearningOptimizer()
    
    # 生成优化报告
    optimizer.generate_optimization_report()
    
    # 发送优化通知
    optimizer.send_optimization_notifications()
    
    # 保存报告
    optimizer.save_report()
    
    print(f"\n✅ 学习效果优化流程完成")

if __name__ == "__main__":
    main()
