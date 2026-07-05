#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版题库生成器 - 第13章 OpenFlow流表实战 & 第14章 VXLAN网络虚拟化
生成高质量题目，包含真实答案和详细解析
"""

import json
import os
from datetime import datetime
from pathlib import Path

# ============================================================
# 第13章 OpenFlow流表实战
# ============================================================
CH13_PROBLEMS = [
    # ---------- 选择题 x2 ----------
    {
        "problem_id": "net-ch13-流表结构-001",
        "domain": "networking",
        "chapter": "ch13",
        "topic": "流表结构",
        "type": "选择",
        "difficulty": "初级",
        "title": "第十三章 OpenFlow流表实战 - 流表结构",
        "description": "OpenFlow流表中的流表项（Flow Entry）由哪三部分组成？",
        "answer": "A. 匹配域、指令集、统计信息",
        "options": [
            "A. 匹配域、指令集、统计信息",
            "B. 源IP、目的IP、端口号",
            "C. 表ID、优先级、超时时间",
            "D. 匹配域、动作队列、优先级"
        ],
        "knowledge": "OpenFlow流表项由匹配域(Match Fields)、指令集(Instructions)和统计信息(Counters)三部分组成",
        "solution": "OpenFlow规范定义每个流表项包含三部分：(1) 匹配域(Match Fields)——用于匹配数据包的头部字段，如入端口、源/目的MAC、源/目的IP、TCP端口等；(2) 指令集(Instructions)——匹配后执行的动作，如转发到指定端口、修改字段、跳转到下一张流表等；(3) 统计信息(Counters)——记录该流表项匹配的数据包数量和字节数，用于网络监控。选项B只是匹配域中可能用到的字段子集；选项C中的表ID和优先级是流表项的管理属性而非核心组成；选项D中'动作队列'并非OpenFlow标准术语。",
        "created_at": datetime.now().isoformat()
    },
    {
        "problem_id": "net-ch13-远程流表配置-002",
        "domain": "networking",
        "chapter": "ch13",
        "topic": "远程流表配置",
        "type": "选择",
        "difficulty": "中级",
        "title": "第十三章 OpenFlow流表实战 - 远程流表配置",
        "description": "在ODL（OpenDaylight）控制器环境下，使用ovs-vsctl命令将Open vSwitch连接到控制器的正确命令是？",
        "answer": "B. ovs-vsctl set-controller br0 tcp:192.168.1.100:6653",
        "options": [
            "A. ovs-vsctl add-controller br0 udp:192.168.1.100:6653",
            "B. ovs-vsctl set-controller br0 tcp:192.168.1.100:6653",
            "C. ovs-vsctl connect br0 tcp:192.168.1.100:6633",
            "D. ovs-vsctl set-bridge br0 controller=tcp:192.168.1.100:6653"
        ],
        "knowledge": "ovs-vsctl set-controller命令用于设置OVS连接远程OpenFlow控制器，默认端口为6653（IANA标准）",
        "solution": "Open vSwitch使用`ovs-vsctl set-controller <bridge> <target>`命令指定远程控制器。OpenFlow协议基于TCP传输，标准端口号为6653（早期版本使用6633，后由IANA正式分配6653）。选项A错误在于使用UDP协议；选项C的connect不是ovs-vsctl的合法子命令，且6633是旧端口；选项D的set-bridge语法不正确。正确格式为`ovs-vsctl set-controller <bridge> tcp:<controller_ip>:<port>`。",
        "created_at": datetime.now().isoformat()
    },

    # ---------- 判断题 x2 ----------
    {
        "problem_id": "net-ch13-Mininet环境-003",
        "domain": "networking",
        "chapter": "ch13",
        "topic": "Mininet环境",
        "type": "判断",
        "difficulty": "入门",
        "title": "第十三章 OpenFlow流表实战 - Mininet环境",
        "description": "Mininet中的'2s4h'拓扑表示2台交换机连接4台主机",
        "answer": "对",
        "options": [],
        "knowledge": "Mininet拓扑命名中，2s4h表示2台Switch和4台Host的拓扑结构",
        "solution": "Mininet中使用简写方式描述拓扑结构，其中s代表Switch（交换机），h代表Host（主机）。因此2s4h表示网络中包含2台交换机和4台主机。这是一种常见的实验拓扑，可以用于验证跨交换机的流表下发和连通性测试。",
        "created_at": datetime.now().isoformat()
    },
    {
        "problem_id": "net-ch13-本地流表配置-004",
        "domain": "networking",
        "chapter": "ch13",
        "topic": "本地流表配置",
        "type": "判断",
        "difficulty": "初级",
        "title": "第十三章 OpenFlow流表实战 - 本地流表配置",
        "description": "使用ovs-ofctl add-flow命令添加流表项时，priority值越大，该流表项的优先级越低",
        "answer": "错",
        "options": [],
        "knowledge": "OpenFlow中priority值越大优先级越高，匹配时优先使用高优先级的流表项",
        "solution": "在OpenFlow协议中，priority（优先级）字段取值范围通常为0~65535，数值越大表示优先级越高。当一个数据包同时匹配多条流表项时，交换机会选择priority值最大的那条来执行。例如priority=100的流表项会优先于priority=10的流表项被匹配。默认流表项（Table-Miss）通常设置为priority=0，作为最低优先级的兜底规则。",
        "created_at": datetime.now().isoformat()
    },

    # ---------- 填空题 x2 ----------
    {
        "problem_id": "net-ch13-ODL控制器-005",
        "domain": "networking",
        "chapter": "ch13",
        "topic": "ODL控制器",
        "type": "填空",
        "difficulty": "初级",
        "title": "第十三章 OpenFlow流表实战 - ODL控制器",
        "description": "OpenFlow协议中，交换机与控制器之间的通信通道称为____通道",
        "answer": "安全",
        "options": [],
        "knowledge": "OpenFlow定义了安全通道(Secure Channel)作为控制器与交换机之间的通信接口",
        "solution": "OpenFlow架构中，安全通道（Secure Channel）是控制器与OpenFlow交换机之间通信的接口。虽然名称中带有'安全'，但实际使用中可以是TLS加密通道，也可以是普通TCP连接。安全通道负责传输OpenFlow协议消息，包括控制器下发的流表项（Flow-Mod消息）、交换机上报的数据包（Packet-In消息）等。在OpenFlow 1.0中，安全通道使用TCP端口6633；从1.3版本起，IANA正式分配了端口6653。",
        "created_at": datetime.now().isoformat()
    },
    {
        "problem_id": "net-ch13-2s4h拓扑-006",
        "domain": "networking",
        "chapter": "ch13",
        "topic": "2s4h拓扑",
        "type": "填空",
        "difficulty": "中级",
        "title": "第十三章 OpenFlow流表实战 - 2s4h拓扑",
        "description": "在Mininet中查看OVS交换机上所有流表项的命令是ovs-ofctl ____-flows <bridge_name>",
        "answer": "dump",
        "options": [],
        "knowledge": "ovs-ofctl dump-flows命令用于显示OVS交换机上当前安装的所有流表项",
        "solution": "ovs-ofctl是管理OpenFlow交换机的命令行工具。`dump-flows`子命令用于导出（dump）交换机上当前所有的流表项。执行后会显示每条流表项的匹配条件、优先级、统计计数器和动作指令。例如`ovs-ofctl dump-flows s1`会显示交换机s1上所有的流表项。这是OpenFlow实验中最常用的调试命令之一，可以验证控制器下发的流表项是否正确安装到了交换机中。",
        "created_at": datetime.now().isoformat()
    },
]

# ============================================================
# 第14章 VXLAN网络虚拟化
# ============================================================
CH14_PROBLEMS = [
    # ---------- 选择题 x2 ----------
    {
        "problem_id": "net-ch14-VXLAN优势-001",
        "domain": "networking",
        "chapter": "ch14",
        "topic": "VXLAN优势",
        "type": "选择",
        "difficulty": "初级",
        "title": "第十四章 VXLAN网络虚拟化 - VXLAN优势",
        "description": "VXLAN相比传统VLAN的最大优势之一是突破了VLAN ID的数量限制。传统VLAN最多支持多少个VLAN ID？",
        "answer": "B. 4094",
        "options": [
            "A. 256",
            "B. 4094",
            "C. 65535",
            "D. 16777216"
        ],
        "knowledge": "传统VLAN使用802.1Q标签中的12位VLAN ID字段，有效范围为1~4094（0和4095保留）",
        "solution": "IEEE 802.1Q标准中，VLAN Tag包含一个12位的VLAN ID（VID）字段，理论上可以表示2^12=4096个值。但VID=0用于优先级标记，VID=4095（0xFFF）保留不用，因此实际可用的VLAN ID范围为1~4094，最多支持4094个VLAN。在大型数据中心和云计算环境中，租户数量可能远超4094，这就成为传统VLAN的严重瓶颈。VXLAN使用24位的VNI（VXLAN Network Identifier），支持2^24=16777216个虚拟网络，彻底解决了这个问题。",
        "created_at": datetime.now().isoformat()
    },
    {
        "problem_id": "net-ch14-封装解封装-002",
        "domain": "networking",
        "chapter": "ch14",
        "topic": "封装解封装",
        "type": "选择",
        "difficulty": "中级",
        "title": "第十四章 VXLAN网络虚拟化 - 封装解封装",
        "description": "VXLAN封装中，原始以太网帧被封装在哪种协议报文中进行隧道传输？",
        "answer": "C. UDP",
        "options": [
            "A. TCP",
            "B. GRE",
            "C. UDP",
            "D. SCTP"
        ],
        "knowledge": "VXLAN使用UDP作为传输层协议封装原始以太网帧，默认目的端口号为4789",
        "solution": "VXLAN（Virtual eXtensible LAN）的封装结构为：原始以太网帧 → VXLAN头部（8字节，含24位VNI） → UDP头部 → 外层IP头部 → 外层以太网头部。选择UDP而非TCP的原因是：(1) UDP无需建立连接，封装开销小、延迟低；(2) UDP可以利用底层网络的ECMP（等价多路径）进行负载均衡，因为UDP源端口号可以基于内层流的哈希值变化；(3) 大多数网络硬件对UDP有良好的转发支持。IANA分配的VXLAN标准UDP目的端口号为4789。GRE（选项B）是另一种隧道协议，被NVGRE使用而非VXLAN。",
        "created_at": datetime.now().isoformat()
    },

    # ---------- 判断题 x2 ----------
    {
        "problem_id": "net-ch14-VTEP-003",
        "domain": "networking",
        "chapter": "ch14",
        "topic": "VTEP",
        "type": "判断",
        "difficulty": "初级",
        "title": "第十四章 VXLAN网络虚拟化 - VTEP",
        "description": "VTEP（VXLAN Tunnel End Point）是VXLAN隧道的端点设备，负责VXLAN报文的封装和解封装",
        "answer": "对",
        "options": [],
        "knowledge": "VTEP是VXLAN网络的关键组件，负责在VXLAN隧道两端进行封装和解封装操作",
        "solution": "VTEP（VXLAN Tunnel End Point）是VXLAN架构中的核心组件。它位于VXLAN网络的边缘，连接VXLAN覆盖网络（Overlay）和底层IP网络（Underlay）。当VM发出原始以太网帧到达VTEP时，VTEP会执行封装操作：添加VXLAN头部、UDP头部和外层IP/以太网头部，然后通过IP网络发送到远端VTEP。远端VTEP收到后执行解封装，还原出原始以太网帧并转发给目标VM。VTEP可以是物理交换机、虚拟交换机（如OVS）或专用网关设备。",
        "created_at": datetime.now().isoformat()
    },
    {
        "problem_id": "net-ch14-MAC学习-004",
        "domain": "networking",
        "chapter": "ch14",
        "topic": "MAC学习",
        "type": "判断",
        "difficulty": "中级",
        "title": "第十四章 VXLAN网络虚拟化 - MAC学习",
        "description": "VXLAN中的MAC地址学习只能通过数据平面洪泛学习，不支持控制平面学习",
        "answer": "错",
        "options": [],
        "knowledge": "VXLAN支持数据平面洪泛学习和控制平面学习两种MAC学习方式",
        "solution": "VXLAN支持两种MAC学习方式：(1) 数据平面学习（洪泛-学习模式）：类似于传统交换机，VTEP通过洪泛BUM（Broadcast, Unknown-unicast, Multicast）流量来学习远端VM的MAC地址和对应的VTEP IP地址。这种方式简单但会产生大量洪泛流量。(2) 控制平面学习：通过EVPN（Ethernet VPN，基于BGP扩展）等控制平面协议，在VTEP之间交换MAC地址可达性信息。控制平面方式可以显著减少洪泛流量，提高大规模VXLAN网络的可扩展性。在现代数据中心中，VXLAN + EVPN是主流的部署方案。",
        "created_at": datetime.now().isoformat()
    },

    # ---------- 填空题 x2 ----------
    {
        "problem_id": "net-ch14-隧道传输-005",
        "domain": "networking",
        "chapter": "ch14",
        "topic": "隧道传输",
        "type": "填空",
        "difficulty": "初级",
        "title": "第十四章 VXLAN网络虚拟化 - 隧道传输",
        "description": "VXLAN使用____位的VNI（VXLAN Network Identifier）来标识不同的虚拟网络",
        "answer": "24",
        "options": [],
        "knowledge": "VXLAN头部中的VNI字段为24位，支持最多16M（2^24）个虚拟网络",
        "solution": "VXLAN头部总长度为8字节，其中包含一个24位的VNI（VXLAN Network Identifier）字段。24位意味着可以标识2^24 = 16,777,216个独立的虚拟网络，相比传统VLAN的4094个VLAN ID有了质的飞跃。VNI的作用类似于VLAN ID，用于在二层隔离不同的租户流量。VXLAN头部的其余位包括：Flags字段（8位，其中I标志位表示有效VNI）、保留字段（24位+8位）。这种设计使VXLAN非常适合多租户云数据中心场景。",
        "created_at": datetime.now().isoformat()
    },
    {
        "problem_id": "net-ch14-VLAN局限-006",
        "domain": "networking",
        "chapter": "ch14",
        "topic": "VLAN局限",
        "type": "填空",
        "difficulty": "初级",
        "title": "第十四章 VXLAN网络虚拟化 - VLAN局限",
        "description": "VXLAN通过在原始以太网帧外封装____层头部来实现跨三层网络的二层互通",
        "answer": "IP",
        "options": [],
        "knowledge": "VXLAN利用IP网络作为Underlay传输封装后的报文，实现跨越三层边界的二层虚拟网络",
        "solution": "VXLAN的核心设计理念是'MAC over IP/UDP'——将原始二层以太网帧封装在IP/UDP报文中进行传输。由于外层使用的是IP路由转发，VXLAN隧道可以跨越三层网络边界，不受物理网络拓扑的限制。这使得同一VNI下的虚拟机可以分布在不同的物理机房或不同IP子网中，实现了真正的网络虚拟化。底层IP网络（Underlay）只需要提供基本的IP可达性，无需感知上层的VXLAN虚拟网络结构。",
        "created_at": datetime.now().isoformat()
    },
]


def main():
    """生成ch13和ch14的题库并写入JSON文件"""
    # 定位输出目录：脚本在 domains/networking/problems/ 下
    # 输出到 domains/networking/problems/problems/ch13|ch14/
    script_dir = Path(__file__).parent
    problems_base = script_dir / "problems"

    chapters = {
        "ch13": {
            "title": "第十三章 OpenFlow流表实战",
            "problems": CH13_PROBLEMS,
        },
        "ch14": {
            "title": "第十四章 VXLAN网络虚拟化",
            "problems": CH14_PROBLEMS,
        },
    }

    total_generated = 0

    for ch_key, ch_info in chapters.items():
        ch_dir = problems_base / ch_key
        ch_dir.mkdir(parents=True, exist_ok=True)

        ch_problems = ch_info["problems"]
        output = {
            "domain": "networking",
            "chapter": ch_key,
            "total": len(ch_problems),
            "generated_at": datetime.now().isoformat(),
            "problems": ch_problems,
        }

        output_path = ch_dir / "problems.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        total_generated += len(ch_problems)
        print(f"  {ch_key} ({ch_info['title']}): {len(ch_problems)} 题 -> {output_path}")

    print(f"\n共生成 {total_generated} 道题目")
    print(f"  第13章 OpenFlow流表实战: {len(CH13_PROBLEMS)} 题")
    print(f"  第14章 VXLAN网络虚拟化: {len(CH14_PROBLEMS)} 题")

    # 按类型统计
    for ch_key, ch_info in chapters.items():
        type_counts = {}
        for p in ch_info["problems"]:
            t = p["type"]
            type_counts[t] = type_counts.get(t, 0) + 1
        detail = "、".join(f"{t}:{c}题" for t, c in sorted(type_counts.items()))
        print(f"  {ch_key} 题型分布: {detail}")


if __name__ == "__main__":
    main()
