#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级网络通信原理 - 题库生成器
基于Manus案例集16章内容
"""

import json
import os
from datetime import datetime

# === 课程大纲 ===
COURSE_OUTLINE = {
    "phase1": {
        "name": "基础篇",
        "chapters": {
            "ch1": {
                "title": "绪论",
                "topics": ["网络演进4阶段", "传统网络", "SDN", "云计算", "AI云", "架构对比"]
            },
            "ch2_3": {
                "title": "交换机原理与STP算法",
                "topics": ["MAC地址学习", "数据帧转发", "STP根桥选举", "端口角色", "BPDU", "环路防止"]
            },
            "ch4_5": {
                "title": "路由器原理与路由协议",
                "topics": ["数据包转发", "静态路由", "动态路由", "OSPF", "路由表"]
            }
        },
        "total_problems": 90
    },
    "phase2": {
        "name": "SDN篇",
        "chapters": {
            "ch13": {
                "title": "OpenFlow流表实战",
                "topics": ["流表结构", "Mininet环境", "ODL控制器", "本地流表配置", "远程流表配置", "2s4h拓扑"]
            },
            "ch14": {
                "title": "VXLAN网络虚拟化",
                "topics": ["VLAN局限", "VXLAN优势", "VTEP", "封装解封装", "MAC学习", "隧道传输"]
            },
            "ch15": {
                "title": "OpenFlow计量表与组表",
                "topics": ["Meter表", "Select组表", "Fast Failover", "负载均衡", "故障转移", "流量模拟"]
            }
        },
        "total_problems": 108
    },
    "phase3": {
        "name": "融合篇",
        "chapters": {
            "ch16": {
                "title": "云网一体化",
                "topics": ["OpenStack", "OpenDayLight", "REST API", "Neutron配置", "ODL配置", "数据一致性"]
            }
        },
        "total_problems": 36
    }
}

# === Manus演示链接 ===
MANUS_LINKS = {
    "ch1": {
        "demo": "https://netanimat-etqrydu8.manus.space",
        "replay": "https://manus.im/share/eOYk8rGG3isVMtkWTzubEb?replay=1"
    },
    "ch2_3": {
        "demo": "https://switchanim-vpufrziz.manus.space",
        "replay": "https://manus.im/share/3RvE1nL9y5G0BIt1tEoGww?replay=1"
    },
    "ch13": {
        "demo": "https://openflowweb-3a49zyfd.manus.space",
        "replay": "https://manus.im/share/AKGUSJvLReB7vsdiTmKsu1?replay=1"
    },
    "ch14": {
        "demo": "https://vxlananim-f9tuwrva.manus.space",
        "replay": "https://manus.im/share/cmmsMVoGdsOZcYUz0uIRKI?replay=1"
    },
    "ch15": {
        "demo": "https://openflowdemo-2remyxaz.manus.space",
        "replay": "https://manus.im/share/w8MsNkXbY2UNRpgAoHYRhw?replay=1"
    },
    "ch16": {
        "demo": "https://cloudnetint-22vpubkm.manus.space",
        "replay": "https://manus.im/share/MsukIoiDbhkBjEw6ohl8GK?replay=1"
    }
}

# === 题目模板 ===
PROBLEM_TEMPLATES = {
    "网络演进4阶段": [
        {"type": "选择", "difficulty": "入门", "template": "网络技术演进的四个阶段按顺序是{传统网络→SDN→云计算→AI云}"},
        {"type": "判断", "difficulty": "入门", "template": "AI云相比云计算具有更高的智能程度（对/错）"},
        {"type": "填空", "difficulty": "初级", "template": "SDN的核心思想是控制面与_面分离"},
    ],
    "MAC地址学习": [
        {"type": "选择", "difficulty": "入门", "template": "交换机学习MAC地址的方式是{查看数据帧源MAC}"},
        {"type": "判断", "difficulty": "入门", "template": "交换机通过查看数据帧的目的MAC来学习（错）"},
        {"type": "填空", "difficulty": "初级", "template": "交换机建立的表称为_MAC地址表_"},
    ],
    "STP根桥选举": [
        {"type": "选择", "difficulty": "初级", "template": "STP根桥选举的依据是{最小的Bridge ID}"},
        {"type": "判断", "difficulty": "初级", "template": "优先级值越大越可能成为根桥（错）"},
        {"type": "填空", "difficulty": "中级", "template": "STP中端口角色包括根端口、_端口和阻塞端口"},
    ],
    "OpenFlow流表": [
        {"type": "选择", "difficulty": "中级", "template": "OpenFlow流表匹配的依据是{包头字段}"},
        {"type": "判断", "difficulty": "中级", "template": "流表规则只能由控制器下发（错，也可本地配置）"},
        {"type": "填空", "difficulty": "中级", "template": "ovs-ofctl命令用于管理_OpenFlow流表_"},
    ],
    "VXLAN封装": [
        {"type": "选择", "difficulty": "中级", "template": "VXLAN的封装方式是{MAC in UDP}"},
        {"type": "判断", "difficulty": "中级", "template": "VXLAN突破了VLAN 4096的数量限制（对）"},
        {"type": "填空", "difficulty": "中级", "template": "VXLAN中VNI的长度是_24比特_"},
    ],
    "负载均衡": [
        {"type": "选择", "difficulty": "高级", "template": "Select组表用于实现{负载均衡}"},
        {"type": "判断", "difficulty": "高级", "template": "Fast Failover组表用于负载均衡（错，用于故障转移）"},
        {"type": "填空", "difficulty": "高级", "template": "Meter表主要用于实现_QoS限速_"},
    ],
}


def generate_networking_problems(output_dir):
    """生成网络通信原理题库"""
    all_problems = []

    for phase, phase_info in COURSE_OUTLINE.items():
        for ch_key, ch_info in phase_info["chapters"].items():
            for topic in ch_info["topics"]:
                templates = PROBLEM_TEMPLATES.get(topic, [
                    {"type": "选择", "difficulty": "入门", "template": f"{topic}基础选择题"},
                    {"type": "判断", "difficulty": "入门", "template": f"{topic}判断题"},
                    {"type": "填空", "difficulty": "初级", "template": f"{topic}填空题"},
                ])

                for i, template in enumerate(templates):
                    problem = {
                        "problem_id": f"net-{phase}-{ch_key}-{topic}-{i+1:03d}",
                        "domain": "networking",
                        "phase": phase,
                        "chapter": ch_key,
                        "topic": topic,
                        "type": template["type"],
                        "difficulty": template["difficulty"],
                        "title": f"{ch_info['title']} - {topic} #{i+1}",
                        "description": template["template"],
                        "answer": "标准答案",
                        "solution": "详细解析",
                        "manus_link": MANUS_LINKS.get(ch_key, {}),
                        "knowledge_points": [topic],
                        "created_at": datetime.now().isoformat()
                    }
                    all_problems.append(problem)

    # 保存
    for phase in COURSE_OUTLINE:
        phase_problems = [p for p in all_problems if p["phase"] == phase]
        phase_dir = os.path.join(output_dir, phase)
        os.makedirs(phase_dir, exist_ok=True)

        with open(os.path.join(phase_dir, "problems.json"), 'w', encoding='utf-8') as f:
            json.dump({
                "domain": "networking",
                "phase": phase,
                "total": len(phase_problems),
                "generated_at": datetime.now().isoformat(),
                "problems": phase_problems
            }, f, ensure_ascii=False, indent=2)

    return all_problems


if __name__ == "__main__":
    output_dir = os.path.join(os.path.dirname(__file__), "problems")
    problems = generate_networking_problems(output_dir)
    print(f"✅ 生成 {len(problems)} 道网络通信原理题目")

    by_phase = {}
    for p in problems:
        by_phase[p["phase"]] = by_phase.get(p["phase"], 0) + 1
    for phase, count in sorted(by_phase.items()):
        print(f"  {phase}: {count}题")
