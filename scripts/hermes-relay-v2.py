#!/usr/bin/env python3
"""
Hermes 中转代理 v2 - 通过 SSH 调用 Hermes 服务器的 hermes chat
"""
import sys, os, json, time, subprocess, glob
from datetime import datetime

SHARED_DIR = "/shared/messages"
FROM_LOBSTER = os.path.join(SHARED_DIR, "from-lobster")
FROM_HERMES = os.path.join(SHARED_DIR, "from-hermes")
ARCHIVE = os.path.join(SHARED_DIR, "archive")

def send_to_hermes(message, timeout=60):
    """发送消息给 Hermes 并等待回复"""
    os.makedirs(FROM_LOBSTER, exist_ok=True)
    os.makedirs(FROM_HERMES, exist_ok=True)
    os.makedirs(ARCHIVE, exist_ok=True)
    
    # 清理旧的回复
    old_replies = glob.glob(os.path.join(FROM_HERMES, "*.msg"))
    for r in old_replies:
        try:
            os.rename(r, os.path.join(ARCHIVE, os.path.basename(r)))
        except:
            pass
    
    # 发送消息
    ts = int(time.time())
    msg_id = f"{ts}-xiaolongxia-relay"
    msg = {
        "id": msg_id,
        "from": "xiaolongxia",
        "to": "hermes",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "message": message,
        "type": "text",
        "relay": True
    }
    
    msg_file = os.path.join(FROM_LOBSTER, f"{msg_id}.msg")
    with open(msg_file, "w", encoding="utf-8") as f:
        json.dump(msg, f, indent=2, ensure_ascii=False)
    
    print(f"📤 已发送: {message}")
    print(f"⏳ 等待 Hermes 回复 (超时 {timeout}s)...")
    
    # 轮询等待回复
    start = time.time()
    while time.time() - start < timeout:
        time.sleep(3)
        replies = glob.glob(os.path.join(FROM_HERMES, "*.msg"))
        if replies:
            for r in sorted(replies):
                try:
                    with open(r, encoding="utf-8") as f:
                        reply = json.load(f)
                    reply_text = reply.get("message", "")
                    reply_time = reply.get("timestamp", "")
                    
                    # 归档
                    os.rename(r, os.path.join(ARCHIVE, os.path.basename(r)))
                    
                    print(f"📥 收到回复 [{reply_time}]:")
                    print(reply_text)
                    return reply_text
                except Exception as e:
                    print(f"⚠️ 读取回复失败: {e}")
    
    print(f"⏰ 超时 {timeout}s，未收到回复")
    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 hermes-relay-v2.py \"消息内容\" [超时秒数]")
        sys.exit(1)
    
    message = sys.argv[1]
    timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    
    result = send_to_hermes(message, timeout)
    if result:
        print(f"\n✅ 中继成功")
    else:
        print(f"\n❌ 中继失败")
