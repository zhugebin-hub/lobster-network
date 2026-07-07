#!/usr/bin/env python3
"""
小龙虾网络实时可视化系统
Lobster Network Real-time Visualization Dashboard

功能：
- 网络拓扑图（节点位置、连接状态）
- 实时节点状态（在线/离线、延迟）
- MQTT Broker状态
- 对局信息
- 消息流量统计
"""

import json
import time
import subprocess
import os
import sys
from datetime import datetime
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

# ============================================================
# 网络拓扑配置
# ============================================================

NETWORK_NODES = {
    "zhugema": {
        "name": "诸葛马 (Hermes)",
        "role": "教练/协调者",
        "ip": "47.93.6.57",
        "private_ip": "172.24.57.34",
        "server_id": "iZ2zeckfeiop1os2jkyy94Z",
        "location": "北京VPC-A",
        "services": ["MQTT Broker", "Hermes Agent", "文件桥接器"],
        "color": "#FF6B6B",
        "icon": "🐴"
    },
    "zhuguxia": {
        "name": "诸葛虾",
        "role": "学员2",
        "ip": "172.24.56.3",
        "server_id": "iZ2zeetm9awnkwdni43joiZ",
        "location": "北京VPC-A",
        "services": ["MQTT Subscriber", "学员AI"],
        "color": "#4ECDC4",
        "icon": "🦐"
    },
    "xiaochen": {
        "name": "小陈 (小龙虾)",
        "role": "学员1",
        "ip": "121.43.80.231",
        "location": "北京VPC-B",
        "services": ["MQTT File Bridge", "学员AI"],
        "color": "#45B7D1",
        "icon": "🦞"
    }
}

# ============================================================
# 状态检测函数
# ============================================================

def check_mqtt_broker():
    """检查MQTT Broker状态"""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "mosquitto"],
            capture_output=True, text=True, timeout=5
        )
        return {
            "status": "online" if result.returncode == 0 else "offline",
            "port": 1883,
            "protocol": "MQTT 3.1.1",
            "broker": "Mosquitto v1.6.15"
        }
    except:
        return {"status": "unknown", "port": 1883}

def check_node_connectivity(ip, timeout=3):
    """检查节点连通性"""
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", str(timeout), ip],
            capture_output=True, text=True, timeout=timeout+2
        )
        if result.returncode == 0:
            # 提取延迟
            output = result.stdout
            if "time=" in output:
                time_part = output.split("time=")[1].split()[0]
                latency = float(time_part.replace("ms", ""))
            else:
                latency = 0
            return {"status": "online", "latency_ms": round(latency, 1)}
        return {"status": "offline", "latency_ms": None}
    except:
        return {"status": "unknown", "latency_ms": None}

def get_mqtt_topics():
    """获取活跃MQTT主题"""
    try:
        result = subprocess.run(
            ["mosquitto_sub", "-h", "localhost", "-t", "lobster/#", 
             "-C", "1", "-W", "2"],
            capture_output=True, text=True, timeout=5
        )
        return {"available": True, "root": "lobster/#"}
    except:
        return {"available": False, "root": "lobster/#"}

def get_system_info():
    """获取系统信息"""
    try:
        uptime = subprocess.run(["uptime"], capture_output=True, text=True, timeout=5)
        cpu = subprocess.run(["top", "-bn1"], capture_output=True, text=True, timeout=5)
        mem = subprocess.run(["free", "-h"], capture_output=True, text=True, timeout=5)
        disk = subprocess.run(["df", "-h", "/"], capture_output=True, text=True, timeout=5)
        
        cpu_line = ""
        for line in cpu.stdout.split('\n'):
            if 'Cpu' in line or 'CPU' in line:
                cpu_line = line.strip()
                break
        
        mem_line = ""
        for line in mem.stdout.split('\n'):
            if line.startswith('Mem:'):
                mem_line = line.strip()
                break
        
        disk_usage = ""
        for line in disk.stdout.split('\n'):
            if line.startswith('/dev'):
                parts = line.split()
                if len(parts) >= 5:
                    disk_usage = parts[4].replace('%', '')
                    break
        
        return {
            "uptime": uptime.stdout.strip(),
            "cpu": cpu_line,
            "memory": mem_line,
            "disk_usage_percent": int(disk_usage) if disk_usage else 0
        }
    except:
        return {"uptime": "N/A", "cpu": "N/A", "memory": "N/A", "disk_usage_percent": 0}

