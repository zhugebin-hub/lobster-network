#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OADP-Science 科学智能体标准化对接协议模块

基于小龙虾网络 OADP (Open Agent Discovery Protocol) 扩展，
提供科学任务专用消息类型、能力封装规范和三层安全护栏。
"""

from .oadp_science import (
    ScienceMessageType,
    ScienceCapability,
    ScienceMessage,
    ScienceHarness,
    OADPScienceProtocol,
)

__all__ = [
    "ScienceMessageType",
    "ScienceCapability",
    "ScienceMessage",
    "ScienceHarness",
    "OADPScienceProtocol",
]
