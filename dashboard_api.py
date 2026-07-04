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

app = Flask(__name__, static_folder='docs', static_url_path='/docs')

# 缓存
_cache = {
    "data": None,
    "timestamp": 0,
    "lock": threading.Lock()
}
CACHE_TTL = 25  # 缓存25秒，API轮询30秒

collector = LobsterDataCollector()

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

if __name__ == '__main__':
    print("=" * 50)
    print("🦞 小龙虾网络仪表盘 API 服务")
    print("=" * 50)
    print(f"监听: 0.0.0.0:5000")
    print(f"监控仪表盘: http://<IP>:5000/")
    print(f"API端点: http://<IP>:5000/api/status")
    print("=" * 50)
    
    # 预加载缓存
    print("📡 首次数据采集...")
    get_cached_data()
    print("✅ 缓存已就绪")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
