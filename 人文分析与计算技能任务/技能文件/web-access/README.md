# web-access Skill for OpenClaw

为 OpenClaw Agent 提供完整的联网能力，包括搜索、网页抓取、浏览器自动化和登录态复用。

## 核心能力

- **智能工具调度**：根据场景自动选择 WebSearch/WebFetch/curl/Jina/CDP
- **CDP Proxy**：直连用户日常 Chrome，天然携带登录态
- **三种点击方式**：JS click、CDP 真实鼠标事件、文件上传
- **并行分治**：多目标时分发子 Agent 并行执行
- **站点经验积累**：按域名存储操作经验，跨 session 复用
- **媒体提取**：从 DOM 直取图片/视频 URL，或视频截帧分析

## 快速开始

### 1. 安装

本 skill 已安装在：
```
~/.openclaw/workspace/skills/web-access/
```

### 2. 启用 Chrome 远程调试

在 Chrome 地址栏打开：
```
chrome://inspect/#remote-debugging
```

勾选 **"Allow remote debugging for this browser instance"**，然后重启 Chrome。

### 3. 检查依赖

```bash
bash ~/.openclaw/workspace/skills/web-access/scripts/check-deps.sh
```

预期输出：
```
node: ok (v24.14.0)
chrome: ok (端口 9222)
```

### 4. 启动 CDP Proxy（按需）

```bash
node ~/.openclaw/workspace/skills/web-access/scripts/cdp-proxy.mjs &
```

Proxy 会运行在 `http://localhost:3456`

## 使用方式

### 简单联网任务

直接让 Agent 执行：
- "帮我搜索 xxx 最新进展"
- "读一下这个页面：[URL]"
- "同时调研这 5 个产品的官网，给我对比摘要"

### 需要登录态的任务

当访问需要登录的网站（如小红书、微信公众号、后台系统等）时，Agent 会自动使用 CDP Proxy 连接你的日常 Chrome，利用已有的登录态。

### CDP Proxy API 示例

```bash
# 创建新 tab
TARGET=$(curl -s "http://localhost:3456/new?url=https://example.com" | jq -r .targetId)

# 执行 JS
curl -s -X POST "http://localhost:3456/eval?target=$TARGET" -d 'document.title'

# 截图
curl -s "http://localhost:3456/screenshot?target=$TARGET&file=/tmp/shot.png"

# 关闭 tab
curl -s "http://localhost:3456/close?target=$TARGET"
```

完整 API 参考：[references/cdp-api.md](references/cdp-api.md)

## 工具选择策略

| 场景 | 推荐工具 |
|------|---------|
| 搜索信息 | searxng skill（优先）或 web_search |
| 读取公开网页 | web_fetch |
| 需要登录态 | CDP Proxy |
| 动态页面/交互 | browser 工具 或 CDP Proxy |
| 原始 HTML | curl |
| 节省 token 读取文章 | Jina (r.jina.ai/URL) |

## 浏览哲学

**像人一样思考** —— 带着目标进入，边看边判断，遇到阻碍就解决，发现内容不够就深入。

1. **明确目标**：什么算完成任务？
2. **选择起点**：根据平台特征选择最可能直达的方式
3. **过程校验**：每一步的结果都是证据，方向错了立即调整
4. **完成判断**：达到成功标准就停止，不过度操作

## 文件结构

```
web-access/
├── SKILL.md                      # 技能主文档
├── scripts/
│   ├── check-deps.sh             # 依赖检查脚本
│   └── cdp-proxy.mjs             # CDP Proxy 服务
└── references/
    ├── cdp-api.md                # CDP API 完整参考
    └── site-patterns/            # 站点经验
        ├── TEMPLATE.md           # 经验文件模板
        └── {domain}.md           # 具体站点经验
```

## 站点经验

访问特定网站（如小红书、微博、知乎等）时积累的经验会保存在 `references/site-patterns/` 目录下。

查看已有经验：
```bash
ls ~/.openclaw/workspace/skills/web-access/references/site-patterns/
```

## 并行分治

当任务包含多个独立调研目标时，Agent 会分治给子 Agent 并行执行：

- 每个子 Agent 创建自己的后台 tab
- 共享一个 Chrome 实例和 Proxy
- 主 Agent 只接收摘要，节省 token

## 注意事项

1. **隐私安全**：CDP Proxy 只连接本地 Chrome，不上传任何数据
2. **最小侵入**：所有操作在后台 tab 进行，不影响用户正常使用
3. **清理习惯**：任务完成后自动关闭创建的 tab
4. **Proxy 持久化**：建议让 Proxy 持续运行，避免重复启动

## 故障排查

### Chrome 未开启远程调试
```
chrome: not connected — 请打开 chrome://inspect/#remote-debugging 并勾选 Allow remote debugging
```
解决：按提示操作，重启 Chrome

### 端口被占用
```
[CDP Proxy] 端口 3456 已被占用
```
解决：检查是否有其他 Proxy 实例在运行，或修改 `CDP_PROXY_PORT` 环境变量

### WebSocket 连接失败
解决：确认 Chrome 已正确开启远程调试，检查防火墙设置

## 更新日志

### v2.4.0-openclaw
- 适配 OpenClaw 环境
- 路径从 `~/.claude/skills/` 改为 `~/.openclaw/workspace/skills/`
- 集成 OpenClaw 内置 `browser` 工具和 `web_fetch` 工具
- 遵循 MEMORY.md，搜索优先使用 `searxng` skill
- 保留核心 CDP Proxy 和浏览哲学

### v2.4.0 (原始版本)
- 站点内 URL 可靠性说明
- 平台错误提示不可信警告
- 小红书站点经验增强

## 许可证

MIT License

## 原作者

一泽 Eze (@eze-is)
GitHub: https://github.com/eze-is/web-access

## OpenClaw 适配

本版本针对 OpenClaw 环境进行了适配，保留了核心的 CDP Proxy 和浏览哲学，同时集成了 OpenClaw 的内置工具链。
