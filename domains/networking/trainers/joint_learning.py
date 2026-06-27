#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小陈和诸葛虾 - 计算机网络联合学习（持久化版本）
"""

import json
import os
from datetime import datetime

# === 学习进度文件 ===
PROGRESS_FILE = os.path.join(
    os.path.dirname(__file__), "state", "network_learning_progress.json"
)

# === 学习计划（硬件感知优化版） ===
LEARNING_PLAN = {
    "students": ["小陈", "诸葛虾", "诸葛马"],
    "course": "高级网络通信原理",
    "start_date": "2026-06-25",
    "hardware_constraints": {
        "memory_mb": 1800,
        "max_concurrent_learners": 2,  # 限制并发学习人数防OOM
        "heartbeat_interval": 60,      # 降低心跳频率省CPU
        "message_batch_size": 5,       # 批量处理消息减开销
    },
    "chapters": {
        "ch1": {
            "title": "第一章 绪论 - 网络技术演进",
            "type": "演进展示",
            "difficulty": "入门",
            "estimated_time": 30,
            "demo_url": "https://netanimat-etqrydu8.manus.space",
            "replay_url": "https://manus.im/share/eOYk8rGG3isVMtkWTzubEb?replay=1",
            "topics": ["传统网络", "SDN", "云计算", "AI云", "架构对比"]
        },
        "ch2_3": {
            "title": "第二、三章 交换机原理与STP算法",
            "type": "协议动画",
            "difficulty": "入门",
            "estimated_time": 45,
            "demo_url": "https://switchanim-vpufrziz.manus.space",
            "replay_url": "https://manus.im/share/3RvE1nL9y5G0BIt1tEoGww?replay=1",
            "topics": ["MAC地址学习", "数据帧转发", "STP根桥选举", "端口角色", "BPDU", "CLI配置"]
        },
        "ch4_5": {
            "title": "第四、五章 路由器原理与路由协议",
            "type": "协议动画",
            "difficulty": "初级",
            "estimated_time": 45,
            "demo_url": "待补充",
            "replay_url": "待补充",
            "topics": ["数据包转发", "静态路由", "动态路由", "OSPF", "路由表"]
        },
        "ch13": {
            "title": "第十三章 OpenFlow流表实战",
            "type": "交互实战",
            "difficulty": "中级",
            "estimated_time": 60,
            "demo_url": "https://openflowweb-3a49zyfd.manus.space",
            "replay_url": "https://manus.im/share/AKGUSJvLReB7vsdiTmKsu1?replay=1",
            "topics": ["流表结构", "Mininet环境", "ODL控制器", "本地流表配置", "远程流表配置", "2s4h拓扑"]
        },
        "ch14": {
            "title": "第十四章 VXLAN网络虚拟化",
            "type": "交互实战",
            "difficulty": "中级",
            "estimated_time": 60,
            "demo_url": "https://vxlananim-f9tuwrva.manus.space",
            "replay_url": "https://manus.im/share/cmmsMVoGdsOZcYUz0uIRKI?replay=1",
            "topics": ["VLAN局限", "VXLAN优势", "VTEP", "封装解封装", "MAC学习", "隧道传输"]
        },
        "ch15": {
            "title": "第十五章 OpenFlow计量表与组表",
            "type": "交互实战",
            "difficulty": "高级",
            "estimated_time": 75,
            "demo_url": "https://openflowdemo-2remyxaz.manus.space",
            "replay_url": "https://manus.im/share/w8MsNkXbY2UNRpgAoHYRhw?replay=1",
            "topics": ["Meter表", "Select组表", "Fast Failover", "负载均衡", "故障转移", "流量模拟"]
        },
        "ch16": {
            "title": "第十六章 云网一体化",
            "type": "配置实战",
            "difficulty": "高级",
            "estimated_time": 90,
            "demo_url": "https://cloudnetint-22vpubkm.manus.space",
            "replay_url": "https://manus.im/share/MsukIoiDbhkBjEw6ohl8GK?replay=1",
            "topics": ["OpenStack", "OpenDayLight", "REST API", "Neutron配置", "ODL配置", "数据一致性"]
        }
    }
}


class LearningManager:
    """学习管理器"""

    def __init__(self):
        self.progress = self._load_progress()

    def _load_progress(self):
        """加载进度"""
        if os.path.exists(PROGRESS_FILE):
            with open(PROGRESS_FILE, 'r') as f:
                return json.load(f)

        # 初始化进度
        progress = {
            "course": "高级网络通信原理",
            "start_date": "2026-06-25",
            "students": {
                "小陈": {
                    "type": "稳健型",
                    "completed_chapters": [],
                    "current_chapter": None,
                    "problems_solved": 0,
                    "problems_correct": 0,
                    "wrong_book": [],
                    "learning_log": []
                },
                "诸葛虾": {
                    "type": "加速型",
                    "completed_chapters": [],
                    "current_chapter": None,
                    "problems_solved": 0,
                    "problems_correct": 0,
                    "wrong_book": [],
                    "learning_log": []
                }
            }
        }
        return progress

    def _save_progress(self):
        """保存进度"""
        os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(self.progress, f, ensure_ascii=False, indent=2)

    def start_chapter(self, student, chapter_id):
        """开始学习章节"""
        if student not in self.progress["students"]:
            return {"error": f"学生 {student} 不存在"}
        if chapter_id not in LEARNING_PLAN["chapters"]:
            return {"error": f"章节 {chapter_id} 不存在"}

        self.progress["students"][student]["current_chapter"] = chapter_id
        self._save_progress()

        chapter = LEARNING_PLAN["chapters"][chapter_id]
        return {
            "status": "started",
            "student": student,
            "chapter": chapter_id,
            "title": chapter["title"],
            "type": chapter["type"],
            "difficulty": chapter["difficulty"],
            "estimated_time": f"{chapter['estimated_time']}分钟",
            "demo_url": chapter["demo_url"],
            "topics": chapter["topics"]
        }

    def complete_chapter(self, student, chapter_id, solved, correct):
        """完成章节学习"""
        if student not in self.progress["students"]:
            return {"error": f"学生 {student} 不存在"}

        p = self.progress["students"][student]

        if chapter_id not in p["completed_chapters"]:
            p["completed_chapters"].append(chapter_id)

        p["problems_solved"] += solved
        p["problems_correct"] += correct
        p["current_chapter"] = None

        # 记录学习日志
        p["learning_log"].append({
            "chapter": chapter_id,
            "date": datetime.now().isoformat(),
            "solved": solved,
            "correct": correct,
            "accuracy": f"{correct/max(solved,1)*100:.1f}%"
        })

        self._save_progress()

        accuracy = correct / max(solved, 1) * 100
        return {
            "status": "completed",
            "student": student,
            "chapter": chapter_id,
            "solved": solved,
            "correct": correct,
            "accuracy": f"{accuracy:.1f}%",
            "total_completed": len(p["completed_chapters"]),
            "total_chapters": 7
        }

    def get_progress(self, student=None):
        """获取学习进度"""
        if student:
            if student not in self.progress["students"]:
                return {"error": f"学生 {student} 不存在"}
            p = self.progress["students"][student]
            return {
                "student": student,
                "type": p["type"],
                "completed": len(p["completed_chapters"]),
                "total": 7,
                "progress_percent": f"{len(p['completed_chapters'])/7*100:.1f}%",
                "problems_solved": p["problems_solved"],
                "problems_correct": p["problems_correct"],
                "current_chapter": p["current_chapter"],
                "completed_chapters": p["completed_chapters"]
            }

        # 返回所有学生进度
        result = {}
        for s in self.progress["students"]:
            result[s] = self.get_progress(s)
        return result


def main():
    """演示学习流程"""
    manager = LearningManager()

    print("🦞 小陈 & 诸葛虾 - 计算机网络联合学习")
    print("=" * 50)

    # 开始第一章
    for student in ["小陈", "诸葛虾"]:
        result = manager.start_chapter(student, "ch1")
        print(f"\n📖 {result['student']} 开始学习: {result['title']}")
        print(f"   类型: {result['type']} | 难度: {result['difficulty']}")
        print(f"   演示: {result['demo_url']}")

    # 模拟完成学习
    for student, correct in [("小陈", 4), ("诸葛虾", 5)]:
        result = manager.complete_chapter(student, "ch1", 5, correct)
        print(f"\n✅ {result['student']} 完成: {result['chapter']}")
        print(f"   做题: {result['solved']}题 | 正确: {result['correct']}题 | 准确率: {result['accuracy']}")

    # 查看进度
    print("\n📊 学习进度:")
    for student in ["小陈", "诸葛虾"]:
        p = manager.get_progress(student)
        print(f"\n  {student} ({p['type']}):")
        print(f"    完成: {p['completed']}/{p['total']} ({p['progress_percent']})")
        print(f"    做题: {p['problems_solved']}题 | 正确: {p['problems_correct']}题")
        print(f"    已完成章节: {', '.join(p['completed_chapters']) or '无'}")


if __name__ == "__main__":
    main()
