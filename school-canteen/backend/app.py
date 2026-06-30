#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学校食堂菜单管理系统 - Flask 后端 API
"""

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from functools import wraps
import sqlite3
import bcrypt
import jwt
import datetime
import os
import json
from io import BytesIO

app = Flask(__name__, static_folder='../public', static_url_path='')
CORS(app)

# 配置
app.config['SECRET_KEY'] = os.environ.get('JWT_SECRET', 'school-canteen-secret-key-2026')
app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), '../database/canteen.db')

# ============ 数据库连接 ============

def get_db():
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    with open(os.path.join(os.path.dirname(__file__), '../database/schema.sql'), 'r', encoding='utf-8') as f:
        db.executescript(f.read())
    
    # 创建默认管理员账号
    password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    db.execute(
        "INSERT OR IGNORE INTO users (username, password_hash, real_name, role) VALUES (?, ?, ?, ?)",
        ('admin', password_hash, '系统管理员', 1)
    )
    db.commit()
    db.close()
    print("✅ 数据库初始化完成！")
    print("👤 默认管理员账号：admin / admin123")

# ============ 认证装饰器 ============

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]
        
        if not token:
            return jsonify({'error': '未授权'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = data
        except:
            return jsonify({'error': '令牌无效'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

def require_role(*roles):
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated(current_user, *args, **kwargs):
            if current_user['role'] not in roles:
                return jsonify({'error': '权限不足'}), 403
            return f(current_user, *args, **kwargs)
        return decorated
    return decorator

# ============ 认证接口 ============

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    db.close()
    
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        return jsonify({'error': '用户名或密码错误'}), 401
    
    token = jwt.encode({
        'id': user['id'],
        'username': user['username'],
        'role': user['role'],
        'real_name': user['real_name'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        'token': token,
        'user': {
            'id': user['id'],
            'username': user['username'],
            'real_name': user['real_name'],
            'role': user['role']
        }
    })

@app.route('/api/user/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    db = get_db()
    user = db.execute(
        'SELECT id, username, real_name, role, created_at FROM users WHERE id = ?',
        (current_user['id'],)
    ).fetchone()
    db.close()
    return jsonify(dict(user)) if user else jsonify({'error': '用户不存在'}), 404

# ============ 用户管理接口 ============

@app.route('/api/users', methods=['GET'])
@require_role(1)
def get_users(current_user):
    db = get_db()
    users = db.execute('SELECT id, username, real_name, role, created_at FROM users').fetchall()
    db.close()
    return jsonify([dict(u) for u in users])

@app.route('/api/users', methods=['POST'])
@require_role(1)
def create_user(current_user):
    data = request.get_json()
    password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    db = get_db()
    try:
        db.execute(
            'INSERT INTO users (username, password_hash, real_name, role) VALUES (?, ?, ?, ?)',
            (data['username'], password_hash, data['real_name'], data['role'])
        )
        db.commit()
        result = db.execute('SELECT last_insert_rowid()').fetchone()
        db.close()
        return jsonify({'id': result[0], 'message': '用户创建成功'})
    except sqlite3.IntegrityError:
        db.close()
        return jsonify({'error': '用户名已存在'}), 400

# ============ 原材料管理接口 ============

@app.route('/api/ingredients', methods=['GET'])
@token_required
def get_ingredients(current_user):
    db = get_db()
    ingredients = db.execute('SELECT * FROM ingredients ORDER BY category, name').fetchall()
    db.close()
    return jsonify([dict(i) for i in ingredients])

@app.route('/api/ingredients', methods=['POST'])
@require_role(1, 2)
def create_ingredient(current_user):
    data = request.get_json()
    db = get_db()
    db.execute(
        'INSERT INTO ingredients (name, category, unit, unit_price, supplier) VALUES (?, ?, ?, ?, ?)',
        (data['name'], data.get('category', ''), data['unit'], data.get('unit_price', 0), data.get('supplier', ''))
    )
    db.commit()
    result = db.execute('SELECT last_insert_rowid()').fetchone()
    db.close()
    return jsonify({'id': result[0], 'message': '原材料创建成功'})

@app.route('/api/ingredients/<int:id>', methods=['PUT'])
@require_role(1, 2)
def update_ingredient(current_user, id):
    data = request.get_json()
    db = get_db()
    db.execute(
        'UPDATE ingredients SET name=?, category=?, unit=?, unit_price=?, supplier=?, updated_at=CURRENT_TIMESTAMP WHERE id=?',
        (data['name'], data.get('category', ''), data['unit'], data.get('unit_price', 0), data.get('supplier', ''), id)
    )
    db.commit()
    db.close()
    return jsonify({'message': '原材料更新成功'})

@app.route('/api/ingredients/<int:id>', methods=['DELETE'])
@require_role(1)
def delete_ingredient(current_user, id):
    db = get_db()
    db.execute('DELETE FROM ingredients WHERE id = ?', (id,))
    db.commit()
    db.close()
    return jsonify({'message': '原材料删除成功'})

# ============ 菜品管理接口 ============

@app.route('/api/dishes', methods=['GET'])
@token_required
def get_dishes(current_user):
    db = get_db()
    dishes = db.execute("""
        SELECT d.*, 
               GROUP_CONCAT(di.ingredient_id) as ingredient_ids,
               SUM(di.cost) as total_cost
        FROM dishes d
        LEFT JOIN dish_ingredients di ON d.id = di.dish_id
        WHERE d.is_active = 1
        GROUP BY d.id
        ORDER BY d.category, d.name
    """).fetchall()
    db.close()
    return jsonify([dict(d) for d in dishes])

@app.route('/api/dishes/<int:id>', methods=['GET'])
@token_required
def get_dish(current_user, id):
    db = get_db()
    dish = db.execute('SELECT * FROM dishes WHERE id = ?', (id,)).fetchone()
    if not dish:
        db.close()
        return jsonify({'error': '菜品不存在'}), 404
    
    ingredients = db.execute("""
        SELECT di.*, i.name as ingredient_name, i.unit as default_unit, i.unit_price
        FROM dish_ingredients di
        JOIN ingredients i ON di.ingredient_id = i.id
        WHERE di.dish_id = ?
    """, (id,)).fetchall()
    db.close()
    
    result = dict(dish)
    result['ingredients'] = [dict(i) for i in ingredients]
    return jsonify(result)

@app.route('/api/dishes', methods=['POST'])
@require_role(1, 2)
def create_dish(current_user):
    data = request.get_json()
    total_time = (data.get('prep_time', 0) or 0) + (data.get('cook_time', 0) or 0)
    
    db = get_db()
    db.execute(
        'INSERT INTO dishes (name, category, description, prep_time, cook_time, total_time, base_cost) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (data['name'], data.get('category', ''), data.get('description', ''), data.get('prep_time', 0), data.get('cook_time', 0), total_time, 0)
    )
    db.commit()
    dish_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    
    # 添加配料
    total_cost = 0
    if data.get('ingredients'):
        for ing in data['ingredients']:
            ingredient = db.execute('SELECT * FROM ingredients WHERE id = ?', (ing['ingredient_id'],)).fetchone()
            cost = (ingredient['unit_price'] or 0) * (ing.get('quantity', 0) or 0) if ingredient else 0
            db.execute(
                'INSERT INTO dish_ingredients (dish_id, ingredient_id, quantity, unit, cost) VALUES (?, ?, ?, ?, ?)',
                (dish_id, ing['ingredient_id'], ing.get('quantity', 0), ing.get('unit') or ingredient['unit'] if ingredient else '', cost)
            )
            total_cost += cost
        
        db.execute('UPDATE dishes SET base_cost = ? WHERE id = ?', (total_cost, dish_id))
        db.commit()
    
    db.close()
    return jsonify({'id': dish_id, 'message': '菜品创建成功'})

@app.route('/api/dishes/<int:id>', methods=['PUT'])
@require_role(1, 2)
def update_dish(current_user, id):
    data = request.get_json()
    total_time = (data.get('prep_time', 0) or 0) + (data.get('cook_time', 0) or 0)
    
    db = get_db()
    db.execute(
        'UPDATE dishes SET name=?, category=?, description=?, prep_time=?, cook_time=?, total_time=?, updated_at=CURRENT_TIMESTAMP WHERE id=?',
        (data['name'], data.get('category', ''), data.get('description', ''), data.get('prep_time', 0), data.get('cook_time', 0), total_time, id)
    )
    
    # 更新配料
    if 'ingredients' in data:
        db.execute('DELETE FROM dish_ingredients WHERE dish_id = ?', (id,))
        total_cost = 0
        for ing in data['ingredients']:
            ingredient = db.execute('SELECT * FROM ingredients WHERE id = ?', (ing['ingredient_id'],)).fetchone()
            cost = (ingredient['unit_price'] or 0) * (ing.get('quantity', 0) or 0) if ingredient else 0
            db.execute(
                'INSERT INTO dish_ingredients (dish_id, ingredient_id, quantity, unit, cost) VALUES (?, ?, ?, ?, ?)',
                (id, ing['ingredient_id'], ing.get('quantity', 0), ing.get('unit') or ingredient['unit'] if ingredient else '', cost)
            )
            total_cost += cost
        db.execute('UPDATE dishes SET base_cost = ? WHERE id = ?', (total_cost, id))
    
    db.commit()
    db.close()
    return jsonify({'message': '菜品更新成功'})

@app.route('/api/dishes/<int:id>', methods=['DELETE'])
@require_role(1)
def delete_dish(current_user, id):
    db = get_db()
    db.execute('UPDATE dishes SET is_active = 0 WHERE id = ?', (id,))
    db.commit()
    db.close()
    return jsonify({'message': '菜品已删除'})

# ============ 周菜单管理接口 ============

@app.route('/api/weekly-menus', methods=['GET'])
@token_required
def get_weekly_menus(current_user):
    db = get_db()
    menus = db.execute("""
        SELECT wm.*, u1.real_name as created_name, u2.real_name as reviewed_name
        FROM weekly_menus wm
        LEFT JOIN users u1 ON wm.created_by = u1.id
        LEFT JOIN users u2 ON wm.reviewed_by = u2.id
        ORDER BY wm.week_start DESC
    """).fetchall()
    db.close()
    return jsonify([dict(m) for m in menus])

@app.route('/api/weekly-menus/<int:id>', methods=['GET'])
@token_required
def get_weekly_menu(current_user, id):
    db = get_db()
    menu = db.execute("""
        SELECT wm.*, u1.real_name as created_name, u2.real_name as reviewed_name
        FROM weekly_menus wm
        LEFT JOIN users u1 ON wm.created_by = u1.id
        LEFT JOIN users u2 ON wm.reviewed_by = u2.id
        WHERE wm.id = ?
    """, (id,)).fetchone()
    
    if not menu:
        db.close()
        return jsonify({'error': '周菜单不存在'}), 404
    
    daily_menus = db.execute("""
        SELECT dm.*, d.name as dish_name, d.category as dish_category, d.prep_time, d.cook_time, d.base_cost
        FROM daily_menus dm
        JOIN dishes d ON dm.dish_id = d.id
        WHERE dm.weekly_menu_id = ?
        ORDER BY dm.day_of_week, dm.meal_type, dm.sort_order
    """, (id,)).fetchall()
    db.close()
    
    result = dict(menu)
    result['daily_menus'] = [dict(dm) for dm in daily_menus]
    return jsonify(result)

@app.route('/api/weekly-menus', methods=['POST'])
@require_role(1, 2)
def create_weekly_menu(current_user):
    data = request.get_json()
    
    db = get_db()
    db.execute(
        'INSERT INTO weekly_menus (week_start, week_end, status, created_by) VALUES (?, ?, 1, ?)',
        (data['week_start'], data['week_end'], current_user['id'])
    )
    db.commit()
    menu_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    
    # 添加每日菜单
    if data.get('daily_menus'):
        for dm in data['daily_menus']:
            db.execute(
                'INSERT INTO daily_menus (weekly_menu_id, day_of_week, meal_type, dish_id, sort_order, notes) VALUES (?, ?, ?, ?, ?, ?)',
                (menu_id, dm['day_of_week'], dm['meal_type'], dm['dish_id'], dm.get('sort_order', 0), dm.get('notes', ''))
            )
        db.commit()
    
    db.close()
    return jsonify({'id': menu_id, 'message': '周菜单创建成功'})

@app.route('/api/weekly-menus/<int:id>', methods=['PUT'])
@require_role(1, 2)
def update_weekly_menu(current_user, id):
    data = request.get_json()
    
    db = get_db()
    db.execute(
        'UPDATE weekly_menus SET week_start=?, week_end=?, status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?',
        (data.get('week_start'), data.get('week_end'), data.get('status', 1), id)
    )
    
    # 更新每日菜单
    if 'daily_menus' in data:
        db.execute('DELETE FROM daily_menus WHERE weekly_menu_id = ?', (id,))
        for dm in data['daily_menus']:
            db.execute(
                'INSERT INTO daily_menus (weekly_menu_id, day_of_week, meal_type, dish_id, sort_order, notes) VALUES (?, ?, ?, ?, ?, ?)',
                (id, dm['day_of_week'], dm['meal_type'], dm['dish_id'], dm.get('sort_order', 0), dm.get('notes', ''))
            )
    
    db.commit()
    db.close()
    return jsonify({'message': '周菜单更新成功'})

@app.route('/api/weekly-menus/<int:id>/review', methods=['POST'])
@require_role(1, 3)
def review_weekly_menu(current_user, id):
    data = request.get_json()
    approved = data.get('approved', False)
    comment = data.get('comment', '')
    
    status = 4 if approved else 1  # 4:已发布，1:草稿
    
    db = get_db()
    db.execute(
        'UPDATE weekly_menus SET status=?, reviewed_by=?, reviewed_at=CURRENT_TIMESTAMP, review_comment=? WHERE id=?',
        (status, current_user['id'], comment, id)
    )
    db.commit()
    db.close()
    
    return jsonify({'message': '菜单已审核通过' if approved else '菜单已驳回'})

@app.route('/api/weekly-menus/<int:id>', methods=['DELETE'])
@require_role(1)
def delete_weekly_menu(current_user, id):
    db = get_db()
    db.execute('DELETE FROM daily_menus WHERE weekly_menu_id = ?', (id,))
    db.execute('DELETE FROM weekly_menus WHERE id = ?', (id,))
    db.commit()
    db.close()
    return jsonify({'message': '周菜单已删除'})

# ============ 导出 Excel ============

@app.route('/api/weekly-menus/<int:id>/export/excel', methods=['GET'])
@token_required
def export_excel(current_user, id):
    try:
        from openpyxl import Workbook
    except ImportError:
        return jsonify({'error': '请安装 openpyxl: pip install openpyxl'}), 500
    
    db = get_db()
    menu = db.execute('SELECT wm.* FROM weekly_menus wm WHERE wm.id = ?', (id,)).fetchone()
    
    daily_menus = db.execute("""
        SELECT dm.*, d.name as dish_name, d.category as dish_category, d.prep_time, d.cook_time, d.base_cost,
               GROUP_CONCAT(i.name || ':' || di.quantity || di.unit) as ingredients
        FROM daily_menus dm
        JOIN dishes d ON dm.dish_id = d.id
        LEFT JOIN dish_ingredients di ON d.id = di.dish_id
        LEFT JOIN ingredients i ON di.ingredient_id = i.id
        WHERE dm.weekly_menu_id = ?
        GROUP BY dm.id
        ORDER BY dm.day_of_week, dm.meal_type, dm.sort_order
    """, (id,)).fetchall()
    db.close()
    
    wb = Workbook()
    ws = wb.active
    ws.title = '周菜单'
    
    ws.append(['日期', '餐次', '菜品名称', '类别', '原材料', '切配时间', '烹饪时间', '成本 (元)'])
    
    meal_types = {1: '中餐', 2: '晚餐'}
    day_names = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    
    for dm in daily_menus:
        from datetime import datetime, timedelta
        base_date = datetime.strptime(menu['week_start'], '%Y-%m-%d')
        date = base_date + timedelta(days=dm['day_of_week'])
        
        ws.append([
            f"{day_names[dm['day_of_week']]} ({date.strftime('%Y-%m-%d')})",
            meal_types[dm['meal_type']],
            dm['dish_name'],
            dm['dish_category'],
            dm['ingredients'] or '',
            f"{dm['prep_time']}分钟",
            f"{dm['cook_time']}分钟",
            dm['base_cost']
        ])
    
    # 保存为 BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    
    from flask import Response
    return Response(
        output.getvalue(),
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': f'attachment; filename="周菜单_{menu["week_start"]}.xlsx"'}
    )

# ============ 操作日志 ============

@app.route('/api/logs', methods=['POST'])
@token_required
def create_log(current_user):
    data = request.get_json()
    db = get_db()
    db.execute(
        'INSERT INTO operation_logs (user_id, action, target_type, target_id, details) VALUES (?, ?, ?, ?, ?)',
        (current_user['id'], data['action'], data.get('target_type'), data.get('target_id'), json.dumps(data.get('details', {})))
    )
    db.commit()
    db.close()
    return jsonify({'message': '日志记录成功'})

@app.route('/api/logs', methods=['GET'])
@require_role(1)
def get_logs(current_user):
    db = get_db()
    logs = db.execute("""
        SELECT ol.*, u.real_name as user_name
        FROM operation_logs ol
        LEFT JOIN users u ON ol.user_id = u.id
        ORDER BY ol.created_at DESC
        LIMIT 100
    """).fetchall()
    db.close()
    return jsonify([dict(l) for l in logs])

# ============ 静态文件 ============

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# ============ 启动 ============

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'init-db':
        init_db()
    else:
        # 检查数据库是否存在
        if not os.path.exists(app.config['DATABASE']):
            print("📦 初始化数据库...")
            init_db()
        
        print("🍽️  学校食堂菜单管理系统运行中：http://localhost:5000")
        print(f"📊 数据库：{app.config['DATABASE']}")
        app.run(host='0.0.0.0', port=5000, debug=False)
