# 🌐 OpenClaw 网页端访问配置教程

## 📋 当前配置状态

✅ **OpenClaw 网关状态：** 运行中  
✅ **端口：** 11676  
✅ **绑定模式：** LAN（允许局域网访问）  
✅ **服务器 IP：** 172.24.56.3  

---

## 🚀 访问方式

### 方式 1：本机访问（在服务器上直接访问）

**访问地址：**
```
http://localhost:11676
```

或

```
http://127.0.0.1:11676
```

---

### 方式 2：局域网访问（推荐）

**访问地址：**
```
http://172.24.56.3:11676
```

**适用场景：**
- 在同一局域网内的其他电脑访问
- 手机/平板访问

**测试连接：**
```bash
# 在其他电脑上测试
curl http://172.24.56.3:11676
```

---

### 方式 3：带认证令牌访问

如果启用了令牌认证，使用以下格式：

```
http://172.24.56.3:11676/?token=728495fa554d2117e44dea4bfcf493d9
```

---

## 🔧 配置说明

### 当前网关配置

从 `~/.openclaw/openclaw.json` 读取：

```json
{
  "gateway": {
    "port": 11676,
    "mode": "local",
    "bind": "lan",
    "controlUi": {
      "basePath": "22131ecf",
      "allowedOrigins": ["http://60.205.139.51:11676"],
      "allowInsecureAuth": true,
      "dangerouslyDisableDeviceAuth": true
    },
    "auth": {
      "mode": "token",
      "token": "728495fa554d2117e44dea4bfcf493d9"
    }
  }
}
```

**配置说明：**
- `port: 11676` - 网关端口
- `bind: lan` - 监听所有网络接口（0.0.0.0）
- `auth.mode: token` - 使用令牌认证
- `allowInsecureAuth: true` - 允许 HTTP（非 HTTPS）访问

---

## 🖥️ 浏览器访问步骤

### 步骤 1：打开浏览器

推荐使用：
- ✅ Google Chrome（推荐）
- ✅ Microsoft Edge
- ✅ Firefox
- ⚠️ Safari（可能部分功能不兼容）

### 步骤 2：输入访问地址

在地址栏输入：
```
http://172.24.56.3:11676
```

### 步骤 3：登录（如需要）

如果提示认证，使用令牌：
```
728495fa554d2117e44dea4bfcf493d9
```

### 步骤 4：开始对话

1. 点击"New Chat"或"+"新建对话
2. 在聊天框输入问题
3. 可以发送图片（点击回形针图标）
4. 查看历史对话（左侧边栏）

---

## 📱 移动端访问

### 手机/平板访问步骤

1. 确保手机连接同一 WiFi
2. 打开手机浏览器
3. 访问：`http://172.24.56.3:11676`
4. 添加到主屏幕（可选）

**iOS Safari：**
- 点击分享按钮
- 选择"添加到主屏幕"

**Android Chrome：**
- 点击右上角菜单
- 选择"添加到主屏幕"

---

## 🔐 安全配置建议

### 当前安全状态

| 配置项 | 当前值 | 安全级别 |
|-------|--------|---------|
| 绑定地址 | 0.0.0.0（所有接口） | ⚠️ 中等 |
| 认证方式 | Token | ✅ 良好 |
| HTTPS | 未启用 | ⚠️ 注意 |
| 设备认证 | 已禁用 | ⚠️ 注意 |

### 家庭/办公室网络（可信环境）

当前配置已足够安全，无需修改。

### 公网访问（需要额外配置）

⚠️ **如需从外网访问，建议：**

1. **启用 HTTPS：**
```bash
# 使用 Let's Encrypt 免费证书
# 或配置反向代理（Nginx + SSL）
```

2. **限制访问 IP：**
```json
{
  "gateway": {
    "auth": {
      "mode": "token",
      "token": "你的强密码",
      "allowedIPs": ["192.168.1.0/24"]
    }
  }
}
```

3. **使用 Tailscale（推荐）：**
```bash
# 启用 Tailscale 组网
openclaw gateway config set gateway.tailscale.mode=on
```

---

## 🛠️ 常见问题排查

### 问题 1：无法访问网页

**症状：** 浏览器显示"无法连接"或"连接超时"

**排查步骤：**

