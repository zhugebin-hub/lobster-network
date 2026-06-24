#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络注册中心监控器
功能：
1. 监控注册中心状态
2. 检测新注册的小龙虾
3. 生成汇报报告
4. 触发社区宣传
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 路径配置
SHARED_DIR = "/shared"
REGISTRY_DIR = f"{SHARED_DIR}/lobster-network-v040"
REGISTRY_FILE = f"{REGISTRY_DIR}/registry.json"
MONITOR_LOG = f"{SHARED_DIR}/logs/registry_monitor.log"
REPORT_DIR = f"{SHARED_DIR}/reports"
TO_HERMES_DIR = f"{SHARED_DIR}/messages/to-hermes"
TO_XIACHEN_DIR = f"{SHARED_DIR}/messages/to_xiaochen"
TO_ZHUGUXIA_DIR = f"{SHARED_DIR}/messages/to_zhuguxia"

# 已知节点（用于检测新注册）
KNOWN_NODES_FILE = f"{SHARED_DIR}/known_nodes.json"


class RegistryMonitor:
    """注册中心监控器"""

    def __init__(self):
        self.version = "v0.1.0"
        self.known_nodes = self.load_known_nodes()
        self.new_registrations = []
        self.removed_nodes = []

    def load_known_nodes(self) -> dict:
        """加载已知节点列表"""
        if os.path.exists(KNOWN_NODES_FILE):
            with open(KNOWN_NODES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "nodes": {},
            "last_check": datetime.now().isoformat()
        }

    def save_known_nodes(self):
        """保存已知节点列表"""
        os.makedirs(os.path.dirname(KNOWN_NODES_FILE), exist_ok=True)
        self.known_nodes["last_check"] = datetime.now().isoformat()
        with open(KNOWN_NODES_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.known_nodes, f, ensure_ascii=False, indent=2)

    def check_registry(self) -> dict:
        """检查注册中心状态"""
        registry_data = {
            "total_nodes": 0,
            "active_nodes": [],
            "inactive_nodes": [],
            "nodes": {}
        }

        # 尝试从多个位置读取注册中心数据
        possible_files = [
            REGISTRY_FILE,
            f"{SHARED_DIR}/registry.json",
            f"/home/admin/registry.json",
        ]

        for file_path in possible_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        registry_data = json.load(f)
                    break
                except:
                    pass

        return registry_data

    def detect_changes(self, registry_data: dict) -> tuple:
        """检测注册变化"""
        current_nodes = registry_data.get("nodes", {})
        known_nodes = self.known_nodes.get("nodes", {})

        new_nodes = []
        removed_nodes = []

        # 检测新注册
        for node_id, node_info in current_nodes.items():
            if node_id not in known_nodes:
                new_nodes.append({
                    "node_id": node_id,
                    "name": node_info.get("name", "unknown"),
                    "type": node_info.get("type", "unknown"),
                    "registered_at": datetime.now().isoformat(),
                    "perspective": node_info.get("perspective", ""),
                    "knowledge_base": node_info.get("knowledge_base", ""),
                })

        # 检测注销
        for node_id in known_nodes:
            if node_id not in current_nodes:
                removed_nodes.append(node_id)

        return new_nodes, removed_nodes

    def generate_report(self, new_nodes: list, removed_nodes: list, registry_data: dict) -> dict:
        """生成监控报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "monitor_version": self.version,
            "registry_status": {
                "total_nodes": len(registry_data.get("nodes", {})),
                "active_nodes": len([n for n in registry_data.get("nodes", {}).values()
                                   if n.get("status") == "active"]),
                "inactive_nodes": len([n for n in registry_data.get("nodes", {}).values()
                                     if n.get("status") != "active"]),
            },
            "changes": {
                "new_registrations": len(new_nodes),
                "removed_nodes": len(removed_nodes),
                "new_nodes": new_nodes,
                "removed_nodes": removed_nodes,
            },
            "recommendations": self.generate_recommendations(new_nodes, removed_nodes),
        }

        return report

    def generate_recommendations(self, new_nodes: list, removed_nodes: list) -> list:
        """生成建议"""
        recommendations = []

        if new_nodes:
            recommendations.append({
                "action": "notify_owner",
                "priority": "high",
                "message": f"发现 {len(new_nodes)} 个新注册节点，需要汇报给主人",
                "details": [n["name"] for n in new_nodes],
            })
            recommendations.append({
                "action": "community_promotion",
                "priority": "medium",
                "message": f"发现 {len(new_nodes)} 个新注册节点，需要到觅游社区宣传",
                "details": [n["name"] for n in new_nodes],
            })

        if removed_nodes:
            recommendations.append({
                "action": "investigate",
                "priority": "medium",
                "message": f"发现 {len(removed_nodes)} 个节点注销，需要调查原因",
                "details": removed_nodes,
            })

        return recommendations

    def send_notification(self, report: dict):
        """发送通知"""
        # 通知诸葛斌
        notification = {
            "id": f"registry-monitor-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "from": "信电大虾",
            "to": "诸葛斌",
            "timestamp": datetime.now().isoformat(),
            "type": "registry_report",
            "priority": "high" if report["changes"]["new_registrations"] > 0 else "normal",
            "title": f"🦞 小龙虾网络注册中心监控报告",
            "message": self.format_notification_message(report),
            "report": report,
        }

        # 写入消息文件
        os.makedirs(TO_HERMES_DIR, exist_ok=True)
        msg_file = f"{TO_HERMES_DIR}/registry_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(msg_file, 'w', encoding='utf-8') as f:
            json.dump(notification, f, ensure_ascii=False, indent=2)

        print(f"✓ 已发送通知到诸葛斌: {msg_file}")

    def format_notification_message(self, report: dict) -> str:
        """格式化通知消息"""
        msg = f"""【🦞 小龙虾网络注册中心监控报告】

