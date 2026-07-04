#!/usr/bin/env python3
"""
小龙虾网络 · 围棋训练监控仪表盘 API
功能：学员管理、对局管理、训练引导、实时数据
"""
import sys
import json
import time
import uuid
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

DATA_DIR = Path(__file__).parent / "go_dashboard_data"
DATA_DIR.mkdir(exist_ok=True)

# 学员数据
STUDENTS = {
    "xiaochen": {
        "id": "xiaochen",
        "name": "小陈",
        "role": "稳健型学员",
        "level": "30级",
        "color": "#3b82f6",
        "stats": {
            "total_games": 11056,
            "wins": 5340,
            "losses": 5716,
            "win_rate": 48.3,
            "problems_solved": 847,
            "wrong_answers": 23,
            "accuracy": 97.3,
            "last_active": "2026-07-01T11:50:12",
            "hours_ago": 80
        },
        "abilities": {
            "calculation": 0.65,
            "judgment": 0.60,
            "layout": 0.55,
            "defense": 0.70,
            "memory": 0.75
        },
        "strengths": ["死活基础", "手筋基础", "官子基础"],
        "weaknesses": ["定式变化", "终盘计算"],
        "training_plan": {
            "phase": "Phase 2",
            "week": 5,
            "day": 28,
            "current_task": "中级死活题训练"
        }
    },
    "zhuguxia": {
        "id": "zhuguxia",
        "name": "诸葛虾",
        "role": "加速型学员",
        "level": "初段",
        "color": "#22c55e",
        "stats": {
            "total_games": 7376,
            "wins": 3658,
            "losses": 3718,
            "win_rate": 49.6,
            "problems_solved": 1023,
            "wrong_answers": 18,
            "accuracy": 98.2,
            "last_active": "2026-07-01T11:50:25",
            "hours_ago": 80
        },
        "abilities": {
            "calculation": 0.70,
            "judgment": 0.75,
            "layout": 0.65,
            "defense": 0.80,
            "memory": 0.80
        },
        "strengths": ["计算速度", "手筋应用", "中盘战斗"],
        "weaknesses": ["布局理论", "官子精度"],
        "training_plan": {
            "phase": "Phase 2",
            "week": 5,
            "day": 28,
            "current_task": "中盘战斗训练"
        }
    },
    "qoder": {
        "id": "qoder",
        "name": "qoder",
        "role": "实战工程师",
        "level": "1级",
        "color": "#a855f7",
        "stats": {
            "total_games": 42,
            "wins": 22,
            "losses": 20,
            "win_rate": 52.4,
            "problems_solved": 520,
            "wrong_answers": 15,
            "accuracy": 97.1,
            "last_active": "2026-06-28T10:30:00",
            "hours_ago": 130
        },
        "abilities": {
            "calculation": 0.60,
            "judgment": 0.70,
            "layout": 0.65,
            "defense": 0.80,
            "memory": 0.70
        },
        "strengths": ["实战对局", "中盘战斗", "代码能力"],
        "weaknesses": ["定式记忆", "布局理论"],
        "training_plan": {
            "phase": "Phase 2",
            "week": 5,
            "day": 22,
            "current_task": "定式训练"
        }
    }
}

