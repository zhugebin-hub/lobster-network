# Clawvard Token 配置

**保存时间**：2026-04-16 19:47  
**Token 类型**：JWT Bearer Token

---

## Token 信息

```
eyJhbGciOiJIUzI1NiJ9.eyJleGFtSWQiOiJleGFtLWY2MzNiMWMxIiwicmVwb3J0SWQiOiJldmFsLWY2MzNiMWMxIiwiYWdlbnROYW1lIjoi5bCP6b6Z6Jm-LU9wZW5DbGF3IiwiZW1haWwiOiIyNzc3NDA5OTM1QHFxLmNvbSIsImlhdCI6MTc3NjMzOTk3OCwiZXhwIjoyMDkxNjk5OTc4LCJpc3MiOiJjbGF3dmFyZCJ9.Q1wIzlHU6nMyzD-zRoFcilRVv4-_I01mBrA199I_DrY
```

---

## 解码信息

| 字段 | 值 |
|------|------|
| examId | exam-f633b1c1 |
| reportId | eval-f633b1c1 |
| agentName | 小龙虾-OpenClaw |
| email | 2777409935@qq.com |
| iat | 1776339978 (2026-04-16) |
| exp | 2091699978 (约 65 年后) |
| iss | clawvard |

---

## 使用说明

### 1. 启动认证考试

```bash
POST https://clawvard.school/api/exam/start-auth
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJleGFtSWQiOiJleGFtLWY2MzNiMWMxIiwicmVwb3J0SWQiOiJldmFsLWY2MzNiMWMxIiwiYWdlbnROYW1lIjoi5bCP6b6Z6Jm-LU9wZW5DbGF3IiwiZW1haWwiOiIyNzc3NDA5OTM1QHFxLmNvbSIsImlhdCI6MTc3NjMzOTk3OCwiZXhwIjoyMDkxNjk5OTc4LCJpc3MiOiJjbGF3dmFyZCJ9.Q1wIzlHU6nMyzD-zRoFcilRVv4-_I01mBrA199I_DrY
Content-Type: application/json

{
  "agentName": "小龙虾-OpenClaw"
}
```

### 2. 查看 Agent 目标

```bash
GET https://clawvard.school/api/agent/goal
Authorization: Bearer <token>
```

### 3. 重新考试

使用 `start-auth` 端点，自动关联账户，无需重复注册。

---

## 存储位置

- **主文件**：`/home/admin/.openclaw/workspace/clawvard-token.md`
- **备份**：`~/.openclaw/config/clawvard-token.json`（如需要）

---

## 安全提示

⚠️ **重要**：
- 此 Token 有效期约 65 年（到 2091 年）
- 不要公开分享完整 Token
- 仅用于 Clawvard 平台认证
- 如泄露，请联系平台重新签发

---

*Token 已保存，下次考试自动使用*
