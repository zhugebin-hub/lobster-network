#!/usr/bin/env python3
"""
论文写作指挥中心 API
Paper Writing Command Center API

功能：
- 学员进度实时监控
- 任务分配与管理
- 合著论文进度追踪
- 研讨会管理
- 写作统计与分析
"""
import sys
import json
import uuid
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, send_from_directory

sys.path.insert(0, str(Path(__file__).parent))
from core.dashboard_collector import LobsterDataCollector

app = Flask(__name__, static_folder='docs', static_url_path='/docs')

# ============================================================
# 数据存储
# ============================================================

DATA_DIR = Path(__file__).parent / "paper_dashboard_data"
DATA_DIR.mkdir(exist_ok=True)

# 学员数据
STUDENTS = {
    "qoder": {
        "id": "qoder",
        "name": "qoder",
        "role": "实战工程师",
        "level": "六段",
        "target_level": "八段",
        "color": "#a855f7",
        "training_mode": "sprint",
        "specialty": "system_architecture",
        "weakness": "experiment_design",
        "collaborative_role": "引言+方法+统稿",
        "stats": {
            "papers_read": 0,
            "papers_target": 15,
            "notes_completed": 0,
            "notes_mastered": 0,
            "notes_reviewing": 0,
            "words_written": 0,
            "words_target": 50000,
            "exercises_done": 0,
            "current_day": 1,
            "total_days": 15,
            "last_active": datetime.now().isoformat(),
            "hours_ago": 0
        },
        "abilities": {
            "reading": 0.75,
            "writing": 0.70,
            "analysis": 0.80,
            "synthesis": 0.75,
            "review": 0.85
        }
    },
    "xiaochen": {
        "id": "xiaochen",
        "name": "小陈",
        "role": "稳健型学员",
        "level": "二段",
        "target_level": "五段",
        "color": "#3b82f6",
        "training_mode": "steady",
        "specialty": "data_analysis",
        "weakness": "academic_writing",
        "collaborative_role": "实验数据",
        "stats": {
            "papers_read": 0,
            "papers_target": 10,
            "notes_completed": 0,
            "notes_mastered": 0,
            "notes_reviewing": 0,
            "words_written": 0,
            "words_target": 30000,
            "exercises_done": 0,
            "current_day": 1,
            "total_days": 15,
            "last_active": datetime.now().isoformat(),
            "hours_ago": 0
        },
        "abilities": {
            "reading": 0.55,
            "writing": 0.50,
            "analysis": 0.65,
            "synthesis": 0.55,
            "review": 0.60
        }
    },
    "zhuguxia": {
        "id": "zhuguxia",
        "name": "诸葛虾",
        "role": "加速型学员",
        "level": "二段",
        "target_level": "五段",
        "color": "#22c55e",
        "training_mode": "balanced",
        "specialty": "rapid_prototyping",
        "weakness": "deep_analysis",
        "collaborative_role": "工具链+可视化",
        "stats": {
            "papers_read": 0,
            "papers_target": 10,
            "notes_completed": 0,
            "notes_mastered": 0,
            "notes_reviewing": 0,
            "words_written": 0,
            "words_target": 30000,
            "exercises_done": 0,
            "current_day": 1,
            "total_days": 15,
            "last_active": datetime.now().isoformat(),
            "hours_ago": 0
        },
        "abilities": {
            "reading": 0.60,
            "writing": 0.55,
            "analysis": 0.60,
            "synthesis": 0.65,
            "review": 0.65
        }
    },
    "hermes": {
        "id": "hermes",
        "name": "诸葛马 (Hermes)",
        "role": "教练/导师",
        "level": "八段",
        "target_level": "九段",
        "color": "#fbbf24",
        "training_mode": "mentor",
        "specialty": "paper_review",
        "weakness": "none",
        "collaborative_role": "总导师/统稿评审",
        "stats": {
            "papers_read": 0,
            "papers_target": 20,
            "notes_completed": 0,
            "notes_mastered": 0,
            "notes_reviewing": 0,
            "words_written": 0,
            "words_target": 40000,
            "exercises_done": 0,
            "current_day": 1,
            "total_days": 15,
            "last_active": datetime.now().isoformat(),
            "hours_ago": 0
        },
        "abilities": {
            "reading": 0.90,
            "writing": 0.85,
            "analysis": 0.95,
            "synthesis": 0.90,
            "review": 0.95
        }
    }
}

