"""
🦞 小龙虾网络 · 网络协议训练引擎
支持：OSI模型/TCP-IP/路由/交换/安全协议
"""

import json
import os
import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class NetworkingEngine:
    """网络协议训练引擎"""
    
    def __init__(self, problems_dir: str = None):
        """初始化引擎"""
        if problems_dir is None:
            problems_dir = os.path.join(
                os.path.dirname(__file__),
                '..', 'networking', 'problems', 'problems'
            )
        self.problems_dir = problems_dir
        self.phases = {}
        self._load_problems()
        
    def _load_problems(self):
        """加载各阶段题库"""
        for phase in ['phase1', 'phase2', 'phase3']:
            phase_dir = os.path.join(self.problems_dir, phase)
            problems_file = os.path.join(phase_dir, 'problems.json')
            if os.path.exists(problems_file):
                with open(problems_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.phases[phase] = data
                    
    def get_problems(self, phase: str = None, problem_type: str = None, 
                     difficulty: str = None, limit: int = 10) -> List[Dict]:
        """获取题目"""
        problems = []
        phases_to_check = [phase] if phase else list(self.phases.keys())
        
        for p in phases_to_check:
            if p not in self.phases:
                continue
            for prob in self.phases[p]['problems']:
                if problem_type and prob.get('type') != problem_type:
                    continue
                if difficulty and prob.get('difficulty') != difficulty:
                    continue
                problems.append(prob)
                
        return problems[:limit]
    
    def simulate_osi_model(self) -> Dict:
        """
        OSI七层模型模拟
        
        Returns:
            模型信息
        """
        layers = [
            {'layer': 7, 'name': '应用层', 'protocol': ['HTTP', 'FTP', 'SMTP', 'DNS'], 'pdu': '数据'},
            {'layer': 6, 'name': '表示层', 'protocol': ['SSL/TLS', 'JPEG', 'MPEG'], 'pdu': '数据'},
            {'layer': 5, 'name': '会话层', 'protocol': ['NetBIOS', 'RPC'], 'pdu': '数据'},
            {'layer': 4, 'name': '传输层', 'protocol': ['TCP', 'UDP'], 'pdu': '段/数据报'},
            {'layer': 3, 'name': '网络层', 'protocol': ['IP', 'ICMP', 'OSPF'], 'pdu': '包'},
            {'layer': 2, 'name': '数据链路层', 'protocol': ['Ethernet', 'PPP', 'ARP'], 'pdu': '帧'},
            {'layer': 1, 'name': '物理层', 'protocol': ['RJ45', '光纤', '无线电'], 'pdu': '比特'}
        ]
        
        return {
            'model': 'OSI七层模型',
            'layers': layers,
            'timestamp': datetime.now().isoformat()
        }
    
    def simulate_tcp_handshake(self) -> Dict:
        """
        TCP三次握手模拟
        
        Returns:
            握手过程
        """
        handshake = [
            {'step': 1, 'from': '客户端', 'to': '服务器', 'flags': 'SYN', 'seq': random.randint(1000, 9999)},
            {'step': 2, 'from': '服务器', 'to': '客户端', 'flags': 'SYN+ACK', 'seq': random.randint(1000, 9999), 'ack': random.randint(1000, 9999)},
            {'step': 3, 'from': '客户端', 'to': '服务器', 'flags': 'ACK', 'seq': random.randint(1000, 9999), 'ack': random.randint(1000, 9999)}
        ]
        
        return {
            'process': 'TCP三次握手',
            'handshake': handshake,
            'status': '连接建立',
            'timestamp': datetime.now().isoformat()
        }
    
    def simulate_routing(self, protocol: str = 'OSPF') -> Dict:
        """
        路由模拟
        
        Args:
            protocol: 路由协议
            
        Returns:
            路由信息
        """
        # 模拟路由表
        routes = [
            {'destination': '192.168.1.0/24', 'gateway': '0.0.0.0', 'interface': 'eth0', 'metric': 0},
            {'destination': '10.0.0.0/8', 'gateway': '192.168.1.1', 'interface': 'eth0', 'metric': 10},
            {'destination': '0.0.0.0/0', 'gateway': '192.168.1.1', 'interface': 'eth0', 'metric': 100}
        ]
        
        # 模拟路由计算
        if protocol == 'OSPF':
            algorithm = 'Dijkstra'
            metric = '成本'
        elif protocol == 'RIP':
            algorithm = 'Bellman-Ford'
            metric = '跳数'
        elif protocol == 'BGP':
            algorithm = '路径向量'
            metric = 'AS路径'
        else:
            algorithm = '未知'
            metric = '未知'
            
        return {
            'protocol': protocol,
            'algorithm': algorithm,
            'metric': metric,
            'routing_table': routes,
            'best_path': routes[1],
            'timestamp': datetime.now().isoformat()
        }
    
    def simulate_switching(self, switch_type: str = 'layer2') -> Dict:
        """
        交换模拟
        
        Args:
            switch_type: 交换机类型
            
        Returns:
            交换信息
        """
        # 模拟MAC地址表
        mac_table = [
            {'mac': '00:1A:2B:3C:4D:5E', 'port': 1, 'vlan': 10},
            {'mac': '00:1A:2B:3C:4D:5F', 'port': 2, 'vlan': 10},
            {'mac': '00:1A:2B:3C:4D:60', 'port': 3, 'vlan': 20}
        ]
        
        # 模拟转发决策
        frame = {
            'src_mac': '00:1A:2B:3C:4D:5E',
            'dst_mac': '00:1A:2B:3C:4D:5F',
            'vlan': 10
        }
        
        # 查找目标端口
        dst_port = None
        for entry in mac_table:
            if entry['mac'] == frame['dst_mac'] and entry['vlan'] == frame['vlan']:
                dst_port = entry['port']
                break
                
        if dst_port:
            action = f'从端口{dst_port}转发'
        else:
            action = '泛洪（未知目标）'
            
        return {
            'switch_type': switch_type,
            'mac_table': mac_table,
            'frame': frame,
            'action': action,
            'timestamp': datetime.now().isoformat()
        }
    
    def simulate_security_protocol(self, protocol: str = 'TLS') -> Dict:
        """
        安全协议模拟
        
        Args:
            protocol: 安全协议
            
        Returns:
            协议信息
        """
        if protocol == 'TLS':
            steps = [
                '客户端Hello（支持套件）',
                '服务器Hello（选择套件 + 证书）',
                '密钥交换',
                '完成（加密通信开始）'
            ]
            features = ['加密', '身份认证', '完整性']
        elif protocol == 'IPsec':
            steps = [
                'IKE协商',
                'SA建立',
                '数据加密传输',
                'SA更新/删除'
            ]
            features = ['加密', '认证', '完整性', '防重放']
        else:
            steps = ['未知协议']
            features = []
            
        return {
            'protocol': protocol,
            'steps': steps,
            'features': features,
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_training_plan(self, student_type: str = 'xiaochen',
                               date: str = None) -> Dict:
        """
        生成每日训练计划
        
        Args:
            student_type: 学员类型
            date: 日期
            
        Returns:
            训练计划
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
            
        # 根据学员类型配置题量
        if student_type == 'zhuguxia':
            config = {
                'osi_model': 3,
                'tcp_ip': 3,
                'routing': 2,
                'switching': 2,
                'security': 2
            }
        else:
            config = {
                'osi_model': 2,
                'tcp_ip': 2,
                'routing': 1,
                'switching': 1,
                'security': 1
            }
            
        # 生成计划
        plan = {
            'date': date,
            'student': student_type,
            'type': 'networking-training',
            'schedule': [],
            'total_problems': 0
        }
        
        time_slots = ['09:00', '14:00', '19:00', '21:00', '22:00']
        slot_idx = 0
        
        type_names = {
            'osi_model': 'OSI模型',
            'tcp_ip': 'TCP/IP',
            'routing': '路由',
            'switching': '交换',
            'security': '安全协议'
        }
        
        for problem_type, count in config.items():
            if count == 0:
                continue
                
            problems = self.get_problems(problem_type=problem_type, limit=count)
            plan['schedule'].append({
                'time': time_slots[slot_idx % len(time_slots)],
                'type': type_names.get(problem_type, problem_type),
                'count': len(problems),
                'problems': problems
            })
            plan['total_problems'] += len(problems)
            slot_idx += 1
            
        return plan


# 演示
if __name__ == '__main__':
    engine = NetworkingEngine()
    
    print("=" * 50)
    print("🦞 小龙虾网络 - 网络协议训练引擎 V1.0")
    print("=" * 50)
    
    # 1. OSI模型
    print("\n📚 OSI七层模型:")
    osi = engine.simulate_osi_model()
    for layer in osi['layers']:
        print(f"   第{layer['layer']}层 {layer['name']}: {', '.join(layer['protocol'][:2])}")
        
    # 2. TCP握手
    print("\n🤝 TCP三次握手:")
    tcp = engine.simulate_tcp_handshake()
    for step in tcp['handshake']:
        print(f"   步骤{step['step']}: {step['from']} → {step['to']} [{step['flags']}]")
        
    # 3. 路由
    print("\n🛣️ 路由模拟:")
    routing = engine.simulate_routing('OSPF')
    print(f"   协议: {routing['protocol']}")
    print(f"   算法: {routing['algorithm']}")
    print(f"   路由表条目: {len(routing['routing_table'])}")
    
    # 4. 交换
    print("\n🔀 交换模拟:")
    switching = engine.simulate_switching()
    print(f"   类型: {switching['switch_type']}")
    print(f"   MAC表条目: {len(switching['mac_table'])}")
    print(f"   转发决策: {switching['action']}")
    
    # 5. 安全协议
    print("\n🔒 安全协议:")
    security = engine.simulate_security_protocol('TLS')
    print(f"   协议: {security['protocol']}")
    print(f"   步骤: {len(security['steps'])}")
    print(f"   特性: {', '.join(security['features'])}")
    
    # 6. 生成训练计划
    print("\n📋 训练计划:")
    plan = engine.generate_training_plan('xiaochen')
    print(f"   日期: {plan['date']}")
    print(f"   总题数: {plan['total_problems']}")
    for slot in plan['schedule']:
        print(f"   [{slot['time']}] {slot['type']}: {slot['count']}题")
        
    print("\n" + "=" * 50)
    print("✅ 网络协议训练引擎测试完成！")
