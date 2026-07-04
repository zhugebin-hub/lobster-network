#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Harness 安全护栏模块
三层硬护栏：L1 输入护栏 / L2 执行护栏 / L3 输出护栏

参考文档：
- 给野马套上缰绳_Agent_Harness工程实践
- 小龙虾网络_Harness_Engineering融合分析
"""

from .agent_harness import AgentHarness, HarnessResult

__all__ = ["AgentHarness", "HarnessResult"]
