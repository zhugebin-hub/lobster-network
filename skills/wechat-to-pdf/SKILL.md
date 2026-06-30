---
name: wechat-to-pdf
description: 微信公众号文章转 PDF 技能。支持从微信公众号链接生成包含完整正文和图片的 PDF 文档。
version: 1.0.0
author: 小龙虾 - 诸葛虾
---

# 微信公众号文章转 PDF 技能

## 功能

将微信公众号文章链接转换为包含完整正文、图片和排版的 PDF 文档。

## 使用场景

- 用户发送微信公众号文章链接，要求生成 PDF
- 需要保存微信公众号文章为可打印格式
- 需要离线阅读微信公众号文章

## 使用方法

### 基本用法

```
用户：把这个文章转成 PDF
链接：https://mp.weixin.qq.com/s/xxxxx
```

### 技能调用

```bash
# 执行转换
bash ~/.openclaw/workspace/skills/wechat-to-pdf/scripts/wechat-to-pdf.sh "https://mp.weixin.qq.com/s/xxxxx"

# 输出文件
# /tmp/wechat_article.pdf
```

## 工作流程

1. **抓取 HTML 源码** - 使用 curl 获取微信公众号文章完整 HTML
2. **提取正文内容** - 使用 Python 解析 `js_content` div
3. **下载图片** - 提取所有 `data-src` 图片并下载
4. **内嵌图片** - 将图片转换为 base64 内嵌到 HTML
5. **生成 PDF** - 使用浏览器渲染 HTML 并导出 PDF
6. **发送文件** - 通过钉钉发送 PDF 文件

## 技术要点

### 微信公众号反爬处理

- `web_fetch` 只能拿到标题（JS 动态渲染）
- 无头浏览器会触发滑块验证
- **解决方案**：curl 直接抓取 HTML 源码，Python 解析 `js_content`

### 图片处理

- 图片路径问题：使用绝对文件系统路径浏览器无法访问
- **解决方案**：将图片内嵌为 base64 data URI

### PDF 压缩

- 原始 PDF 可能较大（4-5MB）
- **解决方案**：使用 Pillow 压缩图片（调整尺寸和质量）

## 文件结构

```
skills/wechat-to-pdf/
├── SKILL.md              # 本文件
├── scripts/
│   ├── wechat-to-pdf.sh  # 主脚本
│   └── extract_wechat.py # Python 提取脚本
└── references/
    └── mp.weixin.qq.com.md  # 站点经验
```

## 依赖

- curl - HTTP 请求
- Python 3 - 文本处理和图片压缩
- Pillow - 图片处理
- OpenClaw browser - PDF 生成

## 注意事项

- 部分文章可能有"阅读更多"折叠，但正文基本都在 `js_content` 里
- 图片不会自动下载，需要额外提取 `data-src` 属性
- 如果遇到微信登录态要求，可能需要 cookie（目前大多数文章不需要）
- PDF 文件较大时，钉钉上传可能失败，需要压缩

## 扩展

- 支持其他平台（知乎、今日头条等）
- 支持自定义 PDF 样式
- 支持批量转换

## 触发词

当用户发送微信公众号文章链接并要求生成 PDF 时，自动调用此技能。

## 示例对话

用户：把这个文章转成 PDF
链接：https://mp.weixin.qq.com/s/xxxxx

AI：好的，我来帮你生成 PDF。

（调用技能）

bash ~/.openclaw/workspace/skills/wechat-to-pdf/scripts/wechat-to-pdf.sh "https://mp.weixin.qq.com/s/xxxxx"

（生成 PDF 并发送）

AI：PDF 已生成并发送！
