---
name: web-access
license: MIT
github: https://github.com/eze-is/web-access
description:
  所有联网操作必须通过此 skill 处理，包括：搜索、网页抓取、登录后操作、网络交互等。
  触发场景：用户要求搜索信息、查看网页内容、访问需要登录的网站、操作网页界面、抓取社交媒体内容、
  读取动态渲染页面、以及任何需要真实浏览器环境的网络任务。
metadata:
  author: 一泽 Eze (适配：OpenClaw)
  version: "2.4.0-openclaw"
---

# web-access Skill for OpenClaw

## 前置检查

在开始联网操作前，先检查 CDP 模式可用性：

```bash
bash ~/.openclaw/workspace/skills/web-access/scripts/check-deps.sh
```

- **Node.js 22+**：必需（使用原生 WebSocket）。当前环境 Node.js v24.14.0 ✅
- **Chrome remote-debugging**：在 Chrome 地址栏打开 `chrome://inspect/#remote-debugging`，勾选 **"Allow remote debugging for this browser instance"** 即可，可能需要重启浏览器。

检查通过后再启动 CDP Proxy 执行操作，未通过则引导用户完成设置。

## 浏览哲学

**像人一样思考，兼顾高效与适应性的完成任务。**

执行任务时不会过度依赖固有印象所规划的步骤，而是带着目标进入，边看边判断，遇到阻碍就解决，发现内容不够就深入——全程围绕「我要达成什么」做决策。

**① 拿到请求** — 先明确用户要做什么，定义成功标准：什么算完成了？需要获取什么信息、执行什么操作、达到什么结果？

**② 选择起点** — 根据任务性质、平台特征、达成条件，选一个最可能直达的方式作为第一步去验证。
- 需要操作页面、需要登录态、已知静态方式不可达的平台（小红书、微信公众号等）→ 直接 CDP

**③ 过程校验** — 每一步的结果都是证据。用结果对照①的成功标准，更新判断：路径在推进吗？发现方向错了立即调整，不在同一个方式上反复重试。

**④ 完成判断** — 对照定义的任务成功标准，确认任务完成后才停止，但也不要过度操作。

## 联网工具选择

OpenClaw 环境可用工具：

| 场景 | 工具 |
|------|------|
| 搜索摘要或关键词结果，发现信息来源 | **searxng skill**（优先）或 `web_search` |
| URL 已知，需要从页面定向提取特定信息 | **`web_fetch`**（拉取网页内容） |
| URL 已知，需要原始 HTML 源码 | **`exec` + curl** |
| 非公开内容，或已知静态层无效的平台 | **浏览器 CDP** |
| 需要登录态、交互操作，或动态渲染页面 | **浏览器 CDP** 或 **`browser` 工具** |

**工具优先级说明：**

1. **searxng** - MEMORY.md 指定优先使用本地 SearXNG 实例，隐私优先
2. **web_fetch** - 轻量级页面提取，适合静态内容
3. **browser 工具** - OpenClaw 内置 Playwright 浏览器自动化
4. **CDP Proxy** - 直连用户日常 Chrome，携带登录态，适合需要登录的场景

**Jina**（可选预处理层）：`r.jina.ai/example.com` 可将网页转为 Markdown，节省 token 但可能有信息损耗。适合文章、博客、文档等以正文为核心的页面。

## 浏览器 CDP 模式

通过 CDP Proxy 直连用户日常 Chrome，天然携带登录态，无需启动独立浏览器。

### 启动 Proxy

```bash
# 检查依赖
bash ~/.openclaw/workspace/skills/web-access/scripts/check-deps.sh

# 启动 Proxy（后台运行）
node ~/.openclaw/workspace/skills/web-access/scripts/cdp-proxy.mjs &
```

Proxy 启动后持续运行在 `http://localhost:3456`。

### Proxy API

所有操作通过 curl 调用 HTTP API：

```bash
# 列出用户已打开的 tab
curl -s http://localhost:3456/targets

# 创建新后台 tab（自动等待加载）
curl -s "http://localhost:3456/new?url=https://example.com"

# 页面信息
curl -s "http://localhost:3456/info?target=ID"

# 执行任意 JS
curl -s -X POST "http://localhost:3456/eval?target=ID" -d 'document.title'

# 截图
curl -s "http://localhost:3456/screenshot?target=ID&file=/tmp/shot.png"

# 导航
curl -s "http://localhost:3456/navigate?target=ID&url=URL"

# 点击（JS click）
curl -s -X POST "http://localhost:3456/click?target=ID" -d 'button.submit'

# 真实鼠标点击（能触发文件对话框）
curl -s -X POST "http://localhost:3456/clickAt?target=ID" -d 'button.upload'

# 文件上传
curl -s -X POST "http://localhost:3456/setFiles?target=ID" \
  -d '{"selector":"input[type=file]","files":["/path/to/file.png"]}'

# 滚动（触发懒加载）
curl -s "http://localhost:3456/scroll?target=ID&direction=bottom"

# 关闭 tab
curl -s "http://localhost:3456/close?target=ID"
```

