#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络注册监控脚本 V4.0
定期检查新注册的小龙虾并生成报告

用法:
    python3 monitor_registrations.py
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List

# 添加父目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class RegistrationMonitor:
    """注册监控器"""

    def __init__(self, data_dir: str = "/shared/lobster-network-data"):
        self.data_dir = data_dir
        self.config_dir = os.path.join(data_dir, "config")
        self.last_check_file = os.path.join(data_dir, "monitor_state.json")
        self.last_check = self.load_last_check()

    def load_last_check(self) -> Dict:
        """加载上次检查状态"""
        if os.path.exists(self.last_check_file):
            with open(self.last_check_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "last_check": datetime.now().isoformat(),
            "known_nodes": [],
            "new_nodes": [],
        }

    def save_last_check(self):
        """保存检查状态"""
        with open(self.last_check_file, 'w', encoding='utf-8') as f:
            json.dump(self.last_check, f, ensure_ascii=False, indent=2)

    def check_new_registrations(self) -> List[Dict]:
        """检查新注册的小龙虾"""
        new_nodes = []

        # 检查配置目录
        if not os.path.exists(self.config_dir):
            return new_nodes

        for filename in os.listdir(self.config_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.config_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                node_id = config.get("node_id", "")
                if node_id and node_id not in self.last_check["known_nodes"]:
                    new_nodes.append(config)
                    self.last_check["known_nodes"].append(node_id)

        return new_nodes

    def generate_report(self, new_nodes: List[Dict]) -> Dict:
        """生成监控报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_nodes": len(self.last_check["known_nodes"]),
            "new_nodes": len(new_nodes),
            "new_nodes_list": new_nodes,
            "last_check": self.last_check["last_check"],
        }

        return report

    def send_notification(self, report: Dict):
        """发送通知"""
        if report["new_nodes"] == 0:
            print("✅ 无新注册")
            return

        # 打印报告
        print("=" * 40)
        print("🦞 小龙虾网络注册监控报告")
        print("=" * 40)
        print(f"时间: {report['timestamp']}")
        print(f"总节点数: {report['total_nodes']}")
        print(f"新注册: {report['new_nodes']}")
        print()

        for node in report["new_nodes_list"]:
            print(f"🆕 {node.get('name', 'unknown')}")
            print(f"   ID: {node.get('node_id', 'unknown')}")
            print(f"   类型: {node.get('type', 'unknown')}")
            print(f"   视角: {node.get('perspective', 'unknown')}")
            print(f"   知识: {node.get('knowledge_base', 'unknown')}")
            print(f"   注册于: {node.get('registered_at', 'unknown')}")
            print()

        print("=" * 40)

    def run(self):
        """运行监控"""
        print(f"[{datetime.now().isoformat()}] 开始检查注册...")

        # 检查新注册
        new_nodes = self.check_new_registrations()

        # 生成报告
        report = self.generate_report(new_nodes)

        # 发送通知
        self.send_notification(report)

        # 保存状态
        self.last_check["last_check"] = datetime.now().isoformat()
        self.save_last_check()

        return report


def main():
    """主函数"""
    monitor = RegistrationMonitor()
    report = monitor.run()

    # 输出摘要
    print(f"\n监控完成: {report['new_nodes']} 个新注册")


if __name__ == "__main__":
    main()