```bash
# 1. 检查 OpenClaw 是否运行
openclaw gateway status

# 2. 检查端口是否监听
netstat -tlnp | grep 11676

# 3. 检查防火墙
sudo ufw status
sudo ufw allow 11676/tcp

# 4. 测试本地访问
curl http://localhost:11676

# 5. 重启服务
openclaw gateway restart
```

### 问题 2：提示认证失败

**症状：** 显示"Unauthorized"或"Invalid token"

**解决方法：**

1. 检查令牌是否正确
2. 在 URL 中添加令牌参数：
   ```
   http://172.24.56.3:11676/?token=728495fa554d2117e44dea4bfcf493d9
   ```

3. 或修改配置禁用认证（仅限可信环境）：
```bash
openclaw gateway config set gateway.auth.mode=none
openclaw gateway restart
```

### 问题 3：局域网内其他设备无法访问

**症状：** 本机可以访问，其他电脑/手机无法访问

**排查步骤：**

```bash
# 1. 检查绑定模式
# 应显示：bind=lan (0.0.0.0)
openclaw gateway status

# 2. 如果不是 LAN 模式，修改配置
openclaw gateway config set gateway.bind=lan
openclaw gateway restart

# 3. 检查防火墙
sudo ufw allow 11676/tcp

# 4. 测试服务器 IP
ping 172.24.56.3

# 5. 测试端口连通性
telnet 172.24.56.3 11676
```

### 问题 4：页面加载缓慢

**可能原因：**
- 网络延迟
- 模型响应慢
- 浏览器缓存

**解决方法：**
1. 清除浏览器缓存
2. 检查网络连接
3. 使用更快的模型（配置中调整）

---

## 📊 高级配置

### 修改端口

```bash
# 修改为其他端口（如 8080）
openclaw gateway config set gateway.port=8080
openclaw gateway restart

# 访问地址变为：
# http://172.24.56.3:8080
```

### 修改绑定模式

```bash
# 仅允许本机访问（更安全）
openclaw gateway config set gateway.bind=localhost
openclaw gateway restart

# 允许所有接口访问（局域网）
openclaw gateway config set gateway.bind=lan
openclaw gateway restart
```

### 修改认证令牌

```bash
# 生成新令牌（使用强密码）
openclaw gateway config set gateway.auth.token=你的新强密码
openclaw gateway restart
```

---

## 🎯 数学学习助手网页端使用技巧

### 1. 发送题目图片

1. 点击聊天框的回形针图标 📎
2. 选择题目图片（支持 JPG、PNG）
3. 输入问题："这道题怎么做？"
4. 等待 AI 分析并引导解题

### 2. 查看历史对话

- 左侧边栏显示所有历史对话
- 点击对话标题切换
- 可以搜索关键词找到特定题目

### 3. 导出学习记录

```bash
# 学习进度文件位置
cat ~/.openclaw/workspace/learning-progress.md

# 转换为 PDF
pandoc ~/.openclaw/workspace/learning-progress.md -o learning-report.pdf
```

### 4. 多会话管理

- 可以为不同学生创建不同会话
- 会话命名建议：
  - "图图 - 数学学习"
  - "张三 - 错题辅导"
  - "预习 - 平行线"

---

## 📞 快速参考卡片

### 访问地址速查

| 场景 | 地址 |
|-----|------|
| 本机访问 | http://localhost:11676 |
| 局域网访问 | http://172.24.56.3:11676 |
| 带令牌访问 | http://172.24.56.3:11676/?token=728495fa554d2117e44dea4bfcf493d9 |

### 常用命令

```bash
# 查看状态
openclaw gateway status

# 重启服务
openclaw gateway restart

# 查看日志
tail -f /tmp/openclaw/openclaw-2026-04-18.log

# 修改配置
openclaw gateway config set <配置项>=<值>
```

### 认证令牌

```
728495fa554d2117e44dea4bfcf493d9
```

---

## ✅ 配置完成检查清单

- [ ] OpenClaw 网关运行正常
- [ ] 可以从本机访问 http://localhost:11676
- [ ] 可以从局域网访问 http://172.24.56.3:11676
- [ ] 认证令牌已记录
- [ ] 防火墙已开放 11676 端口
- [ ] 浏览器已收藏访问地址
- [ ] 测试发送图片和文字正常

---

**配置时间：** 2026-04-18  
**服务器 IP：** 172.24.56.3  
**端口：** 11676  
**状态：** ✅ 运行中