# 合著论文数据
COLLABORATIVE_PAPER = {
    "title": "小龙虾网络：基于大语言模型的多智能体围棋教育框架",
    "status": "planning",  # planning, writing, reviewing, submitted
    "sections": {
        "abstract": {
            "title": "摘要",
            "owner": "qoder (起草)",
            "status": "not_started",
            "word_count": 0,
            "target_words": 500,
            "progress": 0
        },
        "introduction": {
            "title": "1. 引言",
            "owner": "qoder",
            "status": "not_started",
            "word_count": 0,
            "target_words": 3000,
            "progress": 0
        },
        "related_work": {
            "title": "2. 相关工作",
            "owner": "诸葛虾",
            "status": "not_started",
            "word_count": 0,
            "target_words": 2500,
            "progress": 0
        },
        "method": {
            "title": "3. 方法",
            "owner": "qoder",
            "status": "not_started",
            "word_count": 0,
            "target_words": 4000,
            "progress": 0
        },
        "experiment": {
            "title": "4. 实验",
            "owner": "小陈",
            "status": "not_started",
            "word_count": 0,
            "target_words": 3500,
            "progress": 0
        },
        "tools": {
            "title": "5. 工具链",
            "owner": "诸葛虾",
            "status": "not_started",
            "word_count": 0,
            "target_words": 2000,
            "progress": 0
        },
        "conclusion": {
            "title": "6. 结论",
            "owner": "全员",
            "status": "not_started",
            "word_count": 0,
            "target_words": 1500,
            "progress": 0
        },
        "references": {
            "title": "参考文献",
            "owner": "诸葛虾",
            "status": "not_started",
            "word_count": 0,
            "target_words": 1000,
            "progress": 0
        }
    },
    "review_status": {
        "internal_reviews": 0,
        "target_reviews": 3,
        "revisions": 0
    }
}

# 训练任务
TRAINING_TASKS = {
    "qoder": [
        {"id": "q_t1", "type": "阅读", "title": "多智能体系统综述", "difficulty": "六段", "status": "pending", "assigned_day": 1},
        {"id": "q_t2", "type": "写作", "title": "引言草稿", "difficulty": "七段", "status": "pending", "assigned_day": 3},
        {"id": "q_t3", "type": "阅读", "title": "LLM教育应用", "difficulty": "六段", "status": "pending", "assigned_day": 2}
    ],
    "xiaochen": [
        {"id": "x_t1", "type": "阅读", "title": "AI围棋训练方法", "difficulty": "二段", "status": "pending", "assigned_day": 1},
        {"id": "x_t2", "type": "写作", "title": "实验设计文档", "difficulty": "三段", "status": "pending", "assigned_day": 4},
        {"id": "x_t3", "type": "阅读", "title": "教育数据分析", "difficulty": "二段", "status": "pending", "assigned_day": 2}
    ],
    "zhuguxia": [
        {"id": "z_t1", "type": "阅读", "title": "可视化工具比较", "difficulty": "二段", "status": "pending", "assigned_day": 1},
        {"id": "z_t2", "type": "写作", "title": "工具链章节", "difficulty": "三段", "status": "pending", "assigned_day": 5},
        {"id": "z_t3", "type": "阅读", "title": "监控系统设计", "difficulty": "二段", "status": "pending", "assigned_day": 2}
    ],
    "hermes": [
        {"id": "h_t1", "type": "评审", "title": "学员精读笔记评审", "difficulty": "八段", "status": "pending", "assigned_day": 1},
        {"id": "h_t2", "type": "评审", "title": "引言草稿评审", "difficulty": "九段", "status": "pending", "assigned_day": 4},
        {"id": "h_t3", "type": "指导", "title": "写作工作坊", "difficulty": "八段", "status": "pending", "assigned_day": 3}
    ]
}

# 研讨会
SEMINARS = [
    {
        "id": "sem_001",
        "title": "第一次论文研讨会",
        "date": "2026-07-09T20:00:00",
        "type": "paper_discussion",
        "attendees": ["qoder", "xiaochen", "zhuguxia", "hermes"],
        "status": "scheduled",
        "agenda": ["精读笔记分享", "论文框架讨论", "分工确认"]
    },
    {
        "id": "sem_002",
        "title": "第一次内部审稿会",
        "date": "2026-07-12T15:00:00",
        "type": "internal_review",
        "attendees": ["qoder", "xiaochen", "zhuguxia", "hermes"],
        "status": "scheduled",
        "agenda": ["初稿评审", "修改建议", "格式调整"]
    }
]

