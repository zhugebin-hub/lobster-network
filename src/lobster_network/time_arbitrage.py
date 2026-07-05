"""
时间套利引擎 (Time Arbitrage Engine)

时间套利的核心思想：不同节点在时间维度上存在结构性差异，
这些差异不是低效，而是可以被系统性利用的套利机会。

五个维度：
1. 速率套利 (Speed Arbitrage) —— 利用不同Agent的学习速度差
2. 错峰套利 (Off-Peak Arbitrage) —— 利用低谷时段进行高强度计算
3. 反思套利 (Reflection Arbitrage) —— 利用遗忘曲线的最佳复习时机
4. 复利套利 (Compound Arbitrage) —— 多轮对话的涌现指数增长
5. 时距套利 (Temporal Distance Arbitrage) —— 知识的时间价值增值

理论基础：
- 金融套利：利用市场间价差获取无风险收益
- 学习科学：间隔重复（spaced repetition）比集中学习更有效
- 复合增长：知识复利效应，每轮对话在上一轮基础上涌现
- 时间经济学：非高峰时段的计算资源"价格"更低
"""

import math
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from .node import Node
from .dialogue import DialogueEngine, DialogueResult


class ArbitrageType(Enum):
    """套利类型"""
    SPEED = "speed"           # 速率套利
    OFF_PEAK = "off_peak"     # 错峰套利
    REFLECTION = "reflection" # 反思套利
    COMPOUND = "compound"     # 复利套利
    TEMPORAL = "temporal"     # 时距套利


class NodeSpeedProfile(Enum):
    """节点速度档案"""
    FAST = "fast"             # 加速型（诸葛虾：0.5-2s/题, 98%基线）
    STEADY = "steady"         # 稳健型（信电大虾：1-3s/题, 90%基线）
    PRACTICAL = "practical"   # 实战型（qoder：高准确率, 少量题目）


@dataclass
class ArbitrageOpportunity:
    """套利机会"""
    opportunity_id: str
    arbitrage_type: ArbitrageType
    participants: List[str]
    expected_return: float          # 预期收益率 (0-∞)
    time_window: Tuple[str, str]    # 时间窗口 (开始, 结束)
    confidence: float               # 置信度 (0-1)
    description: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "opportunity_id": self.opportunity_id,
            "arbitrage_type": self.arbitrage_type.value,
            "participants": self.participants,
            "expected_return": self.expected_return,
            "time_window": list(self.time_window),
            "confidence": self.confidence,
            "description": self.description,
            "timestamp": self.timestamp,
        }


@dataclass
class ArbitrageResult:
    """套利执行结果"""
    opportunity_id: str
    arbitrage_type: ArbitrageType
    actual_return: float            # 实际收益率
    time_cost_seconds: float        # 时间成本（秒）
    dialogues_triggered: int        # 触发的对话次数
    emergence_generated: float      # 产生的涌现总量
    knowledge_transferred: List[str]  # 转移的知识点
    compound_factor: float = 1.0    # 复利因子
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "opportunity_id": self.opportunity_id,
            "arbitrage_type": self.arbitrage_type.value,
            "actual_return": self.actual_return,
            "time_cost_seconds": self.time_cost_seconds,
            "dialogues_triggered": self.dialogues_triggered,
            "emergence_generated": self.emergence_generated,
            "knowledge_transferred": self.knowledge_transferred,
            "compound_factor": self.compound_factor,
            "timestamp": self.timestamp,
        }


@dataclass
class ForgettingCurve:
    """遗忘曲线（艾宾浩斯模型）"""
    node_id: str
    knowledge_id: str
    learned_at: str
    strength: float = 1.0           # 记忆强度 (0-1)
    stability: float = 1.0          # 记忆稳定性（随复习次数增长）
    last_review: Optional[str] = None
    review_count: int = 0

    def retention_at(self, now: datetime) -> float:
        """
        计算当前时刻的记忆保留率
        R = e^(-t/S)，S为稳定性，t为距上次学习/复习的时间（天）
        """
        reference = datetime.fromisoformat(self.last_review or self.learned_at)
        days_elapsed = (now - reference).total_seconds() / 86400
        if days_elapsed <= 0:
            return 1.0
        return math.exp(-days_elapsed / self.stability)

    def optimal_review_time(self, target_retention: float = 0.85) -> datetime:
        """
        计算最佳复习时间（记忆保留率降到目标值时）
        t = -S * ln(R_target)
        """
        reference = datetime.fromisoformat(self.last_review or self.learned_at)
        days = -self.stability * math.log(target_retention)
        return reference + timedelta(days=days)

    def review(self, now: datetime):
        """执行复习，更新记忆参数"""
        self.last_review = now.isoformat()
        self.review_count += 1
        # 稳定性随复习次数增长（SM-2简化版）
        self.stability *= (1.0 + 0.3 * self.review_count)
        self.strength = 1.0