### 使用原则

- 若无用户明确要求，不操作用户已有 tab，所有操作在后台创建的 tab 中进行
- 任务结束后关闭自己创建的 tab，保持环境整洁
- Proxy 持续运行，不建议主动停止

## 与 OpenClaw 工具集成

### 使用 browser 工具（Playwright）

OpenClaw 内置 `browser` 工具，适合大多数浏览器自动化场景：

```
browser action=snapshot url=https://example.com
browser action=act ref=e1 kind=click
browser action=act ref=e2 kind=type text=hello
```

### 使用 CDP Proxy（需要登录态时）

当需要利用用户日常 Chrome 的登录态时，使用 CDP Proxy：

```bash
# 启动 Proxy
node ~/.openclaw/workspace/skills/web-access/scripts/cdp-proxy.mjs &

# 创建 tab 并访问
TARGET=$(curl -s "http://localhost:3456/new?url=https://example.com" | jq -r .targetId)

# 操作页面
curl -s -X POST "http://localhost:3456/eval?target=$TARGET" -d 'document.title'

# 完成后关闭
curl -s "http://localhost:3456/close?target=$TARGET"
```

## 并行调研：子 Agent 分治策略

任务包含多个**独立**调研目标时，鼓励合理分治给子 Agent 并行执行。

**分治判断标准：**

| 适合分治 | 不适合分治 |
|----------|-----------|
| 目标相互独立，结果互不依赖 | 目标有依赖关系 |
| 每个子任务量足够大 | 简单单页查询 |
| 需要 CDP 浏览器或长时间运行 | 轻量查询 |

**子 Agent Prompt 写法：**
- 必须写 `必须加载 web-access skill 并遵循指引`
- 描述**要什么**，避免过度指定**怎么做**
- 避免用暗示具体手段的动词（「搜索」「抓取」），改用目标导向（「获取」「调研」「了解」）

## 信息核实类任务

核实的目标是**一手来源**，而非更多的二手报道。

| 信息类型 | 一手来源 |
|----------|---------|
| 政策/法规 | 发布机构官网 |
| 企业公告 | 公司官方新闻页 |
| 学术声明 | 原始论文/机构官网 |
| 工具能力/用法 | 官方文档、源码 |

**找不到官网时**：权威媒体的原创报道可作为次级依据，但需向用户说明来源限制。

## 站点经验

操作中积累的特定网站经验，按域名存储在 `references/site-patterns/` 下。

已有经验的站点：`ls ~/.openclaw/workspace/skills/web-access/references/site-patterns/ 2>/dev/null | sed 's/\.md$//' || echo "暂无"`

确定目标网站后，如果上方列表中有匹配的站点，必须读取对应文件获取先验知识。

CDP 操作成功完成后，如果发现了有必要记录经验的新站点或新模式，主动写入对应的站点经验文件。

文件格式：
```markdown
---
domain: example.com
aliases: [示例，Example]
updated: 2026-03-24
---
## 平台特征
架构、反爬行为、登录需求、内容加载方式等事实

## 有效模式
已验证的 URL 模式、操作策略、选择器

## 已知陷阱
什么会失败以及为什么
```

## References 索引

| 文件 | 何时加载 |
|------|---------|
| `references/cdp-api.md` | 需要 CDP API 详细参考时 |
| `references/site-patterns/{domain}.md` | 确定目标网站后，读取对应站点经验 |

## OpenClaw 适配说明

本 skill 已针对 OpenClaw 环境适配：

1. **路径调整**：所有路径从 `~/.claude/skills/` 改为 `~/.openclaw/workspace/skills/`
2. **工具集成**：优先使用 OpenClaw 内置 `browser` 工具和 `web_fetch` 工具
3. **搜索偏好**：遵循 MEMORY.md，联网搜索优先使用 `searxng` skill
4. **CDP Proxy**：保留核心 CDP Proxy 脚本，用于需要登录态的场景
5. **子 Agent**：使用 `sessions_spawn` 实现并行分治
