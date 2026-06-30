#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学生证件照识别系统 - 后端服务
功能：上传学生照片建立数据库，上传现场照片进行识别匹配
"""

import os
import json
import base64
from pathlib import Path
from datetime import datetime

# 尝试导入人脸识别库
try:
    import face_recognition
    import numpy as np
    from PIL import Image
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("⚠️  face_recognition 库未安装，将使用基础模式")

class StudentRecognizer:
    def __init__(self, data_dir="student_data"):
        self.data_dir = Path(data_dir)
        self.photos_dir = self.data_dir / "photos"
        self.db_file = self.data_dir / "student_db.json"
        self.known_encodings = []
        self.known_names = []
        self.known_classes = []
        
        # 创建目录
        self.photos_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载已有数据
        self.load_database()
    
    def load_database(self):
        """加载学生数据库"""
        if not self.db_file.exists():
            return
        
        with open(self.db_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.known_names = data.get('names', [])
        self.known_classes = data.get('classes', [])
        self.known_encodings = []
        
        # 重新编码所有照片
        if FACE_RECOGNITION_AVAILABLE:
            for photo_file in data.get('photos', []):
                photo_path = self.photos_dir / photo_file
                if photo_path.exists():
                    encoding = self.encode_image(str(photo_path))
                    if encoding is not None:
                        self.known_encodings.append(encoding)
    
    def encode_image(self, image_path):
        """将图片转换为人脸特征编码"""
        if not FACE_RECOGNITION_AVAILABLE:
            return None
        
        try:
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                return encodings[0].tolist()
        except Exception as e:
            print(f"编码失败：{e}")
        return None
    
    def add_student(self, photo_data, name, class_name):
        """添加学生到数据库"""
        # 解码 base64 图片
        if ',' in photo_data:
            photo_data = photo_data.split(',')[1]
        
        photo_bytes = base64.b64decode(photo_data)
        photo_filename = f"{name}_{class_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        photo_path = self.photos_dir / photo_filename
        
        # 保存图片
        with open(photo_path, 'wb') as f:
            f.write(photo_bytes)
        
        # 如果是简单模式，只保存信息
        if not FACE_RECOGNITION_AVAILABLE:
            student_data = {
                'names': self.known_names + [name],
                'classes': self.known_classes + [class_name],
                'photos': [photo_filename]
            }
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(student_data, f, ensure_ascii=False, indent=2)
            return True
        
        # 编码人脸
        encoding = self.encode_image(str(photo_path))
        if encoding is None:
            return False
        
        self.known_names.append(name)
        self.known_classes.append(class_name)
        self.known_encodings.append(encoding)
        
        # 保存数据库
        student_data = {
            'names': self.known_names,
            'classes': self.known_classes,
            'photos': [f for f in os.listdir(self.photos_dir) if f.endswith('.jpg')]
        }
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(student_data, f, ensure_ascii=False, indent=2)
        
        return True
    
    def recognize(self, photo_data):
        """识别人脸"""
        # 解码 base64 图片
        if ',' in photo_data:
            photo_data = photo_data.split(',')[1]
        
        photo_bytes = base64.b64decode(photo_data)
        temp_path = self.data_dir / "temp_recognize.jpg"
        
        with open(temp_path, 'wb') as f:
            f.write(photo_bytes)
        
        if not FACE_RECOGNITION_AVAILABLE:
            os.remove(temp_path)
            return {
                'success': False,
                'message': '人脸识别库未安装，仅支持基础模式'
            }
        
        try:
            # 识别人脸
            unknown_image = face_recognition.load_image_file(str(temp_path))
            unknown_encodings = face_recognition.face_encodings(unknown_image)
            
            if not unknown_encodings:
                os.remove(temp_path)
                return {
                    'success': False,
                    'message': '未检测到人脸'
                }
            
            unknown_encoding = unknown_encodings[0]
            
            # 匹配已知人脸
            if not self.known_encodings:
                os.remove(temp_path)
                return {
                    'success': False,
                    'message': '学生数据库为空，请先上传学生证件照'
                }
            
            matches = face_recognition.compare_faces(self.known_encodings, unknown_encoding, tolerance=0.6)
            face_distances = face_recognition.face_distance(self.known_encodings, unknown_encoding)
            
            os.remove(temp_path)
            
            if True in matches:
                best_match_index = np.argmin(face_distances)
                confidence = (1 - face_distances[best_match_index]) * 100
                
                return {
                    'success': True,
                    'name': self.known_names[best_match_index],
                    'class': self.known_classes[best_match_index],
                    'confidence': f"{confidence:.1f}%"
                }
            else:
                return {
                    'success': False,
                    'message': '未找到匹配的学生'
                }
                
        except Exception as e:
            if temp_path.exists():
                os.remove(temp_path)
            return {
                'success': False,
                'message': f'识别失败：{str(e)}'
            }
    
    def get_stats(self):
        """获取数据库统计"""
        return {
            'total_students': len(self.known_names),
            'students': list(zip(self.known_names, self.known_classes))
        }

# 创建 Flask 应用
try:
    from flask import Flask, request, jsonify, send_file
    from flask_cors import CORS
    
    app = Flask(__name__)
    CORS(app)
    recognizer = StudentRecognizer()
    
    @app.route('/')
    def index():
        return send_file('index.html')
    
    @app.route('/api/add_student', methods=['POST'])
    def add_student():
        data = request.json
        photo = data.get('photo')
        name = data.get('name')
        class_name = data.get('class')
        
        if not all([photo, name, class_name]):
            return jsonify({'success': False, 'message': '缺少必要信息'}), 400
        
        success = recognizer.add_student(photo, name, class_name)
        if success:
            return jsonify({'success': True, 'message': f'已添加学生：{name} ({class_name})'})
        else:
            return jsonify({'success': False, 'message': '人脸检测失败'}), 400
    
    @app.route('/api/recognize', methods=['POST'])
    def recognize():
        data = request.json
        photo = data.get('photo')
        
        if not photo:
            return jsonify({'success': False, 'message': '请上传照片'}), 400
        
        result = recognizer.recognize(photo)
        return jsonify(result)
    
    @app.route('/api/stats', methods=['GET'])
    def stats():
        return jsonify(recognizer.get_stats())
    
    if __name__ == '__main__':
        print("🦞 学生证件照识别系统启动中...")
        print("📍 访问地址：http://localhost:5000")
        if not FACE_RECOGNITION_AVAILABLE:
            print("⚠️  提示：安装 face_recognition 获得完整功能")
            print("   pip install face_recognition")
        app.run(host='0.0.0.0', port=5000, debug=True)
        
except ImportError:
    print("⚠️  Flask 未安装，请运行：pip install flask flask-cors")
    print("或者使用 Streamlit 版本：streamlit run app_streamlit.py")
