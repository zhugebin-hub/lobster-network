#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络通信原理 - 仿真平台管理器
管理Manus演示链接和仿真功能
"""

import json
import os
from datetime import datetime

# === 仿真平台配置 ===
SIMULATION_PLATFORMS = {
    "ch1": {
        "title": "第一章 绪论 - 网络技术演进仿真",
        "demo_url": "https://netanimat-etqrydu8.manus.space",
        "replay_url": "https://manus.im/share/eOYk8rGG3isVMtkWTzubEb?replay=1",
        "features": [
            "四阶段演进动画",
            "交互式探索",
            "架构对比表格"
        ],
        "status": "active"
    },
    "ch2_3": {
        "title": "第二、三章 交换机原理与STP算法仿真",
        "demo_url": "https://switchanim-vpufrziz.manus.space",
        "replay_url": "https://manus.im/share/3RvE1nL9y5G0BIt1tEoGww?replay=1",
        "features": [
            "MAC学习动画",
            "STP选举动画",
            "CLI配置模拟"
        ],
        "status": "active"
    },
    "ch13": {
        "title": "第十三章 OpenFlow流表实战仿真",
        "demo_url": "https://openflowweb-3a49zyfd.manus.space",
        "replay_url": "https://manus.im/share/AKGUSJvLReB7vsdiTmKsu1?replay=1",
        "features": [
            "Mininet环境搭建",
            "本地流表配置",
            "远程流表配置"
        ],
        "status": "active"
    },
    "ch14": {
        "title": "第十四章 VXLAN网络虚拟化仿真",
        "demo_url": "https://vxlananim-f9tuwrva.manus.space",
        "replay_url": "https://manus.im/share/cmmsMVoGdsOZcYUz0uIRKI?replay=1",
        "features": [
            "VXLAN封装动画",
            "MAC地址学习",
            "隧道传输模拟"
        ],
        "status": "active"
    },
    "ch15": {
        "title": "第十五章 OpenFlow计量表与组表仿真",
        "demo_url": "https://openflowdemo-2remyxaz.manus.space",
        "replay_url": "https://manus.im/share/w8MsNkXbY2UNRpgAoHYRhw?replay=1",
        "features": [
            "Meter表限速",
            "Select组表负载均衡",
            "Fast Failover故障转移"
        ],
        "status": "active"
    },
    "ch16": {
        "title": "第十六章 云网一体化仿真",
        "demo_url": "https://cloudnetint-22vpubkm.manus.space",
        "replay_url": "https://manus.im/share/MsukIoiDbhkBjEw6ohl8GK?replay=1",
        "features": [
            "OpenStack配置",
            "ODL配置",
            "数据一致性验证"
        ],
        "status": "active"
    }
}


class SimulationManager:
    """仿真平台管理器"""

    def __init__(self):
        self.platforms = SIMULATION_PLATFORMS

    def list_platforms(self):
        """列出所有仿真平台"""
        result = []
        for key, platform in self.platforms.items():
            result.append({
                "id": key,
                "title": platform["title"],
                "demo_url": platform["demo_url"],
                "replay_url": platform["replay_url"],
                "features": platform["features"],
                "status": platform["status"]
            })
        return result

    def get_platform(self, platform_id):
        """获取单个平台详情"""
        if platform_id not in self.platforms:
            return {"error": f"平台 {platform_id} 不存在"}
        return self.platforms[platform_id]

    def open_platform(self, platform_id):
        """打开仿真平台"""
        if platform_id not in self.platforms:
            return {"error": f"平台 {platform_id} 不存在"}
        platform = self.platforms[platform_id]
        return {
            "status": "opened",
            "platform": platform["title"],
            "demo_url": platform["demo_url"],
            "replay_url": platform["replay_url"],
            "features": platform["features"]
        }


def main():
    """演示"""
    manager = SimulationManager()

    print("🖥️ 网络通信原理 - 仿真平台")
    print("=" * 50)

    platforms = manager.list_platforms()
    for p in platforms:
        print(f"\n📌 [{p['id']}] {p['title']}")
        print(f"   演示: {p['demo_url']}")
        print(f"   回放: {p['replay_url']}")
        print(f"   功能: {', '.join(p['features'])}")
        print(f"   状态: {p['status']}")


if __name__ == "__main__":
    main()