# 对局数据
GAMES = {
    "active": [
        {
            "id": "game_001",
            "black": "xiaochen",
            "white": "zhuguxia",
            "board_size": 9,
            "moves": [
                {"move": 1, "color": "black", "coord": "F4", "row": 5, "col": 5},
                {"move": 2, "color": "white", "coord": "E5", "row": 4, "col": 4},
                {"move": 3, "color": "black", "coord": "D4", "row": 3, "col": 3},
                {"move": 4, "color": "white", "coord": "D6", "row": 5, "col": 3},
                {"move": 5, "color": "black", "coord": "F6", "row": 5, "col": 5},
                {"move": 6, "color": "white", "coord": "F2", "row": 1, "col": 5},
                {"move": 7, "color": "black", "coord": "H8", "row": 7, "col": 7},
                {"move": 8, "color": "white", "coord": "B1", "row": 0, "col": 1},
                {"move": 9, "color": "black", "coord": "C6", "row": 5, "col": 2},
                {"move": 10, "color": "white", "coord": "F3", "row": 2, "col": 5},
                {"move": 11, "color": "black", "coord": "E8", "row": 7, "col": 4},
                {"move": 12, "color": "white", "coord": "C2", "row": 1, "col": 2},
                {"move": 13, "color": "black", "coord": "A4", "row": 3, "col": 0},
                {"move": 14, "color": "white", "coord": "B6", "row": 5, "col": 1},
                {"move": 15, "color": "black", "coord": "A7", "row": 6, "col": 0}
            ],
            "status": "playing",
            "current_turn": "white",
            "started_at": "2026-07-04T10:00:00",
            "last_move_at": "2026-07-04T10:12:45",
            "komi": 7.5,
            "result": None
        }
    ],
    "completed": [
        {
            "id": "game_000",
            "black": "xiaochen",
            "white": "zhuguxia",
            "result": "小陈胜",
            "score": "174:167",
            "moves_count": 287,
            "date": "2026-06-27",
            "board_size": 19
        },
        {
            "id": "game_-1",
            "black": "qoder",
            "white": "xiaochen",
            "result": "qoder胜",
            "score": "165:162",
            "moves_count": 245,
            "date": "2026-06-27",
            "board_size": 19
        },
        {
            "id": "game_-2",
            "black": "zhuguxia",
            "white": "qoder",
            "result": "诸葛虾胜",
            "score": "173:162",
            "moves_count": 268,
            "date": "2026-06-27",
            "board_size": 19
        }
    ]
}

# 训练任务
TRAINING_TASKS = {
    "xiaochen": [
        {"id": "t1", "type": "死活题", "difficulty": "中级", "status": "进行中", "progress": 65},
        {"id": "t2", "type": "手筋", "difficulty": "初级", "status": "已完成", "progress": 100},
        {"id": "t3", "type": "官子", "difficulty": "中级", "status": "未开始", "progress": 0}
    ],
    "zhuguxia": [
        {"id": "t4", "type": "中盘战斗", "difficulty": "高级", "status": "进行中", "progress": 45},
        {"id": "t5", "type": "布局理论", "difficulty": "中级", "status": "进行中", "progress": 30},
        {"id": "t6", "type": "官子精度", "difficulty": "高级", "status": "未开始", "progress": 0}
    ],
    "qoder": [
        {"id": "t7", "type": "定式记忆", "difficulty": "中级", "status": "进行中", "progress": 55},
        {"id": "t8", "type": "布局理论", "difficulty": "初级", "status": "未开始", "progress": 0}
    ]
}

# 缓存
_cache = {"data": None, "timestamp": 0, "lock": threading.Lock()}
CACHE_TTL = 25
collector = LobsterDataCollector()

# ============================================================
# API 端点
# ============================================================

@app.route('/')
def index():
    """重定向到围棋仪表盘"""
    return send_from_directory('docs', 'go_dashboard.html')

@app.route('/api/students')
def api_students():
    """获取所有学员数据"""
    return jsonify(STUDENTS)

@app.route('/api/student/<student_id>')
def api_student_detail(student_id):
    """获取单个学员详情"""
    if student_id in STUDENTS:
        student = STUDENTS[student_id]
        student["tasks"] = TRAINING_TASKS.get(student_id, [])
        student["recent_games"] = [g for g in GAMES["completed"] if g["black"] == student_id or g["white"] == student_id][:5]
        return jsonify(student)
    return jsonify({"error": "学员不存在"}), 404

@app.route('/api/games')
def api_games():
    """获取对局列表"""
    return jsonify({
        "active": GAMES["active"],
        "completed": GAMES["completed"][-10:]
    })

@app.route('/api/game/<game_id>')
def api_game_detail(game_id):
    """获取对局详情"""
    for game in GAMES["active"] + GAMES["completed"]:
        if game["id"] == game_id:
            return jsonify(game)
    return jsonify({"error": "对局不存在"}), 404

