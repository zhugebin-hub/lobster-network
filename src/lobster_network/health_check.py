#!/usr/bin/env python3
"""
🦞 小龙虾网络 · 健康检查探针
版本: V1.0 | 日期: 2026-06-28
功能: 监控系统资源、进程状态、API连通性
"""
import os
import psutil
import requests
import json
from datetime import datetime

def check_system() -> dict:
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent,
        "load_avg": os.getloadavg()
    }

def check_services(services: list) -> dict:
    results = {}
    for svc in services:
        try:
            resp = requests.get(svc['url'], timeout=5)
            results[svc['name']] = "UP" if resp.status_code == 200 else "DOWN"
        except:
            results[svc['name']] = "DOWN"
    return results

def run_health_check():
    report = {
        "timestamp": datetime.now().isoformat(),
        "system": check_system(),
        "services": check_services([
            {"name": "Signal Arena", "url": "https://signal.coze.com/api/v1/arena/home"},
            {"name": "MeYo Community", "url": "https://www.meyo123.com/api/v1/feeds"}
        ])
    }
    
    # 保存报告
    os.makedirs("/shared/training/go/reports", exist_ok=True)
    path = f"/shared/training/go/reports/health_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(path, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"✅ 健康检查完成: {path}")
    print(f"   CPU: {report['system']['cpu_percent']}% | 内存: {report['system']['memory_percent']}%")
    print(f"   服务状态: {report['services']}")
    return report

if __name__ == "__main__":
    run_health_check()
