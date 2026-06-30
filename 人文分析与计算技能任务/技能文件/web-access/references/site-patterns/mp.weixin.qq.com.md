---
domain: mp.weixin.qq.com
aliases: [微信公众号, WeChat MP]
updated: 2026-04-25
---

## 平台特征

- 正文通过 JavaScript 动态渲染，`web_fetch` 和 `readability` 只能拿到标题壳
- 无头浏览器（Playwright/Puppeteer）会触发**滑块验证**反爬
- Jina Reader (`r.jina.ai`) 被微信屏蔽，返回失败
- 但 HTML 源码中**完整包含正文内容**，藏在 `id="js_content"` 的 div 里

## 有效模式

### ✅ curl 直接抓取 HTML 源码（推荐）

```bash
curl -s -L \
  -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36" \
  -H "Accept: text/html" \
  -H "Accept-Language: zh-CN,zh;q=0.9" \
  "https://mp.weixin.qq.com/s/URL" | python3 -c "
import sys, re, html
content = sys.stdin.read()
match = re.search(r'id=\"js_content\"[^>]*>(.*?)</div>\s*<script', content, re.DOTALL)
if match:
    text = match.group(1)
    text = re.sub(r'<[^>]+>', '', text)
    text = html.unescape(text)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    print('\n'.join(lines))
else:
    print('CONTENT_NOT_FOUND')
"
```

**关键要点：**
- 必须用真实 User-Agent（模拟 Chrome 浏览器）
- 必须带 `Accept-Language: zh-CN` 头
- 用 Python 从 HTML 中提取 `js_content` div 并去标签
- 正则匹配 `id="js_content"` 到 `</div>\s*<script` 之间的内容

### 备用方案：截图 + image 工具

如果 curl 也失败，用 `browser` 截图 + `image` 工具 OCR 识别。

## 已知陷阱

| 方法 | 结果 | 原因 |
|------|------|------|
| `web_fetch` | ❌ 只有标题 | 不执行 JS，正文未渲染 |
| `browser` 工具 | ❌ 滑块验证 | 无头浏览器被反爬检测 |
| Jina Reader | ❌ 连接失败 | 微信屏蔽 Jina 爬虫 |
| curl + Python 解析 | ✅ 成功 | 源码中已包含完整内容 |

## 注意事项

- 部分文章可能有"阅读更多"折叠，但正文基本都在 `js_content` 里
- 图片不会自动下载，需要额外提取 `data-src` 属性
- 如果遇到微信登录态要求，可能需要 cookie（目前大多数文章不需要）
