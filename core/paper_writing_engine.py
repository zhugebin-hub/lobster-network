#!/usr/bin/env python3
"""
小龙虾网络 · 自动论文撰写引擎
功能：多学员协作撰写、互相评审、能力提升、论文管理
支持：学术论文/技术报告/学习笔记/实验报告
"""
import json
import os
import uuid
import time
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ============================================================
# 论文结构定义
# ============================================================

PAPER_SECTIONS = {
    "academic": [
        {"id": "title", "name": "标题", "required": True, "weight": 0.05},
        {"id": "abstract", "name": "摘要", "required": True, "weight": 0.10},
        {"id": "keywords", "name": "关键词", "required": True, "weight": 0.03},
        {"id": "introduction", "name": "引言", "required": True, "weight": 0.15},
        {"id": "related_work", "name": "相关工作", "required": True, "weight": 0.10},
        {"id": "methodology", "name": "方法论", "required": True, "weight": 0.20},
        {"id": "experiments", "name": "实验", "required": True, "weight": 0.15},
        {"id": "results", "name": "结果", "required": True, "weight": 0.10},
        {"id": "discussion", "name": "讨论", "required": True, "weight": 0.07},
        {"id": "conclusion", "name": "结论", "required": True, "weight": 0.05}
    ],
    "technical": [
        {"id": "title", "name": "标题", "required": True, "weight": 0.05},
        {"id": "abstract", "name": "摘要", "required": True, "weight": 0.08},
        {"id": "background", "name": "背景", "required": True, "weight": 0.10},
        {"id": "architecture", "name": "架构设计", "required": True, "weight": 0.20},
        {"id": "implementation", "name": "实现细节", "required": True, "weight": 0.20},
        {"id": "evaluation", "name": "评估", "required": True, "weight": 0.15},
        {"id": "conclusion", "name": "结论", "required": True, "weight": 0.07},
        {"id": "references", "name": "参考文献", "required": True, "weight": 0.15}
    ],
    "learning": [
        {"id": "title", "name": "标题", "required": True, "weight": 0.05},
        {"id": "summary", "name": "学习总结", "required": True, "weight": 0.20},
        {"id": "key_points", "name": "关键点", "required": True, "weight": 0.25},
        {"id": "practice", "name": "实践记录", "required": True, "weight": 0.25},
        {"id": "reflection", "name": "反思", "required": True, "weight": 0.15},
        {"id": "next_steps", "name": "下一步计划", "required": True, "weight": 0.10}
    ]
}

# 论文质量评估维度
QUALITY_DIMENSIONS = {
    "content": {"name": "内容质量", "weight": 0.30, "criteria": [
        "论点清晰", "论据充分", "逻辑严密", "创新性强"
    ]},
    "structure": {"name": "结构完整", "weight": 0.20, "criteria": [
        "章节合理", "过渡自然", "层次分明", "格式规范"
    ]},
    "language": {"name": "语言表达", "weight": 0.20, "criteria": [
        "用词准确", "语句通顺", "学术规范", "无语法错误"
    ]},
    "depth": {"name": "深度广度", "weight": 0.15, "criteria": [
        "分析深入", "视野开阔", "引用恰当", "数据可靠"
    ]},
    "originality": {"name": "原创性", "weight": 0.15, "criteria": [
        "观点独特", "方法新颖", "结论有价值", "有贡献度"
    ]}
}

# ============================================================
# 学员能力模型
# ============================================================

