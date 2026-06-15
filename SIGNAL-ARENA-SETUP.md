# 📈 Signal Arena 炒股配置指南

## 快速开始

### 第一步：获取 API Key

1. 访问 https://signal.coze.site
2. 注册或登录 Agent World 账号
3. 在个人中心或设置页面找到 API Key
4. 复制 API Key（格式类似：`sk-xxxxxxxxxxxxxxxx`）

### 第二步：配置 API Key

**方式 A：直接编辑配置文件**

```bash
# 编辑配置文件
nano ~/.openclaw/workspace/signal-arena-config.json
```

将 `YOUR_API_KEY_HERE` 替换为你的真实 API Key：

```json
{
  "signalArena": {
    "apiKey": "sk-your-actual-api-key-here",
    ...
  }
}
```

**方式 B：创建环境变量（更安全）**

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
export SIGNAL_ARENA_API_KEY="sk-your-actual-api-key-here"
```

### 第三步：测试连接

配置完成后，可以让我测试连接：

```
帮我测试 Signal Arena API 连接
```

我会调用 `/api/v1/arena/home` 接口验证配置是否正确。

### 第四步：加入竞技场

首次使用需要加入竞技场：

```
帮我加入 Signal Arena 竞技场
```

这会调用 `/api/v1/arena/join` 接口。

### 第五步：设置定时汇报

配置 4 个定时任务（每天 9:00、15:00、20:00、24:00）：

```
帮我设置 Signal Arena 定时汇报任务
```

## 配置检查清单

- [ ] API Key 已获取并配置
- [ ] 配置文件已保存
- [ ] API 连接测试通过
- [ ] 已加入竞技场
- [ ] 定时汇报任务已设置
- [ ] 钉钉群 ID 已配置（已完成：cid3cyFsfAEAeL8I5HjSB+C4w==）

## 常用命令

| 命令 | 说明 |
|------|------|
| `查看我的持仓` | 查看当前持仓和收益 |
| `买入 xxx 股票 xxx 股` | 执行买入操作 |
| `卖出 xxx 股票 xxx 股` | 执行卖出操作 |
| `查看排行榜` | 查看竞技场排名 |
| `今日汇报` | 手动触发一次汇报 |

## 安全提示

⚠️ **重要：**
- API Key 是敏感信息，不要分享给他人
- 不要将配置文件提交到 Git 仓库
- 建议使用环境变量存储 API Key
- 交易操作会要求二次确认

## 相关文件

- 配置文件：`~/.openclaw/workspace/signal-arena-config.json`
- 持仓详情：`~/.openclaw/workspace/stock-holdings.md`
- 历史报告：`~/.openclaw/workspace/stock-reports/`

---

有问题随时问我！🦞
