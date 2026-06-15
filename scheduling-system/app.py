#!/usr/bin/env python3
"""
学校排课系统 - Web 版
Flask 后端 API
"""
from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_cors import CORS
import sqlite3
import os
from pathlib import Path
import sys

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from src.scheduler import Scheduler
from utils.db import Database

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# 数据库实例
db = Database("data/school.db")
db.connect()


# ==================== 页面路由 ====================

@app.route('/')
def index():
    """首页"""
    return send_file('static/index.html')


@app.route('/download')
def download_page():
    """下载页面"""
    return send_file('static/download.html')


@app.route('/qr')
def qr_page():
    """二维码下载页面"""
    return send_file('static/qr-download.html')


@app.route('/downloads/<filename>')
def download_file(filename):
    """下载文件"""
    return send_from_directory('../downloads', filename, as_attachment=True)


# ==================== API 路由 ====================

@app.route('/api/teachers', methods=['GET'])
def get_teachers():
    """获取教师列表"""
    rows = db.fetch_all("SELECT * FROM teachers ORDER BY id")
    return jsonify([dict(row) for row in rows])


@app.route('/api/teachers', methods=['POST'])
def add_teacher():
    """添加教师"""
    data = request.json
    result = db.insert("teachers", {
        "name": data["name"],
        "subject": data["subject"],
        "max_weekly_hours": data.get("max_weekly_hours", 16),
        "email": data.get("email", ""),
        "phone": data.get("phone", ""),
        "notes": data.get("notes", "")
    })
    return jsonify({"success": True, "id": result})


@app.route('/api/teachers/<int:id>', methods=['DELETE'])
def delete_teacher(id):
    """删除教师"""
    db.delete("teachers", "id = ?", (id,))
    return jsonify({"success": True})


@app.route('/api/classes', methods=['GET'])
def get_classes():
    """获取班级列表"""
    rows = db.fetch_all("""
        SELECT c.*, t.name as homeroom_teacher_name
        FROM classes c
        LEFT JOIN teachers t ON c.homeroom_teacher_id = t.id
        ORDER BY c.grade, c.name
    """)
    return jsonify([dict(row) for row in rows])


@app.route('/api/classes', methods=['POST'])
def add_class():
    """添加班级"""
    data = request.json
    result = db.insert("classes", {
        "name": data["name"],
        "grade": data["grade"],
        "student_count": data.get("student_count", 45),
        "homeroom_teacher_id": data.get("homeroom_teacher_id")
    })
    return jsonify({"success": True, "id": result})


@app.route('/api/classes/<int:id>', methods=['DELETE'])
def delete_class(id):
    """删除班级"""
    db.delete("classes", "id = ?", (id,))
    return jsonify({"success": True})


@app.route('/api/courses', methods=['GET'])
def get_courses():
    """获取课程列表"""
    rows = db.fetch_all("""
        SELECT c.*, cl.name as class_name, t.name as teacher_name
        FROM courses c
        JOIN classes cl ON c.class_id = cl.id
        JOIN teachers t ON c.teacher_id = t.id
        ORDER BY cl.name, c.subject
    """)
    return jsonify([dict(row) for row in rows])


@app.route('/api/courses', methods=['POST'])
def add_course():
    """添加课程"""
    data = request.json
    result = db.insert("courses", {
        "class_id": data["class_id"],
        "teacher_id": data["teacher_id"],
        "subject": data["subject"],
        "weekly_hours": data.get("weekly_hours", 2),
        "consecutive": data.get("consecutive", 1),
        "requirements": data.get("requirements", "")
    })
    return jsonify({"success": True, "id": result})


@app.route('/api/courses/<int:id>', methods=['DELETE'])
def delete_course(id):
    """删除课程"""
    db.delete("courses", "id = ?", (id,))
    return jsonify({"success": True})


@app.route('/api/meetings', methods=['GET'])
def get_meetings():
    """获取会议时间"""
    rows = db.fetch_all("SELECT * FROM meetings ORDER BY day_of_week, period")
    return jsonify([dict(row) for row in rows])


@app.route('/api/meetings', methods=['POST'])
def add_meeting():
    """添加会议时间"""
    data = request.json
    result = db.insert("meetings", {
        "name": data["name"],
        "day_of_week": data["day_of_week"],
        "period": data["period"],
        "recurring": 1 if data.get("recurring", True) else 0
    })
    return jsonify({"success": True, "id": result})


@app.route('/api/meetings/<int:id>', methods=['DELETE'])
def delete_meeting(id):
    """删除会议时间"""
    db.delete("meetings", "id = ?", (id,))
    return jsonify({"success": True})


@app.route('/api/schedule/run', methods=['POST'])
def run_schedule():
    """执行排课"""
    scheduler = Scheduler(db)
    result = scheduler.run()
    return jsonify(result)


@app.route('/api/schedule/<int:class_id>', methods=['GET'])
def get_schedule(class_id):
    """获取班级课表"""
    rows = db.fetch_all("""
        SELECT s.*, c.name as class_name, t.name as teacher_name, co.subject
        FROM schedules s
        JOIN classes c ON s.class_id = c.id
        JOIN teachers t ON s.teacher_id = t.id
        JOIN courses co ON s.course_id = co.id
        WHERE s.class_id = ?
        ORDER BY s.day_of_week, s.period
    """, (class_id,))
    return jsonify([dict(row) for row in rows])


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取统计数据"""
    teachers = db.fetch_one("SELECT COUNT(*) as count FROM teachers")["count"]
    classes = db.fetch_one("SELECT COUNT(*) as count FROM classes")["count"]
    courses = db.fetch_one("SELECT COUNT(*) as count FROM courses")["count"]
    schedules = db.fetch_one("SELECT COUNT(*) as count FROM schedules")["count"]
    
    return jsonify({
        "teachers": teachers,
        "classes": classes,
        "courses": courses,
        "schedules": schedules
    })


@app.route('/api/reset', methods=['POST'])
def reset_data():
    """重置所有数据"""
    db.execute("DELETE FROM schedules")
    db.execute("DELETE FROM meetings")
    db.execute("DELETE FROM courses")
    db.execute("DELETE FROM classes")
    db.execute("DELETE FROM teachers")
    db.commit()
    return jsonify({"success": True})


if __name__ == '__main__':
    print("🚀 排课系统 Web 版启动中...")
    print("📱 访问地址：http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
