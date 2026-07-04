#!/usr/bin/env python3
"""
大麦抢票助手 - Web 管理界面
Flask + Playwright 实现
"""

import json
import threading
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# 任务状态
task_status = {
    "running": False,
    "message": "",
    "step": "",
    "start_time": None,
    "grab_time": None,
}

# 抢票配置
grab_config = {}


def run_grabber(config):
    """在后台线程中运行抢票脚本"""
    global task_status
    task_status["running"] = True
    task_status["message"] = "正在启动浏览器..."
    task_status["step"] = "init"
    task_status["start_time"] = datetime.now().strftime("%H:%M:%S")

    try:
        from grabber import DamaiGrabber

        grabber = DamaiGrabber(config, task_status)
        grabber.run()

    except Exception as e:
        task_status["running"] = False
        task_status["message"] = f"错误: {str(e)}"
        task_status["step"] = "error"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status")
def status():
    return jsonify(task_status)


@app.route("/api/start", methods=["POST"])
def start():
    global grab_config, task_status

    if task_status["running"]:
        return jsonify({"error": "抢票任务已在运行中"})

    data = request.json
    grab_config = {
        "item_id": data.get("item_id", ""),
        "sku_id": data.get("sku_id", ""),
        "count": int(data.get("count", 1)),
        "buyer_name": data.get("buyer_name", ""),
        "buyer_phone": data.get("buyer_phone", ""),
        "grab_time": data.get("grab_time", ""),  # 格式: HH:MM:SS
        "refresh_interval": float(data.get("refresh_interval", 0.5)),
        "headless": data.get("headless", False),
    }

    task_status = {
        "running": True,
        "message": "正在初始化...",
        "step": "init",
        "start_time": datetime.now().strftime("%H:%M:%S"),
        "grab_time": None,
    }

    thread = threading.Thread(target=run_grabber, args=(grab_config,), daemon=True)
    thread.start()

    return jsonify({"success": True, "message": "抢票任务已启动"})


@app.route("/api/stop")
def stop():
    global task_status
    task_status["running"] = False
    task_status["message"] = "已停止"
    task_status["step"] = "stopped"
    return jsonify({"success": True})


if __name__ == "__main__":
    print("=" * 50)
    print("🎫 大麦抢票助手")
    print("=" * 50)
    print("请在浏览器打开: http://localhost:5000")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=True)
