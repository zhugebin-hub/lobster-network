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
from core.enhanced_dashboard_collector import EnhancedDataCollector

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
enhanced_collector = EnhancedDataCollector()

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
    """重定向到增强版综合仪表盘 V2"""
    return send_from_directory('docs', 'dashboard_enhanced_v2.html')

@app.route('/v1')
def index_v1():
    """重定向到原版监控仪表盘"""
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
# 增强版综合仪表盘 V2 API
# ============================================================

@app.route('/api/enhanced/status')
def api_enhanced_status():
    """API: 增强版综合状态数据"""
    data = enhanced_collector.collect_all()
    return jsonify(data)

@app.route('/api/enhanced/nodes')
def api_enhanced_nodes():
    """API: 增强版节点数据"""
    data = enhanced_collector.collect_all()
    return jsonify({"nodes": data["nodes"], "timestamp": data["timestamp"]})

@app.route('/api/enhanced/go-training')
def api_enhanced_go_training():
    """API: 增强版围棋训练数据"""
    data = enhanced_collector.collect_all()
    return jsonify({"go_training": data["go_training"], "timestamp": data["timestamp"]})

@app.route('/api/enhanced/paper-learning')
def api_enhanced_paper_learning():
    """API: 增强版论文学习数据"""
    data = enhanced_collector.collect_all()
    return jsonify({"paper_learning": data["paper_learning"], "timestamp": data["timestamp"]})

@app.route('/api/enhanced/rewards')
def api_enhanced_rewards():
    """API: 增强版奖励数据"""
    data = enhanced_collector.collect_all()
    return jsonify({"rewards": data["rewards"], "timestamp": data["timestamp"]})

@app.route('/api/enhanced/health')
def api_enhanced_health():
    """API: 增强版健康评分"""
    data = enhanced_collector.collect_all()
    return jsonify({"health_score": data["health_score"], "timestamp": data["timestamp"]})

@app.route('/api/enhanced/git')
def api_enhanced_git():
    """API: 增强版Git状态"""
    data = enhanced_collector.collect_all()
    return jsonify({"git_status": data["git_status"], "timestamp": data["timestamp"]})

@app.route('/api/enhanced/summary')
def api_enhanced_summary():
    """API: 增强版汇总数据"""
    data = enhanced_collector.collect_all()
    return jsonify({"summary": data["summary"], "timestamp": data["timestamp"]})


@app.route('/join')
def lobster_join():
    """🦞 小龙虾网络 · 新节点注册指南（仪表盘风格渲染）"""
    import markdown
    from flask import Response
    
    guide_path = Path(__file__).parent / 'docs' / '新小龙虾注册指南_V1.0_20260715.md'
    if not guide_path.exists():
        return "注册指南文件不存在", 404
    
    with open(guide_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    html_body = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
    
    page = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🦞 小龙虾网络 · 新节点注册指南</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0a0e17;--card:#111827;--border:#1e293b;--text:#e2e8f0;--dim:#64748b;--accent:#fbbf24;--green:#22c55e;--red:#ef4444;--blue:#3b82f6;--purple:#a855f7;--cyan:#06b6d4}
body{font-family:'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--text);line-height:1.8}
.header{background:linear-gradient(135deg,#111827 0%,#1e1b4b 100%);border-bottom:1px solid var(--border);padding:16px 24px;display:flex;justify-content:space-between;align-items:center}
.header h1{font-size:20px;color:var(--accent)}
.header a{color:var(--dim);font-size:13px;text-decoration:none}
.header a:hover{color:var(--accent)}
.content{max-width:900px;margin:0 auto;padding:24px}
.content h1{font-size:22px;color:var(--accent);margin:24px 0 12px;border-bottom:1px solid var(--border);padding-bottom:8px}
.content h2{font-size:18px;color:var(--cyan);margin:20px 0 10px;border-bottom:1px solid var(--border);padding-bottom:6px}
.content h3{font-size:15px;color:var(--purple);margin:16px 0 8px}
.content p{margin:8px 0}
.content strong{color:var(--accent)}
.content em{color:var(--dim)}
.content table{width:100%;border-collapse:collapse;margin:12px 0;font-size:13px}
.content th{background:#1e293b;color:var(--accent);padding:8px 10px;text-align:left;border:1px solid var(--border)}
.content td{padding:6px 10px;border:1px solid var(--border);background:#0f172a}
.content code{background:#1e293b;padding:2px 6px;border-radius:4px;font-size:12px;color:var(--cyan)}
.content pre{background:#0f172a;border:1px solid var(--border);border-radius:8px;padding:14px;overflow-x:auto;margin:12px 0}
.content pre code{background:none;padding:0;color:var(--text)}
.content blockquote{border-left:3px solid var(--accent);padding:8px 14px;margin:12px 0;background:rgba(251,191,36,.05);color:var(--dim);font-style:italic}
.content ul,.content ol{padding-left:24px;margin:8px 0}
.content li{margin:4px 0}
.content a{color:var(--blue);text-decoration:none}
.content a:hover{text-decoration:underline}
.footer{text-align:center;padding:24px;color:var(--dim);font-size:11px;border-top:1px solid var(--border);margin-top:32px}
</style>
</head>
<body>
<div class="header">
    <h1>🦞 小龙虾网络 · 新节点注册指南</h1>
    <a href="/">← 返回仪表盘</a>
</div>
<div class="content">
PLACEHOLDER_HTML
</div>
<div class="footer">
    🦞 小龙虾网络 V3.3 | 诸葛马 (Hermes) 教练端 | 浙江工商大学数智商研实验室
</div>
</body>
</html>"""
    
    return Response(page.replace('PLACEHOLDER_HTML', html_body), mimetype='text/html')

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
