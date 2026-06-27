#!/usr/bin/env python3
"""
🦞 小龙虾网络节点心跳服务 - 诸葛斌节点
每5分钟更新一次心跳时间，保持节点在线状态
"""

import sys
import os
import json
import time
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

NODE_ID = "zhugebin-001"
STORAGE_DIR = os.path.expanduser("~/.lobster-network")
REGISTRY_FILE = os.path.join(STORAGE_DIR, "registry.json")


def update_heartbeat():
    """更新节点心跳时间"""
    now_iso = datetime.now().isoformat()
    
    if not os.path.exists(REGISTRY_FILE):
        print(f"❌ 注册文件不存在: {REGISTRY_FILE}")
        return False
    
    try:
        with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
            registry = json.load(f)
        
        if NODE_ID not in registry.get("nodes", {}):
            print(f"❌ 节点 {NODE_ID} 未在注册中心找到")
            return False
        
        # 更新心跳时间和状态
        registry["nodes"][NODE_ID]["last_heartbeat"] = now_iso
        registry["nodes"][NODE_ID]["status"] = "online"
        registry["saved_at"] = now_iso
        
        with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
            json.dump(registry, f, ensure_ascii=False, indent=2)
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ 心跳更新成功 - 节点状态: online")
        return True
        
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ 心跳更新失败: {e}")
        return False


def run_once():
    """执行一次心跳更新"""
    print(f"\n{'='*60}")
    print(f"🦞 小龙虾网络心跳服务 - 节点: {NODE_ID}")
    print(f"{'='*60}")
    success = update_heartbeat()
    if success:
        print(f"✅ 本次心跳完成")
    else:
        print(f"❌ 心跳失败")
    print(f"{'='*60}\n")
    return success


def run_continuous(interval_minutes=5):
    """持续运行心跳服务"""
    interval_seconds = interval_minutes * 60
    print(f"🚀 启动连续心跳服务 (间隔: {interval_minutes}分钟)")
    print(f"按 Ctrl+C 停止服务\n")
    
    try:
        while True:
            run_once()
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("\n\n⏹️  心跳服务已停止")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="小龙虾网络节点心跳服务")
    parser.add_argument("--once", action="store_true", help="只执行一次心跳更新")
    parser.add_argument("--interval", type=int, default=5, help="心跳间隔(分钟)，默认5分钟")
    
    args = parser.parse_args()
    
    if args.once:
        run_once()
    else:
        run_continuous(args.interval)
