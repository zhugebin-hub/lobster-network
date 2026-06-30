---
name: wechat-article-fetcher
description: 获取微信公众号文章全文内容并提取正文。当用户提供微信公众号链接（mp.weixin.qq.com）并要求阅读、分析、总结文章内容时使用。支持处理微信反爬机制（滑块验证等）。
---

# 微信公众号文章获取

## 使用场景

用户提供 `mp.weixin.qq.com/s/...` 链接，要求阅读、分析、总结文章内容。

## 工作流程

### 第一步：尝试 web_fetch

先用 `web_fetch` 工具直接抓取：

```
web_fetch(url="https://mp.weixin.qq.com/s/...", maxChars=15000)
```

如果返回的正文内容超过 500 字符，说明成功获取，进入分析环节。

### 第二步：curl 备用方案（web_fetch 失败时）

如果 `web_fetch` 只返回标题或极少内容（微信反爬），使用 curl 命令：

```bash
curl -s -L -A "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1" "URL" 2>/dev/null | python3 -c "
import sys, re
from html import unescape
html = sys.stdin.read()
match = re.search(r'id=\"js_content\"[^>]*>(.*?)</div>\s*<div class=\"rich_media_tool\"', html, re.DOTALL)
if not match:
    match = re.search(r'id=\"js_content\"[^>]*>(.*?)$', html, re.DOTALL)
if match:
    content = match.group(1)
    content = re.sub(r'<[^>]+>', ' ', content)
    content = unescape(content)
    content = re.sub(r'\s+', ' ', content).strip()
    print(content[:5000])
else:
    print('EXTRACT_FAILED')
"
```

将 URL 替换为实际的微信公众号链接。

### 第三步：浏览器方案（curl 也失败时）

如果 curl 也触发验证，用 browser 工具打开链接：

```
browser(action="open", url="...", profile="openclaw")
browser(action="act", kind="wait", timeMs=3000)
browser(action="snapshot")
```

如果碰到滑块验证，告知用户手动打开链接并把内容发给你。

## 内容分析

成功获取正文后：

1. **提取核心信息**：标题、作者、来源公众号、发布日期
2. **总结要点**：文章的核心观点和论据
3. **结构化输出**：用表格/列表呈现关键数据
4. **关联分析**：结合上下文提供延伸见解

## 注意事项

- 微信文章可能包含图片，curl 方案无法获取图片内容
- 部分文章可能有阅读限制，无法获取全文
- 如果所有方案都失败，礼貌告知用户并建议手动复制内容
