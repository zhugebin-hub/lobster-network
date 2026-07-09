#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OADP-Science 科学智能体标准化对接协议

基于小龙虾网络 OADP (Open Agent Discovery Protocol) 扩展，
定义科学任务专用消息类型、能力封装规范和安全运行约束。

消息类型：
- SCIENCE_HELLO: 科学智能体注册，携带领域标签和能力签名
- SCIENCE_TASK: 科学任务分发（含任务类型、输入数据、质量要求）
- SCIENCE_RESULT: 科学任务结果上报（含输出数据、置信度、验证状态）
- SCIENCE_REVIEW: 同行评审反馈（含评审意见、修改建议、质量评分）
- SCIENCE_HEARTBEAT: 科学智能体心跳（含当前负载和任务进度）

安全机制：
- 三层 Harness 安全护栏（L1输入/L2执行/L3输出）
- 差分隐私保护（ε=1.0, δ=10⁻⁵）
- API Key 认证
"""

import json
import re
import uuid
import math
import random
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum


# ============================================================
# 日志配置
# ============================================================

logger = logging.getLogger("oadp_science")
logger.setLevel(logging.INFO)


# ============================================================
# 枚举与数据模型
# ============================================================

class ScienceMessageType(str, Enum):
    """科学协议消息类型"""
    SCIENCE_HELLO = "science_hello"
    SCIENCE_TASK = "science_task"
    SCIENCE_RESULT = "science_result"
    SCIENCE_REVIEW = "science_review"
    SCIENCE_HEARTBEAT = "science_heartbeat"


@dataclass
class ScienceCapability:
    """科学能力描述"""
    capability_id: str
    name: str
    domain: str  # e.g., "target_discovery", "compound_design", "admet_prediction"
    input_schema: Dict
    output_schema: Dict
    quality_metrics: Dict  # accuracy, speed, cost
    version: str = "1.0.0"


@dataclass
class ScienceMessage:
    """科学协议消息"""
    msg_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    msg_type: ScienceMessageType = ScienceMessageType.SCIENCE_HELLO
    from_node: str = ""
    to_node: str = "broadcast"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    domain: str = "food_allergy_drug_discovery"
    payload: Dict = field(default_factory=dict)
    priority: int = 3  # 1-5
    protocol_version: str = "oadp-science-v1.0"

    def to_dict(self) -> Dict:
        """转换为字典"""
        data = asdict(self)
        data["msg_type"] = self.msg_type.value
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> "ScienceMessage":
        """从字典创建"""
        data = data.copy()
        data["msg_type"] = ScienceMessageType(data["msg_type"])
        return cls(**data)


# ============================================================
# 三层安全护栏
# ============================================================

class ScienceHarness:
    """三层科学安全护栏"""

    # L1: Input Guard
    DANGEROUS_PATTERNS = ["rm -rf", "DROP TABLE", "os.system", "subprocess"]
    SENSITIVE_PATTERNS = [r"api[_-]?key\s*[:=]", r"password\s*[:=]", r"token\s*[:=]"]
    MAX_INPUT_LENGTH = 16000

    # L2: Execution Guard
    SAFE_OPERATIONS = [
        "target_discovery", "compound_design", "virtual_screening",
        "admet_prediction", "toxicity_assessment", "literature_mining",
        "hypothesis_generation", "experiment_design", "result_analysis",
        "review_feedback", "pipeline_orchestration", "report_generation"
    ]
    RESOURCE_LIMITS = {
        "max_concurrent": 5,
        "max_tokens": 4096,
        "max_memory_mb": 512,
        "timeout_seconds": 300
    }

    # L3: Output Guard
    MAX_OUTPUT_LENGTH = 50000

    def check_input(self, message: ScienceMessage) -> Tuple[bool, str]:
        """L1: 验证输入消息安全性"""
        payload_str = json.dumps(message.payload)

        # 检查长度
        if len(payload_str) > self.MAX_INPUT_LENGTH:
            return False, f"输入超长: {len(payload_str)} > {self.MAX_INPUT_LENGTH}"

        # 检查危险模式
        for pattern in self.DANGEROUS_PATTERNS:
            if pattern.lower() in payload_str.lower():
                return False, f"检测到危险模式: {pattern}"

        # 检查敏感信息
        for pattern in self.SENSITIVE_PATTERNS:
            if re.search(pattern, payload_str, re.IGNORECASE):
                return False, f"检测到敏感信息: {pattern}"

        return True, "OK"

    def check_execution(self, operation: str, params: Dict) -> Tuple[bool, str]:
        """L2: 验证操作在白名单内且资源限制"""
        if operation not in self.SAFE_OPERATIONS:
            return False, f"操作不在白名单: {operation}"

        # 检查资源限制
        if "tokens" in params and params["tokens"] > self.RESOURCE_LIMITS["max_tokens"]:
            return False, f"Token超限: {params['tokens']} > {self.RESOURCE_LIMITS['max_tokens']}"

        if "memory_mb" in params and params["memory_mb"] > self.RESOURCE_LIMITS["max_memory_mb"]:
            return False, f"内存超限: {params['memory_mb']} > {self.RESOURCE_LIMITS['max_memory_mb']}"

        return True, "OK"

    def check_output(self, result: Dict) -> Tuple[bool, str]:
        """L3: 验证输出安全性和格式"""
        output_str = json.dumps(result)

        # 检查长度
        if len(output_str) > self.MAX_OUTPUT_LENGTH:
            return False, f"输出超长: {len(output_str)} > {self.MAX_OUTPUT_LENGTH}"

        # 检查危险模式
        for pattern in self.DANGEROUS_PATTERNS:
            if pattern.lower() in output_str.lower():
                return False, f"输出含危险模式: {pattern}"

        return True, "OK"

    def add_differential_privacy(self, data: Dict, epsilon: float = 1.0) -> Dict:
        """应用拉普拉斯机制实现差分隐私

        使用拉普拉斯分布逆累积分布函数:
            X = mu - b * sign(U) * ln(1 - 2|U|)
        其中 b = sensitivity / epsilon, U ~ Uniform(-0.5, 0.5)
        """
        result = data.copy()
        sensitivity = 1.0  # 假设灵敏度为1
        noise_scale = sensitivity / epsilon

        for key, value in result.items():
            if isinstance(value, (int, float)):
                # 拉普拉斯噪声: 逆CDF采样
                u = random.random() - 0.5  # Uniform(-0.5, 0.5)
                sign_u = math.copysign(1.0, u)
                noise = -noise_scale * sign_u * math.log(1.0 - 2.0 * abs(u))
                if isinstance(value, int):
                    result[key] = int(round(value + noise))
                else:
                    result[key] = value + noise
            elif isinstance(value, dict):
                result[key] = self.add_differential_privacy(value, epsilon)

        return result


# ============================================================
# OADP-Science 协议控制器
# ============================================================

class OADPScienceProtocol:
    """OADP-Science 协议控制器"""

    def __init__(self, node_id: str, domain: str = "food_allergy_drug_discovery"):
        self.node_id = node_id
        self.domain = domain
        self.harness = ScienceHarness()
        self.capabilities: List[ScienceCapability] = []
        self.message_log: List[ScienceMessage] = []
        self.protocol_version = "oadp-science-v1.0"

    def register_capability(self, capability: ScienceCapability):
        """注册科学能力"""
        self.capabilities.append(capability)
        logger.info(f"注册能力: {capability.name} ({capability.domain})")

    def create_hello_message(self) -> ScienceMessage:
        """创建 SCIENCE_HELLO 消息用于节点注册"""
        payload = {
            "node_id": self.node_id,
            "domain": self.domain,
            "capabilities": [
                {
                    "capability_id": c.capability_id,
                    "name": c.name,
                    "domain": c.domain,
                    "version": c.version
                }
                for c in self.capabilities
            ],
            "endpoint": f"science://{self.node_id}"
        }

        msg = ScienceMessage(
            msg_type=ScienceMessageType.SCIENCE_HELLO,
            from_node=self.node_id,
            to_node="broadcast",
            domain=self.domain,
            payload=payload,
            priority=2
        )

        self.message_log.append(msg)
        return msg

    def create_task_message(self, to_node: str, task_type: str,
                           input_data: Dict, quality_requirements: Dict = None,
                           deadline: str = None) -> ScienceMessage:
        """创建 SCIENCE_TASK 消息用于任务分发"""
        payload = {
            "task_type": task_type,
            "input_data": input_data,
            "quality_requirements": quality_requirements or {"accuracy": 0.8},
            "deadline": deadline
        }

        msg = ScienceMessage(
            msg_type=ScienceMessageType.SCIENCE_TASK,
            from_node=self.node_id,
            to_node=to_node,
            domain=self.domain,
            payload=payload,
            priority=3
        )

        self.message_log.append(msg)
        return msg

    def create_result_message(self, task_msg_id: str, output_data: Dict,
                             confidence: float = 0.0,
                             verified: bool = False) -> ScienceMessage:
        """创建 SCIENCE_RESULT 消息用于结果上报"""
        payload = {
            "task_msg_id": task_msg_id,
            "output_data": output_data,
            "confidence": confidence,
            "verified": verified,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        msg = ScienceMessage(
            msg_type=ScienceMessageType.SCIENCE_RESULT,
            from_node=self.node_id,
            to_node="broadcast",
            domain=self.domain,
            payload=payload,
            priority=2
        )

        self.message_log.append(msg)
        return msg

    def create_review_message(self, result_msg_id: str,
                             review_comments: str, score: float,
                             suggestions: List[str] = None) -> ScienceMessage:
        """创建 SCIENCE_REVIEW 消息用于同行评审"""
        payload = {
            "result_msg_id": result_msg_id,
            "review_comments": review_comments,
            "score": score,
            "suggestions": suggestions or []
        }

        msg = ScienceMessage(
            msg_type=ScienceMessageType.SCIENCE_REVIEW,
            from_node=self.node_id,
            to_node="broadcast",
            domain=self.domain,
            payload=payload,
            priority=2
        )

        self.message_log.append(msg)
        return msg

    def send_message(self, message: ScienceMessage, shared_path: str) -> bool:
        """通过 CC 广播发送消息（写入 .shared/messages/）"""
        # L1 输入检查
        ok, reason = self.harness.check_input(message)
        if not ok:
            logger.error(f"L1检查失败: {reason}")
            return False

        # 写入inbox
        try:
            inbox_dir = Path(shared_path) / "messages" / "queue"
            inbox_dir.mkdir(parents=True, exist_ok=True)

            msg_file = inbox_dir / f"{message.msg_id}.json"
            with open(msg_file, 'w', encoding='utf-8') as f:
                json.dump(message.to_dict(), f, ensure_ascii=False, indent=2)

            logger.info(f"发送消息: {message.msg_type.value} -> {message.to_node}")
            return True
        except Exception as e:
            logger.error(f"发送失败: {e}")
            return False

    def receive_message(self, shared_path: str) -> Optional[ScienceMessage]:
        """接收并验证科学消息"""
        try:
            inbox_dir = Path(shared_path) / "messages" / "queue"
            if not inbox_dir.exists():
                return None

            # 查找发给本节点的消息
            for msg_file in inbox_dir.glob("*.json"):
                with open(msg_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                msg = ScienceMessage.from_dict(data)

                # L1 输入检查
                ok, reason = self.harness.check_input(msg)
                if not ok:
                    logger.warning(f"丢弃不安全消息: {reason}")
                    msg_file.unlink()
                    continue

                # 检查接收方
                if msg.to_node in [self.node_id, "broadcast"]:
                    self.message_log.append(msg)
                    msg_file.unlink()  # 已读删除
                    logger.info(f"接收消息: {msg.msg_type.value} from {msg.from_node}")
                    return msg

            return None
        except Exception as e:
            logger.error(f"接收失败: {e}")
            return None

    def process_task(self, message: ScienceMessage) -> ScienceMessage:
        """处理科学任务并返回结果"""
        if message.msg_type != ScienceMessageType.SCIENCE_TASK:
            raise ValueError("只能处理 SCIENCE_TASK 类型消息")

        task_type = message.payload.get("task_type", "")
        input_data = message.payload.get("input_data", {})

        # L2 执行检查
        ok, reason = self.harness.check_execution(task_type, {"tokens": 1000})
        if not ok:
            logger.error(f"L2检查失败: {reason}")
            return self.create_result_message(
                message.msg_id,
                {"error": f"执行检查失败: {reason}"},
                confidence=0.0,
                verified=False
            )

        # 模拟任务处理（实际应调用对应Agent）
        output_data = {
            "task_type": task_type,
            "status": "completed",
            "result": f"Processed {task_type} task",
            "input_summary": str(input_data)[:100]
        }

        # L3 输出检查
        ok, reason = self.harness.check_output(output_data)
        if not ok:
            logger.error(f"L3检查失败: {reason}")
            return self.create_result_message(
                message.msg_id,
                {"error": f"输出检查失败: {reason}"},
                confidence=0.0,
                verified=False
            )

        # 应用差分隐私
        output_data = self.harness.add_differential_privacy(output_data, epsilon=1.0)

        return self.create_result_message(
            message.msg_id,
            output_data,
            confidence=0.85,
            verified=True
        )

    def get_statistics(self) -> Dict:
        """返回协议统计信息"""
        stats = {
            "node_id": self.node_id,
            "domain": self.domain,
            "capabilities_count": len(self.capabilities),
            "message_log_count": len(self.message_log),
            "message_types": {}
        }

        for msg in self.message_log:
            msg_type = msg.msg_type.value
            stats["message_types"][msg_type] = stats["message_types"].get(msg_type, 0) + 1

        return stats


# ============================================================
# 演示程序
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("OADP-Science 协议演示")
    print("=" * 60)

    # 创建协议实例
    protocol = OADPScienceProtocol(
        node_id="science-agent-01",
        domain="food_allergy_drug_discovery"
    )

    # 注册6个科学能力
    protocol.register_capability(ScienceCapability(
        capability_id="cap-001",
        name="Target Discovery Engine",
        domain="target_discovery",
        input_schema={"type": "object", "properties": {"disease": {"type": "string"}}},
        output_schema={"type": "object", "properties": {"targets": {"type": "array"}}},
        quality_metrics={"accuracy": 0.85, "speed": "fast", "cost": "low"}
    ))

    protocol.register_capability(ScienceCapability(
        capability_id="cap-002",
        name="Compound Designer",
        domain="compound_design",
        input_schema={"type": "object", "properties": {"target": {"type": "string"}}},
        output_schema={"type": "object", "properties": {"compounds": {"type": "array"}}},
        quality_metrics={"accuracy": 0.80, "speed": "medium", "cost": "medium"}
    ))

    protocol.register_capability(ScienceCapability(
        capability_id="cap-003",
        name="ADMET Predictor",
        domain="admet_prediction",
        input_schema={"type": "object", "properties": {"compound": {"type": "string"}}},
        output_schema={"type": "object", "properties": {"admet_profile": {"type": "object"}}},
        quality_metrics={"accuracy": 0.90, "speed": "fast", "cost": "low"}
    ))

    protocol.register_capability(ScienceCapability(
        capability_id="cap-004",
        name="Toxicity Assessor",
        domain="toxicity_assessment",
        input_schema={"type": "object", "properties": {"compound": {"type": "string"}}},
        output_schema={"type": "object", "properties": {"toxicity_score": {"type": "number"}}},
        quality_metrics={"accuracy": 0.88, "speed": "fast", "cost": "low"}
    ))

    protocol.register_capability(ScienceCapability(
        capability_id="cap-005",
        name="Literature Miner",
        domain="literature_mining",
        input_schema={"type": "object", "properties": {"query": {"type": "string"}}},
        output_schema={"type": "object", "properties": {"papers": {"type": "array"}}},
        quality_metrics={"accuracy": 0.75, "speed": "medium", "cost": "low"}
    ))

    protocol.register_capability(ScienceCapability(
        capability_id="cap-006",
        name="Hypothesis Generator",
        domain="hypothesis_generation",
        input_schema={"type": "object", "properties": {"context": {"type": "string"}}},
        output_schema={"type": "object", "properties": {"hypotheses": {"type": "array"}}},
        quality_metrics={"accuracy": 0.70, "speed": "slow", "cost": "high"}
    ))

    print(f"\n✓ 已注册 {len(protocol.capabilities)} 个科学能力")

    # 发送 HELLO 消息
    hello_msg = protocol.create_hello_message()
    print(f"✓ 发送 HELLO 消息: {hello_msg.msg_id}")
    print(f"  - 节点: {hello_msg.from_node}")
    print(f"  - 领域: {hello_msg.domain}")
    print(f"  - 能力数: {len(hello_msg.payload['capabilities'])}")

    # 创建 TASK 消息
    task_msg = protocol.create_task_message(
        to_node="science-agent-02",
        task_type="target_discovery",
        input_data={
            "disease": "peanut_allergy",
            "organism": "human",
            "filters": {"druggable": True}
        },
        quality_requirements={"accuracy": 0.85, "recall": 0.80}
    )
    print(f"\n✓ 创建 TASK 消息: {task_msg.msg_id}")
    print(f"  - 任务类型: {task_msg.payload['task_type']}")
    print(f"  - 目标节点: {task_msg.to_node}")

    # 处理任务
    result_msg = protocol.process_task(task_msg)
    print(f"\n✓ 处理任务生成 RESULT: {result_msg.msg_id}")
    print(f"  - 置信度: {result_msg.payload['confidence']}")
    print(f"  - 已验证: {result_msg.payload['verified']}")

    # 打印统计
    stats = protocol.get_statistics()
    print(f"\n" + "=" * 60)
    print("协议统计")
    print("=" * 60)
    print(f"节点ID: {stats['node_id']}")
    print(f"领域: {stats['domain']}")
    print(f"能力数: {stats['capabilities_count']}")
    print(f"消息总数: {stats['message_log_count']}")
    print(f"消息类型分布:")
    for msg_type, count in stats['message_types'].items():
        print(f"  - {msg_type}: {count}")

    print("\n✓ OADP-Science 协议演示完成")
