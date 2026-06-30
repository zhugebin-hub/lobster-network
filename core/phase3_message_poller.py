#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 Phase 3 - 学员端消息轮询持久化
功能：
1. 学员端消息持久化存储（SQLite）
2. 消息轮询断点续传
3. 消息去重和顺序保证
4. 消息状态追踪（pending/processing/completed/failed）

作者：诸葛马 (Hermes)
日期：2026-06-30
版本：v1.0
"""

import json
import os
import sqlite3
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# ============================================================
# 配置
# ============================================================

class Config:
    """消息轮询持久化配置"""
    
    # 学员配置
    STUDENTS = {
        "xiaochen": {
            "name": "小陈",
            "inbox_dir": "/home/admin/go-training/shared/training/xiaochen/inbox",
            "db_path": "/home/admin/go-training/shared/messages/xiaochen_messages.db",
        },
        "zhuguxia": {
            "name": "诸葛虾",
            "inbox_dir": "/home/admin/go-training/shared/training/zhuguxia/inbox",
            "db_path": "/home/admin/go-training/shared/messages/zhuguxia_messages.db",
        },
        "qoder": {
            "name": "qoder",
            "inbox_dir": "/home/admin/go-training/shared/training/qoder/inbox",
            "db_path": "/home/admin/go-training/shared/messages/qoder_messages.db",
        },
    }
    
    # 共享目录
    SHARED_DIR = "/home/admin/go-training/shared/"
    MESSAGES_DIR = f"{SHARED_DIR}messages/"
    
    # 轮询配置
    POLL_INTERVAL = 30  # 轮询间隔（秒）
    MAX_RETRY = 3       # 最大重试次数
    MESSAGE_TTL = 86400 * 7  # 消息有效期（7天）


# ============================================================
# 消息数据库
# ============================================================

class MessageDB:
    """消息持久化数据库（SQLite）"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                message_id TEXT UNIQUE,
                from_sender TEXT,
                to_receiver TEXT,
                message_type TEXT,
                content TEXT,
                checksum TEXT,
                status TEXT DEFAULT 'pending',
                retry_count INTEGER DEFAULT 0,
                created_at TEXT,
                updated_at TEXT,
                processed_at TEXT,
                error_message TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS message_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT,
                action TEXT,
                timestamp TEXT,
                details TEXT
            )
        """)
        
        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_status ON messages(status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created ON messages(created_at)
        """)
        
        conn.commit()
        conn.close()
    
    def insert_message(self, message: Dict) -> bool:
        """插入消息（去重）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        message_id = message.get("id") or message.get("message_id")
        if not message_id:
            return False
        
        # 计算校验和
        content_str = json.dumps(message, sort_keys=True)
        checksum = hashlib.md5(content_str.encode()).hexdigest()
        
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO messages 
                (id, message_id, from_sender, to_receiver, message_type, content, checksum, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?)
            """, (
                message_id,
                message_id,
                message.get("from", "unknown"),
                message.get("to", "unknown"),
                message.get("type", "unknown"),
                json.dumps(message, ensure_ascii=False),
                checksum,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ))
            
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"❌ 插入消息失败: {e}")
            return False
        finally:
            conn.close()
    
    def get_pending_messages(self, limit: int = 10) -> List[Dict]:
        """获取待处理消息"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM messages 
            WHERE status = 'pending' 
            ORDER BY created_at ASC
            LIMIT ?
        """, (limit,))
        
        messages = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return messages
    
    def update_message_status(self, message_id: str, status: str, error_message: str = None):
        """更新消息状态"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE messages 
            SET status = ?, updated_at = ?, processed_at = ?, error_message = ?
            WHERE message_id = ?
        """, (
            status,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S") if status in ["completed", "failed"] else None,
            error_message,
            message_id,
        ))
        
        conn.commit()
        conn.close()
    
    def increment_retry(self, message_id: str) -> int:
        """增加重试次数，返回当前重试次数"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE messages 
            SET retry_count = retry_count + 1, updated_at = ?
            WHERE message_id = ?
        """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message_id))
        
        cursor.execute("SELECT retry_count FROM messages WHERE message_id = ?", (message_id,))
        result = cursor.fetchone()
        retry_count = result[0] if result else 0
        
        conn.commit()
        conn.close()
        
        return retry_count
    
    def get_message_stats(self) -> Dict:
        """获取消息统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        for status in ["pending", "processing", "completed", "failed"]:
            cursor.execute("SELECT COUNT(*) FROM messages WHERE status = ?", (status,))
            stats[status] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM messages")
        stats["total"] = cursor.fetchone()[0]
        
        conn.close()
        return stats
    
    def cleanup_old_messages(self, ttl_days: int = 7):
        """清理过期消息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            DELETE FROM messages 
            WHERE status IN ('completed', 'failed') 
            AND created_at < datetime('now', '-{} days')
        """.format(ttl_days))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted


# ============================================================
# 消息轮询器
# ============================================================

class MessagePoller:
    """消息轮询器"""
    
    def __init__(self, student_id: str):
        self.student_id = student_id
        self.config = Config()
        student_config = self.config.STUDENTS[student_id]
        
        self.inbox_dir = student_config["inbox_dir"]
        self.db = MessageDB(student_config["db_path"])
        self.last_poll_time = None
        self.last_poll_file = None
    
    def poll(self) -> List[Dict]:
        """轮询新消息"""
        new_messages = []
        
        if not os.path.exists(self.inbox_dir):
            return []
        
        # 扫描inbox目录
        for filename in sorted(os.listdir(self.inbox_dir)):
            if not filename.endswith(".json"):
                continue
            
            filepath = os.path.join(self.inbox_dir, filename)
            
            # 检查是否已处理
            message_id = filename.replace(".json", "")
            
            try:
                with open(filepath, "r") as f:
                    message = json.load(f)
                
                # 插入数据库（自动去重）
                is_new = self.db.insert_message(message)
                
                if is_new:
                    new_messages.append(message)
                    
            except Exception as e:
                print(f"❌ 读取消息失败 {filename}: {e}")
        
        self.last_poll_time = datetime.now()
        return new_messages
    
    def process_pending(self, processor_func) -> Dict:
        """处理待处理消息"""
        pending = self.db.get_pending_messages()
        results = {"processed": 0, "succeeded": 0, "failed": 0, "retried": 0}
        
        for message in pending:
            message_id = message["message_id"]
            
            try:
                # 更新状态为processing
                self.db.update_message_status(message_id, "processing")
                
                # 调用处理函数
                content = json.loads(message["content"])
                result = processor_func(content)
                
                if result.get("success", False):
                    self.db.update_message_status(message_id, "completed")
                    results["succeeded"] += 1
                else:
                    # 处理失败，重试
                    retry_count = self.db.increment_retry(message_id)
                    if retry_count >= Config.MAX_RETRY:
                        self.db.update_message_status(
                            message_id, "failed",
                            error_message=result.get("error", "超过最大重试次数")
                        )
                        results["failed"] += 1
                    else:
                        self.db.update_message_status(message_id, "pending")
                        results["retried"] += 1
                
                results["processed"] += 1
                
            except Exception as e:
                retry_count = self.db.increment_retry(message_id)
                if retry_count >= Config.MAX_RETRY:
                    self.db.update_message_status(message_id, "failed", error_message=str(e))
                    results["failed"] += 1
                else:
                    results["retried"] += 1
        
        return results
    
    def get_stats(self) -> Dict:
        """获取轮询统计"""
        stats = self.db.get_message_stats()
        stats["student_id"] = self.student_id
        stats["last_poll_time"] = self.last_poll_time.strftime("%Y-%m-%d %H:%M:%S") if self.last_poll_time else None
        return stats


# ============================================================
# 命令行接口
# ============================================================

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="消息轮询持久化")
    parser.add_argument("action", choices=["poll", "process", "stats", "cleanup"],
                       help="操作: poll(轮询) | process(处理) | stats(统计) | cleanup(清理)")
    parser.add_argument("--student", type=str, required=True, help="学员ID")
    
    args = parser.parse_args()
    
    if args.student not in Config.STUDENTS:
        print(f"❌ 未知学员: {args.student}")
        return
    
    poller = MessagePoller(args.student)
    
    if args.action == "poll":
        messages = poller.poll()
        print(f"📥 轮询到 {len(messages)} 条新消息")
        for msg in messages:
            print(f"  - {msg.get('id', 'unknown')}: {msg.get('type', 'unknown')}")
    
    elif args.action == "process":
        # 示例处理函数
        def dummy_processor(message):
            print(f"  处理消息: {message.get('id', 'unknown')}")
            return {"success": True}
        
        results = poller.process_pending(dummy_processor)
        print(json.dumps(results, ensure_ascii=False, indent=2))
    
    elif args.action == "stats":
        stats = poller.get_stats()
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    
    elif args.action == "cleanup":
        deleted = poller.db.cleanup_old_messages()
        print(f"🧹 清理了 {deleted} 条过期消息")


if __name__ == "__main__":
    main()