# 缓存
_cache = {"data": None, "timestamp": 0, "lock": threading.Lock()}
CACHE_TTL = 25
collector = LobsterDataCollector()

# ============================================================
# API 端点
# ============================================================

@app.route('/')
def index():
    """重定向到论文指挥中心"""
    return send_from_directory('docs', 'paper_dashboard.html')

@app.route('/api/paper/students')
def api_students():
    """获取所有学员数据"""
    return jsonify(STUDENTS)

@app.route('/api/paper/student/<student_id>')
def api_student_detail(student_id):
    """获取学员详情"""
    if student_id in STUDENTS:
        student = STUDENTS[student_id]
        student["tasks"] = TRAINING_TASKS.get(student_id, [])
        return jsonify(student)
    return jsonify({"error": "学员不存在"}), 404

@app.route('/api/paper/paper')
def api_paper():
    """获取合著论文状态"""
    return jsonify(COLLABORATIVE_PAPER)

@app.route('/api/paper/paper/section/<section_id>', methods=['PUT'])
def api_update_section(section_id):
    """更新论文章节进度"""
    if section_id not in COLLABORATIVE_PAPER["sections"]:
        return jsonify({"error": "章节不存在"}), 404
    
    data = request.json
    section = COLLABORATIVE_PAPER["sections"][section_id]
    
    if "word_count" in data:
        section["word_count"] = data["word_count"]
        section["progress"] = min(100, int(data["word_count"] / section["target_words"] * 100))
    if "status" in data:
        section["status"] = data["status"]
    
    return jsonify({"status": "ok", "section": section})

@app.route('/api/paper/tasks')
def api_tasks():
    """获取所有训练任务"""
    return jsonify(TRAINING_TASKS)

@app.route('/api/paper/task/<task_id>', methods=['PUT'])
def api_update_task(task_id):
    """更新任务状态"""
    data = request.json
    
    for student_tasks in TRAINING_TASKS.values():
        for task in student_tasks:
            if task["id"] == task_id:
                if "status" in data:
                    task["status"] = data["status"]
                if "progress" in data:
                    task["progress"] = data["progress"]
                return jsonify({"status": "ok", "task": task})
    
    return jsonify({"error": "任务不存在"}), 404

@app.route('/api/paper/seminars')
def api_seminars():
    """获取研讨会列表"""
    return jsonify(SEMINARS)

@app.route('/api/paper/seminar/<seminar_id>', methods=['PUT'])
def api_update_seminar(seminar_id):
    """更新研讨会状态"""
    data = request.json
    
    for seminar in SEMINARS:
        if seminar["id"] == seminar_id:
            if "status" in data:
                seminar["status"] = data["status"]
            if "notes" in data:
                seminar["notes"] = data["notes"]
            return jsonify({"status": "ok", "seminar": seminar})
    
    return jsonify({"error": "研讨会不存在"}), 404

