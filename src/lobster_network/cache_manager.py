#!/usr/bin/env python3
"""
🦞 小龙虾网络 · 结果缓存管理器
版本: V1.0 | 日期: 2026-06-28
功能: 高频 API 响应缓存，降低重复请求成本
"""
import json
import os
import time
import hashlib
from datetime import datetime

CACHE_DIR = "/tmp/lobster_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def get_cache_key(url: str, params: dict = None) -> str:
    raw = url + json.dumps(params or {}, sort_keys=True)
    return hashlib.md5(raw.encode()).hexdigest()

def get_cached_response(url: str, params: dict = None, ttl: int = 300) -> dict | None:
    key = get_cache_key(url, params)
    cache_file = os.path.join(CACHE_DIR, f"{key}.json")
    
    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            data = json.load(f)
            if time.time() - data["cached_at"] < ttl:
                return data["response"]
            else:
                os.remove(cache_file)
    return None

def set_cached_response(url: str, response: dict, params: dict = None):
    key = get_cache_key(url, params)
    cache_file = os.path.join(CACHE_DIR, f"{key}.json")
    with open(cache_file, "w") as f:
        json.dump({
            "cached_at": time.time(),
            "response": response
        }, f)

def clear_expired_cache():
    for f in os.listdir(CACHE_DIR):
        path = os.path.join(CACHE_DIR, f)
        try:
            with open(path) as fh:
                data = json.load(fh)
                if time.time() - data["cached_at"] > 3600: # 1小时过期
                    os.remove(path)
        except:
            os.remove(path)
    print("🧹 缓存清理完成")

if __name__ == "__main__":
    # 测试缓存
    test_url = "https://api.example.com/data"
    set_cached_response(test_url, {"status": "ok", "data": [1,2,3]})
    cached = get_cached_response(test_url)
    print(f"📦 缓存读取: {cached}")
    clear_expired_cache()
