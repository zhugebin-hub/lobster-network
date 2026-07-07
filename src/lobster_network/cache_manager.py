#!/usr/bin/env python3
<<<<<<< HEAD
# -*- coding: utf-8 -*-
"""
缓存管理器 (Cache Manager) - 小龙虾网络 V3.1
基于 MD5 键值 + TTL 的本地 JSON 缓存

功能:
- 高频请求本地缓存，减少 API 调用
- TTL 自动过期
- 缓存命中率统计
- 持久化到本地 JSON 文件
"""

import os
import json
import time
import hashlib
import logging
from typing import Any, Optional, Dict, Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from threading import Lock

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: Any
    created_at: float
    expires_at: float
    access_count: int = 0
    last_accessed: float = 0.0
    size_bytes: int = 0

    def is_expired(self) -> bool:
        return time.time() > self.expires_at

    def to_dict(self) -> Dict:
        return {
            "key": self.key,
            "value": self.value,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed,
            "size_bytes": self.size_bytes,
        }

    @classmethod
    def from_dict(cls, d: Dict) -> "CacheEntry":
        return cls(
            key=d["key"],
            value=d["value"],
            created_at=d["created_at"],
            expires_at=d["expires_at"],
            access_count=d.get("access_count", 0),
            last_accessed=d.get("last_accessed", 0.0),
            size_bytes=d.get("size_bytes", 0),
        )