@app.route('/api/game/start', methods=['POST'])
def api_game_start():
    """发起新对局"""
    data = request.json
    black = data.get("black")
    white = data.get("white")
    board_size = data.get("board_size", 9)
    
    if black not in STUDENTS or white not in STUDENTS:
        return jsonify({"error": "学员不存在"}), 400
    
    game_id = f"game_{uuid.uuid4().hex[:8]}"
    new_game = {
        "id": game_id,
        "black": black,
        "white": white,
        "board_size": board_size,
        "moves": [],
        "status": "playing",
        "current_turn": "black",
        "started_at": datetime.now().isoformat(),
        "last_move_at": datetime.now().isoformat(),
        "komi": 7.5,
        "result": None
    }
    GAMES["active"].append(new_game)
    
    return jsonify({"status": "ok", "game": new_game})

@app.route('/api/game/<game_id>/move', methods=['POST'])
def api_game_move(game_id):
    """落子"""
    data = request.json
    color = data.get("color")
    row = data.get("row")
    col = data.get("col")
    
    # 查找对局
    game = None
    for g in GAMES["active"]:
        if g["id"] == game_id:
            game = g
            break
    
    if not game:
        return jsonify({"error": "对局不存在"}), 404
    
    if game["current_turn"] != color:
        return jsonify({"error": "不是你的回合"}), 400
    
    # 坐标转换
    REV_COL_MAP = {i: c for i, c in enumerate('ABCDEFGHJKLMNOPQRST')}
    coord = f"{REV_COL_MAP[col]}{row+1}"
    
    move_num = len(game["moves"]) + 1
    new_move = {
        "move": move_num,
        "color": color,
        "coord": coord,
        "row": row,
        "col": col,
        "timestamp": datetime.now().isoformat()
    }
    game["moves"].append(new_move)
    game["last_move_at"] = datetime.now().isoformat()
    
    # 切换回合
    game["current_turn"] = "white" if color == "black" else "black"
    
    return jsonify({"status": "ok", "move": new_move, "current_turn": game["current_turn"]})

@app.route('/api/game/<game_id>/resign', methods=['POST'])
def api_game_resign(game_id):
    """认输"""
    data = request.json
    resign_color = data.get("color")
    
    for game in GAMES["active"]:
        if game["id"] == game_id:
            winner = "white" if resign_color == "black" else "black"
            winner_name = STUDENTS[game["white"] if winner == "white" else game["black"]]["name"]
            game["status"] = "completed"
            game["result"] = f"{winner_name}胜 (对方认输)"
            game["completed_at"] = datetime.now().isoformat()
            GAMES["active"].remove(game)
            GAMES["completed"].append(game)
            return jsonify({"status": "ok", "result": game["result"]})
    
    return jsonify({"error": "对局不存在"}), 404

@app.route('/api/training')
def api_training():
    """获取所有训练任务"""
    return jsonify(TRAINING_TASKS)

@app.route('/api/training/<student_id>')
def api_student_training(student_id):
    """获取学员训练任务"""
    if student_id in TRAINING_TASKS:
        return jsonify(TRAINING_TASKS[student_id])
    return jsonify({"error": "学员不存在"}), 404

@app.route('/api/training/start', methods=['POST'])
def api_training_start():
    """开始训练任务"""
    data = request.json
    student_id = data.get("student_id")
    task_type = data.get("task_type")
    difficulty = data.get("difficulty", "中级")
    
    if student_id not in TRAINING_TASKS:
        TRAINING_TASKS[student_id] = []
    
    task_id = f"t{uuid.uuid4().hex[:6]}"
    new_task = {
        "id": task_id,
        "type": task_type,
        "difficulty": difficulty,
        "status": "进行中",
        "progress": 0,
        "started_at": datetime.now().isoformat()
    }
    TRAINING_TASKS[student_id].append(new_task)
    
    return jsonify({"status": "ok", "task": new_task})

@app.route('/api/training/<task_id>/progress', methods=['POST'])
def api_training_progress(task_id):
    """更新训练进度"""
    data = request.json
    progress = data.get("progress", 0)
    
    for student_tasks in TRAINING_TASKS.values():
        for task in student_tasks:
            if task["id"] == task_id:
                task["progress"] = progress
                if progress >= 100:
                    task["status"] = "已完成"
                return jsonify({"status": "ok", "task": task})
    
    return jsonify({"error": "任务不存在"}), 404

