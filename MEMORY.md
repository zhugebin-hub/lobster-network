# MEMORY.md - Long-Term Memory

## Preferences

- **联网搜索优先使用 searxng skill** —— 只要涉及联网搜索任务，优先调用 searxng 技能而非直接使用 web_search 工具。

## Notes

- Created: 2026-03-05

## Installed Skills

- **web-access** (v2.4.0-openclaw) - 完整联网能力 skill，安装于 2026-03-24
  - 路径：`~/.openclaw/workspace/skills/web-access/`
  - 核心能力：CDP Proxy 直连 Chrome（携带登录态）、三层工具调度、站点经验积累、并行分治
  - 使用场景：搜索、网页抓取、需要登录的网站、动态页面、社交媒体内容获取
  - 前置要求：Chrome 需开启远程调试（`chrome://inspect/#remote-debugging`）
