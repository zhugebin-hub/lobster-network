# 在学校排课系统 - 本地安装指南

## 📥 第一步：准备文件

将以下文件夹完整复制到您的电脑：
```
scheduling-system/
├── app.py
├── requirements.txt
├── run-web.sh
├── static/
│   └── index.html
├── src/
│   ├── main.py
│   ├── models.py
│   └── scheduler.py
├── utils/
│   └── db.py
├── ui/
│   ├── main_window.py
│   └── dialogs.py
└── data/
```

---

## 🖥️ Windows 用户

### 1. 安装 Python
1. 访问 https://www.python.org/downloads/
2. 下载 Python 3.8 或更高版本
3. **重要**：安装时勾选 ✅ "Add Python to PATH"

### 2. 安装依赖
打开命令提示符（按 Win+R，输入 `cmd`）：
```cmd
cd 您的\scheduling-system\路径
pip install flask flask-cors
```

### 3. 启动系统
```cmd
python app.py
```

### 4. 访问
浏览器打开：http://localhost:5000

---

## 🍎 Mac 用户

### 1. 安装 Python（如已安装可跳过）
```bash
brew install python3
```

### 2. 安装依赖
```bash
cd scheduling-system
pip3 install flask flask-cors
```

### 3. 启动系统
```bash
python3 app.py
```

### 4. 访问
浏览器打开：http://localhost:5000

---

## 🐧 Linux 用户

### 1. 安装依赖
```bash
cd scheduling-system
pip3 install flask flask-cors
```

### 2. 启动系统
```bash
python3 app.py
```

### 3. 访问
浏览器打开：http://localhost:5000

---

## ✅ 验证成功

看到以下提示表示成功：
```
🚀 排课系统 Web 版启动中...
📱 访问地址：http://localhost:5000
 * Running on http://127.0.0.1:5000
```

---

## 💡 使用流程

1. 打开浏览器访问 http://localhost:5000
2. 录入教师信息
3. 录入班级信息
4. 设置课程
5. 点击"自动排课"
6. 查看课表

---

## 🔧 常见问题

**Q: pip 命令找不到？**
- Windows: 重新安装 Python，确保勾选"Add to PATH"
- Mac/Linux: 尝试 `pip3` 代替 `pip`

**Q: 端口被占用？**
- 关闭其他程序或修改 app.py 中的端口号

**Q: 数据保存在哪？**
- `data/school.db` 文件
- 备份此文件即可保存所有数据

---

## 📞 需要帮助？

如有问题，请联系技术支持。
