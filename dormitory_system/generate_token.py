#!/usr/bin/env python3
"""
生成 API Token
用法: python3 generate_token.py [token_name]
"""
import secrets
import sys
from pathlib import Path

TOKENS_FILE = Path(__file__).parent / ".api_tokens"

name = sys.argv[1] if len(sys.argv) > 1 else "default"
token = f"dorm_{name}_{secrets.token_hex(24)}"

# 写入 tokens 文件
existing = set()
if TOKENS_FILE.exists():
    for line in TOKENS_FILE.read_text().strip().split("\n"):
        line = line.strip()
        if line and not line.startswith("#"):
            existing.add(line)

existing.add(token)
TOKENS_FILE.write_text(
    "# API Tokens for Dormitory Selection System\n"
    + "# Format: one token per line\n"
    + "# Lines starting with # are comments\n"
    + "\n".join(existing) + "\n"
)

print(f"✅ Token 已生成: {name}")
print(f"   Token: {token}")
print(f"   存储: {TOKENS_FILE}")
print(f"\n使用时在请求头中添加:")
print(f"   Authorization: Bearer {token}")
print(f"   或 X-API-Key: {token}")
