#!/usr/bin/env python3
"""
小龙虾网络仪表盘 API 服务
提供实时数据采集接口，供前端仪表盘AJAX调用
"""
import sys
import json
import time
import threading
from pathlib import Path
from flask import Flask, jsonify, send_from_directory

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))
from core.dashboard_collector import LobsterDataCollector
from core.paper_dashboard_collector import PaperDataCollector

app = Flask(__name__, static_folder='docs', static_url_path='/docs')

# 缓存
_cache = {
    "data": None,
    "timestamp": 0,
    "lock": threading.Lock()
}
CACHE_TTL = 25  # 缓存25秒，API轮询30秒

collector = LobsterDataCollector()
paper_collector = PaperDataCollector()

def get_cached_data():
    """获取缓存数据，超时则重新采集"""
    now = time.time()
    with _cache["lock"]:
        if _cache["data"] is None or (now - _cache["timestamp"]) > CACHE_TTL:
            _cache["data"] = collector.collect_all()
            _cache["timestamp"] = now
        return _cache["data"]

@app.route('/')
def index():
    """重定向到监控仪表盘"""
    return send_from_directory('docs', 'dashboard_monitoring.html')

@app.route('/api/status')
def api_status():
    """API: 获取最新状态数据"""
    data = get_cached_data()
    return jsonify(data)

@app.route('/api/nodes')
def api_nodes():
    """API: 仅节点数据"""
    data = get_cached_data()
    return jsonify({"nodes": data["nodes"], "timestamp": data["timestamp"]})

@app.route('/api/messages')
def api_messages():
    """API: 仅消息数据"""
    data = get_cached_data()
    return jsonify({"messages": data["messages"], "timestamp": data["timestamp"]})

@app.route('/api/mqtt')
def api_mqtt():
    """API: 仅MQTT数据"""
    data = get_cached_data()
    return jsonify({"mqtt": data["mqtt"], "timestamp": data["timestamp"]})

@app.route('/api/git')
def api_git():
    """API: 仅Git数据"""
    data = get_cached_data()
    return jsonify({"git": data["git"], "timestamp": data["timestamp"]})

@app.route('/api/domains')
def api_domains():
    """API: 仅栏目数据"""
    data = get_cached_data()
    return jsonify({"domains": data["domains"], "timestamp": data["timestamp"]})

@app.route('/api/alerts')
def api_alerts():
    """API: 仅告警数据"""
    data = get_cached_data()
    return jsonify({"alerts": data["alerts"], "timestamp": data["timestamp"]})

@app.route('/api/training')
def api_training():
    """API: 仅训练数据"""
    data = get_cached_data()
    return jsonify({"training": data["training"], "timestamp": data["timestamp"]})

@app.route('/api/force-refresh')
def api_force_refresh():
    """API: 强制刷新缓存"""
    with _cache["lock"]:
        _cache["data"] = None
        _cache["timestamp"] = 0
    data = get_cached_data()
    return jsonify({"status": "refreshed", "timestamp": data["timestamp"]})

@app.route('/api/health')
def api_health():
    """API: 服务健康检查"""
    return jsonify({
        "status": "ok",
        "cache_age": round(time.time() - _cache["timestamp"], 1),
        "has_cache": _cache["data"] is not None
    })

# ============================================================
# 论文写作指挥中心 API
# ============================================================

@app.route('/paper')
def paper_dashboard():
    """重定向到论文写作指挥中心"""
    return send_from_directory('docs', 'paper_dashboard.html')

@app.route('/api/paper/status')
def api_paper_status():
    """API: 论文写作全部数据"""
    data = paper_collector.collect_all()
    return jsonify(data)

@app.route('/api/paper/students')
def api_paper_students():
    """API: 学员数据"""
    data = paper_collector.collect_all()
    return jsonify(data["students"])

@app.route('/api/paper/student/<student_id>')
def api_paper_student_detail(student_id):
    """API: 单个学员详情"""
    data = paper_collector.collect_all()
    students = data["students"]
    if student_id in students:
        return jsonify(students[student_id])
    return jsonify({"error": "学员不存在"}), 404

@app.route('/api/paper/paper')
def api_paper_paper():
    """API: 合著论文进度"""
    data = paper_collector.collect_all()
    return jsonify(data["paper"])

@app.route('/api/paper/tasks')
def api_paper_tasks():
    """API: 训练任务"""
    data = paper_collector.collect_all()
    return jsonify(data["tasks"])

@app.route('/api/paper/tasks/<student_id>')
def api_paper_student_tasks(student_id):
    """API: 学员训练任务"""
    data = paper_collector.collect_all()
    tasks = data["tasks"]
    if student_id in tasks:
        return jsonify(tasks[student_id])
    return jsonify({"error": "学员不存在"}), 404

@app.route('/api/paper/documents')
def api_paper_documents():
    """API: 文档状态"""
    data = paper_collector.collect_all()
    return jsonify(data["documents"])

@app.route('/api/paper/schedule')
def api_paper_schedule():
    """API: 日程安排"""
    data = paper_collector.collect_all()
    return jsonify(data["schedule"])

@app.route('/api/paper/problem-bank')
def api_paper_problem_bank():
    """API: 练习题库"""
    data = paper_collector.collect_all()
    return jsonify(data["problem_bank"])

@app.route('/api/paper/force-refresh')
def api_paper_force_refresh():
    """API: 强制刷新论文数据"""
    data = paper_collector.collect_all()
    return jsonify({"status": "refreshed", "timestamp": data["timestamp"]})

@app.route('/api/paper/health')
def api_paper_health():
    """API: 论文服务健康检查"""
    return jsonify({
        "status": "ok",
        "service": "paper_dashboard",
        "timestamp": datetime.now().isoformat()
    })

from datetime import datetime

if __name__ == '__main__':
    print("=" * 50)
    print("🦞 小龙虾网络仪表盘 API 服务")
    print("=" * 50)
    print(f"监听: 0.0.0.0:5000")
    print(f"监控仪表盘: http://<IP>:5000/")
    print(f"论文指挥中心: http://<IP>:5000/paper")
    print(f"API端点: http://<IP>:5000/api/status")
    print("=" * 50)
    
    # 预加载缓存
    print("📡 首次数据采集...")
    get_cached_data()
    print("✅ 缓存已就绪")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