@dataclass
class CacheStats:
    """缓存统计"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    evictions: int = 0
    errors: int = 0

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0

    def to_dict(self) -> Dict:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "sets": self.sets,
            "evictions": self.evictions,
            "errors": self.errors,
            "hit_rate": round(self.hit_rate, 1),
            "total_requests": self.hits + self.misses,
        }


class CacheManager:
    """本地 JSON 缓存管理器"""

    def __init__(
        self,
        name: str = "default",
        cache_dir: Optional[str] = None,
        default_ttl: int = 300,         # 默认 TTL 5 分钟
        max_entries: int = 500,         # 最大条目数
        max_size_mb: int = 50,          # 最大缓存大小 MB
        auto_save: bool = True,
        save_interval: int = 60,        # 自动保存间隔（秒）
    ):
        self.name = name
        self.default_ttl = default_ttl
        self.max_entries = max_entries
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.auto_save = auto_save

        # 缓存存储
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = Lock()
        self._stats = CacheStats()
        self._last_save = 0.0

        # 持久化路径
        if cache_dir:
            self._cache_dir = Path(cache_dir)
            self._cache_file = self._cache_dir / f"cache_{name}.json"
            self._cache_dir.mkdir(parents=True, exist_ok=True)
            self._load()
        else:
            self._cache_dir = None
            self._cache_file = None

        logger.info(f"[缓存:{self.name}] 初始化: TTL={default_ttl}s, "
                     f"max_entries={max_entries}, max_size={max_size_mb}MB")

    def _make_key(self, *args, **kwargs) -> str:
        """生成缓存键（MD5）"""
        raw = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
        return hashlib.md5(raw.encode('utf-8')).hexdigest()

    def _serialize_value(self, value: Any) -> Any:
        """序列化值（处理不可 JSON 的类型）"""
        try:
            json.dumps(value)
            return value
        except (TypeError, ValueError):
            return str(value)

    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                self._stats.misses += 1
                return None

            if entry.is_expired():
                del self._cache[key]
                self._stats.misses += 1
                self._stats.evictions += 1
                return None

            entry.access_count += 1
            entry.last_accessed = time.time()
            self._stats.hits += 1
            return entry.value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存"""
        ttl = ttl or self.default_ttl
        now = time.time()

        value = self._serialize_value(value)
        size = len(json.dumps(value, default=str).encode('utf-8'))

        with self._lock:
            # 检查容量
            if len(self._cache) >= self.max_entries and key not in self._cache:
                self._evict_expired()
                if len(self._cache) >= self.max_entries:
                    # 淘汰最少访问的
                    self._evict_lru()

            # 检查总大小
            total_size = sum(e.size_bytes for e in self._cache.values())
            if total_size + size > self.max_size_bytes:
                self._evict_lru()

            entry = CacheEntry(
                key=key,
                value=value,
                created_at=now,
                expires_at=now + ttl,
                size_bytes=size,
            )
            self._cache[key] = entry
            self._stats.sets += 1

            if self.auto_save and (now - self._last_save) > 60:
                self._save()
                self._last_save = now

            return True

    def delete(self, key: str) -> bool:
        """删除缓存"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self):
        """清空所有缓存"""
        with self._lock:
            self._cache.clear()
            self._stats.evictions = 0
        logger.info(f"[缓存:{self.name}] 已清空")

    def _evict_expired(self):
        """淘汰过期条目"""
        expired = [k for k, v in self._cache.items() if v.is_expired()]
        for k in expired:
            del self._cache[k]
            self._stats.evictions += 1
        if expired:
            logger.debug(f"[缓存:{self.name}] 淘汰 {len(expired)} 个过期条目")

    def _evict_lru(self):
        """淘汰最少访问的条目"""
        if not self._cache:
            return
        # 按 access_count 排序，淘汰最少的
        lru_key = min(self._cache, key=lambda k: self._cache[k].access_count)
        del self._cache[lru_key]
        self._stats.evictions += 1

    def _save(self):
        """持久化到文件"""
        if not self._cache_file:
            return
        try:
            data = {
                "name": self.name,
                "saved_at": datetime.now().isoformat(),
                "stats": self._stats.to_dict(),
                "entries": {k: v.to_dict() for k, v in self._cache.items()},
            }
            tmp_file = self._cache_file.with_suffix('.tmp')
            with open(tmp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            tmp_file.rename(self._cache_file)
        except Exception as e:
            self._stats.errors += 1
            logger.warning(f"[缓存:{self.name}] 持久化失败: {e}")

    def _load(self):
        """从文件加载"""
        if not self._cache_file or not self._cache_file.exists():
            return
        try:
            with open(self._cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for k, v in data.get("entries", {}).items():
                entry = CacheEntry.from_dict(v)
                if not entry.is_expired():
                    self._cache[k] = entry
            loaded = len(self._cache)
            logger.info(f"[缓存:{self.name}] 从文件加载 {loaded} 个有效条目")
        except Exception as e:
            logger.warning(f"[缓存:{self.name}] 加载失败: {e}")
            self._cache.clear()

    def get_stats(self) -> Dict:
        """获取统计信息"""
        with self._lock:
            return {
                "name": self.name,
                "entries": len(self._cache),
                "stats": self._stats.to_dict(),
            }

    def save(self):
        """手动保存"""
        with self._lock:
            self._save()
            self._last_save = time.time()


# ========== 装饰器 ==========

def cached(cache_mgr: CacheManager, ttl: Optional[int] = None):
    """缓存装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            key = cache_mgr._make_key(func.__name__, *args, **kwargs)
            result = cache_mgr.get(key)
            if result is not None:
                return result
            result = func(*args, **kwargs)
            cache_mgr.set(key, result, ttl)
            return result
        wrapper.cache = cache_mgr
        return wrapper
    return decorator


# ========== 预定义缓存实例 ==========

# API 响应缓存（短 TTL，高频）
api_cache = CacheManager(
    name="api",
    default_ttl=60,       # 1 分钟
    max_entries=200,
)

# 模型数据缓存（长 TTL，低频更新）
model_cache = CacheManager(
    name="model",
    default_ttl=3600,     # 1 小时
    max_entries=100,
)

# 训练结果缓存（中等 TTL）
training_cache = CacheManager(
    name="training",
    default_ttl=300,      # 5 分钟
    max_entries=300,
)

# 全局缓存注册表
_caches: Dict[str, CacheManager] = {
    "api": api_cache,
    "model": model_cache,
    "training": training_cache,
}


def get_cache(name: str, **kwargs) -> CacheManager:
    """获取或创建命名缓存"""
    if name not in _caches:
        _caches[name] = CacheManager(name=name, **kwargs)
    return _caches[name]


def get_all_cache_stats() -> Dict:
    """获取所有缓存统计"""
    return {name: c.get_stats() for name, c in _caches.items()}
=======
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
>>>>>>> fbc3017db51a546a289ef16bd15ae36823f768d7
