---
domain: xetslk.com
aliases: [小鹅通, 浙江大学继续教育学院]
updated: 2026-04-30
---

## 平台特征

- **架构**：SPA（小鹅通 xiaoe-tech 提供技术支持）
- **反爬行为**：强 JS 渲染，web_fetch 无法提取有效内容
- **登录需求**：部分课程/回放内容需要登录才能观看
- **内容加载方式**：JavaScript 动态渲染，需要完整浏览器环境

## 有效模式

### URL 模式
```
# 分享链接（短链）
https://xxx.xetslk.com/sl/{id}

# 实际跳转域名
https://apper*.pc.xiaoe-tech.com/detail/{path}
```

### 操作策略
- **必须使用 browser 工具或 CDP Proxy**，web_fetch 无效
- 短链会自动跳转到 xiaoe-tech.com 域名
- 页面需要等待 JS 渲染完成才能获取内容

## 已知陷阱

### 陷阱 1：web_fetch 返回空内容
- **现象**：web_fetch 只能拿到 "Chrome 立即升级" 等提示文字，无实际页面内容
- **原因**：小鹅通是纯 SPA，内容全部通过 JS 动态渲染
- **解决**：直接使用 `browser` 工具（Playwright）或 CDP Proxy 访问

### 陷阱 2：登录态
- **现象**：部分内容（如直播回看）需要登录后才能进入
- **原因**：小鹅通课程有观看权限控制
- **解决**：使用 CDP Proxy 连接用户日常 Chrome（携带登录态），或引导用户手动登录

## 发现日期

- 2026-04-30: 初始版本 — 浙江大学继续教育学院课程页面
