#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级网络通信原理 - 学习场景管理器
管理16章交互式学习场景的创建、加载和导航
"""

import json
import os
from datetime import datetime
from pathlib import Path


# === Manus演示链接 ===
MANUS_SCENARIOS = {
    "ch1": {
        "title": "第一章 绪论 - 网络技术演进",
        "description": "传统网络 → SDN → 云计算 → AI云 四阶段演进对比",
        "type": "演进展示",
        "demo_url": "https://netanimat-etqrydu8.manus.space",
        "replay_url": "https://manus.im/share/eOYk8rGG3isVMtkWTzubEb?replay=1",
        "topics": ["传统网络", "软件定义网络(SDN)", "云计算", "AI云", "架构对比"],
        "difficulty": "入门",
        "estimated_time": 30
    },
    "ch2_3": {
        "title": "第二、三章 交换机原理与STP算法",
        "description": "MAC地址学习、数据帧转发、STP根桥选举与环路防止",
        "type": "协议动画",
        "demo_url": "https://switchanim-vpufrziz.manus.space",
        "replay_url": "https://manus.im/share/3RvE1nL9y5G0BIt1tEoGww?replay=1",
        "topics": ["MAC地址学习", "数据帧转发与过滤", "STP根桥选举", "端口角色分配", "BPDU交换", "CLI配置"],
        "difficulty": "入门",
        "estimated_time": 45
    },
    "ch4_5": {
        "title": "第四、五章 路由器原理与路由协议",
        "description": "数据包转发、静态路由配置、OSPF动态路由",
        "type": "协议动画",
        "demo_url": "待补充",
        "replay_url": "待补充",
        "topics": ["数据包转发", "静态路由", "动态路由", "OSPF协议", "路由表"],
        "difficulty": "初级",
        "estimated_time": 45
    },
    "ch13": {
        "title": "第十三章 OpenFlow流表实战",
        "description": "Mininet+ODL环境搭建、2s4h拓扑、本地/远程流表配置",
        "type": "交互实战",
        "demo_url": "https://openflowweb-3a49zyfd.manus.space",
        "replay_url": "https://manus.im/share/AKGUSJvLReB7vsdiTmKsu1?replay=1",
        "topics": ["流表结构", "Mininet环境搭建", "ODL控制器", "2s4h拓扑创建", "本地流表配置", "远程流表配置"],
        "difficulty": "中级",
        "estimated_time": 60
    },
    "ch14": {
        "title": "第十四章 VXLAN网络虚拟化",
        "description": "VLAN局限、VXLAN封装、MAC地址学习机制",
        "type": "交互实战",
        "demo_url": "https://vxlananim-f9tuwrva.manus.space",
        "replay_url": "https://manus.im/share/cmmsMVoGdsOZcYUz0uIRKI?replay=1",
        "topics": ["VLAN vs VXLAN", "VTEP概念", "封装与解封装", "MAC地址学习", "隧道传输"],
        "difficulty": "中级",
        "estimated_time": 60
    },
    "ch15": {
        "title": "第十五章 OpenFlow计量表与组表",
        "description": "Meter表限速、Select组表负载均衡、Fast Failover故障转移",
        "type": "交互实战",
        "demo_url": "https://openflowdemo-2remyxaz.manus.space",
        "replay_url": "https://manus.im/share/w8MsNkXbY2UNRpgAoHYRhw?replay=1",
        "topics": ["Meter表", "Select组表", "Fast Failover", "负载均衡", "故障转移", "流量模拟"],
        "difficulty": "高级",
        "estimated_time": 75
    },
    "ch16": {
        "title": "第十六章 云网一体化",
        "description": "OpenStack+OpenDayLight对接、配置编辑器、验证方法",
        "type": "配置实战",
        "demo_url": "https://cloudnetint-22vpubkm.manus.space",
        "replay_url": "https://manus.im/share/MsukIoiDbhkBjEw6ohl8GK?replay=1",
        "topics": ["OpenStack", "OpenDayLight", "REST API对接", "Neutron配置", "ODL配置", "数据一致性"],
        "difficulty": "高级",
        "estimated_time": 90
    }
}


class SceneManager:
    """学习场景管理器"""

    def __init__(self):
        self.scenarios = MANUS_SCENARIOS
        self.state_file = os.path.join(
            os.path.dirname(__file__), "state", "learning_progress.json"
        )
        self.progress = self._load_progress()

    def _load_progress(self):
        """加载学习进度"""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {
            "completed_scenarios": [],
            "current_scenario": None,
            "started_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat()
        }

    def _save_progress(self):
        """保存进度"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        self.progress["last_activity"] = datetime.now().isoformat()
        with open(self.state_file, 'w') as f:
            json.dump(self.progress, f, ensure_ascii=False, indent=2)

    def list_scenarios(self):
        """列出所有场景"""
        result = []
        for key, scene in self.scenarios.items():
            completed = key in self.progress["completed_scenarios"]
            result.append({
                "id": key,
                "title": scene["title"],
                "type": scene["type"],
                "difficulty": scene["difficulty"],
                "estimated_time": f"{scene['estimated_time']}分钟",
                "topics": len(scene["topics"]),
                "completed": completed,
                "demo_url": scene["demo_url"]
            })
        return result

    def get_scenario(self, scenario_id):
        """获取单个场景详情"""
        if scenario_id not in self.scenarios:
            return {"error": f"场景 {scenario_id} 不存在"}

        scene = self.scenarios[scenario_id]
        return {
            **scene,
            "completed": scenario_id in self.progress["completed_scenarios"],
            "topic_list": scene["topics"]
        }

    def start_scenario(self, scenario_id):
        """开始学习场景"""
        if scenario_id not in self.scenarios:
            return {"error": f"场景 {scenario_id} 不存在"}

        self.progress["current_scenario"] = scenario_id
        self._save_progress()

        scene = self.scenarios[scenario_id]
        return {
            "status": "started",
            "scenario": scene["title"],
            "demo_url": scene["demo_url"],
            "replay_url": scene["replay_url"],
            "topics": scene["topics"],
            "estimated_time": f"{scene['estimated_time']}分钟"
        }

    def complete_scenario(self, scenario_id):
        """完成场景学习"""
        if scenario_id not in self.scenarios:
            return {"error": f"场景 {scenario_id} 不存在"}

        if scenario_id not in self.progress["completed_scenarios"]:
            self.progress["completed_scenarios"].append(scenario_id)

        self._save_progress()
        return {
            "status": "completed",
            "scenario": self.scenarios[scenario_id]["title"],
            "total_completed": len(self.progress["completed_scenarios"]),
            "total_scenarios": len(self.scenarios)
        }

    def get_progress(self):
        """获取学习进度"""
        completed = len(self.progress["completed_scenarios"])
        total = len(self.scenarios)
        return {
            "completed": completed,
            "total": total,
            "progress_percent": f"{completed/total*100:.1f}%",
            "completed_scenarios": self.progress["completed_scenarios"],
            "current_scenario": self.progress.get("current_scenario"),
            "started_at": self.progress["started_at"]
        }


def main():
    """演示"""
    manager = SceneManager()

    print("📚 高级网络通信原理 - 学习场景")
    print("=" * 50)

    scenarios = manager.list_scenarios()
    for s in scenarios:
        status = "✅" if s["completed"] else "⬜"
        print(f"  {status} [{s['id']}] {s['title']}")
        print(f"      类型: {s['type']} | 难度: {s['difficulty']} | 时长: {s['estimated_time']}")
        print(f"      主题: {s['topics']}个 | 演示: {s['demo_url']}")
        print()

    print(f"📊 进度: {manager.get_progress()['progress_percent']}")


if __name__ == "__main__":
    main()
