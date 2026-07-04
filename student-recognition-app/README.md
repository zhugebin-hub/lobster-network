# 🎓 学生证件照识别系统

基于人脸识别的学生身份识别应用，嘉兴南湖主题背景。

## 🚀 快速启动

### 方法一：Flask 版本（推荐）

```bash
# 1. 安装依赖
pip install flask flask-cors

# 2. 可选：安装人脸识别库（获得完整功能）
pip install face_recognition

# 3. 启动应用
cd ~/.openclaw/workspace/student-recognition-app
python app.py

# 4. 访问应用
浏览器打开：http://localhost:5000
```

### 方法二：Streamlit 版本（更简单）

```bash
# 1. 安装依赖
pip install streamlit

# 2. 启动应用
streamlit run app_streamlit.py
```

## 📋 功能说明

### 学生注册
1. 上传学生证件照（支持拖拽）
2. 输入学生姓名
3. 输入班级信息
4. 点击"添加学生"

### 人脸识别
1. 上传现场拍摄照片
2. 点击"开始识别"
3. 系统自动匹配学生信息

### 数据统计
- 查看已注册学生总数
- 浏览所有学生名单

## 🎨 界面特色

- ✨ 清爽简洁的现代化界面
- 🏞️ 嘉兴南湖主题背景
- 📱 响应式设计，支持手机/平板
- 🖱️ 支持拖拽上传照片
- ⚡ 实时识别反馈

## 📦 技术栈

- **前端**: HTML5 + CSS3 + JavaScript
- **后端**: Python + Flask
- **人脸识别**: face_recognition (基于 dlib)
- **数据存储**: JSON + 本地文件

## 🔧 依赖安装

### macOS
```bash
pip install cmake
pip install dlib
pip install face_recognition
```

### Ubuntu/Debian
```bash
sudo apt-get install cmake
sudo apt-get install libdlib-dev
pip install dlib
pip install face_recognition
```

### Windows
```bash
# 需要先安装 Visual C++ Build Tools
# 然后：
pip install face_recognition
```

## 📁 文件结构

```
student-recognition-app/
├── app.py              # Flask 后端服务
├── index.html          # 前端界面
├── app_streamlit.py    # Streamlit 版本（可选）
├── student_data/       # 数据存储目录（自动创建）
│   ├── photos/         # 学生照片
│   └── student_db.json # 学生数据库
└── README.md           # 本文件
```

## 🔐 隐私说明

- 所有数据存储在本地
- 不会上传到任何服务器
- 照片仅用于本地识别

## 💡 使用建议

1. **证件照质量**: 使用清晰、正面、光线充足的证件照
2. **识别环境**: 识别时尽量保证光线良好，正面拍摄
3. **批量导入**: 可以逐个添加学生，建议先建立完整数据库
4. **定期备份**: 备份 `student_data/` 目录防止数据丢失

## 🐛 常见问题

**Q: 识别准确率低？**
A: 确保上传的证件照清晰，识别照片光线良好。可以调整识别阈值（代码中 tolerance 参数）。

**Q: face_recognition 安装失败？**
A: 可以先使用基础模式（不安装该库），只支持照片管理，不支持自动识别。

**Q: 如何更换背景？**
A: 修改 `index.html` 中的 `body::before` 背景图片 URL。

## 📞 技术支持

如有问题，请检查：
1. Python 版本（建议 3.7+）
2. 依赖库是否正确安装
3. 端口 5000 是否被占用

---

**版本**: 1.0.0  
**作者**: 诸葛虾 🦞  
**日期**: 2026-04-17
