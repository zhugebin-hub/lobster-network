"""
网络协议训练引擎 V1.0
=================

支持（对齐 Meyo 推送的 90 题体系）：
1. OSI 七层模型 / TCP-IP 详解
2. 路由协议（OSPF/BGP）/ 交换原理
3. IPv6 / SDN / 网络安全协议
4. 抓包实战（tcpdump / Wireshark）

题目路径：domains/learning/problems/problems/network-protocol/phase{1,2,3}/problems.json
"""

import json
import os
import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime


# ========== 知识点分类（用于成绩分析）==========
KNOWLEDGE_TAGS = {
    "np1": "网络基础/OSI模型",
    "np2": "传输层/路由/应用层",
    "np3": "IPv6/SDN/网络安全",
}


class NetworkProtocolEngine:
    """网络协议训练引擎"""

    def __init__(self, problems_dir: str = None):
        if problems_dir is None:
            problems_dir = os.path.join(
                os.path.dirname(__file__),
                "problems", "network-protocol"
            )
        self.problems_dir = problems_dir
        self.phases = {}
        self._load_problems()

    def _load_problems(self):
        """加载三个阶段的所有题目"""
        for phase in ["phase1", "phase2", "phase3"]:
            phase_dir = os.path.join(self.problems_dir, phase)
            problems_file = os.path.join(phase_dir, "problems.json")
            if os.path.exists(problems_file):
                with open(problems_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # JSON 文件格式：{"phase1": {"title":..., "questions": [...]}}
                    # 取内层字典，使 self.phases[phase]["questions"] 可直接访问
                    if phase in data:
                        self.phases[phase] = data[phase]
                    else:
                        self.phases[phase] = data

    def get_problems(self, phase: str = None, limit: int = None) -> List[Dict]:
        """获取题目列表"""
        result = []
        phases = [phase] if phase else list(self.phases.keys())
        for p in phases:
            if p in self.phases:
                result.extend(self.phases[p]["questions"])
        if limit:
            result = result[:limit]
        return result

    def get_question(self, phase: str, index: int) -> Optional[Dict]:
        """按索引获取题目"""
        if phase not in self.phases:
            return None
        questions = self.phases[phase]["questions"]
        if index < 0 or index >= len(questions):
            return None
        return questions[index]

    def check_answer(self, question: Dict, user_answer: int) -> Tuple[bool, str]:
        """检查答案，返回 (是否正确, 解析)"""
        correct_index = question.get("correct", -1)
        is_correct = (user_answer == correct_index)
        explanation = question.get("explanation", "（无解析）")
        return is_correct, explanation

    def quiz(self, phase: str = None, count: int = 5) -> List[Dict]:
        """
        随机抽题生成一场测验
        返回题目列表（含 correct 字段，调用方比对）
        """
        all_q = self.get_problems(phase)
        if not all_q:
            return []
        sample_count = min(count, len(all_q))
        return random.sample(all_q, sample_count)

    def analyze_results(self, results: List[Dict]) -> Dict:
        """
        分析答题结果，返回按知识点分类的准确率
        results 格式: [{"id": "np1-001", "correct": true}, ...]
        """
        stats = {}
        for r in results:
            qid = r["id"]
            prefix = qid.split("-")[0]  # "np1"
            tag = KNOWLEDGE_TAGS.get(prefix, "其他")
            if tag not in stats:
                stats[tag] = {"total": 0, "correct": 0}
            stats[tag]["total"] += 1
            if r.get("correct"):
                stats[tag]["correct"] += 1

        # 计算准确率
        analysis = {}
        for tag, s in stats.items():
            analysis[tag] = {
                "total": s["total"],
                "correct": s["correct"],
                "accuracy": round(s["correct"] / s["total"] * 100, 1) if s["total"] > 0 else 0
            }
        return analysis

    def get_phase_info(self, phase: str) -> Optional[Dict]:
        """获取阶段信息"""
        if phase not in self.phases:
            return None
        data = self.phases[phase]
        return {
            "title": data.get("title", ""),
            "description": data.get("description", ""),
            "question_count": len(data.get("questions", []))
        }

    def simulate_osi_model(self) -> Dict:
        """OSI 七层模型速查（教学辅助）"""
        layers = [
            {"layer": 7, "name": "应用层", "protocols": ["HTTP", "FTP", "SMTP", "DNS", "DHCP"], "pdu": "数据"},
            {"layer": 6, "name": "表示层", "protocols": ["SSL/TLS", "JPEG", "ASCII"], "pdu": "数据"},
            {"layer": 5, "name": "会话层", "protocols": ["NetBIOS", "RPC", "SQL"], "pdu": "数据"},
            {"layer": 4, "name": "传输层", "protocols": ["TCP", "UDP"], "pdu": "段/数据报"},
            {"layer": 3, "name": "网络层", "protocols": ["IP", "ICMP", "OSPF", "BGP", "ARP"], "pdu": "包/分组"},
            {"layer": 2, "name": "数据链路层", "protocols": ["Ethernet", "PPP", "VLAN"], "pdu": "帧"},
            {"layer": 1, "name": "物理层", "protocols": ["RJ45", "光纤", "WiFi物理层"], "pdu": "比特"},
        ]
        return {"model": "OSI七层模型", "layers": layers}

    def simulate_tcp_handshake(self) -> Dict:
        """TCP 三次握手过程（教学辅助）"""
        return {
            "process": "TCP三次握手",
            "steps": [
                {"step": 1, "direction": "客户端 → 服务器", "flags": "SYN", "description": "发送初始序列号 ISN(c)"},
                {"step": 2, "direction": "服务器 → 客户端", "flags": "SYN+ACK", "description": "发送 ISN(s)，确认 ISN(c)+1"},
                {"step": 3, "direction": "客户端 → 服务器", "flags": "ACK", "description": "确认 ISN(s)+1，连接建立"},
            ],
            "note": "四次挥手：FIN → ACK → FIN → ACK（主动关闭方进入 TIME_WAIT）"
        }


# ========== CLI 演示 ==========
if __name__ == "__main__":
    engine = NetworkProtocolEngine()
    print("=" * 50)
    print("🦞 小龙虾网络 · 网络协议训练引擎 V1.0")
    print("=" * 50)

    # 1. 显示各阶段信息
    print("\n📚 题目库概况：")
    for phase in ["phase1", "phase2", "phase3"]:
        info = engine.get_phase_info(phase)
        if info:
            print(f"   {phase}: {info['title']}（{info['question_count']} 题）")

    # 2. OSI 模型速查
    print("\n🗂️  OSI 七层模型：")
    osi = engine.simulate_osi_model()
    for layer in osi["layers"]:
        print(f"   L{layer['layer']} {layer['name']}: {', '.join(layer['protocols'][:3])}")

    # 3. TCP 三次握手
    print("\n🤝 TCP 三次握手：")
    tcp = engine.simulate_tcp_handshake()
    for step in tcp["steps"]:
        print(f"   步骤{step['step']}: {step['direction']} [{step['flags']}] {step['description']}")

    # 4. 随机抽题演示
    print("\n🎲 随机抽题（3道）演示：")
    quiz = engine.quiz(count=3)
    for i, q in enumerate(quiz, 1):
        print(f"\n   [{i}] {q['question']}")
        for j, opt in enumerate(q["options"]):
            print(f"        {chr(65+j)}. {opt}")
        print(f"   ✅ 正确答案：{chr(65 + q['correct'])}")

    print("\n" + "=" * 50)
    print("✅ 网络协议训练引擎加载成功！")
