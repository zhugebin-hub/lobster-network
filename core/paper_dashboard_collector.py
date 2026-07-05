#!/usr/bin/env python3
"""
论文写作指挥中心数据采集器
实时采集论文学习进度、学员状态、合著论文进展
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

class PaperDataCollector:
    """论文写作数据采集器"""
    
    def __init__(self):
        self.now = datetime.now()
        self.paper_dir = Path("/home/admin/lobster-network/domains/paper")
        self.student_dir = self.paper_dir / "student_data"
        self.problem_bank = self.paper_dir / "problem_bank"
        self.docs_dir = self.paper_dir / "docs"
        self.queue_dir = Path("/home/admin/lobster-network/lobster-data/messages/queue")
    
    def collect_students(self):
        """收集所有学员数据"""
        students = {}
        
        student_configs = {
            "qoder": {
                "name": "qoder小龙虾",
                "role": "系统架构专家",
                "level": "六段",
                "target_level": "八段",
                "color": "#a855f7",
                "collaborative_role": "引言+方法+统稿",
                "specialty": "system_architecture",
                "weakness": "experiment_design"
            },
            "xiaochen": {
                "name": "小陈",
                "role": "实验数据分析师",
                "level": "二段",
                "target_level": "五段",
                "color": "#3b82f6",
                "collaborative_role": "实验数据",
                "specialty": "data_analysis",
                "weakness": "academic_writing"
            },
            "zhuguxia": {
                "name": "诸葛虾",
                "role": "工具链与可视化专家",
                "level": "二段",
                "target_level": "五段",
                "color": "#22c55e",
                "collaborative_role": "工具链+可视化",
                "specialty": "rapid_prototyping",
                "weakness": "deep_analysis"
            },
            "hermes": {
                "name": "诸葛马 (Hermes)",
                "role": "总导师/统稿评审",
                "level": "八段",
                "target_level": "九段",
                "color": "#fbbf24",
                "collaborative_role": "总导师/统稿评审",
                "specialty": "paper_review",
                "weakness": "none"
            }
        }
        
        for sid, config in student_configs.items():
            student_path = self.student_dir / sid
            profile_path = student_path / "profile.json"
            
            student_data = {
                "id": sid,
                **config,
                "status": "unknown",
                "current_day": 1,
                "papers_read": 0,
                "papers_target": 15 if sid == "qoder" else 10 if sid != "hermes" else 20,
                "notes_completed": 0,
                "words_written": 0,
                "words_target": 50000 if sid == "qoder" else 30000 if sid != "hermes" else 40000,
                "exercises_done": 0,
                "review_progress": {},
                "recent_activities": [],
                "tasks": []
            }
            
            # 读取profile.json
            if profile_path.exists():
                try:
                    with open(profile_path) as f:
                        profile = json.load(f)
                    student_data.update({
                        "current_day": profile.get("current_day", 1),
                        "papers_read": profile.get("papers_read", 0),
                        "notes_completed": profile.get("notes_completed", 0),
                        "words_written": profile.get("words_written", 0),
                        "exercises_done": len(profile.get("exercises_done", [])),
                        "review_queue": profile.get("review_queue", []),
                        "status": "active"
                    })
                except:
                    pass
            
            # 检查通知消息
            inbox_dir = self.queue_dir / sid / "inbox"
            if inbox_dir.exists():
                paper_msgs = list(inbox_dir.glob("paper_launch_*.json"))
                student_data["notification_received"] = len(paper_msgs) > 0
                student_data["pending_messages"] = len(list(inbox_dir.glob("*.json")))
            else:
                student_data["notification_received"] = False
                student_data["pending_messages"] = 0
            
            # 生成模拟进度（基于当前是第1天）
            if sid == "hermes":
                student_data["progress_pct"] = 5  # 导师刚加入
            else:
                student_data["progress_pct"] = 0  # 刚开始
            
            students[sid] = student_data
        
        return students
    
    def collect_collaborative_paper(self):
        """收集合著论文进度"""
        paper = {
            "title": "小龙虾网络：基于大语言模型的多智能体围棋教育框架",
            "status": "planning",
            "current_phase": "Phase 1: 基础训练",
            "day": 1,
            "total_days": 15,
            "sections": {
                "abstract": {
                    "name": "摘要",
                    "owner": "qoder起草，全员修改",
                    "status": "pending",
                    "progress": 0,
                    "word_count": 0,
                    "target_words": 300
                },
                "introduction": {
                    "name": "1. 引言",
                    "owner": "qoder",
                    "status": "pending",
                    "progress": 0,
                    "word_count": 0,
                    "target_words": 3000
                },
                "related_work": {
                    "name": "2. 相关工作",
                    "owner": "诸葛虾",
                    "status": "pending",
                    "progress": 0,
                    "word_count": 0,
                    "target_words": 2500
                },
                "method": {
                    "name": "3. 方法",
                    "owner": "qoder",
                    "status": "pending",
                    "progress": 0,
                    "word_count": 0,
                    "target_words": 4000
                },
                "experiment": {
                    "name": "4. 实验",
                    "owner": "小陈",
                    "status": "pending",
                    "progress": 0,
                    "word_count": 0,
                    "target_words": 3500
                },
                "tools": {
                    "name": "5. 工具链",
                    "owner": "诸葛虾",
                    "status": "pending",
                    "progress": 0,
                    "word_count": 0,
                    "target_words": 2000
                },
                "conclusion": {
                    "name": "6. 结论",
                    "owner": "全员",
                    "status": "pending",
                    "progress": 0,
                    "word_count": 0,
                    "target_words": 1500
                },
                "references": {
                    "name": "参考文献",
                    "owner": "诸葛虾",
                    "status": "pending",
                    "progress": 0,
                    "word_count": 0,
                    "target_words": 2000
                }
            },
            "milestones": [
                {"day": 5, "name": "Phase 1 完成", "status": "pending", "description": "精读笔记完成，引言草稿"},
                {"day": 10, "name": "Phase 2 完成", "status": "pending", "description": "初稿汇总，方法章节完成"},
                {"day": 15, "name": "Phase 3 完成", "status": "pending", "description": "投稿准备，格式调整"}
            ]
        }
        
        # 计算总体进度
        total_progress = sum(s["progress"] for s in paper["sections"].values())
        paper["overall_progress"] = total_progress / len(paper["sections"])
        
        return paper
    
    def collect_training_tasks(self):
        """收集训练任务"""
        tasks = {
            "qoder": [
                {"id": "t1", "type": "阅读练习", "difficulty": "六段", "title": "文献综述片段", "status": "pending", "time_limit": 90},
                {"id": "t2", "type": "写作练习", "difficulty": "六段", "title": "相关工作章节", "status": "pending", "time_limit": 120}
            ],
            "xiaochen": [
                {"id": "t3", "type": "阅读练习", "difficulty": "二段", "title": "方法论复述", "status": "pending", "time_limit": 30},
                {"id": "t4", "type": "写作练习", "difficulty": "二段", "title": "英文摘要撰写", "status": "pending", "time_limit": 45}
            ],
            "zhuguxia": [
                {"id": "t5", "type": "阅读练习", "difficulty": "二段", "title": "方法论复述", "status": "pending", "time_limit": 30},
                {"id": "t6", "type": "写作练习", "difficulty": "二段", "title": "英文摘要撰写", "status": "pending", "time_limit": 45}
            ],
            "hermes": [
                {"id": "t7", "type": "阅读练习", "difficulty": "八段", "title": "完整方法论章节", "status": "pending", "time_limit": 180},
                {"id": "t8", "type": "写作练习", "difficulty": "八段", "title": "审稿回复信", "status": "pending", "time_limit": 120}
            ]
        }
        return tasks
    
    def collect_documents(self):
        """收集文档状态"""
        docs = []
        
        doc_files = {
            "PAPER_LEARNING_PLAN_V1.md": "训练计划 - 15天三龙虾学术协同作战方案",
            "COLLABORATIVE_PLAN.md": "协同作战计划 - 全员参与方案",
            "PAPER_READING_TEMPLATE.md": "精读模板 - 三遍阅读法",
            "WRITING_WORKFLOW.md": "写作工作流 - 七阶段流程",
            "JOURNAL_GUIDE.md": "期刊指南 - 投稿决策树"
        }
        
        for filename, description in doc_files.items():
            filepath = self.docs_dir / filename
            exists = filepath.exists()
            size = filepath.stat().st_size if exists else 0
            
            docs.append({
                "filename": filename,
                "description": description,
                "exists": exists,
                "size_kb": round(size / 1024, 1),
                "path": str(filepath)
            })
        
        return docs
    
    def collect_schedule(self):
        """收集日程安排"""
        now = self.now
        
        schedule = [
            {
                "time": "每日",
                "event": "精读1篇论文 + 写作练习",
                "type": "daily",
                "status": "pending"
            },
            {
                "time": "周四 20:00",
                "event": "论文研讨会",
                "type": "seminar",
                "status": "upcoming"
            },
            {
                "time": "周日 15:00",
                "event": "内部审稿会",
                "type": "review",
                "status": "upcoming"
            },
            {
                "time": f"Day 5 ({(now + timedelta(days=4)).strftime('%m/%d')})",
                "event": "Phase 1 完成检查",
                "type": "milestone",
                "status": "upcoming"
            },
            {
                "time": f"Day 10 ({(now + timedelta(days=9)).strftime('%m/%d')})",
                "event": "Phase 2 完成检查",
                "type": "milestone",
                "status": "upcoming"
            },
            {
                "time": f"Day 15 ({(now + timedelta(days=14)).strftime('%m/%d')})",
                "event": "Phase 3 完成 + 投稿",
                "type": "milestone",
                "status": "upcoming"
            }
        ]
        
        return schedule
    
    def collect_problem_bank(self):
        """收集练习题库"""
        reading_exercises = []
        writing_exercises = []
        
        reading_file = self.problem_bank / "reading_exercises.json"
        writing_file = self.problem_bank / "writing_exercises.json"
        
        if reading_file.exists():
            try:
                with open(reading_file) as f:
                    data = json.load(f)
                    reading_exercises = data if isinstance(data, list) else data.get("exercises", [])
            except:
                pass
        
        if writing_file.exists():
            try:
                with open(writing_file) as f:
                    data = json.load(f)
                    writing_exercises = data if isinstance(data, list) else data.get("exercises", [])
            except:
                pass
        
        return {
            "reading": {
                "count": len(reading_exercises),
                "exercises": reading_exercises[:10]  # 只取前10个
            },
            "writing": {
                "count": len(writing_exercises),
                "exercises": writing_exercises[:10]
            }
        }
    
    def collect_all(self):
        """采集全部数据"""
        return {
            "timestamp": self.now.isoformat(),
            "students": self.collect_students(),
            "paper": self.collect_collaborative_paper(),
            "tasks": self.collect_training_tasks(),
            "documents": self.collect_documents(),
            "schedule": self.collect_schedule(),
            "problem_bank": self.collect_problem_bank()
        }


if __name__ == "__main__":
    collector = PaperDataCollector()
    data = collector.collect_all()
    print(json.dumps(data, indent=2, ensure_ascii=False))
