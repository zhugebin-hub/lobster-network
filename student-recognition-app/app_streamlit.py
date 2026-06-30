#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学生证件照识别系统 - Streamlit 版本
更简单的部署方式，单文件运行
"""

import streamlit as st
import json
import base64
from pathlib import Path
from datetime import datetime
import os

# 尝试导入人脸识别库
try:
    import face_recognition
    import numpy as np
    from PIL import Image
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False

# 页面配置
st.set_page_config(
    page_title="学生证件照识别系统",
    page_icon="🎓",
    layout="centered"
)

# 自定义 CSS 样式（南湖主题）
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 30px;
        margin: 20px;
    }
    h1 {
        text-align: center;
        color: #2c3e50;
    }
    .subtitle {
        text-align: center;
        color: #7f8c8d;
        font-size: 14px;
        margin-bottom: 30px;
    }
    .stButton>button {
        width: 100%;
        background: #3498db;
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 16px;
        font-weight: 600;
    }
    .stButton>button:hover {
        background: #2980b9;
    }
</style>
""", unsafe_allow_html=True)

# 初始化会话状态
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.recognizer = StudentRecognizer()

class StudentRecognizer:
    def __init__(self, data_dir="student_data"):
        self.data_dir = Path(data_dir)
        self.photos_dir = self.data_dir / "photos"
        self.db_file = self.data_dir / "student_db.json"
        self.known_encodings = []
        self.known_names = []
        self.known_classes = []
        
        self.photos_dir.mkdir(parents=True, exist_ok=True)
        self.load_database()
    
    def load_database(self):
        if not self.db_file.exists():
            return
        
        with open(self.db_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.known_names = data.get('names', [])
        self.known_classes = data.get('classes', [])
        self.known_encodings = []
        
        if FACE_RECOGNITION_AVAILABLE:
            for photo_file in data.get('photos', []):
                photo_path = self.photos_dir / photo_file
                if photo_path.exists():
                    encoding = self.encode_image(str(photo_path))
                    if encoding is not None:
                        self.known_encodings.append(encoding)
    
    def encode_image(self, image_path):
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
        if ',' in photo_data:
            photo_data = photo_data.split(',')[1]
        
        photo_bytes = base64.b64decode(photo_data)
        photo_filename = f"{name}_{class_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        photo_path = self.photos_dir / photo_filename
        
        with open(photo_path, 'wb') as f:
            f.write(photo_bytes)
        
        if not FACE_RECOGNITION_AVAILABLE:
            student_data = {
                'names': self.known_names + [name],
                'classes': self.known_classes + [class_name],
                'photos': [photo_filename]
            }
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(student_data, f, ensure_ascii=False, indent=2)
            return True
        
        encoding = self.encode_image(str(photo_path))
        if encoding is None:
            return False
        
        self.known_names.append(name)
        self.known_classes.append(class_name)
        self.known_encodings.append(encoding)
        
        student_data = {
            'names': self.known_names,
            'classes': self.known_classes,
            'photos': [f for f in os.listdir(self.photos_dir) if f.endswith('.jpg')]
        }
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(student_data, f, ensure_ascii=False, indent=2)
        
        return True
    
    def recognize(self, photo_data):
        if ',' in photo_data:
            photo_data = photo_data.split(',')[1]
        
        photo_bytes = base64.b64decode(photo_data)
        temp_path = self.data_dir / "temp_recognize.jpg"
        
        with open(temp_path, 'wb') as f:
            f.write(photo_bytes)
        
        if not FACE_RECOGNITION_AVAILABLE:
            if temp_path.exists():
                os.remove(temp_path)
            return {
                'success': False,
                'message': '人脸识别库未安装'
            }
        
        try:
            unknown_image = face_recognition.load_image_file(str(temp_path))
            unknown_encodings = face_recognition.face_encodings(unknown_image)
            
            if not unknown_encodings:
                if temp_path.exists():
                    os.remove(temp_path)
                return {
                    'success': False,
                    'message': '未检测到人脸'
                }
            
            unknown_encoding = unknown_encodings[0]
            
            if not self.known_encodings:
                if temp_path.exists():
                    os.remove(temp_path)
                return {
                    'success': False,
                    'message': '学生数据库为空'
                }
            
            matches = face_recognition.compare_faces(self.known_encodings, unknown_encoding, tolerance=0.6)
            face_distances = face_recognition.face_distance(self.known_encodings, unknown_encoding)
            
            if temp_path.exists():
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
        return {
            'total_students': len(self.known_names),
            'students': list(zip(self.known_names, self.known_classes))
        }

# 主界面
st.title("🎓 学生证件照识别系统")
st.markdown('<p class="subtitle">嘉兴南湖 · 智能人脸识别</p>', unsafe_allow_html=True)

# 标签页
tab1, tab2, tab3 = st.tabs(["📝 学生注册", "🔍 人脸识别", "📊 数据统计"])

# 学生注册
with tab1:
    uploaded_file = st.file_uploader("上传学生证件照", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file:
        st.image(uploaded_file, caption="预览", use_column_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        student_name = st.text_input("学生姓名")
    with col2:
        student_class = st.text_input("班级")
    
    if st.button("添加学生"):
        if not uploaded_file:
            st.error("请先上传照片")
        elif not student_name or not student_class:
            st.error("请填写姓名和班级")
        else:
            # 转换图片为 base64
            photo_data = base64.b64encode(uploaded_file.read()).decode('utf-8')
            photo_data = f"data:image/jpeg;base64,{photo_data}"
            
            with st.spinner("添加中..."):
                success = st.session_state.recognizer.add_student(
                    photo_data, student_name, student_class
                )
                
                if success:
                    st.success(f"✅ 已添加学生：{student_name} ({student_class})")
                else:
                    st.error("❌ 人脸检测失败")

# 人脸识别
with tab2:
    recognize_file = st.file_uploader("上传现场照片", type=['jpg', 'jpeg', 'png'], key="recognize")
    
    if recognize_file:
        st.image(recognize_file, caption="预览", use_column_width=True)
    
    if st.button("开始识别"):
        if not recognize_file:
            st.error("请先上传照片")
        else:
            photo_data = base64.b64encode(recognize_file.read()).decode('utf-8')
            photo_data = f"data:image/jpeg;base64,{photo_data}"
            
            with st.spinner("识别中..."):
                result = st.session_state.recognizer.recognize(photo_data)
                
                if result['success']:
                    st.success("✅ 识别成功")
                    st.info(f"""
                    **姓名**: {result['name']}  
                    **班级**: {result['class']}  
                    **匹配度**: {result['confidence']}
                    """)
                else:
                    st.error(f"❌ {result['message']}")

# 数据统计
with tab3:
    stats = st.session_state.recognizer.get_stats()
    st.metric("总学生数", stats['total_students'])
    
    if stats['students']:
        st.write("**学生名单**:")
        for name, cls in stats['students']:
            st.write(f"• {name} - {cls}")
    else:
        st.info("暂无学生数据")

# 侧边栏信息
with st.sidebar:
    st.header("ℹ️ 使用说明")
    st.markdown("""
    1. **学生注册**: 上传证件照，填写信息
    2. **人脸识别**: 上传现场照片自动识别
    3. **数据统计**: 查看已注册学生
    
    **提示**: 
    - 使用清晰的正面照片
    - 保证光线充足
    - 支持拖拽上传
    """)
    
    if not FACE_RECOGNITION_AVAILABLE:
        st.warning("⚠️ 未安装 face_recognition 库，仅支持基础功能")
        st.code("pip install face_recognition")
