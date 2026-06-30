# 信电学院 AI 知识问答系统 - 部署指南

## 当前状态

✅ **服务已部署并启用 HTTPS**
- 本地服务：`http://localhost:8900/webhook/dingtalk`（内部）
- HTTPS服务：`https://60.205.139.51/webhook/dingtalk`（对外）
- HTTP自动重定向到HTTPS
- SSL证书：自签名证书（有效期1年）
- Nginx反向代理已配置
- 状态：运行中

## 待完成配置

### 1. 阿里云安全组配置

**需要开放端口：80, 443**

操作步骤：
1. 登录阿里云控制台：https://ecs.console.aliyun.com
2. 进入实例：`i-2zeetm9awnkwdni43joi`（北京区域）
3. 点击「安全组」→「配置规则」
4. 添加安全组规则：
   - 方向：入方向
   - 协议：TCP
   - 端口：80, 443
   - 授权对象：0.0.0.0/0
   - 描述：信电学院AI问答系统（HTTP/HTTPS）

### 2. 钉钉机器人配置

**回调 URL：** `https://60.205.139.51/webhook/dingtalk`

操作步骤：
1. 登录钉钉开放平台：https://open-dev.dingtalk.com
2. 进入应用：虾尔（dinguyiasfrbtjioamwc）
3. 配置消息接收地址：
   - 消息接收模式：HTTP 模式
   - 消息接收地址：`https://60.205.139.51/webhook/dingtalk`
4. 保存配置

**注意：** 钉钉可能不支持自签名证书。如果回调失败，需要：
- 方案A：获取域名并申请 Let's Encrypt 免费证书
- 方案B：在钉钉后台配置时忽略证书验证（如有此选项）
- 方案C：使用内网穿透工具（如 frp/ngrok）获取可信证书

### 3. 测试验证

配置完成后，在钉钉群或私聊中发送消息测试：
- 课程问题：「基尔霍夫定律是什么？」
- 闲聊：「你好」

## 服务管理

```bash
# 查看状态
cd /home/admin/.openclaw/workspace/projects/xindian-qa
./start.sh status

# 查看日志
tail -f logs/bot.log

# 重启服务
./start.sh stop && ./start.sh server

# 停止服务
./start.sh stop
```

## 注意事项

1. **安全组必须开放**：否则钉钉无法回调（需要开放 80, 443 端口）
2. **公网 IP 可能变化**：如果服务器重启，IP 可能变化，需要更新钉钉配置
3. **HTTPS 已配置**：使用自签名证书，钉钉可能需要可信证书
4. **防火墙**：系统防火墙已配置，Nginx 监听 80/443 端口

## 下一步优化

- [ ] 获取域名并申请 Let's Encrypt 免费证书（钉钉需要可信证书）
- [ ] 配置域名解析
- [ ] 配置 systemd 服务实现开机自启
- [ ] 添加日志轮转
- [ ] 监控和告警配置

## HTTPS 配置详情

### 当前配置
- **证书类型**：自签名证书
- **证书路径**：`/etc/nginx/ssl/server.crt`
- **私钥路径**：`/etc/nginx/ssl/server.key`
- **有效期**：365天（2026-06-02 至 2027-06-02）
- **协议**：TLSv1.2, TLSv1.3

### 升级为 Let's Encrypt 证书（推荐）
如果有域名，可以免费获取可信证书：
```bash
# 安装 certbot
sudo yum install -y certbot python3-certbot-nginx

# 获取证书（替换为你的域名）
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

### Nginx 配置
- 配置文件：`/etc/nginx/conf.d/xindian-qa.conf`
- HTTP (80) → 自动重定向到 HTTPS
- HTTPS (443) → 反向代理到 localhost:8900
