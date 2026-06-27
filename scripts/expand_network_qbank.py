#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络协议题库扩充脚本：60题 → 90题
每个阶段从20题扩充到30题（新增10题）
"""
import json, os

BASE = "/Users/zgb/WorkBuddy/Claw/lobster-network/domains/learning/problems/problems/network-protocol"

# Phase 1 新增10题
P1_NEW = [
  {"id":"np1-021","question":"下列哪种网络拓扑的可靠性最高？","type":"multiple_choice","options":["总线型","星型","环型","网状型"],"correct":3,"explanation":"网状型拓扑每个节点都有多条路径可达其他节点，单条链路故障不影响整体连通，可靠性最高。"},
  {"id":"np1-022","question":"双绞线（Twisted Pair）最常见的接口类型是？","type":"multiple_choice","options":["BNC","RJ45","SC","RS232"],"correct":1,"explanation":"RJ45是双绞线以太网最常用的接口类型，有8P8C（8针8触点）结构。"},
  {"id":"np1-023","question":"单模光纤（Single-mode）的工作波长主要是？","type":"multiple_choice","options":["850nm","1300nm","1310nm和1550nm","650nm"],"correct":2,"explanation":"单模光纤主要工作于1310nm和1550nm波长，传输距离远、带宽大，用于长距离通信。"},
  {"id":"np1-024","question":"CRC（循环冗余校验）用于OSI哪一层？","type":"multiple_choice","options":["物理层","数据链路层","网络层","传输层"],"correct":1,"explanation":"CRC校验由数据链路层（如Ethernet的FCS字段）提供，用于检测帧传输中的错误。"},
  {"id":"np1-025","question":"子网掩码255.255.255.0对应CIDR前缀长度是？","type":"multiple_choice","options":["/24","/25","/23","/22"],"correct":0,"explanation":"/24对应255.255.255.0，表示前24位为网络位，后8位为主机位。"},
  {"id":"np1-026","question":"私有IP地址段不包括下列哪个？","type":"multiple_choice","options":["10.0.0.0/8","172.16.0.0/12","192.168.0.0/16","202.96.128.0/24"],"correct":3,"explanation":"RFC1918定义的私有IP段为10.0.0.0/8、172.16.0.0/12、192.168.0.0/16。202.96.128.0/24是公网地址。"},
  {"id":"np1-027","question":"集线器（Hub）工作在OSI哪一层？","type":"multiple_choice","options":["物理层","数据链路层","网络层","传输层"],"correct":0,"explanation":"Hub是物理层设备，仅对信号进行放大和广播转发，不识别MAC地址。"},
  {"id":"np1-028","question":"下列关于交换机的说法，正确的是？","type":"multiple_choice","options":["交换机基于IP地址转发","交换机基于MAC地址转发","交换机不能隔离冲突域","交换机分割广播域"],"correct":1,"explanation":"交换机基于MAC地址表进行转发，每个端口是一个独立冲突域，但默认不分割广播域（需VLAN）。"},
  {"id":"np1-029","question":"OSI模型中，数据链路层的数据单位称为？","type":"multiple_choice","options":["Bit","报文","帧","数据包"],"correct":2,"explanation":"数据链路层的PDU是帧（Frame），物理层是比特（Bit），网络层是数据包（Packet），应用层是报文（Message）。"},
  {"id":"np1-030","question":"在Ethernet II帧中，类型字段（EtherType）值为0x0800表示上层协议是？","type":"multiple_choice","options":["ARP","IPv4","IPv6","LLC"],"correct":1,"explanation":"EtherType=0x0800表示承载IPv4数据包；0x0806=ARP；0x86DD=IPv6。"}
]

# Phase 2 新增10题
P2_NEW = [
  {"id":"np2-021","question":"HTTP/3协议基于下列哪个传输层协议？","type":"multiple_choice","options":["TCP","UDP","QUIC","SCTP"],"correct":2,"explanation":"HTTP/3基于QUIC协议（运行在UDP上），解决了TCP队头阻塞问题，支持0-RTT建立连接。"},
  {"id":"np2-022","question":"DNSSEC的主要功能是什么？","type":"multiple_choice","options":["加速DNS解析","对DNS响应进行数字签名验证","隐藏DNS查询内容","负载均衡"],"correct":1,"explanation":"DNSSEC通过数字签名验证DNS响应的真实性，防止DNS劫持和缓存污染攻击。"},
  {"id":"np2-023","question":"下列属于NAT穿透技术的是？","type":"multiple_choice","options":["OSPF","STUN/TURN","BGP","ARP"],"correct":1,"explanation":"STUN和TURN是NAT穿透（NAT Traversal）的标准技术，用于P2P通信中穿越NAT网关。"},
  {"id":"np2-024","question":"防火墙的三层过滤指的是哪三层？","type":"multiple_choice","options":["物理/链路/网络","网络/传输/应用","数据链路/网络/传输","会话/表示/应用"],"correct":1,"explanation":"状态检测防火墙通常过滤网络层（IP）、传输层（TCP/UDP端口）、应用层（协议内容）信息。"},
  {"id":"np2-025","question":"BGP-4使用下列哪个端口建立TCP连接？","type":"multiple_choice","options":["179","80","443","520"],"correct":0,"explanation":"BGP使用TCP端口179建立邻居连接，相比OSPF的IP协议89，BGP依赖TCP的可靠性。"},
  {"id":"np2-026","question":"关于OSPF区域（Area）的说法，正确的是？","type":"multiple_choice","options":["所有区域必须直接连接到Area 1","Area 0是骨干区域","一个路由器只能属于一个区域","NSSA区域不允许外部路由"],"correct":1,"explanation":"OSPF骨干区域必须是Area 0，所有非骨干区域必须直接或间接连接到Area 0。"},
  {"id":"np2-027","question":"TLS 1.3相比TLS 1.2，握手轮次减少到几次？","type":"multiple_choice","options":["4次","3次","2次","1次"],"correct":3,"explanation":"TLS 1.3支持0-RTT（恢复连接）和1-RTT（新建连接），相比TLS 1.2的2-RTT大幅减少延迟。"},
  {"id":"np2-028","question":"下列哪项是HTTPS的默认端口？","type":"multiple_choice","options":["80","443","8080","8443"],"correct":1,"explanation":"HTTPS默认使用TCP端口443。端口80是HTTP，8080和8443常用于代理或开发环境。"},
  {"id":"np2-029","question":"ARP协议的作用是什么？","type":"multiple_choice","options":["将IP地址解析为MAC地址","将域名解析为IP地址","自动分配IP地址","建立TCP连接"],"correct":0,"explanation":"ARP（地址解析协议）用于在同一局域网内将IPv4地址解析为MAC地址。"},
  {"id":"np2-030","question":"在多接入网络中，OSPF选举DR（指定路由器）的依据是？","type":"multiple_choice","options":["IP地址最小","Router ID最大","链路成本最小","区域号最小"],"correct":1,"explanation":"OSPF的DR选举首先比较优先级（默认1），相同则选Router ID（通常取最大IP）最大的路由器。"}
]

# Phase 3 新增10题
P3_NEW = [
  {"id":"np3-021","question":"VXLAN协议使用的UDP端口号是？","type":"multiple_choice","options":["4789","443","80","53"],"correct":0,"explanation":"VXLAN使用UDP端口4789（IANA分配）封装二层帧，实现跨三层网络的二层延伸。"},
  {"id":"np3-022","question":"EVPN主要用于解决下列哪个问题？","type":"multiple_choice","options":["IP地址冲突","数据中心二层互联的控制平面学习","路由震荡","DNS劫持"],"correct":1,"explanation":"EVPN（以太网VPN）为VXLAN等Overlay技术提供控制平面，通过BGP分发MAC/IP可达性信息，替代泛洪学习。"},
  {"id":"np3-023","question":"Netconf协议使用的传输层协议和默认端口是？","type":"multiple_choice","options":["TCP/22","TCP/830","UDP/161","TCP/443"],"correct":1,"explanation":"Netconf基于SSH传输，默认使用TCP端口830，用于网络设备配置管理。"},
  {"id":"np3-024","question":"YANG模型的主要作用是？","type":"multiple_choice","options":["路由计算","描述网络配置和状态的数据模型","加密数据传输","分配IP地址"],"correct":1,"explanation":"YANG是一种数据建模语言，用于定义网络设备的配置和状态数据格式，配合Netconf使用。"},
  {"id":"np3-025","question":"Zero Trust（零信任）网络的核心原则是？","type":"multiple_choice","options":["内网默认可信","永远验证，永不信任","仅边界防御","使用MAC地址认证"],"correct":1,"explanation":"零信任模型假设网络内部也不可信，要求对所有访问请求进行持续验证，遵循「永不信任，始终验证」原则。"},
  {"id":"np3-026","question":"INT（In-band Network Telemetry）技术的主要用途是？","type":"multiple_choice","options":["加密数据传输","实时收集网络内部排队和延迟信息","路由计算","地址分配"],"correct":1,"explanation":"INT允许数据包在转发路径上收集交换机的队列深度、延迟等遥测数据，实现精细化的网络性能监控。"},
  {"id":"np3-027","question":"Ipv6的地址长度是多少位？","type":"multiple_choice","options":["32位","64位","128位","256位"],"correct":2,"explanation":"Ipv6地址长度为128位，是Ipv4（32位）的4倍，可提供约3.4×10³⁸个地址。"},
  {"id":"np3-028","question":"SDN架构中，数据平面与控制平面的接口协议通常是？","type":"multiple_choice","options":["OSPF","OpenFlow","BGP","ARP"],"correct":1,"explanation":"OpenFlow是SDN中最经典的控制平面—数据平面接口协议，控制器通过OpenFlow下发流表到交换机。"},
  {"id":"np3-029","question":"在Ipv6中，无状态地址自动配置（SLAAC）依赖下列哪个协议？","type":"multiple_choice","options":["ARP","DHCPv6","ICMPv6","BGP"],"correct":2,"explanation":"SLAAC基于ICMPv6的路由器通告（RA）消息，主机无需DHCPv6即可自动生成全球单播地址。"},
  {"id":"np3-030","question":"VXLAN的网络标识符（VNI）占多少比特？","type":"multiple_choice","options":["12位","16位","24位","32位"],"correct":2,"explanation":"VNI（VXLAN Network Identifier）占24位，理论上可支持约1600万个虚拟二层网络。"}
]

def append_questions(phase_file, new_qs):
    with open(phase_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    questions = data[phase_file.split("/")[-2].replace("phase", "phase")]["questions"]
    existing_ids = {q["id"] for q in questions}
    added = 0
    for q in new_qs:
        if q["id"] not in existing_ids:
            questions.append(q)
            added += 1
    with open(phase_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  ✓ {phase_file.split('/')[-2]}: 新增{added}题，共{len(questions)}题")

for phase, new_qs in [("phase1", P1_NEW), ("phase2", P2_NEW), ("phase3", P3_NEW)]:
    fpath = os.path.join(BASE, phase, "problems.json")
    print(f"处理 {phase}...")
    append_questions(fpath, new_qs)

print("\n✅ 题库扩充完成！每个阶段现各30题，共90题。")