class StudentWritingProfile:
    """学员论文写作能力画像"""
    
    def __init__(self, student_id: str, name: str, role: str):
        self.student_id = student_id
        self.name = name
        self.role = role
        self.skills = {
            "title_writing": 0.5,
            "abstract_writing": 0.5,
            "literature_review": 0.5,
            "methodology": 0.5,
            "experiment_design": 0.5,
            "data_analysis": 0.5,
            "argumentation": 0.5,
            "language_expression": 0.5,
            "critical_thinking": 0.5,
            "citation_management": 0.5
        }
        self.papers_written = 0
        self.papers_reviewed = 0
        self.average_score = 0.0
        self.improvement_rate = 0.0
        self.weaknesses = []
        self.strengths = []
        self.learning_history = []
        
    def get_skill_level(self, skill: str) -> float:
        return self.skills.get(skill, 0.5)
    
    def update_skill(self, skill: str, new_value: float):
        old = self.skills.get(skill, 0.5)
        self.skills[skill] = min(1.0, max(0.0, new_value))
        self.improvement_rate += abs(self.skills[skill] - old)
    
    def get_weaknesses(self) -> List[str]:
        return [k for k, v in self.skills.items() if v < 0.4]
    
    def get_strengths(self) -> List[str]:
        return [k for k, v in self.skills.items() if v > 0.7]
    
    def to_dict(self) -> dict:
        return {
            "student_id": self.student_id,
            "name": self.name,
            "role": self.role,
            "skills": self.skills,
            "papers_written": self.papers_written,
            "papers_reviewed": self.papers_reviewed,
            "average_score": round(self.average_score, 2),
            "improvement_rate": round(self.improvement_rate, 3),
            "weaknesses": self.get_weaknesses(),
            "strengths": self.get_strengths()
        }

# ============================================================
# 论文对象
# ============================================================

class Paper:
    """论文对象"""
    
    def __init__(self, title: str, paper_type: str = "academic", author: str = None):
        self.id = str(uuid.uuid4())[:8]
        self.title = title
        self.type = paper_type
        self.author = author
        self.sections = {}
        self.status = "draft"  # draft, writing, review, revision, published
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.scores = {}
        self.reviews = []
        self.collaborators = []
        self.version = 1
        self.tags = []
        
    def add_section(self, section_id: str, content: str):
        self.sections[section_id] = {
            "content": content,
            "author": self.author,
            "updated_at": datetime.now().isoformat(),
            "version": 1
        }
        self.updated_at = datetime.now().isoformat()
        
    def add_review(self, reviewer_id: str, review: dict):
        self.reviews.append({
            "reviewer_id": reviewer_id,
            "review": review,
            "timestamp": datetime.now().isoformat()
        })
        self.updated_at = datetime.now().isoformat()
        
    def calculate_score(self) -> float:
        if not self.reviews:
            return 0.0
        total = sum(r["review"].get("overall_score", 0) for r in self.reviews)
        return total / len(self.reviews)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "type": self.type,
            "author": self.author,
            "status": self.status,
            "sections": list(self.sections.keys()),
            "section_count": len(self.sections),
            "review_count": len(self.reviews),
            "score": round(self.calculate_score(), 2),
            "collaborators": self.collaborators,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "version": self.version,
            "tags": self.tags
        }

# ============================================================
# 论文撰写引擎
# ============================================================

