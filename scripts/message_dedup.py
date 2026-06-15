#!/usr/bin/env python3
"""
消息去重管理器 (message_dedup.py)
功能：基于内容 Hash 的去重，防止重复发送
作者：小龙虾-诸葛虾 🦞
日期：2026-05-17
"""

import json
import hashlib
import time
import os
from pathlib import Path
from datetime import datetime

class MessageDeduplicator:
    def __init__(self, cache_dir="/home/admin/.openclaw/data/message-cache", window=120):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.window = window  # 去重窗口（秒）
        
    def generate_fingerprint(self, content: str, sender: str = "") -> str:
        """生成消息指纹（基于内容前 200 字符 + 发送者）"""
        key = f"{content[:200]}|{sender}"
        return hashlib.md5(key.encode()).hexdigest()
    
    def check_duplicate(self, fingerprint: str) -> dict:
        """检查是否重复，返回 {is_duplicate: bool, last_sent: int}"""
        cache_file = self.cache_dir / f"{fingerprint}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                
                last_sent = data.get('last_sent', 0)
                elapsed = int(time.time()) - last_sent
                
                if elapsed < self.window:
                    return {
                        'is_duplicate': True,
                        'last_sent': last_sent,
                        'elapsed': elapsed,
                        'send_count': data.get('send_count', 1)
                    }
            except Exception:
                pass
        
        return {'is_duplicate': False, 'last_sent': 0, 'elapsed': 0}
    
    def record_sent(self, fingerprint: str, message_id: str = ""):
        """记录消息已发送"""
        cache_file = self.cache_dir / f"{fingerprint}.json"
        
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
            send_count = data.get('send_count', 0) + 1
        except Exception:
            send_count = 1
        
        data = {
            'fingerprint': fingerprint,
            'message_id': message_id,
            'last_sent': int(time.time()),
            'send_count': send_count
        }
        
        with open(cache_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        self.cleanup()
    
    def cleanup(self):
        """清理过期缓存"""
        now = int(time.time())
        cleaned = 0
        
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                
                if now - data.get('last_sent', 0) > self.window:
                    cache_file.unlink()
                    cleaned += 1
            except Exception:
                pass
        
        if cleaned > 0:
            with open(self.cache_dir / "cleanup.log", 'a') as f:
                f.write(f"[{datetime.now()}] 清理了 {cleaned} 条过期缓存\n")
    
    def get_stats(self) -> dict:
        """获取去重统计"""
        total = len(list(self.cache_dir.glob("*.json")))
        recent = 0
        now = int(time.time())
        
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                if now - data.get('last_sent', 0) < self.window:
                    recent += 1
            except Exception:
                pass
        
        return {'total_cached': total, 'recent_sends': recent}

# 测试代码
if __name__ == "__main__":
    dedup = MessageDeduplicator()
    
    # 测试去重
    content = "让我先把我的所有技能复制到 NFS 共享目录..."
    fingerprint = dedup.generate_fingerprint(content, "xiaolongxia")
    result = dedup.check_duplicate(fingerprint)
    
    if result['is_duplicate']:
        print(f"⏭️  跳过重复消息（{result['elapsed']}s 前已发送）")
    else:
        print("✅ 消息唯一，可以发送")
        dedup.record_sent(fingerprint, "msg_test_001")
        
    # 显示统计
    stats = dedup.get_stats()
    print(f"📊 缓存统计: {stats}")
