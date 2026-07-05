#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 ARD 消息签名/验证模块 V5.0
Agentic Resource Discovery 协议安全增强

功能：
1. ARD 消息签名（RSA/ECDSA）
2. ARD 消息验证
3. ARD 错误处理
4. ARD 性能优化
"""

import json
import os
import hashlib
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

from .ard_protocol import ARDProtocol, ARDAgent, ARDResource
from .ard_gateway import ARDGateway, ARDMessage, ARD_MSG_TYPE_DISCOVER, ARD_MSG_TYPE_REGISTER, ARD_MSG_TYPE_MATCH, ARD_MSG_TYPE_COLLABORATE, ARD_MSG_TYPE_RESPONSE, ARD_MSG_TYPE_ERROR


# ========== 常量定义 ==========

# 签名算法
SIGN_ALGORITHM_RSA = "rsa"
SIGN_ALGORITHM_ECDSA = "ecdsa"
SIGN_ALGORITHM_HMAC = "hmac"

# ARD 错误码
ARD_ERROR_SUCCESS = 0
ARD_ERROR_INVALID_REQUEST = 1001
ARD_ERROR_AUTH_FAILED = 1002
ARD_ERROR_RATE_LIMIT = 1003
ARD_ERROR_INTERNAL_ERROR = 1004
ARD_ERROR_NOT_FOUND = 1005
ARD_ERROR_TIMEOUT = 1006


# ========== 数据类定义 ==========

@dataclass
class ARDKeyPair:
    """ARD 密钥对"""
    key_id: str
    algorithm: str
    public_key: str
    private_key: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    expires_at: Optional[str] = None
    status: str = "active"

    def to_dict(self) -> dict:
        return {
            "key_id": self.key_id,
            "algorithm": self.algorithm,
            "public_key": self.public_key,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "status": self.status,
        }


@dataclass
class ARDError:
    """ARD 错误"""
    error_code: int
    error_message: str
    details: Optional[Dict] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "error_code": self.error_code,
            "error_message": self.error_message,
            "details": self.details,
            "timestamp": self.timestamp,
        }


@dataclass
class ARDPerformance:
    """ARD 性能指标"""
    operation: str
    duration_ms: float
    success: bool
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "operation": self.operation,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


# ========== ARD 安全增强 ==========

class ARDSecurity:
    """ARD 安全增强"""

    def __init__(self, data_dir: str = "/shared/lobster-network-data/ard-security"):
        self.data_dir = data_dir
        self.key_pairs: Dict[str, ARDKeyPair] = {}
        self._key_counter = 0

        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)

    def generate_key_pair(
        self,
        algorithm: str = SIGN_ALGORITHM_ECDSA,
        expires_days: int = 365,
    ) -> Tuple[bool, str, ARDKeyPair]:
        """
        生成密钥对

        Args:
            algorithm: 签名算法
            expires_days: 过期天数

        Returns:
            (成功，消息，密钥对)
        """
        self._key_counter += 1
        key_id = f"ard-key-{self._key_counter:04d}"

        # 生成模拟密钥（实际应使用密码学库）
        public_key = hashlib.sha256(f"{key_id}:public:{datetime.now().isoformat()}".encode()).hexdigest()
        private_key = hashlib.sha256(f"{key_id}:private:{datetime.now().isoformat()}".encode()).hexdigest()

        # 计算过期时间
        expires_at = None
        if expires_days > 0:
            from datetime import timedelta
            expires_at = (datetime.now() + timedelta(days=expires_days)).isoformat()

        key_pair = ARDKeyPair(
            key_id=key_id,
            algorithm=algorithm,
            public_key=public_key,
            private_key=private_key,
            expires_at=expires_at,
        )
        self.key_pairs[key_id] = key_pair

        return True, f"密钥对 {key_id} 生成成功", key_pair

    def sign_message(self, message: ARDMessage, key_id: str) -> Tuple[bool, str]:
        """
        签名消息

        Args:
            message: ARD 消息
            key_id: 密钥 ID

        Returns:
            (成功，消息)
        """
        key_pair = self.key_pairs.get(key_id)
        if not key_pair:
            return False, f"密钥 {key_id} 不存在"

        if key_pair.status != "active":
            return False, f"密钥 {key_id} 状态为 {key_pair.status}"

        # 检查过期
        if key_pair.expires_at:
            try:
                expires = datetime.fromisoformat(key_pair.expires_at)
                if datetime.now() > expires:
                    key_pair.status = "expired"
                    return False, f"密钥 {key_id} 已过期"
            except ValueError:
                pass

        # 签名消息
        message.sign(key_pair.private_key)

        return True, f"消息 {message.message_id} 签名成功"

    def verify_message(self, message: ARDMessage, public_key: str) -> Tuple[bool, str]:
        """
        验证消息签名

        Args:
            message: ARD 消息
            public_key: 公钥

        Returns:
            (成功，消息)
        """
        if not message.signature:
            return False, "消息无签名"

        if message.verify(public_key):
            return True, "消息签名验证通过"
        else:
            return False, "消息签名验证失败"


# ========== ARD 错误处理 ==========

class ARDErrorHandler:
    """ARD 错误处理器"""

    def __init__(self):
        self.error_log: List[ARDError] = []

    def create_error(self, error_code: int, error_message: str, details: Dict = None) -> ARDError:
        """
        创建错误

        Args:
            error_code: 错误码
            error_message: 错误消息
            details: 详细信息

        Returns:
            ARD 错误
        """
        error = ARDError(
            error_code=error_code,
            error_message=error_message,
            details=details,
        )
        self.error_log.append(error)
        return error

    def handle_error(self, error: ARDError) -> Tuple[bool, str]:
        """
        处理错误

        Args:
            error: ARD 错误

        Returns:
            (成功，消息)
        """
        # 记录错误
        print(f"[ARD Error] {error.error_code}: {error.error_message}")

        # 根据错误码处理
        if error.error_code == ARD_ERROR_INVALID_REQUEST:
            return False, "请求无效"
        elif error.error_code == ARD_ERROR_AUTH_FAILED:
            return False, "认证失败"
        elif error.error_code == ARD_ERROR_RATE_LIMIT:
            return False, "请求频率限制"
        elif error.error_code == ARD_ERROR_INTERNAL_ERROR:
            return False, "内部错误"
        elif error.error_code == ARD_ERROR_NOT_FOUND:
            return False, "资源未找到"
        elif error.error_code == ARD_ERROR_TIMEOUT:
            return False, "请求超时"
        else:
            return False, f"未知错误: {error.error_code}"

    def get_error_log(self, limit: int = 20) -> List[Dict]:
        """获取错误日志"""
        return [e.to_dict() for e in self.error_log[-limit:]]

    def get_error_statistics(self) -> Dict:
        """获取错误统计"""
        error_counts = {}
        for error in self.error_log:
            error_counts[error.error_code] = error_counts.get(error.error_code, 0) + 1

        return {
            "total_errors": len(self.error_log),
            "error_counts": error_counts,
        }


# ========== ARD 性能优化 ==========

class ARDPerformanceOptimizer:
    """ARD 性能优化器"""

    def __init__(self):
        self.performance_log: List[ARDPerformance] = []
        self.cache: Dict[str, Any] = {}
        self.cache_ttl: int = 300  # 缓存 TTL（秒）

    def record_performance(self, operation: str, duration_ms: float, success: bool, metadata: Dict = None):
        """
        记录性能指标

        Args:
            operation: 操作名称
            duration_ms: 耗时（毫秒）
            success: 是否成功
            metadata: 元数据
        """
        performance = ARDPerformance(
            operation=operation,
            duration_ms=duration_ms,
            success=success,
            metadata=metadata or {},
        )
        self.performance_log.append(performance)

    def get_performance_statistics(self) -> Dict:
        """获取性能统计"""
        if not self.performance_log:
            return {
                "total_operations": 0,
                "avg_duration_ms": 0,
                "max_duration_ms": 0,
                "min_duration_ms": 0,
                "success_rate": 0,
            }

        durations = [p.duration_ms for p in self.performance_log]
        success_count = sum(1 for p in self.performance_log if p.success)

        return {
            "total_operations": len(self.performance_log),
            "avg_duration_ms": sum(durations) / len(durations),
            "max_duration_ms": max(durations),
            "min_duration_ms": min(durations),
            "success_rate": success_count / len(self.performance_log),
        }

    def cache_get(self, key: str) -> Optional[Any]:
        """
        获取缓存

        Args:
            key: 缓存键

        Returns:
            缓存值
        """
        if key in self.cache:
            value, timestamp = self.cache[key]
            # 检查过期
            if (datetime.now() - timestamp).total_seconds() < self.cache_ttl:
                return value
            else:
                del self.cache[key]
        return None

    def cache_set(self, key: str, value: Any):
        """
        设置缓存

        Args:
            key: 缓存键
            value: 缓存值
        """
        self.cache[key] = (value, datetime.now())

    def cache_clear(self):
        """清空缓存"""
        self.cache.clear()

    def optimize_discover(self, ard_gateway: ARDGateway, criteria: Dict) -> List:
        """
        优化发现操作（使用缓存）

        Args:
            ard_gateway: ARD 网关
            criteria: 发现标准

        Returns:
            发现结果
        """
        # 生成缓存键
        cache_key = f"discover:{hashlib.md5(json.dumps(criteria, sort_keys=True).encode()).hexdigest()}"

        # 检查缓存
        cached_result = self.cache_get(cache_key)
        if cached_result is not None:
            self.record_performance("discover", 0.1, True, {"cached": True})
            return cached_result

        # 执行发现
        start_time = time.time()
        result = ard_gateway.ard_protocol.discover_agents(criteria)
        duration_ms = (time.time() - start_time) * 1000

        # 缓存结果
        self.cache_set(cache_key, result)

        # 记录性能
        self.record_performance("discover", duration_ms, True, {"cached": False, "count": len(result)})

        return result

    def optimize_match(self, ard_gateway: ARDGateway, task_id: str, match_algorithm: str = "hybrid") -> Tuple[bool, str, List[str]]:
        """
        优化匹配操作（使用缓存）

        Args:
            ard_gateway: ARD 网关
            task_id: 任务 ID
            match_algorithm: 匹配算法

        Returns:
            (成功，消息，匹配的 Agent ID 列表)
        """
        # 生成缓存键
        cache_key = f"match:{task_id}:{match_algorithm}"

        # 检查缓存
        cached_result = self.cache_get(cache_key)
        if cached_result is not None:
            self.record_performance("match", 0.1, True, {"cached": True})
            return cached_result

        # 执行匹配
        start_time = time.time()
        ok, msg, matched_agents = ard_gateway.ard_protocol.match_agents(task_id, match_algorithm)
        duration_ms = (time.time() - start_time) * 1000

        # 缓存结果
        if ok:
            self.cache_set(cache_key, (ok, msg, matched_agents))

        # 记录性能
        self.record_performance("match", duration_ms, ok, {"cached": False})

        return ok, msg, matched_agents


# ========== ARD 安全增强网关 ==========

class ARDSecurityGateway(ARDGateway):
    """ARD 安全增强网关"""

    def __init__(self, ard_protocol: ARDProtocol, data_dir: str = "/shared/lobster-network-data/ard-security-gateway"):
        super().__init__(ard_protocol, data_dir)

        # 初始化安全组件
        self.security = ARDSecurity(data_dir=os.path.join(data_dir, "security"))
        self.error_handler = ARDErrorHandler()
        self.performance_optimizer = ARDPerformanceOptimizer()

    def send_secure_message(
        self,
        msg_type: str,
        sender_id: str,
        receiver_id: str,
        payload: Dict,
        key_id: str = "",
    ) -> Tuple[bool, str]:
        """
        发送安全 ARD 消息

        Args:
            msg_type: 消息类型
            sender_id: 发送方 ID
            receiver_id: 接收方 ID
            payload: 消息载荷
            key_id: 密钥 ID

        Returns:
            (成功，消息)
        """
        # 发送消息
        ok, msg = self.send_message(msg_type, sender_id, receiver_id, payload)
        if not ok:
            return ok, msg

        # 获取消息
        message = self.receive_message(msg.split("(")[1].split(")")[0] if "(" in msg else f"ard-msg-{self._message_counter:06d}")
        if not message:
            return False, "消息未找到"

        # 签名消息
        if key_id:
            ok, msg = self.security.sign_message(message, key_id)
            if not ok:
                return ok, msg

        return True, f"安全消息 {message.message_id} 发送成功"

    def process_secure_message(self, message: ARDMessage) -> Tuple[bool, str]:
        """
        处理安全 ARD 消息

        Args:
            message: ARD 消息

        Returns:
            (成功，消息)
        """
        # 验证签名
        if message.signature:
            # 获取发送方公钥
            public_key = self._get_public_key(message.sender_id)
            if public_key:
                ok, msg = self.security.verify_message(message, public_key)
                if not ok:
                    error = self.error_handler.create_error(
                        error_code=ARD_ERROR_AUTH_FAILED,
                        error_message="消息签名验证失败",
                        details={"message_id": message.message_id},
                    )
                    return self.error_handler.handle_error(error)

        # 性能优化
        start_time = time.time()
        ok, msg = self.process_message(message)
        duration_ms = (time.time() - start_time) * 1000

        # 记录性能
        self.performance_optimizer.record_performance(
            operation=f"process_{message.msg_type}",
            duration_ms=duration_ms,
            success=ok,
            metadata={"message_id": message.message_id},
        )

        return ok, msg

    def _get_public_key(self, sender_id: str) -> Optional[str]:
        """获取发送方公钥"""
        # 简化实现：从端点获取
        for endpoint in self.endpoints.values():
            if endpoint.endpoint_id == sender_id:
                return endpoint.metadata.get("public_key")
        return None

    def get_security_statistics(self) -> Dict:
        """获取安全统计"""
        return {
            "total_keys": len(self.security.key_pairs),
            "total_errors": len(self.error_handler.error_log),
            "error_statistics": self.error_handler.get_error_statistics(),
            "performance_statistics": self.performance_optimizer.get_performance_statistics(),
        }