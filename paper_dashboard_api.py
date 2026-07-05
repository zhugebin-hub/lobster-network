#!/usr/bin/env python3
"""
小龙虾网络 · 论文撰写仪表盘 API
"""
import sys
import json
import time
import threading
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory

sys.path.insert(0, str(Path(__file__).parent))
from core.paper_writing_engine import PaperWritingEngine, init_sample_data

app = Flask(__name__, static_folder='docs', static_url_path='/docs')

# 初始化引擎
engine = PaperWritingEngine()
engine = init_sample_data(engine)

# 缓存
_cache = {"data": None, "timestamp": 0, "lock": threading.Lock()}
CACHE_TTL = 25

# ============================================================
# 页面路由
# ============================================================

@app.route('/')
def index():
    return send_from_directory('docs', 'paper_dashboard.html')

# ============================================================
# 学员管理 API
# ============================================================

@app.route('/api/students')
def api_students():
    """获取所有学员"""
    return jsonify({sid: s.to_dict() for sid, s in engine.students.items()})

@app.route('/api/student/<student_id>')
def api_student_detail(student_id):
    """获取学员详情"""
    if student_id in engine.students:
        return jsonify(engine.get_student_stats(student_id))
    return jsonify({"error": "学员不存在"}), 404

@app.route('/api/student/add', methods=['POST'])
def api_add_student():
    """添加学员"""
    data = request.json
    student_id = data.get("student_id")
    name = data.get("name")
    role = data.get("role", "学员")
    skills = data.get("skills")
    
    if not student_id or not name:
        return jsonify({"error": "缺少必要参数"}), 400
    
    profile = engine.add_student(student_id, name, role, skills)
    return jsonify({"status": "ok", "student": profile.to_dict()})

@app.route('/api/match/<student_id>')
def api_match_peers(student_id):
    """匹配学习伙伴"""
    matches = engine.match_peers(student_id)
    return jsonify(matches)

# ============================================================
# 论文管理 API
# ============================================================

@app.route('/api/papers')
def api_papers():
    """获取所有论文"""
    return jsonify([p.to_dict() for p in engine.papers.values()])

@app.route('/api/paper/<paper_id>')
def api_paper_detail(paper_id):
    """获取论文详情"""
    if paper_id in engine.papers:
        paper = engine.papers[paper_id]
        return jsonify({
            "paper": paper.to_dict(),
            "sections": paper.sections,
            "reviews": paper.reviews
        })
    return jsonify({"error": "论文不存在"}), 404

@app.route('/api/paper/create', methods=['POST'])
def api_create_paper():
    """创建论文"""
    data = request.json
    title = data.get("title")
    paper_type = data.get("type", "academic")
    author = data.get("author")
    collaborators = data.get("collaborators", [])
    
    if not title:
        return jsonify({"error": "缺少标题"}), 400
    
    paper = engine.create_paper(title, paper_type, author, collaborators)
    return jsonify({"status": "ok", "paper": paper.to_dict()})

@app.route('/api/paper/<paper_id>/section', methods=['POST'])
def api_write_section(paper_id):
    """撰写章节"""
    data = request.json
    section_id = data.get("section_id")
    content = data.get("content")
    author = data.get("author")
    
    if not section_id or not content:
        return jsonify({"error": "缺少必要参数"}), 400
    
    success = engine.write_section(paper_id, section_id, content, author)
    if success:
        return jsonify({"status": "ok"})
    return jsonify({"error": "章节不存在"}), 404

@app.route('/api/paper/<paper_id>/review', methods=['POST'])
def api_review_paper(paper_id):
    """评审论文"""
    data = request.json
    reviewer_id = data.get("reviewer_id")
    scores = data.get("scores", {})
    comments = data.get("comments")
    
    if not reviewer_id or not scores:
        return jsonify({"error": "缺少必要参数"}), 400
    
    success = engine.review_paper(paper_id, reviewer_id, scores, comments)
    if success:
        return jsonify({"status": "ok"})
    return jsonify({"error": "论文不存在"}), 404

@app.route('/api/paper/<paper_id>/collaborate', methods=['POST'])
def api_collaborative_write(paper_id):
    """协作撰写"""
    data = request.json
    assignments = data.get("assignments", {})
    
    result = engine.collaborative_write(paper_id, assignments)
    return jsonify(result)

# ============================================================
# 学习系统 API
# ============================================================

@app.route('/api/learning-plan/<student_id>')
def api_learning_plan(student_id):
    """获取学习计划"""
    plan = engine.generate_learning_plan(student_id)
    return jsonify(plan)

@app.route('/api/learning-tasks')
def api_learning_tasks():
    """获取所有学习任务"""
    return jsonify(engine.learning_tasks)

# ============================================================
# 统计 API
# ============================================================

@app.route('/api/stats')
def api_stats():
    """获取全网统计"""
    return jsonify(engine.get_network_stats())

@app.route('/api/health')
def api_health():
    """健康检查"""
    return jsonify({
        "status": "ok",
        "students": len(engine.students),
        "papers": len(engine.papers),
        "cache_age": round(time.time() - _cache["timestamp"], 1)
    })

if __name__ == '__main__':
    print("=" * 50)
    print("📝 小龙虾网络 · 论文撰写仪表盘 API")
    print("=" * 50)
    print(f"监听: 0.0.0.0:5002")
    print(f"仪表盘: http://<IP>:5002/")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5002, debug=False)