@app.route('/api/paper/stats')
def api_stats():
    """获取整体统计"""
    total_papers = sum(s["stats"]["papers_target"] for s in STUDENTS.values())
    read_papers = sum(s["stats"]["papers_read"] for s in STUDENTS.values())
    total_words = sum(s["stats"]["words_target"] for s in STUDENTS.values())
    written_words = sum(s["stats"]["words_written"] for s in STUDENTS.values())
    
    # 论文整体进度
    paper_progress = 0
    for section in COLLABORATIVE_PAPER["sections"].values():
        paper_progress += section["progress"]
    paper_progress = paper_progress / len(COLLABORATIVE_PAPER["sections"])
    
    return jsonify({
        "total_papers": total_papers,
        "read_papers": read_papers,
        "paper_reading_progress": round(read_papers / total_papers * 100, 1) if total_papers > 0 else 0,
        "total_words": total_words,
        "written_words": written_words,
        "writing_progress": round(written_words / total_words * 100, 1) if total_words > 0 else 0,
        "paper_progress": round(paper_progress, 1),
        "active_tasks": sum(1 for tasks in TRAINING_TASKS.values() for t in tasks if t["status"] == "in_progress"),
        "completed_tasks": sum(1 for tasks in TRAINING_TASKS.values() for t in tasks if t["status"] == "completed"),
        "total_tasks": sum(len(tasks) for tasks in TRAINING_TASKS.values()),
        "upcoming_seminars": len([s for s in SEMINARS if s["status"] == "scheduled"]),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/paper/recommendations')
def api_recommendations():
    """获取教练推荐"""
    recommendations = []
    
    for sid, student in STUDENTS.items():
        abilities = student["abilities"]
        
        # 阅读能力弱 → 推荐精读训练
        if abilities["reading"] < 0.7:
            recommendations.append({
                "student_id": sid,
                "student_name": student["name"],
                "type": "训练",
                "priority": "高",
                "content": f"{student['name']}阅读能力({abilities['reading']*100:.0f}%)偏低，建议加强论文精读训练",
                "action": "start_reading"
            })
        
        # 写作能力弱 → 推荐写作练习
        if abilities["writing"] < 0.6:
            recommendations.append({
                "student_id": sid,
                "student_name": student["name"],
                "type": "训练",
                "priority": "高",
                "content": f"{student['name']}写作能力({abilities['writing']*100:.0f}%)偏低，建议增加写作练习",
                "action": "start_writing"
            })
        
        # 分析能力强 → 推荐审稿
        if abilities["analysis"] > 0.8:
            recommendations.append({
                "student_id": sid,
                "student_name": student["name"],
                "type": "任务",
                "priority": "中",
                "content": f"{student['name']}分析能力强({abilities['analysis']*100:.0f}%)，可承担审稿任务",
                "action": "assign_review"
            })
    
    return jsonify(recommendations)

@app.route('/api/paper/weekly-report')
def api_weekly_report():
    """生成周报"""
    stats = api_stats().get_json()
    
    report = {
        "week": 1,
        "date": datetime.now().isoformat(),
        "summary": {
            "total_students": len(STUDENTS),
            "active_students": len([s for s in STUDENTS.values() if s["stats"]["hours_ago"] < 24]),
            "papers_read": stats["read_papers"],
            "words_written": stats["written_words"],
            "tasks_completed": stats["completed_tasks"],
            "seminars_held": len([s for s in SEMINARS if s["status"] == "completed"])
        },
        "student_details": {},
        "recommendations": api_recommendations().get_json()
    }
    
    for sid, student in STUDENTS.items():
        report["student_details"][sid] = {
            "name": student["name"],
            "level": student["level"],
            "papers_read": student["stats"]["papers_read"],
            "words_written": student["stats"]["words_written"],
            "tasks": TRAINING_TASKS.get(sid, [])
        }
    
    return jsonify(report)

@app.route('/api/system')
def api_system():
    """系统状态"""
    with _cache["lock"]:
        if _cache["data"] is None or (time.time() - _cache["timestamp"]) > CACHE_TTL:
            _cache["data"] = collector.collect_all()
            _cache["timestamp"] = time.time()
        data = _cache["data"]
    
    return jsonify({
        "system": data["system"],
        "nodes": data["nodes"],
        "alerts": data["alerts"],
        "timestamp": data["timestamp"]
    })

@app.route('/api/force-refresh')
def api_force_refresh():
    """强制刷新"""
    with _cache["lock"]:
        _cache["data"] = None
        _cache["timestamp"] = 0
    data = collector.collect_all()
    with _cache["lock"]:
        _cache["data"] = data
        _cache["timestamp"] = time.time()
    return jsonify({"status": "refreshed"})

@app.route('/api/health')
def api_health():
    """健康检查"""
    return jsonify({
        "status": "ok",
        "cache_age": round(time.time() - _cache["timestamp"], 1),
        "has_cache": _cache["data"] is not None,
        "students": len(STUDENTS),
        "paper_sections": len(COLLABORATIVE_PAPER["sections"])
    })

if __name__ == '__main__':
    print("=" * 50)
    print("📝 论文写作指挥中心 API")
    print("=" * 50)
    print(f"监听: 0.0.0.0:5002")
    print(f"仪表盘: http://<IP>:5002/")
    print("=" * 50)
    
    # 预加载缓存
    print("📡 首次数据采集...")
    with _cache["lock"]:
        _cache["data"] = collector.collect_all()
        _cache["timestamp"] = time.time()
    print("✅ 缓存已就绪")
    
    app.run(host='0.0.0.0', port=5002, debug=False)
