#!/usr/bin/env python3
"""
本地搜索脚本 - 使用 SearXNG 实例（无需 API Key）
自动根据查询语言选择最优搜索引擎组合
"""

import argparse
import json
import sys
import urllib.request
import urllib.parse
import re

SEARXNG_URL = "http://localhost:8080"

# 中文查询优先引擎
CHINESE_ENGINES = "baidu,sogou,google,duckduckgo,bing,wikipedia"
# 英文查询优先引擎
ENGLISH_ENGINES = "google,duckduckgo,bing,brave,wikipedia"
# 新闻查询引擎
NEWS_ENGINES = "baidu,google news,duckduckgo news,bing news"

def has_chinese(text):
    """检测文本是否包含中文字符"""
    return bool(re.search(r'[\u4e00-\u9fff]', text))

def search(query, max_results=10, search_type="general", time_range=None, output_format="text"):
    """执行搜索"""
    # 根据查询语言选择引擎
    if search_type == "news":
        engines = NEWS_ENGINES
    elif has_chinese(query):
        engines = CHINESE_ENGINES
    else:
        engines = ENGLISH_ENGINES

    # 构建请求参数
    params = {
        "q": query,
        "format": "json",
        "engines": engines,
        "language": "zh-CN" if has_chinese(query) else "en-US",
    }
    if time_range:
        params["time_range"] = time_range

    url = f"{SEARXNG_URL}/search?{urllib.parse.urlencode(params)}"

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"搜索错误: {e}", file=sys.stderr)
        return []

    results = data.get("results", [])[:max_results]

    # 去重（按 URL）
    seen = set()
    unique = []
    for r in results:
        url_key = r.get("url", "")
        if url_key not in seen:
            seen.add(url_key)
            unique.append(r)
        if len(unique) >= max_results:
            break

    return unique

def format_results(results, fmt="text"):
    """格式化输出"""
    if fmt == "json":
        output = []
        for r in results:
            output.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("content", ""),
                "engine": r.get("engine", ""),
            })
        return json.dumps(output, ensure_ascii=False, indent=2)

    if fmt == "markdown":
        lines = []
        for i, r in enumerate(results, 1):
            lines.append(f"## {i}. {r.get('title', '')}")
            lines.append(f"**URL:** {r.get('url', '')}")
            lines.append(f"")
            lines.append(r.get("content", "")[:200])
            lines.append(f"_来源: {r.get('engine', '')}_")
            lines.append("")
        return "\n".join(lines)

    # text format (default)
    lines = []
    for i, r in enumerate(results, 1):
        lines.append(f"{i}. {r.get('title', '')}")
        lines.append(f"   URL: {r.get('url', '')}")
        content = r.get("content", "")[:200]
        if content:
            lines.append(f"   {content}")
        lines.append(f"   来源: {r.get('engine', '')}")
        lines.append("")
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="本地搜索（SearXNG）")
    parser.add_argument("query", help="搜索关键词")
    parser.add_argument("--max-results", "-n", type=int, default=10, help="最大结果数")
    parser.add_argument("--type", "-t", choices=["general", "news"], default="general", help="搜索类型")
    parser.add_argument("--time-range", choices=["day", "week", "month", "year"], help="时间范围")
    parser.add_argument("--format", "-f", choices=["text", "markdown", "json"], default="text", help="输出格式")
    parser.add_argument("--output", "-o", help="输出文件路径")

    args = parser.parse_args()

    results = search(args.query, args.max_results, args.type, args.time_range, args.format)

    output = format_results(results, args.format)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"结果已保存到: {args.output}", file=sys.stderr)
    else:
        print(output)

    if not results:
        print(f"\n未找到结果。尝试其他关键词或检查 SearXNG 是否运行在 {SEARXNG_URL}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