# ============================================================
# API端点
# ============================================================

@app.route('/')
def dashboard():
    """主仪表盘页面"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/status')
def api_status():
    """网络状态API"""
    nodes_status = {}
    
    # 检查诸葛马自身
    nodes_status["zhugema"] = {
        **NETWORK_NODES["zhugema"],
        **check_node_connectivity("127.0.0.1"),
        "system": get_system_info(),
        "mqtt": check_mqtt_broker(),
        "last_seen": datetime.now().isoformat()
    }
    
    # 检查诸葛虾
    zhuguxia_status = check_node_connectivity("172.24.56.3")
    nodes_status["zhuguxia"] = {
        **NETWORK_NODES["zhuguxia"],
        **zhuguxia_status,
        "last_seen": datetime.now().isoformat() if zhuguxia_status["status"] == "online" else "unknown"
    }
    
    # 检查小陈
    xiaochen_status = check_node_connectivity("121.43.80.231")
    nodes_status["xiaochen"] = {
        **NETWORK_NODES["xiaochen"],
        **xiaochen_status,
        "last_seen": datetime.now().isoformat() if xiaochen_status["status"] == "online" else "unknown"
    }
    
    return jsonify({
        "timestamp": datetime.now().isoformat(),
        "nodes": nodes_status,
        "mqtt_topics": get_mqtt_topics()
    })

@app.route('/api/match')
def api_match():
    """对局信息API"""
    # 检查是否有活跃对局
    match_dir = "/home/admin/lobster-network/data/matches/"
    matches = []
    
    if os.path.exists(match_dir):
        for f in os.listdir(match_dir):
            if f.endswith('.json'):
                try:
                    with open(os.path.join(match_dir, f)) as fp:
                        match = json.load(fp)
                        matches.append(match)
                except:
                    pass
    
    return jsonify({
        "active_matches": matches,
        "total_matches": len(matches)
    })

@app.route('/api/messages')
def api_messages():
    """消息统计API"""
    shared_dir = "/home/admin/go-training/shared/"
    stats = {}
    
    for subdir in ["from-xiaochen", "to-xiaochen", "from-hermes", "from-lobster"]:
        path = os.path.join(shared_dir, subdir)
        if os.path.exists(path):
            files = os.listdir(path)
            stats[subdir] = {
                "file_count": len(files),
                "latest": max(files) if files else None
            }
    
    return jsonify({
        "message_dirs": stats,
        "timestamp": datetime.now().isoformat()
    })

# ============================================================
# HTML模板
# ============================================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🦞 小龙虾网络 - 实时监控仪表盘</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        :root {
            --bg-primary: #0a0e1a;
            --bg-secondary: #1a1f2e;
            --bg-card: #242b3d;
            --text-primary: #e8eaf6;
            --text-secondary: #9fa8da;
            --accent-red: #FF6B6B;
            --accent-teal: #4ECDC4;
            --accent-blue: #45B7D1;
            --accent-gold: #FFD93D;
            --accent-green: #6BCB77;
            --accent-purple: #9B59B6;
            --border-color: #2d3548;
        }
        
        body {
            font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        /* Header */
        .header {
            background: linear-gradient(135deg, #1a1f2e 0%, #2d3548 100%);
            padding: 20px 30px;
            border-bottom: 2px solid var(--accent-gold);
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .header h1 {
            font-size: 24px;
            background: linear-gradient(90deg, var(--accent-gold), var(--accent-red));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .header .status-bar {
            display: flex;
            gap: 20px;
            align-items: center;
        }
        
        .header .status-item {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
            color: var(--text-secondary);
        }
        
        .pulse-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        .pulse-dot.online { background: var(--accent-green); }
        .pulse-dot.offline { background: var(--accent-red); }
        .pulse-dot.unknown { background: var(--accent-gold); }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(0.8); }
        }
        
        /* Main Layout */
        .main-container {
            display: grid;
            grid-template-columns: 1fr 380px;
            gap: 20px;
            padding: 20px;
            max-width: 1600px;
            margin: 0 auto;
        }
        
        /* Topology Section */
        .topology-section {
            background: var(--bg-secondary);
            border-radius: 16px;
            padding: 24px;
            border: 1px solid var(--border-color);
        }
        
        .section-title {
            font-size: 18px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
            color: var(--accent-gold);
        }
        
        #topology-canvas {
            width: 100%;
            height: 420px;
            background: var(--bg-primary);
            border-radius: 12px;
            border: 1px solid var(--border-color);
        }
        
        /* Cards Grid */
        .cards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 16px;
            margin-top: 20px;
        }
        
        .node-card {
            background: var(--bg-card);
            border-radius: 12px;
            padding: 20px;
            border-left: 4px solid var(--accent-teal);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .node-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        }
        
        .node-card.zhugema { border-left-color: var(--accent-red); }
        .node-card.zhuguxia { border-left-color: var(--accent-teal); }
        .node-card.xiaochen { border-left-color: var(--accent-blue); }
        
        .node-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }
        
        .node-name {
            font-size: 16px;
            font-weight: 600;
        }
        
        .node-role {
            font-size: 12px;
            color: var(--text-secondary);
            background: var(--bg-primary);
            padding: 3px 10px;
            border-radius: 20px;
        }
        
        .node-info {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            font-size: 13px;
        }
        
        .node-info-item {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }
        
        .node-info-label {
            color: var(--text-secondary);
            font-size: 11px;
        }
        
        .node-info-value {
            font-family: 'Courier New', monospace;
            font-size: 13px;
        }
        
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
        
        .status-badge.online {
            background: rgba(107, 203, 119, 0.15);
            color: var(--accent-green);
        }
        
        .status-badge.offline {
            background: rgba(255, 107, 107, 0.15);
            color: var(--accent-red);
        }
        
        .status-badge.unknown {
            background: rgba(255, 217, 61, 0.15);
            color: var(--accent-gold);
        }
        
        /* Sidebar */
        .sidebar {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        
        .sidebar-card {
            background: var(--bg-secondary);
            border-radius: 16px;
            padding: 20px;
            border: 1px solid var(--border-color);
        }
        
        .mqtt-status {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px;
            background: var(--bg-primary);
            border-radius: 10px;
            margin-bottom: 12px;
        }
        
        .mqtt-icon {
            font-size: 28px;
        }
        
        .mqtt-info h3 {
            font-size: 14px;
            margin-bottom: 4px;
        }
        
        .mqtt-info p {
            font-size: 12px;
            color: var(--text-secondary);
        }
        
        .topic-list {
            list-style: none;
            font-size: 12px;
            font-family: 'Courier New', monospace;
        }
        
        .topic-list li {
            padding: 6px 10px;
            margin: 4px 0;
            background: var(--bg-primary);
            border-radius: 6px;
            display: flex;
            justify-content: space-between;
        }
        
        .topic-list li .qos {
            color: var(--accent-gold);
            font-size: 11px;
        }
        
        /* System Stats */
        .stat-bar {
            margin: 10px 0;
        }
        
        .stat-bar-header {
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            margin-bottom: 6px;
        }
        
        .stat-bar-track {
            height: 8px;
            background: var(--bg-primary);
            border-radius: 4px;
            overflow: hidden;
        }
        
        .stat-bar-fill {
            height: 100%;
            border-radius: 4px;
            transition: width 0.5s ease;
        }
        
        .stat-bar-fill.green { background: linear-gradient(90deg, #6BCB77, #4ECDC4); }
        .stat-bar-fill.yellow { background: linear-gradient(90deg, #FFD93D, #FF6B6B); }
        .stat-bar-fill.red { background: linear-gradient(90deg, #FF6B6B, #e74c3c); }
        
        /* Messages Table */
        .msg-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
        }
        
        .msg-table th {
            text-align: left;
            padding: 8px;
            background: var(--bg-primary);
            color: var(--text-secondary);
            font-weight: 500;
        }
        
        .msg-table td {
            padding: 8px;
            border-bottom: 1px solid var(--border-color);
        }
        
        .msg-table tr:hover td {
            background: rgba(78, 205, 196, 0.05);
        }
        
        /* Refresh Control */
        .refresh-control {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .refresh-btn {
            background: linear-gradient(135deg, var(--accent-teal), var(--accent-blue));
            border: none;
            color: white;
            padding: 8px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            transition: opacity 0.2s;
        }
        
        .refresh-btn:hover { opacity: 0.85; }
        
        .auto-refresh {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 12px;
            color: var(--text-secondary);
        }
        
        .toggle-switch {
            position: relative;
            width: 40px;
            height: 22px;
            background: var(--bg-primary);
            border-radius: 11px;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .toggle-switch.active {
            background: var(--accent-green);
        }
        
        .toggle-switch::after {
            content: '';
            position: absolute;
            width: 18px;
            height: 18px;
            background: white;
            border-radius: 50%;
            top: 2px;
            left: 2px;
            transition: transform 0.3s;
        }
        
        .toggle-switch.active::after {
            transform: translateX(18px);
        }
        
        /* Loading */
        .loading {
            text-align: center;
            padding: 40px;
            color: var(--text-secondary);
        }
        
        .loading .spinner {
            display: inline-block;
            width: 30px;
            height: 30px;
            border: 3px solid var(--border-color);
            border-top-color: var(--accent-gold);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        /* Footer */
        .footer {
            text-align: center;
            padding: 20px;
            color: var(--text-secondary);
            font-size: 12px;
            border-top: 1px solid var(--border-color);
        }
        
        /* Responsive */
        @media (max-width: 1100px) {
            .main-container {
                grid-template-columns: 1fr;
            }
        }
        
        /* Connection Lines Animation */
        @keyframes flowLine {
            0% { stroke-dashoffset: 20; }
            100% { stroke-dashoffset: 0; }
        }
    </style>
</head>
<body>
    <!-- Header -->
    <div class="header">
        <h1>🦞 小龙虾网络 · 实时监控仪表盘</h1>
        <div class="status-bar">
            <div class="status-item">
                <span class="pulse-dot" id="global-status-dot"></span>
                <span id="global-status-text">检测中...</span>
            </div>
            <div class="refresh-control">
                <button class="refresh-btn" onclick="fetchStatus()">🔄 刷新</button>
                <div class="auto-refresh">
                    <span>自动刷新</span>
                    <div class="toggle-switch active" id="auto-refresh-toggle" onclick="toggleAutoRefresh()"></div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Main Content -->
    <div class="main-container">
        <!-- Left: Topology + Nodes -->
        <div class="left-panel">
            <!-- Network Topology -->
            <div class="topology-section">
                <div class="section-title">🌐 网络拓扑</div>
                <canvas id="topology-canvas"></canvas>
            </div>
            
            <!-- Node Cards -->
            <div class="cards-grid" id="node-cards">
                <div class="loading">
                    <div class="spinner"></div>
                    <p style="margin-top: 12px;">正在加载网络状态...</p>
                </div>
            </div>
        </div>
        
        <!-- Right: Sidebar -->
        <div class="sidebar">
            <!-- MQTT Status -->
            <div class="sidebar-card">
                <div class="section-title">📡 MQTT Broker</div>
                <div class="mqtt-status">
                    <span class="mqtt-icon">🔌</span>
                    <div class="mqtt-info">
                        <h3 id="mqtt-broker-status">检测中...</h3>
                        <p id="mqtt-broker-details">47.93.6.57:1883</p>
                    </div>
                </div>
                <div class="section-title" style="font-size:14px; margin-top:16px;">📋 主题结构</div>
                <ul class="topic-list">
                    <li>lobster/match/{id}/move/ <span class="qos">QoS 1</span></li>
                    <li>lobster/match/{id}/board/ <span class="qos">QoS 1</span></li>
                    <li>lobster/match/{id}/result/ <span class="qos">QoS 2</span></li>
                    <li>lobster/coach/{student}/cmd/ <span class="qos">QoS 1</span></li>
                    <li>lobster/{student}/coach/ack/ <span class="qos">QoS 1</span></li>
                    <li>lobster/broadcast/ <span class="qos">QoS 0</span></li>
                </ul>
            </div>
            
            <!-- System Resources -->
            <div class="sidebar-card">
                <div class="section-title">💻 系统资源 (诸葛马)</div>
                <div class="stat-bar">
                    <div class="stat-bar-header">
                        <span>CPU</span>
                        <span id="cpu-value">--</span>
                    </div>
                    <div class="stat-bar-track">
                        <div class="stat-bar-fill green" id="cpu-bar" style="width: 0%"></div>
                    </div>
                </div>
                <div class="stat-bar">
                    <div class="stat-bar-header">
                        <span>内存</span>
                        <span id="mem-value">--</span>
                    </div>
                    <div class="stat-bar-track">
                        <div class="stat-bar-fill green" id="mem-bar" style="width: 0%"></div>
                    </div>
                </div>
                <div class="stat-bar">
                    <div class="stat-bar-header">
                        <span>磁盘</span>
                        <span id="disk-value">--</span>
                    </div>
                    <div class="stat-bar-track">
                        <div class="stat-bar-fill green" id="disk-bar" style="width: 0%"></div>
                    </div>
                </div>
            </div>
            
            <!-- Messages -->
            <div class="sidebar-card">
                <div class="section-title">📨 消息目录</div>
                <table class="msg-table">
                    <thead>
                        <tr><th>目录</th><th>文件数</th><th>最新</th></tr>
                    </thead>
                    <tbody id="msg-table-body">
                        <tr><td colspan="3" style="text-align:center; color: var(--text-secondary);">加载中...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <!-- Footer -->
    <div class="footer">
        🦞 小龙虾网络 v0.4.1 · 最后更新: <span id="last-update">--</span> · 
        自动刷新: <span id="refresh-interval">5s</span>
    </div>
    
    <script>
        // ============================================================
        // Configuration
        // ============================================================
        let autoRefresh = true;
        let refreshTimer = null;
        const REFRESH_INTERVAL = 5000; // 5 seconds
        
        // ============================================================
        // Topology Canvas Drawing
        // ============================================================
        const canvas = document.getElementById('topology-canvas');
        const ctx = canvas.getContext('2d');
        
        function resizeCanvas() {
            const rect = canvas.parentElement.getBoundingClientRect();
            canvas.width = rect.width - 48;
            canvas.height = 420;
        }
        
        function drawTopology(nodes) {
            resizeCanvas();
            const w = canvas.width;
            const h = canvas.height;
            
            ctx.clearRect(0, 0, w, h);
            
            // Node positions
            const nodePositions = {
                zhugema: { x: w * 0.5, y: h * 0.35 },
                zhuguxia: { x: w * 0.25, y: h * 0.75 },
                xiaochen: { x: w * 0.75, y: h * 0.75 }
            };
            
            // Draw connection lines
            const connections = [
                { from: 'zhugema', to: 'zhuguxia', label: 'MQTT 直连', color: '#4ECDC4' },
                { from: 'zhugema', to: 'xiaochen', label: 'SSH 文件桥接', color: '#45B7D1' }
            ];
            
            connections.forEach(conn => {
                const from = nodePositions[conn.from];
                const to = nodePositions[conn.to];
                const fromStatus = nodes[conn.from]?.status || 'unknown';
                const toStatus = nodes[conn.to]?.status || 'unknown';
                const isActive = fromStatus === 'online' && toStatus === 'online';
                
                // Line
                ctx.beginPath();
                ctx.moveTo(from.x, from.y);
                ctx.lineTo(to.x, to.y);
                ctx.strokeStyle = isActive ? conn.color : '#444';
                ctx.lineWidth = 2;
                ctx.setLineDash(isActive ? [8, 4] : [4, 8]);
                if (isActive) ctx.setLineDash([8, 4]);
                ctx.stroke();
                ctx.setLineDash([]);
                
                // Animated dots for active connections
                if (isActive) {
                    const time = Date.now() / 1000;
                    for (let i = 0; i < 3; i++) {
                        const t = ((time * 0.3 + i * 0.33) % 1);
                        const dx = from.x + (to.x - from.x) * t;
                        const dy = from.y + (to.y - from.y) * t;
                        ctx.beginPath();
                        ctx.arc(dx, dy, 4, 0, Math.PI * 2);
                        ctx.fillStyle = conn.color;
                        ctx.fill();
                    }
                }
                
                // Label
                const midX = (from.x + to.x) / 2;
                const midY = (from.y + to.y) / 2;
                ctx.font = '12px "PingFang SC", sans-serif';
                ctx.fillStyle = isActive ? conn.color : '#666';
                ctx.textAlign = 'center';
                ctx.fillText(conn.label, midX, midY - 10);
                
                // Latency
                if (isActive && nodes[conn.to]?.latency_ms != null) {
                    ctx.fillStyle = '#9fa8da';
                    ctx.font = '11px monospace';
                    ctx.fillText(nodes[conn.to].latency_ms + 'ms', midX, midY + 8);
                }
            });
            
            // Draw nodes
            Object.entries(nodePositions).forEach(([key, pos]) => {
                const node = nodes[key];
                const status = node?.status || 'unknown';
                const color = node?.color || '#888';
                const icon = node?.icon || '❓';
                const name = node?.name || key;
                
                // Glow effect
                if (status === 'online') {
                    const gradient = ctx.createRadialGradient(pos.x, pos.y, 20, pos.x, pos.y, 60);
                    gradient.addColorStop(0, color + '40');
                    gradient.addColorStop(1, 'transparent');
                    ctx.beginPath();
                    ctx.arc(pos.x, pos.y, 60, 0, Math.PI * 2);
                    ctx.fillStyle = gradient;
                    ctx.fill();
                }
                
                // Node circle
                ctx.beginPath();
                ctx.arc(pos.x, pos.y, 32, 0, Math.PI * 2);
                ctx.fillStyle = status === 'online' ? color + '20' : '#333';
                ctx.fill();
                ctx.strokeStyle = status === 'online' ? color : '#555';
                ctx.lineWidth = 3;
                ctx.stroke();
                
                // Icon
                ctx.font = '28px serif';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(icon, pos.x, pos.y);
                
                // Name label
                ctx.font = 'bold 14px "PingFang SC", sans-serif';
                ctx.fillStyle = '#e8eaf6';
                ctx.textBaseline = 'top';
                ctx.fillText(name, pos.x, pos.y + 42);
                
                // Status badge
                const statusText = status === 'online' ? '● 在线' : status === 'offline' ? '● 离线' : '● 未知';
                ctx.font = '11px monospace';
                ctx.fillStyle = status === 'online' ? '#6BCB77' : status === 'offline' ? '#FF6B6B' : '#FFD93D';
                ctx.fillText(statusText, pos.x, pos.y + 62);
                
                // IP
                ctx.font = '11px monospace';
                ctx.fillStyle = '#9fa8da';
                ctx.fillText(node?.ip || '--', pos.x, pos.y + 78);
            });
            
            // Redraw if auto-refresh is on
            if (autoRefresh) {
                requestAnimationFrame(() => drawTopology(nodes));
            }
        }
        
        // ============================================================
        // Data Fetching
        // ============================================================
        async function fetchStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                updateDashboard(data);
            } catch (err) {
                console.error('Failed to fetch status:', err);
            }
        }
        
        async function fetchMessages() {
            try {
                const response = await fetch('/api/messages');
                const data = await response.json();
                updateMessages(data);
            } catch (err) {
                console.error('Failed to fetch messages:', err);
            }
        }
        
        // ============================================================
        // UI Updates
        // ============================================================
        function updateDashboard(data) {
            const nodes = data.nodes;
            const timestamp = data.timestamp;
            
            // Update global status
            const onlineCount = Object.values(nodes).filter(n => n.status === 'online').length;
            const totalCount = Object.keys(nodes).length;
            const globalDot = document.getElementById('global-status-dot');
            const globalText = document.getElementById('global-status-text');
            
            if (onlineCount === totalCount) {
                globalDot.className = 'pulse-dot online';
                globalText.textContent = `${onlineCount}/${totalCount} 节点在线`;
            } else if (onlineCount > 0) {
                globalDot.className = 'pulse-dot unknown';
                globalText.textContent = `${onlineCount}/${totalCount} 节点在线`;
            } else {
                globalDot.className = 'pulse-dot offline';
                globalText.textContent = '网络异常';
            }
            
            // Update node cards
            const cardsContainer = document.getElementById('node-cards');
            cardsContainer.innerHTML = '';
            
            Object.entries(nodes).forEach(([key, node]) => {
                const card = document.createElement('div');
                card.className = `node-card ${key}`;
                
                const statusClass = node.status || 'unknown';
                const statusText = statusClass === 'online' ? '在线' : statusClass === 'offline' ? '离线' : '未知';
                
                card.innerHTML = `
                    <div class="node-header">
                        <span class="node-name">${node.icon || ''} ${node.name}</span>
                        <span class="status-badge ${statusClass}">${statusText}</span>
                    </div>
                    <div class="node-role">${node.role}</div>
                    <div class="node-info" style="margin-top: 12px;">
                        <div class="node-info-item">
                            <span class="node-info-label">公网IP</span>
                            <span class="node-info-value">${node.ip || '--'}</span>
                        </div>
                        <div class="node-info-item">
                            <span class="node-info-label">延迟</span>
                            <span class="node-info-value">${node.latency_ms != null ? node.latency_ms + 'ms' : '--'}</span>
                        </div>
                        <div class="node-info-item">
                            <span class="node-info-label">区域</span>
                            <span class="node-info-value">${node.location || '--'}</span>
                        </div>
                        <div class="node-info-item">
                            <span class="node-info-label">服务</span>
                            <span class="node-info-value">${(node.services || []).join(', ')}</span>
                        </div>
                    </div>
                    ${node.mqtt ? `
                    <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--border-color);">
                        <div class="node-info-item">
                            <span class="node-info-label">MQTT Broker</span>
                            <span class="node-info-value" style="color: ${node.mqtt.status === 'online' ? '#6BCB77' : '#FF6B6B'}">
                                ${node.mqtt.status === 'online' ? '● 运行中' : '● 已停止'}
                            </span>
                        </div>
                    </div>` : ''}
                `;
                cardsContainer.appendChild(card);
            });
            
            // Update topology
            drawTopology(nodes);
            
            // Update system resources
            if (nodes.zhugema?.system) {
                const sys = nodes.zhugema.system;
                
                // CPU (estimate from load average)
                const cpuMatch = sys.uptime?.match(/load average: ([\d.]+)/);
                const load = cpuMatch ? parseFloat(cpuMatch[1]) : 0;
                const cpuPercent = Math.min(100, Math.round(load * 20)); // rough estimate
                document.getElementById('cpu-value').textContent = cpuPercent + '%';
                document.getElementById('cpu-bar').style.width = cpuPercent + '%';
                document.getElementById('cpu-bar').className = 'stat-bar-fill ' + (cpuPercent > 80 ? 'red' : cpuPercent > 50 ? 'yellow' : 'green');
                
                // Memory
                const memMatch = sys.memory?.match(/(\d+)M\s+(\d+)M\s+(\d+)M/);
                if (memMatch) {
                    const total = parseInt(memMatch[1]);
                    const used = parseInt(memMatch[2]);
                    const memPercent = Math.round((used / total) * 100);
                    document.getElementById('mem-value').textContent = memPercent + '%';
                    document.getElementById('mem-bar').style.width = memPercent + '%';
                    document.getElementById('mem-bar').className = 'stat-bar-fill ' + (memPercent > 80 ? 'red' : memPercent > 50 ? 'yellow' : 'green');
                }
                
                // Disk
                const diskPercent = sys.disk_usage_percent || 0;
                document.getElementById('disk-value').textContent = diskPercent + '%';
                document.getElementById('disk-bar').style.width = diskPercent + '%';
                document.getElementById('disk-bar').className = 'stat-bar-fill ' + (diskPercent > 80 ? 'red' : diskPercent > 50 ? 'yellow' : 'green');
            }
            
            // Update MQTT broker status
            if (nodes.zhugema?.mqtt) {
                const mqtt = nodes.zhugema.mqtt;
                const mqttStatusEl = document.getElementById('mqtt-broker-status');
                const mqttDetailsEl = document.getElementById('mqtt-broker-details');
                
                if (mqtt.status === 'online') {
                    mqttStatusEl.textContent = '● Mosquitto 运行中';
                    mqttStatusEl.style.color = '#6BCB77';
                    mqttDetailsEl.textContent = `${mqtt.broker || 'Mosquitto'} | 端口 ${mqtt.port}`;
                } else {
                    mqttStatusEl.textContent = '● MQTT 已停止';
                    mqttStatusEl.style.color = '#FF6B6B';
                    mqttDetailsEl.textContent = '47.93.6.57:1883';
                }
            }
            
            // Update timestamp
            document.getElementById('last-update').textContent = new Date(timestamp).toLocaleString('zh-CN');
        }
        
        function updateMessages(data) {
            const tbody = document.getElementById('msg-table-body');
            tbody.innerHTML = '';
            
            const dirs = data.message_dirs || {};
            const dirNames = {
                'from-xiaochen': '小陈→',
                'to-xiaochen': '→小陈',
                'from-hermes': '诸葛马→',
                'from-lobster': '小龙虾→'
            };
            
            Object.entries(dirs).forEach(([dir, info]) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${dirNames[dir] || dir}</td>
                    <td>${info.file_count}</td>
                    <td style="font-family: monospace; font-size: 11px; color: var(--text-secondary);">
                        ${info.latest ? info.latest.substring(0, 20) + '...' : '空'}
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }
        
        // ============================================================
        // Auto Refresh Control
        // ============================================================
        function toggleAutoRefresh() {
            autoRefresh = !autoRefresh;
            const toggle = document.getElementById('auto-refresh-toggle');
            toggle.classList.toggle('active', autoRefresh);
            
            if (autoRefresh) {
                startAutoRefresh();
            } else {
                clearInterval(refreshTimer);
            }
        }
        
        function startAutoRefresh() {
            clearInterval(refreshTimer);
            refreshTimer = setInterval(() => {
                fetchStatus();
                fetchMessages();
            }, REFRESH_INTERVAL);
        }
        
        // ============================================================
        // Initialization
        // ============================================================
        window.addEventListener('load', () => {
            fetchStatus();
            fetchMessages();
            startAutoRefresh();
        });
        
        window.addEventListener('resize', () => {
            fetchStatus();
        });
    </script>
</body>
</html>
"""

# ============================================================
# 启动服务
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print("🦞 小龙虾网络实时监控仪表盘")
    print("   本地访问: http://localhost:5000")
    print("   外网访问: http://47.93.6.57:5000")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=False)