class TimeArbitrageEngine:
    """
    时间套利引擎
    
    系统性识别和利用网络中节点之间的时间差异，
    最大化知识涌现和转移的效率。
    """

    # 速度档案：解题时间范围(秒)和准确率基线
    SPEED_PROFILES = {
        NodeSpeedProfile.FAST: {"solve_time": (0.5, 2.0), "accuracy_baseline": 0.98},
        NodeSpeedProfile.STEADY: {"solve_time": (1.0, 3.0), "accuracy_baseline": 0.90},
        NodeSpeedProfile.PRACTICAL: {"solve_time": (2.0, 5.0), "accuracy_baseline": 0.95},
    }

    # 错峰时段定义（北京时间）
    OFF_PEAK_WINDOWS = {
        "deep_night": ("00:00", "06:00", 1.5),    # 深夜：算力成本系数1.5x收益
        "early_morning": ("06:00", "08:00", 1.2),  # 清晨：预热期
        "work_hours": ("08:00", "18:00", 1.0),     # 工作时段：基准
        "evening": ("18:00", "22:00", 1.1),        # 晚间：轻度提升
        "late_night": ("22:00", "00:00", 1.3),     # 深夜前：加速期
    }

    def __init__(self, dialogue_engine: DialogueEngine = None):
        """
        初始化时间套利引擎
        
        Args:
            dialogue_engine: 对话引擎实例（如不提供则创建默认）
        """
        self.dialogue_engine = dialogue_engine or DialogueEngine()
        self.node_speed_profiles: Dict[str, NodeSpeedProfile] = {}
        self.forgetting_curves: Dict[str, List[ForgettingCurve]] = {}
        self.opportunities: List[ArbitrageOpportunity] = []
        self.results: List[ArbitrageResult] = []
        self.compound_dialogue_chains: Dict[str, List[DialogueResult]] = {}

    # =========================================================================
    # 节点注册与配置
    # =========================================================================

    def register_node(self, node_id: str, speed_profile: NodeSpeedProfile):
        """
        注册节点的速度档案
        
        Args:
            node_id: 节点ID
            speed_profile: 速度档案类型
        """
        self.node_speed_profiles[node_id] = speed_profile

    def add_knowledge(self, node_id: str, knowledge_id: str, learned_at: datetime = None):
        """
        为节点添加知识追踪（用于反思套利）
        
        Args:
            node_id: 节点ID
            knowledge_id: 知识点ID
            learned_at: 学习时间
        """
        if node_id not in self.forgetting_curves:
            self.forgetting_curves[node_id] = []
        
        curve = ForgettingCurve(
            node_id=node_id,
            knowledge_id=knowledge_id,
            learned_at=(learned_at or datetime.now()).isoformat(),
        )
        self.forgetting_curves[node_id].append(curve)

    # =========================================================================
    # 1. 速率套利 (Speed Arbitrage)
    # =========================================================================

    def detect_speed_arbitrage(
        self,
        fast_node: Node,
        slow_node: Node,
        topic: str = "",
    ) -> Optional[ArbitrageOpportunity]:
        """
        检测速率套利机会
        
        原理：快速节点先生成原始洞见（低成本），
        慢速节点深化验证（高质量），形成知识价差。
        快速节点的"浅而广"与慢速节点的"深而窄"互补。
        
        Args:
            fast_node: 快速节点
            slow_node: 慢速节点
            topic: 套利主题
        
        Returns:
            ArbitrageOpportunity: 套利机会（如果有）
        """
        fast_profile = self.node_speed_profiles.get(fast_node.node_id)
        slow_profile = self.node_speed_profiles.get(slow_node.node_id)

        if not fast_profile or not slow_profile:
            return None
        if fast_profile == slow_profile:
            return None

        fast_time = self.SPEED_PROFILES[fast_profile]["solve_time"]
        slow_time = self.SPEED_PROFILES[slow_profile]["solve_time"]

        # 速度比：快节点在慢节点解一题的时间内可以解多少题
        speed_ratio = (slow_time[0] + slow_time[1]) / (fast_time[0] + fast_time[1])

        # 预期收益 = 速度比 × 视角差异加成
        perspective_bonus = 1.0 if fast_node.seed["perspective"] != slow_node.seed["perspective"] else 0.5
        expected_return = speed_ratio * perspective_bonus

        # 置信度基于速度差的显著性
        confidence = min(speed_ratio / 3.0, 1.0)

        if expected_return < 1.2:
            return None

        opp_id = f"speed-{fast_node.node_id}-{slow_node.node_id}-{datetime.now().strftime('%H%M%S')}"
        return ArbitrageOpportunity(
            opportunity_id=opp_id,
            arbitrage_type=ArbitrageType.SPEED,
            participants=[fast_node.node_id, slow_node.node_id],
            expected_return=expected_return,
            time_window=(datetime.now().isoformat(), "immediate"),
            confidence=confidence,
            description=f"速率套利：{fast_node.name}({fast_profile.value})以{speed_ratio:.1f}倍速"
                        f"生成原始洞见，{slow_node.name}({slow_profile.value})深化验证。"
                        f"预期收益={expected_return:.2f}x",
        )

    def execute_speed_arbitrage(
        self,
        fast_node: Node,
        slow_node: Node,
        rounds: int = 3,
    ) -> ArbitrageResult:
        """
        执行速率套利
        
        流程：
        1. 快速节点批量生成N个原始洞见
        2. 慢速节点选取最有价值的洞见深化
        3. 深化结果反馈给快速节点，加速下一轮
        
        Args:
            fast_node: 快速节点
            slow_node: 慢速节点
            rounds: 套利轮数
        
        Returns:
            ArbitrageResult: 执行结果
        """
        start_time = datetime.now()
        total_emergence = 0.0
        dialogues_count = 0
        knowledge_transferred = []

        for i in range(rounds):
            # 快速节点 → 慢速节点：传递原始洞见
            result = self.dialogue_engine.dialogue(fast_node, slow_node, f"速率套利-R{i+1}-快→慢")
            total_emergence += result.emergence_score
            dialogues_count += 1
            if result.treasure_unlocked:
                knowledge_transferred.append(f"R{i+1}-insight-{result.treasure_unlocked}")

            # 慢速节点 → 快速节点：反馈深化结果
            result_back = self.dialogue_engine.dialogue(slow_node, fast_node, f"速率套利-R{i+1}-慢→快")
            total_emergence += result_back.emergence_score
            dialogues_count += 1
            if result_back.treasure_unlocked:
                knowledge_transferred.append(f"R{i+1}-deepened-{result_back.treasure_unlocked}")

        elapsed = (datetime.now() - start_time).total_seconds()

        return ArbitrageResult(
            opportunity_id=f"speed-result-{datetime.now().strftime('%H%M%S')}",
            arbitrage_type=ArbitrageType.SPEED,
            actual_return=total_emergence / max(rounds * 2, 1),
            time_cost_seconds=elapsed,
            dialogues_triggered=dialogues_count,
            emergence_generated=total_emergence,
            knowledge_transferred=knowledge_transferred,
            compound_factor=1.0 + (total_emergence / (rounds * 2)),
        )

    # =========================================================================
    # 2. 错峰套利 (Off-Peak Arbitrage)
    # =========================================================================

    def detect_off_peak_arbitrage(
        self,
        nodes: List[Node],
        current_hour: int = None,
    ) -> Optional[ArbitrageOpportunity]:
        """
        检测错峰套利机会
        
        原理：非高峰时段的计算资源"价格"更低（无人类注意力竞争），
        适合执行高强度批量任务。V6深夜特训已验证此模式。
        
        Args:
            nodes: 参与节点列表
            current_hour: 当前小时（北京时间，默认自动检测）
        
        Returns:
            ArbitrageOpportunity: 套利机会
        """
        if current_hour is None:
            current_hour = datetime.now().hour

        current_window = None
        current_multiplier = 1.0
        for name, (start, end, mult) in self.OFF_PEAK_WINDOWS.items():
            start_h = int(start.split(":")[0])
            end_h = int(end.split(":")[0])
            if start_h <= end_h:
                if start_h <= current_hour < end_h:
                    current_window = name
                    current_multiplier = mult
                    break
            else:  # 跨午夜
                if current_hour >= start_h or current_hour < end_h:
                    current_window = name
                    current_multiplier = mult
                    break

        if current_multiplier <= 1.0:
            return None

        node_ids = [n.node_id for n in nodes]
        opp_id = f"offpeak-{current_window}-{datetime.now().strftime('%H%M%S')}"

        return ArbitrageOpportunity(
            opportunity_id=opp_id,
            arbitrage_type=ArbitrageType.OFF_PEAK,
            participants=node_ids,
            expected_return=current_multiplier * len(nodes),
            time_window=(f"{current_hour:02d}:00", "next_peak"),
            confidence=0.9,  # 错峰套利置信度高（确定性收益）
            description=f"错峰套利：当前处于{current_window}时段，"
                        f"算力收益系数{current_multiplier}x，"
                        f"建议对{len(nodes)}个节点执行高强度批量训练。",
        )

    def get_optimal_schedule(self, nodes: List[Node]) -> Dict:
        """
        生成最优错峰调度方案
        
        Args:
            nodes: 节点列表
        
        Returns:
            Dict: 调度方案
        """
        schedule = {}
        for name, (start, end, mult) in self.OFF_PEAK_WINDOWS.items():
            if mult > 1.0:
                schedule[name] = {
                    "window": f"{start}-{end}",
                    "multiplier": mult,
                    "recommended_tasks": self._recommend_tasks_for_window(name, nodes),
                    "intensity": "high" if mult >= 1.3 else "medium",
                }
        return schedule

    def _recommend_tasks_for_window(self, window: str, nodes: List[Node]) -> List[str]:
        """根据时段推荐任务类型"""
        if window == "deep_night":
            return ["极限死活题", "AI定式导入", "19路夜战对局", "AI深度复盘"]
        elif window == "late_night":
            return ["热身训练", "错题重练", "次日计划预览"]
        elif window == "early_morning":
            return ["复盘整理", "知识沉淀", "状态更新"]
        else:
            return ["常规训练"]

    # =========================================================================
    # 3. 反思套利 (Reflection Arbitrage)
    # =========================================================================

    def detect_reflection_arbitrage(
        self,
        node_id: str,
        target_retention: float = 0.85,
        now: datetime = None,
    ) -> List[ArbitrageOpportunity]:
        """
        检测反思套利机会
        
        原理：基于艾宾浩斯遗忘曲线，当记忆保留率降到最佳复习点时，
        复习的边际收益最高。过早复习浪费（记忆还很强），
        过晚复习损失大（已经遗忘太多）。
        
        V4调度器的错题本每3天重做机制就是这个模式的原始版本。
        
        Args:
            node_id: 节点ID
            target_retention: 目标保留率（降到此值时复习最优）
            now: 当前时间
        
        Returns:
            List[ArbitrageOpportunity]: 需要复习的知识点列表
        """
        if now is None:
            now = datetime.now()

        curves = self.forgetting_curves.get(node_id, [])
        opportunities = []

        for curve in curves:
            retention = curve.retention_at(now)
            optimal_time = curve.optimal_review_time(target_retention)

            # 当前保留率在目标值附近（±10%）是最佳复习窗口
            if target_retention * 0.9 <= retention <= target_retention * 1.1:
                opp_id = f"reflect-{node_id}-{curve.knowledge_id}-{now.strftime('%H%M%S')}"
                urgency = 1.0 - retention  # 越接近遗忘，越紧急

                opportunities.append(ArbitrageOpportunity(
                    opportunity_id=opp_id,
                    arbitrage_type=ArbitrageType.REFLECTION,
                    participants=[node_id],
                    expected_return=1.0 + curve.review_count * 0.3,  # 复习次数越多，收益越高
                    time_window=(now.isoformat(), optimal_time.isoformat()),
                    confidence=0.7 + 0.3 * (1 - retention),
                    description=f"反思套利：{node_id}的知识点{curve.knowledge_id}"
                                f"保留率降至{retention:.0%}，已达最佳复习窗口。"
                                f"第{curve.review_count + 1}次复习，稳定性将提升"
                                f"{(1 + 0.3 * (curve.review_count + 1)):.1f}x。",
                ))

        return opportunities

    def execute_reflection(
        self,
        node_id: str,
        knowledge_id: str,
        now: datetime = None,
    ) -> Optional[ArbitrageResult]:
        """
        执行反思套利（复习一个知识点）
        
        Args:
            node_id: 节点ID
            knowledge_id: 知识点ID
            now: 当前时间
        
        Returns:
            ArbitrageResult: 复习结果
        """
        if now is None:
            now = datetime.now()

        curves = self.forgetting_curves.get(node_id, [])
        target_curve = None
        for c in curves:
            if c.knowledge_id == knowledge_id:
                target_curve = c
                break

        if not target_curve:
            return None

        retention_before = target_curve.retention_at(now)
        old_stability = target_curve.stability

        # 执行复习
        target_curve.review(now)

        # 计算收益
        stability_gain = target_curve.stability / old_stability

        return ArbitrageResult(
            opportunity_id=f"reflect-result-{knowledge_id}",
            arbitrage_type=ArbitrageType.REFLECTION,
            actual_return=stability_gain,
            time_cost_seconds=0.0,
            dialogues_triggered=0,
            emergence_generated=0.0,
            knowledge_transferred=[f"reviewed-{knowledge_id}"],
            compound_factor=stability_gain,
        )

    # =========================================================================
    # 4. 复利套利 (Compound Arbitrage)
    # =========================================================================

    def start_compound_chain(
        self,
        node_a: Node,
        node_b: Node,
        chain_id: str = None,
    ) -> str:
        """
        启动复利对话链
        
        原理：多轮对话的涌现呈指数增长——
        每轮对话的输出成为下轮的输入上下文，
        N轮对话产生的涌现远大于N × 单轮涌现。
        
        数学模型：E_total = E_1 × (1 + r)^(N-1)
        其中 r 为复利因子（由视角深度和知识互补性决定）
        
        Args:
            node_a: 节点A
            node_b: 节点B
            chain_id: 链ID（自动生成）
        
        Returns:
            str: 链ID
        """
        if chain_id is None:
            chain_id = f"chain-{node_a.node_id}-{node_b.node_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        self.compound_dialogue_chains[chain_id] = []
        return chain_id

    def compound_dialogue(
        self,
        chain_id: str,
        node_a: Node,
        node_b: Node,
        trigger: str = "",
    ) -> DialogueResult:
        """
        执行复利对话链中的一轮对话
        
        每轮的涌现值受前序轮次影响：
        - 如果前序涌现高，本轮起点更高（动量效应）
        - 对话深度随轮次增长（深度效应）
        
        Args:
            chain_id: 链ID
            node_a: 节点A
            node_b: 节点B
            trigger: 触发描述
        
        Returns:
            DialogueResult: 对话结果
        """
        chain = self.compound_dialogue_chains.get(chain_id, [])
        round_number = len(chain) + 1

        # 执行基础对话
        result = self.dialogue_engine.dialogue(node_a, node_b, f"复利-R{round_number}: {trigger}")

        # 复利加成：前序轮次的涌现会增强本轮
        if chain:
            prev_avg_emergence = sum(d.emergence_score for d in chain) / len(chain)
            # 复利因子 r = 前序平均涌现 × 0.2
            compound_bonus = prev_avg_emergence * 0.2 * round_number
            result.emergence_score = min(result.emergence_score + compound_bonus, 1.0)

        chain.append(result)
        self.compound_dialogue_chains[chain_id] = chain

        return result

    def get_compound_statistics(self, chain_id: str) -> Dict:
        """
        获取复利对话链的统计信息
        
        Args:
            chain_id: 链ID
        
        Returns:
            Dict: 统计信息
        """
        chain = self.compound_dialogue_chains.get(chain_id, [])
        if not chain:
            return {"rounds": 0, "total_emergence": 0, "compound_factor": 1.0}

        scores = [d.emergence_score for d in chain]
        total = sum(scores)
        single_avg = scores[0] if scores else 0

        # 复利因子 = 总涌现 / (轮数 × 单轮基准涌现)
        compound_factor = total / (len(chain) * max(single_avg, 0.01))

        return {
            "rounds": len(chain),
            "total_emergence": total,
            "avg_emergence": total / len(chain),
            "emergence_per_round": scores,
            "compound_factor": compound_factor,
            "growth_rate": (scores[-1] - scores[0]) / max(scores[0], 0.01) if len(scores) > 1 else 0,
        }

    # =========================================================================
    # 5. 时距套利 (Temporal Distance Arbitrage)
    # =========================================================================

    def create_time_locked_treasure(
        self,
        source_node_id: str,
        knowledge_content: str,
        unlock_conditions: Dict,
        lock_duration_hours: int = 72,
    ) -> Dict:
        """
        创建时间锁宝藏
        
        原理：知识具有时间价值——今天的洞见在下周可能更有价值，
        因为届时其他节点可能已经积累了相关知识，能够更好地理解和利用。
        
        类似金融的"期货"：现在投资，未来收获更高的回报。
        
        Args:
            source_node_id: 来源节点ID
            knowledge_content: 知识内容
            unlock_conditions: 解锁条件（如：某节点达到某世界版本）
            lock_duration_hours: 锁定时长（小时）
        
        Returns:
            Dict: 宝藏信息
        """
        now = datetime.now()
        unlock_time = now + timedelta(hours=lock_duration_hours)

        treasure = {
            "treasure_id": f"temporal-{source_node_id}-{now.strftime('%Y%m%d%H%M%S')}",
            "type": "time_locked",
            "source_node": source_node_id,
            "content": knowledge_content,
            "created_at": now.isoformat(),
            "unlock_at": unlock_time.isoformat(),
            "lock_duration_hours": lock_duration_hours,
            "unlock_conditions": unlock_conditions,
            "expected_appreciation": self._estimate_appreciation(lock_duration_hours),
            "status": "locked",
        }

        return treasure

    def _estimate_appreciation(self, hours: int) -> float:
        """
        估算知识的时间增值
        
        模型：知识价值随时间先增后减（倒U型曲线）
        峰值出现在 48-72 小时后（其他节点有时间消化但还没遗忘）
        """
        # 简化的倒U型：V(t) = 1 + 0.5 * sin(π * t / T_peak)
        T_peak = 72.0  # 峰值时间
        if hours <= 0:
            return 1.0
        t = min(hours, T_peak * 2)
        return 1.0 + 0.5 * math.sin(math.pi * t / T_peak)

    # =========================================================================
    # 综合套利策略
    # =========================================================================

    def scan_all_opportunities(
        self,
        nodes: List[Node],
        now: datetime = None,
    ) -> List[ArbitrageOpportunity]:
        """
        扫描所有套利机会
        
        综合检测五个维度的套利机会，按预期收益排序。
        
        Args:
            nodes: 网络中的节点列表
            now: 当前时间
        
        Returns:
            List[ArbitrageOpportunity]: 按收益排序的套利机会列表
        """
        if now is None:
            now = datetime.now()

        all_opportunities = []

        # 1. 速率套利：检测所有节点对的速度差异
        for i, node_a in enumerate(nodes):
            for node_b in nodes[i+1:]:
                opp = self.detect_speed_arbitrage(node_a, node_b)
                if opp:
                    all_opportunities.append(opp)
                opp = self.detect_speed_arbitrage(node_b, node_a)
                if opp:
                    all_opportunities.append(opp)

        # 2. 错峰套利
        opp = self.detect_off_peak_arbitrage(nodes, now.hour)
        if opp:
            all_opportunities.append(opp)

        # 3. 反思套利
        for node in nodes:
            opps = self.detect_reflection_arbitrage(node.node_id, now=now)
            all_opportunities.extend(opps)

        # 按预期收益排序
        all_opportunities.sort(key=lambda o: o.expected_return * o.confidence, reverse=True)

        self.opportunities = all_opportunities
        return all_opportunities

    def get_portfolio_summary(self) -> Dict:
        """
        获取套利组合概览
        
        Returns:
            Dict: 组合统计
        """
        by_type = {}
        for atype in ArbitrageType:
            type_opps = [o for o in self.opportunities if o.arbitrage_type == atype]
            type_results = [r for r in self.results if r.arbitrage_type == atype]
            by_type[atype.value] = {
                "pending_opportunities": len(type_opps),
                "executed": len(type_results),
                "total_return": sum(r.actual_return for r in type_results),
                "avg_return": (sum(r.actual_return for r in type_results) / len(type_results))
                              if type_results else 0,
            }

        return {
            "total_opportunities": len(self.opportunities),
            "total_executed": len(self.results),
            "portfolio_return": sum(r.actual_return for r in self.results),
            "by_type": by_type,
            "compound_chains": len(self.compound_dialogue_chains),
            "tracked_knowledge": sum(len(c) for c in self.forgetting_curves.values()),
        }
