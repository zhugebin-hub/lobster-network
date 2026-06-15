# 🦞 腾讯云服务器安装 OpenClaw（小龙虾）—— 小白保姆级教程

> 从头到尾，一步一步跟着做，保证能装上。

---

## 第一步：购买腾讯云服务器

1. 打开腾讯云官网：https://cloud.tencent.com
2. 登录你的账号
3. 搜索 **"轻量应用服务器"** 或 **"CVM 云服务器"**
4. 选择配置：
   - **操作系统**：Ubuntu 22.04 LTS（⚠️ 一定选这个，别选 CentOS）
   - **CPU/内存**：最低 2核4G
   - **带宽**：1Mbps 起步
   - **地域**：就近选（如广州、上海）
5. 付款购买，等待 1-2 分钟，服务器就创建好了

---

## 第二步：获取服务器登录信息

1. 进入腾讯云控制台 → 轻量应用服务器
2. 找到你的服务器，记下 **公网 IP 地址**（类似 `60.205.x.x`）
3. 设置登录密码：
   - 点击服务器 → "重置密码"
   - 设置一个你能记住的密码
   - 用户名是：`ubuntu`

---

## 第三步：连接服务器（用 SSH 终端）

### 方法一：腾讯云网页终端（最简单）
1. 在服务器详情页面，点击 **"登录"** → **"网页登录"**
2. 输入用户名 `ubuntu` 和你的密码
3. 看到类似 `ubuntu@VM-xxx:~$` 就表示连上了

### 方法二：用本地终端（Mac/Linux）
```bash
ssh ubuntu@你的服务器IP
# 输入密码
```

### 方法三：Windows 用 PuTTY 或 PowerShell
```powershell
ssh ubuntu@你的服务器IP
```

---

## 第四步：更新系统（连接成功后第一步）

在终端里依次输入以下命令，每输一行按回车：

```bash
# 1. 更新软件列表
sudo apt update

# 2. 升级已安装的软件
sudo apt upgrade -y
```

> ⏱️ 这步可能需要 1-3 分钟，等它跑完。

---

## 第五步：安装 Node.js（运行环境）

依次输入以下命令：

```bash
# 1. 安装 curl（下载工具）
sudo apt install -y curl

# 2. 添加 Node.js 22 的安装源
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo bash -

# 3. 安装 Node.js
sudo apt install -y nodejs

# 4. 验证安装成功（会显示版本号）
node -v
npm -v
```

✅ 如果 `node -v` 显示 `v22.x.x`，说明安装成功！

---

## 第六步：安装 OpenClaw（小龙虾）

```bash
# 用 npm 全局安装 openclaw
sudo npm install -g openclaw

# 验证安装成功
openclaw --version
```

✅ 如果显示了版本号，说明安装成功！

---

## 第七步：初始化 OpenClaw

```bash
# 运行初始化向导
openclaw init
```

这时候会引导你：
1. 选择 AI 模型（默认即可）
2. 输入 API Key（你的大模型 API 密钥）
3. 其他配置按需填写

> ⚠️ 如果没有 API Key，可以去以下平台申请：
> - 阿里云 DashScope：https://dashscope.console.aliyun.com
> - 智谱 AI：https://open.bigmodel.cn
> - 通义千问：https://tongyi.aliyun.com

---

## 第八步：启动 OpenClaw Gateway

```bash
# 启动服务
openclaw gateway start

# 查看运行状态
openclaw gateway status
```

✅ 如果显示 `running`，说明服务已经跑起来了！

---

## 第九步：配置开机自启动（可选但推荐）

```bash
# 设置开机自启
openclaw gateway enable
```

这样服务器重启后，OpenClaw 会自动运行，不用手动启动。

---

## 第十步：开放安全组端口

在腾讯云控制台：

1. 找到你的服务器 → "防火墙" 或 "安全组"
2. 添加规则，放行以下端口：
   - **3000**（Web 界面）
   - **80**（HTTP）
   - **443**（HTTPS）

> 🔒 只开放你需要的端口，不要开所有端口。

---

## 第十一步：访问 Web 界面

在浏览器输入：

```
http://你的服务器IP:3000
```

就能看到 OpenClaw 的 Web 管理界面了。

---

## 🆘 常见问题排查

### 问题1：命令找不到 `openclaw`
```bash
# 检查 npm 全局路径
npm config get prefix

# 如果路径不对，重新安装
sudo npm install -g openclaw --prefix /usr/local
```

### 问题2：Node.js 版本太低
```bash
# 查看当前版本
node -v

# 必须 v20 以上，如果不是，重新安装 v22
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo bash -
sudo apt install -y nodejs
```

### 问题3：端口被占用
```bash
# 查看 3000 端口是否被占用
sudo lsof -i :3000

# 如果被占用，可以杀掉进程或换一个端口
```

### 问题4：网关启动失败
```bash
# 查看错误日志
openclaw gateway status

# 查看详细日志
cat ~/.openclaw/logs/gateway.log
```

### 问题5：外网访问不了
1. 确认安全组已开放 3000 端口
2. 确认防火墙没拦截：`sudo ufw allow 3000`
3. 确认服务在运行：`openclaw gateway status`

---

## 📋 快速检查清单

完成后对照检查：

- [ ] 服务器购买成功，能登录
- [ ] `node -v` 显示 v20 以上
- [ ] `openclaw --version` 有输出
- [ ] `openclaw gateway status` 显示 running
- [ ] 浏览器能访问 `http://IP:3000`
- [ ] 安全组已放行 3000 端口

---

## 🎯 下一步

安装完成后：
1. 配置钉钉/微信等消息渠道
2. 设置你的 AI 助手人格
3. 开始使用！

有问题随时问，我看到会回复 👋