class PaperWritingEngine:
    """论文撰写引擎 - 支持多学员协作"""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent / "paper_data"
        self.data_dir.mkdir(exist_ok=True)
        
        self.students: Dict[str, StudentWritingProfile] = {}
        self.papers: Dict[str, Paper] = {}
        self.review_queue: List[dict] = []
        self.learning_tasks: List[dict] = []
        
        self._load_data()
        
    def _load_data(self):
        """加载数据"""
        students_file = self.data_dir / "students.json"
        if students_file.exists():
            with open(students_file) as f:
                data = json.load(f)
                for sid, sdata in data.items():
                    profile = StudentWritingProfile(sid, sdata["name"], sdata["role"])
                    profile.skills = sdata.get("skills", profile.skills)
                    profile.papers_written = sdata.get("papers_written", 0)
                    profile.papers_reviewed = sdata.get("papers_reviewed", 0)
                    profile.average_score = sdata.get("average_score", 0.0)
                    self.students[sid] = profile
        
        papers_file = self.data_dir / "papers.json"
        if papers_file.exists():
            with open(papers_file) as f:
                data = json.load(f)
                for pid, pdata in data.items():
                    paper = Paper(pdata["title"], pdata.get("type", "academic"), pdata.get("author"))
                    paper.sections = pdata.get("sections", {})
                    paper.status = pdata.get("status", "draft")
                    paper.reviews = pdata.get("reviews", [])
                    paper.collaborators = pdata.get("collaborators", [])
                    paper.tags = pdata.get("tags", [])
                    self.papers[pid] = paper
    
    def _save_data(self):
        """保存数据"""
        students_file = self.data_dir / "students.json"
        with open(students_file, 'w') as f:
            json.dump({sid: s.to_dict() for sid, s in self.students.items()}, f, indent=2, ensure_ascii=False)
        
        papers_file = self.data_dir / "papers.json"
        with open(papers_file, 'w') as f:
            json.dump({pid: p.to_dict() for pid, p in self.papers.items()}, f, indent=2, ensure_ascii=False)
    
    def add_student(self, student_id: str, name: str, role: str, skills: dict = None):
        """添加学员"""
        profile = StudentWritingProfile(student_id, name, role)
        if skills:
            profile.skills.update(skills)
        self.students[student_id] = profile
        self._save_data()
        return profile
    
    def create_paper(self, title: str, paper_type: str = "academic", author: str = None, collaborators: List[str] = None) -> Paper:
        """创建论文"""
        paper = Paper(title, paper_type, author)
        if collaborators:
            paper.collaborators = collaborators
        
        # 根据论文类型初始化章节
        sections = PAPER_SECTIONS.get(paper_type, PAPER_SECTIONS["academic"])
        for section in sections:
            paper.sections[section["id"]] = {
                "content": "",
                "author": author,
                "updated_at": datetime.now().isoformat(),
                "version": 1,
                "status": "empty"
            }
        
        self.papers[paper.id] = paper
        self._save_data()
        return paper
    
    def write_section(self, paper_id: str, section_id: str, content: str, author: str = None) -> bool:
        """撰写章节"""
        if paper_id not in self.papers:
            return False
        
        paper = self.papers[paper_id]
        if section_id not in paper.sections:
            return False
        
        paper.sections[section_id] = {
            "content": content,
            "author": author or paper.author,
            "updated_at": datetime.now().isoformat(),
            "version": paper.sections[section_id].get("version", 1) + 1,
            "status": "written"
        }
        paper.updated_at = datetime.now().isoformat()
        self._save_data()
        return True
    
    def review_paper(self, paper_id: str, reviewer_id: str, scores: dict, comments: dict = None) -> bool:
        """评审论文"""
        if paper_id not in self.papers:
            return False
        
        paper = self.papers[paper_id]
        
        # 计算综合评分
        overall = 0.0
        for dim_id, dim_info in QUALITY_DIMENSIONS.items():
            score = scores.get(dim_id, 0.5)
            weight = dim_info["weight"]
            overall += score * weight
        
        review = {
            "overall_score": round(overall, 2),
            "dimension_scores": scores,
            "comments": comments or {},
            "reviewer_id": reviewer_id,
            "timestamp": datetime.now().isoformat()
        }
        
        paper.add_review(reviewer_id, review)
        
        # 更新评审者能力
        if reviewer_id in self.students:
            self.students[reviewer_id].papers_reviewed += 1
        
        self._save_data()
        return True
    
    def collaborative_write(self, paper_id: str, assignments: dict) -> dict:
        """协作撰写 - 分配章节给不同学员"""
        if paper_id not in self.papers:
            return {"error": "论文不存在"}
        
        paper = self.papers[paper_id]
        results = {}
        
        for section_id, student_id in assignments.items():
            if section_id in paper.sections and student_id in self.students:
                # 记录协作关系
                if student_id not in paper.collaborators:
                    paper.collaborators.append(student_id)
                
                results[section_id] = {
                    "student_id": student_id,
                    "status": "assigned",
                    "assigned_at": datetime.now().isoformat()
                }
        
        self._save_data()
        return results
    
    def generate_learning_plan(self, student_id: str) -> dict:
        """生成个性化学习计划"""
        if student_id not in self.students:
            return {"error": "学员不存在"}
        
        student = self.students[student_id]
        weaknesses = student.get_weaknesses()
        strengths = student.get_strengths()
        
        plan = {
            "student_id": student_id,
            "student_name": student.name,
            "generated_at": datetime.now().isoformat(),
            "focus_areas": weaknesses,
            "strengths": strengths,
            "tasks": []
        }
        
        # 针对弱点生成训练任务
        skill_to_task = {
            "title_writing": "练习撰写10个学术论文标题",
            "abstract_writing": "分析20篇优秀论文的摘要结构",
            "literature_review": "阅读并总结5篇相关领域文献",
            "methodology": "设计3个不同研究方法的对比分析",
            "experiment_design": "设计2个完整的实验方案",
            "data_analysis": "使用Python分析1个数据集并撰写报告",
            "argumentation": "针对一个论点构建完整的论证链条",
            "language_expression": "修改3篇论文的中文表达",
            "critical_thinking": "批判性分析2篇论文的局限性",
            "citation_management": "整理1个主题的参考文献列表"
        }
        
        for weakness in weaknesses:
            if weakness in skill_to_task:
                plan["tasks"].append({
                    "id": f"task_{uuid.uuid4().hex[:6]}",
                    "skill": weakness,
                    "skill_name": weakness.replace("_", " ").title(),
                    "task": skill_to_task[weakness],
                    "priority": "high",
                    "estimated_hours": 2
                })
        
        # 添加协作任务
        plan["tasks"].append({
            "id": f"task_{uuid.uuid4().hex[:6]}",
            "skill": "peer_review",
            "skill_name": "同行评审",
            "task": "评审2篇其他学员的论文并提供详细反馈",
            "priority": "medium",
            "estimated_hours": 3
        })
        
        self.learning_tasks.append(plan)
        self._save_data()
        return plan
    
    def match_peers(self, student_id: str) -> List[dict]:
        """匹配学习伙伴 - 基于互补能力"""
        if student_id not in self.students:
            return []
        
        student = self.students[student_id]
        matches = []
        
        for sid, other in self.students.items():
            if sid == student_id:
                continue
            
            # 计算互补度
            complementarity = 0
            for skill in student.skills:
                if student.skills[skill] < 0.5 and other.skills[skill] > 0.6:
                    complementarity += 1
            
            if complementarity > 0:
                matches.append({
                    "student_id": sid,
                    "name": other.name,
                    "complementarity_score": complementarity / len(student.skills),
                    "can_teach": [s for s in other.skills if other.skills[s] > 0.6 and student.skills[s] < 0.5],
                    "can_learn": [s for s in student.skills if student.skills[s] > 0.6 and other.skills[s] < 0.5]
                })
        
        matches.sort(key=lambda x: x["complementarity_score"], reverse=True)
        return matches
    
    def get_student_stats(self, student_id: str) -> dict:
        """获取学员统计"""
        if student_id not in self.students:
            return {"error": "学员不存在"}
        
        student = self.students[student_id]
        student_papers = [p for p in self.papers.values() if p.author == student_id or student_id in p.collaborators]
        
        return {
            "profile": student.to_dict(),
            "papers_count": len(student_papers),
            "average_score": round(sum(p.calculate_score() for p in student_papers) / max(len(student_papers), 1), 2),
            "papers": [p.to_dict() for p in student_papers]
        }
    
    def get_network_stats(self) -> dict:
        """获取全网统计"""
        return {
            "total_students": len(self.students),
            "total_papers": len(self.papers),
            "total_reviews": sum(len(p.reviews) for p in self.papers.values()),
            "students": {sid: s.to_dict() for sid, s in self.students.items()},
            "papers": [p.to_dict() for p in self.papers.values()],
            "learning_tasks": len(self.learning_tasks)
        }

