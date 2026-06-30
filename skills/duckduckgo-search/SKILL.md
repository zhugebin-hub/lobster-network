# DuckDuckGo Search Skill

⚠️ **注意**: 由于系统 Python 版本 (3.6.8) 过老，duckduckgo-search 库不兼容。
**请使用已安装的 `searxng` 技能作为替代** —— 它同样提供隐私友好的搜索，且无 API 依赖。

## 替代方案：使用 searxng

```bash
# searxng 已安装在 /home/admin/.openclaw/workspace/skills/searxng/
# 支持搜索网页、新闻、图片等
```

## 原始设计（需 Python 3.10+）

```bash
ddg-search "搜索关键词" --num 10 --region us
```

## 依赖

- Python 3.10+ (当前系统为 3.6.8，不兼容)
- duckduckgo-search 库
