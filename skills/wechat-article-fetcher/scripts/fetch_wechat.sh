#!/usr/bin/env bash
# fetch_wechat.sh - Fetch WeChat public account article content
# Usage: bash fetch_wechat.sh <url>

set -euo pipefail

URL="$1"

curl -s -L \
  -A "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1" \
  "$URL" 2>/dev/null | python3 -c "
import sys, re
from html import unescape

html = sys.stdin.read()

# Try multiple extraction patterns
patterns = [
    r'id=\"js_content\"[^>]*>(.*?)</div>\s*<div class=\"rich_media_tool\"',
    r'id=\"js_content\"[^>]*>(.*?)</div>\s*<div class=\"rich_media_area_extra\"',
    r'id=\"js_content\"[^>]*>(.*?)$',
]

content = None
for pat in patterns:
    match = re.search(pat, html, re.DOTALL)
    if match:
        content = match.group(1)
        break

if content:
    # Remove HTML tags
    content = re.sub(r'<[^>]+>', ' ', content)
    # Unescape HTML entities
    content = unescape(content)
    # Clean whitespace
    content = re.sub(r'\s+', ' ', content).strip()
    # Print up to 8000 chars
    print(content[:8000])
else:
    print('EXTRACT_FAILED: Could not extract article content')
    sys.exit(1)
"