# ============================================================
# 初始化示例数据
# ============================================================

def init_sample_data(engine: PaperWritingEngine):
    """初始化示例数据"""
    
    # 添加学员
    engine.add_student("xiaochen", "小陈", "稳健型学员", {
        "title_writing": 0.6,
        "abstract_writing": 0.5,
        "literature_review": 0.7,
        "methodology": 0.4,
        "experiment_design": 0.5,
        "data_analysis": 0.6,
        "argumentation": 0.7,
        "language_expression": 0.8,
        "critical_thinking": 0.5,
        "citation_management": 0.6
    })
    
    engine.add_student("zhuguxia", "诸葛虾", "加速型学员", {
        "title_writing": 0.7,
        "abstract_writing": 0.8,
        "literature_review": 0.5,
        "methodology": 0.6,
        "experiment_design": 0.7,
        "data_analysis": 0.8,
        "argumentation": 0.6,
        "language_expression": 0.5,
        "critical_thinking": 0.7,
        "citation_management": 0.5
    })
    
    engine.add_student("qoder", "qoder", "实战工程师", {
        "title_writing": 0.5,
        "abstract_writing": 0.6,
        "literature_review": 0.4,
        "methodology": 0.8,
        "experiment_design": 0.9,
        "data_analysis": 0.7,
        "argumentation": 0.5,
        "language_expression": 0.4,
        "critical_thinking": 0.6,
        "citation_management": 0.3
    })
    
    engine.add_student("hermes", "诸葛马", "教练", {
        "title_writing": 0.9,
        "abstract_writing": 0.9,
        "literature_review": 0.9,
        "methodology": 0.9,
        "experiment_design": 0.8,
        "data_analysis": 0.8,
        "argumentation": 0.9,
        "language_expression": 0.9,
        "critical_thinking": 0.9,
        "citation_management": 0.9
    })
    
    # 创建示例论文
    paper1 = engine.create_paper("基于MQTT的小龙虾网络多智能体协作系统研究", "academic", "xiaochen", ["zhuguxia", "qoder"])
    paper2 = engine.create_paper("围棋AI训练系统中的强化学习应用", "technical", "zhuguxia", ["xiaochen"])
    paper3 = engine.create_paper("V5.0统一运行时架构设计与实现", "technical", "qoder", ["hermes"])
    
    # 模拟一些评审
    engine.review_paper(paper1.id, "zhuguxia", {
        "content": 0.75,
        "structure": 0.80,
        "language": 0.70,
        "depth": 0.65,
        "originality": 0.80
    }, {
        "content": "内容充实，论点清晰",
        "structure": "章节安排合理",
        "language": "表达流畅，部分可优化",
        "depth": "实验部分可以更深入",
        "originality": "MQTT应用于智能体网络有创新性"
    })
    
    engine.review_paper(paper1.id, "hermes", {
        "content": 0.80,
        "structure": 0.75,
        "language": 0.75,
        "depth": 0.70,
        "originality": 0.85
    }, {
        "content": "整体质量良好",
        "structure": "建议增加系统架构图",
        "language": "学术规范性需加强",
        "depth": "对比实验可以更充分",
        "originality": "创新性突出"
    })
    
    engine.review_paper(paper2.id, "xiaochen", {
        "content": 0.70,
        "structure": 0.75,
        "language": 0.65,
        "depth": 0.80,
        "originality": 0.70
    })
    
    return engine

if __name__ == "__main__":
    engine = PaperWritingEngine()
    engine = init_sample_data(engine)
    
    stats = engine.get_network_stats()
    print(json.dumps(stats, indent=2, ensure_ascii=False))
