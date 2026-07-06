#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 A2A 智能体间通信协议模块

基于 Google A2A 协议规范，实现 Agent Card / Task Object /
Agent Registry / 跨Agent消息路由等核心通信能力。
"""

from .a2a_protocol import (
    AgentCard,
    AgentCapability,
    AgentStatus,
    TaskObject,
    TaskStatus,
    AgentRegistry,
    MessageRouter,
    A2AProtocol,
)

__all__ = [
    "AgentCard",
    "AgentCapability",
    "AgentStatus",
    "TaskObject",
    "TaskStatus",
    "AgentRegistry",
    "MessageRouter",
    "A2AProtocol",
]