@app.route('/api/coach/guide', methods=['POST'])
def api_coach_guide():
    """教练引导"""
    data = request.json
    student_id = data.get("student_id")
    action = data.get("action")  # "start_training", "play_game", "review", "rest"
    message = data.get("message", "")
    
    if student_id not in STUDENTS:
        return jsonify({"error": "学员不存在"}), 400
    
    # 记录引导
    guide_log = {
        "id": f"guide_{uuid.uuid4().hex[:6]}",
        "student_id": student_id,
        "action": action,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "coach": "诸葛马"
    }
    
    return jsonify({"status": "ok", "guide": guide_log})

@app.route('/api/coach/recommendations')
def api_coach_recommendations():
    """获取教练推荐"""
    recommendations = []
    
    for sid, student in STUDENTS.items():
        # 基于能力画像的推荐
        abilities = student["abilities"]
        
        # 计算力弱 → 推荐死活题
        if abilities["calculation"] < 0.7:
            recommendations.append({
                "student_id": sid,
                "student_name": student["name"],
                "type": "训练",
                "priority": "高",
                "content": f"{student['name']}计算力({abilities['calculation']*100:.0f}%)偏低，建议加强死活题训练",
                "action": "start_training",
                "task_type": "死活题",
                "difficulty": "中级"
            })
        
        # 布局力弱 → 推荐布局理论
        if abilities["layout"] < 0.6:
            recommendations.append({
                "student_id": sid,
                "student_name": student["name"],
                "type": "训练",
                "priority": "中",
                "content": f"{student['name']}布局力({abilities['layout']*100:.0f}%)偏低，建议学习布局理论",
                "action": "start_training",
                "task_type": "布局理论",
                "difficulty": "初级"
            })
        
        # 长时间未活跃 → 提醒
        if student["stats"]["hours_ago"] > 48:
            recommendations.append({
                "student_id": sid,
                "student_name": student["name"],
                "type": "提醒",
                "priority": "高",
                "content": f"{student['name']}已{student['stats']['hours_ago']}小时未活跃，建议跟进",
                "action": "remind"
            })
        
        # 胜率低于50% → 建议对局
        if student["stats"]["win_rate"] < 50:
            recommendations.append({
                "student_id": sid,
                "student_name": student["name"],
                "type": "对局",
                "priority": "中",
                "content": f"{student['name']}胜率({student['stats']['win_rate']}%)偏低，建议增加对局练习",
                "action": "play_game"
            })
    
    return jsonify(recommendations)

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
        "mqtt": data["mqtt"],
        "timestamp": data["timestamp"]
    })

@app.route('/api/force-refresh')
def api_force_refresh():
    """强制刷新缓存"""
    with _cache["lock"]:
        _cache["data"] = None
        _cache["timestamp"] = 0
    data = collector.collect_all()
    with _cache["lock"]:
        _cache["data"] = data
        _cache["timestamp"] = time.time()
    return jsonify({"status": "refreshed", "timestamp": data["timestamp"]})

@app.route('/api/health')
def api_health():
    """健康检查"""
    return jsonify({
        "status": "ok",
        "cache_age": round(time.time() - _cache["timestamp"], 1),
        "has_cache": _cache["data"] is not None,
        "active_games": len(GAMES["active"]),
        "total_students": len(STUDENTS)
    })

if __name__ == '__main__':
    print("=" * 50)
    print("🦞 围棋训练监控仪表盘 API")
    print("=" * 50)
    print(f"监听: 0.0.0.0:5001")
    print(f"仪表盘: http://<IP>:5001/")
    print("=" * 50)
    
    # 预加载缓存
    print("📡 首次数据采集...")
    with _cache["lock"]:
        _cache["data"] = collector.collect_all()
        _cache["timestamp"] = time.time()
    print("✅ 缓存已就绪")
    
    app.run(host='0.0.0.0', port=5001, debug=False)
