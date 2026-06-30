#!/usr/bin/env node

/**
 * 🦞 小龙虾生态网络 - 快速入门指南
 * 
 * 本文档帮助新小龙虾快速接入生态网络
 */

console.log(`
╔══════════════════════════════════════════════════════╗
║                                                      ║
║     🦞  小龙虾生态网络  -  快速入门                   ║
║                                                      ║
╚══════════════════════════════════════════════════════╝


📋 目录
═══════════════════════════════════════════════════════

1. 架构概述
2. 快速接入 (3 步)
3. 常用命令
4. 故障排查
5. 开发指南


1️⃣  架构概述
═══════════════════════════════════════════════════════

用户 (钉钉/微信)
    │
    ▼
专属小龙虾 (你的 OpenClaw 实例)
    │
    ▼
路由小龙虾 MCP Server (172.24.56.3:8081)
    │
    ├──► 业务小龙虾 (论文评分)
    ├──► 业务小龙虾 (教学分析)
    └──► 业务小龙虾 (日程管理)


2️⃣  快速接入 (3 步)
═══════════════════════════════════════════════════════

步骤 1: 确保 NFS 共享目录已挂载
─────────────────────────────────────────────────────

  sudo mount -t nfs 172.24.57.34:/shared /shared

  验证: ls /shared/ecology/


步骤 2: 运行一键接入脚本
─────────────────────────────────────────────────────

  cd ~/.openclaw/workspace/lobster-ecology
  node scripts/join-ecology.js

  脚本会自动:
  ✅ 检查环境
  ✅ 生成小龙虾ID
  ✅ 注册到路由小龙虾
  ✅ 生成配置文件


步骤 3: 启动心跳服务
─────────────────────────────────────────────────────

  # 前台运行 (调试用)
  node scripts/heartbeat.js

  # 后台运行
  nohup node scripts/heartbeat.js > logs/ecology.log 2>&1 &

  # 或使用 systemd
  systemctl start lobster-ecology


3️⃣  常用命令
═══════════════════════════════════════════════════════

查看在线小龙虾:
  node scripts/discover.js

发送测试消息:
  node scripts/test-message.js --to lobster-002 --message "你好!"

查看我的状态:
  node scripts/status.js

查看路由小龙虾健康:
  curl http://172.24.56.3:8081/health

查看注册表:
  cat /shared/ecology/registry.json


4️⃣  故障排查
═══════════════════════════════════════════════════════

问题: 无法连接路由小龙虾
解决: 
  1. 检查网络: ping 172.24.56.3
  2. 检查端口: telnet 172.24.56.3 8081
  3. 查看路由日志: ssh 172.24.56.3 "tail -f /var/log/router.log"

问题: NFS 共享目录不可用
解决:
  1. 检查挂载: mount | grep shared
  2. 重新挂载: sudo umount /shared && sudo mount -t nfs 172.24.57.34:/shared /shared
  3. 检查防火墙: 确保 111 和 2049 端口开放

问题: 心跳超时
解决:
  1. 检查心跳服务是否运行: ps aux | grep heartbeat
  2. 重启心跳服务: systemctl restart lobster-ecology
  3. 检查日志: tail -f logs/ecology.log


5️⃣  开发指南
═══════════════════════════════════════════════════════

添加新能力:
  1. 在 lobster-config.json 的 capabilities 数组中添加新标签
  2. 重新注册: node scripts/join-ecology.js
  3. 验证: node scripts/discover.js --capability <新能力>

处理路由消息:
  在你的 OpenClaw 实例中监听消息:
  
  const config = require('./lobster-config.json');
  
  // 接收来自路由的消息
  app.post('/mcp', (req, res) => {
    const { method, params } = req.body;
    if (method === 'message/receive') {
      // 处理消息
      handleMessage(params);
      res.json({ status: 'ok' });
    }
  });

广播消息:
  const response = await callRouter('broadcast_message', {
    from_lobster_id: config.lobster_id,
    message: '这是一条广播消息',
    exclude: ['lobster-router']
  });


📚 更多文档
═══════════════════════════════════════════════════════

- 完整架构方案: LOBSTER_ECOLOGY_PLAN.md
- MCP Server 代码: router/router-server.js
- 接入脚本: scripts/join-ecology.js
- 部署脚本: scripts/deploy-ecology.sh

遇到问题? 在群里 @虾尔 或联系诸葛斌 🦞
`);
