#!/usr/bin/env python3
"""
小龙虾网络节点健康检查脚本

功能：
- 检查所有注册节点的状态
- 验证心跳超时
- 生成健康报告
- 自动清理超时节点

使用方法：
    python3 scripts/check_node_health.py [--verbose] [--cleanup]
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# ========== 配置 ==========

REGISTRY_DIR = Path(__file__).parent.parent / "registry" / "nodes"
HEARTBEAT_TIMEOUT = 300  # 5 分钟超时（秒）
VERBOSE = False
AUTO_CLEANUP = False

# ========== 工具函数 ==========

def parse_args():
    """解析命令行参数"""
    global VERBOSE, AUTO_CLEANUP
    for arg in sys.argv[1:]:
        if arg == "--verbose":
            VERBOSE = True
        elif arg == "--cleanup":
            AUTO_CLEANUP = True

def load_node(node_id: str) -> dict:
    """加载节点注册信息"""
    node_file = REGISTRY_DIR / f"{node_id}.json"
    if not node_file.exists():
        return None
    with open(node_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def parse_time(time_str: str) -> datetime:
    """解析时间字符串（兼容 Python 3.6）"""
    try:
        return datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%f%z")
    except ValueError:
        pass
    try:
        return datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S%z")
    except ValueError:
        pass
    try:
        return datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError:
        pass
    try:
        return datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        pass
    return None

def check_node_health(node_id: str) -> dict:
    """检查单个节点健康状态"""
    node = load_node(node_id)
    if not node:
        return {
            "node_id": node_id,
            "status": "not_found",
            "healthy": False,
            "message": "节点注册文件不存在"
        }
    
    # 检查状态
    status = node.get("status", "unknown")
    
    # 检查心跳
    last_heartbeat = node.get("last_heartbeat")
    if last_heartbeat:
        heartbeat_time = parse_time(last_heartbeat)
        if heartbeat_time:
            now = datetime.now()
            if heartbeat_time.tzinfo:
                now = now.replace(tzinfo=heartbeat_time.tzinfo)
            time_diff = (now - heartbeat_time).total_seconds()
            
            if time_diff > HEARTBEAT_TIMEOUT:
                return {
                    "node_id": node_id,
                    "status": status,
                    "healthy": False,
                    "message": f"心跳超时（{int(time_diff)}秒前）",
                    "last_heartbeat": last_heartbeat,
                    "time_diff": time_diff
                }
            else:
                return {
                    "node_id": node_id,
                    "status": status,
                    "healthy": True,
                    "message": f"正常（{int(time_diff)}秒前心跳）",
                    "last_heartbeat": last_heartbeat,
                    "time_diff": time_diff
                }
        else:
            return {
                "node_id": node_id,
                "status": status,
                "healthy": False,
                "message": "心跳时间格式错误"
            }
    else:
        return {
            "node_id": node_id,
            "status": status,
            "healthy": False,
            "message": "无心跳记录"
        }

def cleanup_offline_nodes(healthy_nodes: list, unhealthy_nodes: list):
    """清理离线节点"""
    if not AUTO_CLEANUP:
        return
    
    print("\n🧹 清理离线节点...")
    for node in unhealthy_nodes:
        if node["status"] == "not_found":
            continue
        
        node_file = REGISTRY_DIR / f"{node['node_id']}.json"
        if node_file.exists():
            # 备份
            backup_file = node_file.with_suffix('.json.bak')
            node_file.rename(backup_file)
            print(f"  ✅ 已备份 {node['node_id']} -> {backup_file.name}")
            
            # 更新状态为离线
            node_data = load_node(node['node_id'])
            if node_data:
                node_data["status"] = "offline"
                node_data["last_status_change"] = datetime.now().isoformat()
                with open(node_file, 'w', encoding='utf-8') as f:
                    json.dump(node_data, f, ensure_ascii=False, indent=2)
                print(f"  ✅ 已标记 {node['node_id']} 为离线")

def generate_report(healthy_nodes: list, unhealthy_nodes: list):
    """生成健康报告"""
    print("\n" + "="*60)
    print("🦞 小龙虾网络健康报告")
    print("="*60)
    print(f"检查时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"总节点数：{len(healthy_nodes) + len(unhealthy_nodes)}")
    print(f"健康节点：{len(healthy_nodes)}")
    print(f"不健康节点：{len(unhealthy_nodes)}")
    print()
    
    if healthy_nodes:
        print("✅ 健康节点：")
        for node in healthy_nodes:
            print(f"  • {node['node_id']} - {node['message']}")
        print()
    
    if unhealthy_nodes:
        print("❌ 不健康节点：")
        for node in unhealthy_nodes:
            print(f"  • {node['node_id']} - {node['message']}")
        print()
    
    # 网络连通率
    total = len(healthy_nodes) + len(unhealthy_nodes)
    if total > 0:
        connectivity = len(healthy_nodes) / total * 100
        print(f"网络连通率：{connectivity:.1f}%")
    print("="*60)

def main():
    """主函数"""
    parse_args()
    
    # 检查注册目录
    if not REGISTRY_DIR.exists():
        print(f"❌ 注册目录不存在：{REGISTRY_DIR}")
        sys.exit(1)
    
    # 获取所有节点
    node_files = list(REGISTRY_DIR.glob("*.json"))
    node_ids = [f.stem for f in node_files]
    
    if not node_ids:
        print("⚠️  没有注册节点")
        sys.exit(0)
    
    print(f"🔍 检查 {len(node_ids)} 个节点...")
    
    # 检查每个节点
    healthy_nodes = []
    unhealthy_nodes = []
    
    for node_id in node_ids:
        result = check_node_health(node_id)
        if result["healthy"]:
            healthy_nodes.append(result)
        else:
            unhealthy_nodes.append(result)
        
        if VERBOSE:
            print(f"  {node_id}: {result['message']}")
    
    # 清理离线节点
    cleanup_offline_nodes(healthy_nodes, unhealthy_nodes)
    
    # 生成报告
    generate_report(healthy_nodes, unhealthy_nodes)
    
    # 返回状态码
    if unhealthy_nodes:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
