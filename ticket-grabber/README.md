# 🎫 大麦抢票助手

## 方案说明

- **后端**: Python Flask + Playwright（控制真实浏览器）
- **前端**: 简洁 Web 界面，配置抢票任务
- **流程**: 网页配置 → 后台自动打开大麦 → 高频刷新 → 有票自动填单 → 你最后确认付款

## 在 Ubuntu VM 中部署

### 1. 安装依赖

```bash
# 安装 Python 环境
sudo apt update
sudo apt install -y python3 python3-pip python3-venv xvfb

# 创建项目目录
mkdir -p ~/ticket-grabber && cd ~/ticket-grabber

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装 Python 包
pip install flask playwright

# 安装浏览器（Chromium）
playwright install chromium
# 安装系统依赖
playwright install-deps chromium
```

### 2. 启动服务

```bash
cd ~/ticket-grabber
source venv/bin/activate
python app.py
```

### 3. 打开网页

```bash
# 如果有桌面环境，打开浏览器访问：
http://localhost:5000

# 如果是纯命令行 VM，需要装桌面或用 VNC：
sudo apt install -y xfce4 xfce4-goodies tightvncserver
# 然后 VNC 连接后打开浏览器访问 localhost:5000
```

## 使用方式

1. 打开 http://localhost:5000
2. 输入大麦演唱会页面 URL
3. 选择票档、数量
4. 设置抢票开始时间（开票前几分钟）
5. 点击"开始抢票"
6. 浏览器会自动打开（带界面），登录大麦账号
7. 到时间后自动高频刷新，有票自动提交订单
8. **你只需要最后确认付款**

## 文件说明

- `app.py` — Flask 主程序
- `grabber.py` — Playwright 抢票核心逻辑
- `templates/index.html` — Web 界面
- `static/style.css` — 样式

## 注意事项

- ⚠️ 大麦有反爬机制，建议频率不要太高（1-2秒/次）
- ⚠️ 可能需要手动通过验证码
- ⚠️ 仅用于个人抢票，不要用于倒卖
- ⚠️ 需要图形界面才能显示浏览器（VM 里装 VNC/远程桌面）
