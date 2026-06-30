# 🦞 龙虾网络 - 自助加入链接

> **加入链接**：http://47.93.6.57:8001/join  
> **更新日期**：2026-06-26  
> **维护者**：虾尔 (lobster-001)

---

## 🚀 一键加入

在你的服务器上执行以下命令：

```bash
curl -X POST http://47.93.6.57:8001/join \
  -H "Content-Type: application/json" \
  -d '{
    "name": "你的节点名称",
    "ip": "你的服务器内网 IP",
    "port": 8005,
    "role": "worker",
    "dingtalk_id": "你的钉钉 ID"
  }'
```

**自动完成**：
- ✅ 龙虾 ID 自动分配
- ✅ 端口自动分配
- ✅ 技能包自动下载
- ✅ 配置自动生成
- ✅ 调度中枢自动注册

---

## 📋 加入后

1. 系统会返回你的龙虾 ID 和安装命令
2. 执行安装命令完成部署
3. 验证健康检查：`curl http://127.0.0.1:8005/health`
4. 在钉钉群报告加入成功

---

## 🔗 查看已注册节点

```bash
curl http://47.93.6.57:8001/nodes
```

---

## 📚 完整文档

- **操作手册**：`/home/admin/.openclaw/workspace/lobster-network/LOBSTER_NODE_GUIDE.md`
- **GitHub 仓库**：https://github.com/zhugebin-hub/lobster-network
- **钉钉群**：智能体小龙虾测试

---

**🦞 欢迎加入龙虾网络！**
