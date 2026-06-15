# VM 无桌面环境？安装 VNC 远程桌面

抢票需要显示浏览器窗口（因为要手动登录大麦），所以 VM 需要图形界面。

## 方案一：安装轻量桌面 + VNC（推荐）

```bash
# 1. 安装 XFCE 桌面（轻量，约 200MB）
sudo apt update
sudo apt install -y xfce4 xfce4-goodies tightvncserver

# 2. 设置 VNC 密码（首次运行会要求设置）
vncserver :1

# 3. 配置 VNC 启动 XFCE
cat > ~/.vnc/xstartup << 'EOF'
#!/bin/bash
xreset -display $DISPLAY &
startxfce4 &
EOF
chmod +x ~/.vnc/xstartup

# 4. 重启 VNC
vncserver -kill :1
vncserver :1 -geometry 1280x720

# 5. 使用 VNC 客户端连接
#    地址: VM的IP:5901
#    推荐客户端: RealVNC Viewer (免费)
```

## 方案二：NoVNC（浏览器访问）

```bash
# 1. 安装
sudo apt install -y novnc websockify

# 2. 启动 VNC
vncserver :1 -geometry 1280x720

# 3. 启动 NoVNC
websockify --web /usr/share/novnc 6080 localhost:5901 &

# 4. 浏览器访问
#    http://VM的IP:6080
```

## 方案三：X11 转发（如果本地有 Linux/Mac）

```bash
# 本地终端运行（不需要 VNC）
ssh -X user@VM的IP

# 然后在 VM 中直接运行
source ~/ticket-grabber/venv/bin/activate
python app.py
# 浏览器会自动在你的本地显示
```

## 连接后使用

1. 打开 VNC 远程桌面
2. 打开终端
3. 运行：
   ```bash
   cd ~/ticket-grabber
   source venv/bin/activate
   python app.py
   ```
4. 打开浏览器访问 http://localhost:5000
5. 配置抢票参数，点击开始
6. 浏览器会自动打开大麦页面，手动登录
7. 等待自动抢票
