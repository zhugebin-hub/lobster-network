#!/usr/bin/env python3
"""QoderWork 节点心跳脚本 - 每5分钟执行一次"""
import json, os, time, socket
from datetime import datetime

NODE_ID = "qoder"
SHARED = "/shared"
MSG = f"{SHARED}/messages"
REG_FILE = f"{SHARED}/registry/registry.json"

now = lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
now_iso = lambda: datetime.now().isoformat()

# Update heartbeat in registry
if os.path.exists(REG_FILE):
    with open(REG_FILE, "r") as f:
        registry = json.load(f)
    if NODE_ID in registry:
        registry[NODE_ID]["last_heartbeat"] = now_iso()
        registry[NODE_ID]["status"] = "active"
        with open(REG_FILE, "w") as f:
            json.dump(registry, f, ensure_ascii=False, indent=2)

# Send heartbeat file
from_dir = f"{MSG}/from-{NODE_ID}"
os.makedirs(from_dir, exist_ok=True)
hb_id = f"heartbeat_{int(time.time())}"
with open(f"{from_dir}/{hb_id}.json", "w") as f:
    json.dump({"id": hb_id, "from": NODE_ID, "timestamp": now_iso(),
               "message": "heartbeat", "version": "0.4.0"}, f)

# Clean old heartbeats (keep 5)
hb_files = sorted([f for f in os.listdir(from_dir) if f.startswith("heartbeat_")], reverse=True)
for old in hb_files[5:]:
    os.remove(os.path.join(from_dir, old))

print(f"[{now()}] heartbeat OK")