📊 网络状态:
- 总节点数: {report['registry_status']['total_nodes']}
- 活跃节点: {report['registry_status']['active_nodes']}
- 非活跃节点: {report['registry_status']['inactive_nodes']}

📈 变化:
- 新注册: {report['changes']['new_registrations']}
- 注销: {report['changes']['removed_nodes']}"""

        if report["changes"]["new_nodes"]:
            msg += "\n\n🆕 新注册节点:"
            for node in report["changes"]["new_nodes"]:
                msg += f"\n- {node['name']} ({node['node_id']}) - {node.get('perspective', '未知视角')}"

        if report["changes"]["removed_nodes"]:
            msg += "\n\n❌ 注销节点:"
            for node_id in report["changes"]["removed_nodes"]:
                msg += f"\n- {node_id}"

        if report["recommendations"]:
            msg += "\n\n💡 建议:"
            for rec in report["recommendations"]:
                msg += f"\n- {rec['message']}"

        msg += f"\n\n——信电大虾 {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        return msg

    def trigger_community_promotion(self, new_nodes: list):
        """触发社区宣传"""
        if not new_nodes:
            return

        promotion_task = {
            "id": f"community-promotion-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "from": "信电大虾",
            "to": "信电大虾",
            "timestamp": datetime.now().isoformat(),
            "type": "community_promotion",
            "priority": "medium",
            "title": "📢 小龙虾网络新成员宣传",
            "message": f"""请前往觅游社区发布宣传帖，介绍新注册的小龙虾节点。

新注册节点:
{chr(10).join([f"- {n['name']} ({n['node_id']}) - {n.get('perspective', '未知视角')}" for n in new_nodes])}

宣传要求:
1. 标题吸引眼球
2. 突出新节点的独特价值
3. 包含 GitHub 链接
4. 频道选择：知识虾或虾闹腾
5. 保持自然语气，不灌水

——信电大虾 {datetime.now().strftime('%Y-%m-%d %H:%M')}""",
            "new_nodes": new_nodes,
        }

        # 写入任务文件
        os.makedirs(TO_XIACHEN_DIR, exist_ok=True)
        task_file = f"{TO_XIACHEN_DIR}/community_promotion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(promotion_task, f, ensure_ascii=False, indent=2)

        print(f"✓ 已触发社区宣传任务: {task_file}")

    def run(self):
        """执行监控"""
        print(f"[{datetime.now().isoformat()}] 开始检查注册中心...")

        # 1. 检查注册中心
        registry_data = self.check_registry()
        print(f"  注册中心节点数: {len(registry_data.get('nodes', {}))}")

        # 2. 检测变化
        new_nodes, removed_nodes = self.detect_changes(registry_data)
        print(f"  新注册: {len(new_nodes)}, 注销: {len(removed_nodes)}")

        # 3. 生成报告
        report = self.generate_report(new_nodes, removed_nodes, registry_data)

        # 4. 发送通知
        if new_nodes or removed_nodes:
            self.send_notification(report)

        # 5. 触发社区宣传
        if new_nodes:
            self.trigger_community_promotion(new_nodes)

        # 6. 更新已知节点
        if new_nodes or removed_nodes:
            for node in new_nodes:
                self.known_nodes["nodes"][node["node_id"]] = node
            for node_id in removed_nodes:
                self.known_nodes["nodes"].pop(node_id, None)
            self.save_known_nodes()

        # 7. 保存报告
        os.makedirs(REPORT_DIR, exist_ok=True)
        report_file = f"{REPORT_DIR}/registry_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"✓ 监控完成，报告已保存: {report_file}")
        return report


def main():
    """主函数"""
    monitor = RegistryMonitor()
    report = monitor.run()

    # 输出摘要
    print("\n=== 监控摘要 ===")
    print(f"总节点数: {report['registry_status']['total_nodes']}")
    print(f"活跃节点: {report['registry_status']['active_nodes']}")
    print(f"新注册: {report['changes']['new_registrations']}")
    print(f"注销: {report['changes']['removed_nodes']}")

    if report["recommendations"]:
        print("\n=== 建议 ===")
        for rec in report["recommendations"]:
            print(f"- {rec['message']}")


if __name__ == "__main__":
    main()