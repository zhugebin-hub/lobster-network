"""
🦞 小龙虾网络 · 网络安全训练引擎
支持：漏洞扫描、加密技术、攻防模拟、安全评估
"""

import json
import os
import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class CybersecurityEngine:
    """网络安全训练引擎"""
    
    def __init__(self, problems_dir: str = None):
        """初始化引擎"""
        if problems_dir is None:
            problems_dir = os.path.join(
                os.path.dirname(__file__),
                '..', 'cybersecurity', 'problems', 'problems'
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
    
    def scan_vulnerabilities(self, target: str = 'web_app') -> Dict:
        """
        漏洞扫描模拟
        
        Args:
            target: 扫描目标
            
        Returns:
            扫描结果
        """
        vuln_types = ['SQL注入', 'XSS', 'CSRF', '文件上传', '命令注入', '路径遍历']
        severities = ['低', '中', '高', '严重']
        
        # 模拟扫描
        vulnerabilities = []
        for _ in range(random.randint(3, 8)):
            vuln = {
                'type': random.choice(vuln_types),
                'severity': random.choice(severities),
                'description': f'发现{random.choice(vuln_types)}漏洞',
                'cvss_score': round(random.uniform(3.0, 9.8), 1),
                'remediation': '修复建议：更新补丁/修改配置'
            }
            vulnerabilities.append(vuln)
            
        # 统计
        severity_count = {}
        for v in vulnerabilities:
            severity_count[v['severity']] = severity_count.get(v['severity'], 0) + 1
            
        return {
            'target': target,
            'scan_time': datetime.now().isoformat(),
            'total_vulnerabilities': len(vulnerabilities),
            'severity_distribution': severity_count,
            'vulnerabilities': vulnerabilities,
            'risk_level': '高' if severity_count.get('严重', 0) > 0 else '中' if severity_count.get('高', 0) > 0 else '低',
            'timestamp': datetime.now().isoformat()
        }
    
    def simulate_attack(self, attack_type: str = 'DDoS',
                       target_system: str = 'web_server') -> Dict:
        """
        攻击模拟
        
        Args:
            attack_type: 攻击类型
            target_system: 目标系统
            
        Returns:
            攻击结果
        """
        # 模拟攻击过程
        attack_phases = [
            '侦察',
            '武器化',
            '投递',
            '漏洞利用',
            '安装',
            '命令控制',
            '目标达成'
        ]
        
        # 模拟防御
        defense_success = random.random() < 0.6
        
        if defense_success:
            blocked_at = random.randint(1, 5)
            result = {
                'attack_type': attack_type,
                'target': target_system,
                'status': '防御成功',
                'blocked_at_phase': attack_phases[blocked_at],
                'blocked_at_index': blocked_at,
                'damage': '无',
                'defense_measures': ['防火墙规则', '入侵检测', '流量清洗'],
                'timestamp': datetime.now().isoformat()
            }
        else:
            result = {
                'attack_type': attack_type,
                'target': target_system,
                'status': '防御失败',
                'reached_phase': attack_phases[-1],
                'damage': random.choice(['数据泄露', '服务中断', '系统被控']),
                'recommendations': ['加强防火墙', '更新补丁', '部署WAF'],
                'timestamp': datetime.now().isoformat()
            }
            
        return result
    
    def encrypt_decrypt(self, algorithm: str = 'AES',
                       message: str = 'Hello World') -> Dict:
        """
        加密解密模拟
        
        Args:
            algorithm: 加密算法
            message: 明文消息
            
        Returns:
            加密解密结果
        """
        import base64
        
        # 模拟加密
        encrypted = base64.b64encode(message.encode()).decode()
        
        # 模拟解密
        decrypted = base64.b64decode(encrypted).decode()
        
        return {
            'algorithm': algorithm,
            'original_message': message,
            'encrypted': encrypted,
            'decrypted': decrypted,
            'is_correct': message == decrypted,
            'key_length': random.choice([128, 192, 256]) if algorithm == 'AES' else None,
            'timestamp': datetime.now().isoformat()
        }
    
    def security_assessment(self, system_type: str = 'web_app') -> Dict:
        """
        安全评估
        
        Args:
            system_type: 系统类型
            
        Returns:
            评估结果
        """
        categories = [
            '身份认证',
            '访问控制',
            '数据加密',
            '安全日志',
            '漏洞管理',
            '应急响应'
        ]
        
        scores = {}
        for cat in categories:
            scores[cat] = round(random.uniform(60, 95), 1)
            
        # 综合评分
        overall = sum(scores.values()) / len(scores)
        
        # 风险等级
        if overall >= 85:
            risk = '低'
        elif overall >= 70:
            risk = '中'
        else:
            risk = '高'
            
        return {
            'system_type': system_type,
            'assessment_time': datetime.now().isoformat(),
            'category_scores': scores,
            'overall_score': round(overall, 1),
            'risk_level': risk,
            'weaknesses': [k for k, v in scores.items() if v < 75],
            'strengths': [k for k, v in scores.items() if v >= 85],
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
                'vulnerability_scan': 4,
                'attack_simulation': 3,
                'encryption': 2,
                'security_assessment': 2
            }
        else:
            config = {
                'vulnerability_scan': 3,
                'attack_simulation': 2,
                'encryption': 1,
                'security_assessment': 1
            }
            
        # 生成计划
        plan = {
            'date': date,
            'student': student_type,
            'type': 'cybersecurity-training',
            'schedule': [],
            'total_problems': 0
        }
        
        time_slots = ['09:00', '14:00', '19:00', '21:00']
        slot_idx = 0
        
        type_names = {
            'vulnerability_scan': '漏洞扫描',
            'attack_simulation': '攻击模拟',
            'encryption': '加密技术',
            'security_assessment': '安全评估'
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
    engine = CybersecurityEngine()
    
    print("=" * 50)
    print("🦞 小龙虾网络 - 网络安全训练引擎 V1.0")
    print("=" * 50)
    
    # 1. 漏洞扫描
    print("\n🔍 漏洞扫描:")
    scan = engine.scan_vulnerabilities('web_app')
    print(f"   目标: {scan['target']}")
    print(f"   发现漏洞: {scan['total_vulnerabilities']}")
    print(f"   风险等级: {scan['risk_level']}")
    for v in scan['vulnerabilities'][:3]:
        print(f"   - {v['type']} ({v['severity']}) CVSS:{v['cvss_score']}")
        
    # 2. 攻击模拟
    print("\n⚔️ 攻击模拟:")
    attack = engine.simulate_attack('DDoS', 'web_server')
    print(f"   攻击类型: {attack['attack_type']}")
    print(f"   目标: {attack['target']}")
    print(f"   结果: {attack['status']}")
    if attack['status'] == '防御成功':
        print(f"   阻断阶段: {attack['blocked_at_phase']}")
        
    # 3. 加密解密
    print("\n🔐 加密解密:")
    crypto = engine.encrypt_decrypt('AES', 'Hello World')
    print(f"   算法: {crypto['algorithm']}")
    print(f"   明文: {crypto['original_message']}")
    print(f"   密文: {crypto['encrypted']}")
    print(f"   解密: {crypto['decrypted']}")
    print(f"   正确: {'✅' if crypto['is_correct'] else '❌'}")
    
    # 4. 安全评估
    print("\n📊 安全评估:")
    assessment = engine.security_assessment('web_app')
    print(f"   系统: {assessment['system_type']}")
    print(f"   综合评分: {assessment['overall_score']:.1f}")
    print(f"   风险等级: {assessment['risk_level']}")
    print(f"   优势: {', '.join(assessment['strengths'])}")
    print(f"   劣势: {', '.join(assessment['weaknesses'])}")
    
    # 5. 生成训练计划
    print("\n📋 训练计划:")
    plan = engine.generate_training_plan('xiaochen')
    print(f"   日期: {plan['date']}")
    print(f"   总题数: {plan['total_problems']}")
    for slot in plan['schedule']:
        print(f"   [{slot['time']}] {slot['type']}: {slot['count']}题")
        
    print("\n" + "=" * 50)
    print("✅ 网络安全训练引擎测试完成！")
