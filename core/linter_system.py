#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Linter 约束系统 - 实现铁律四：能写成 Linter 的约束，别写成文档
功能：
1. 训练任务 Linter（超时检查、工具调用限制）
2. 通信 Linter（ACK 超时、外发消息合规）
3. 工具调用 Linter（签名验证、权限检查）

作者：信电大虾 (小龙虾网络)
日期：2026-06-30
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

# 路径配置
REPO_ROOT = Path(__file__).parent.parent
WORKSPACE_DIR = REPO_ROOT / ".shared" / "workspace"
LOCKS_DIR = WORKSPACE_DIR / "locks"


class TrainingLinter:
    """训练任务 Linter"""
    
    # 约束配置
    TIMEOUT_HOURS = 24          # 训练任务超时时间
    MAX_TOOL_CALLS = 5          # 最大工具调用次数
    MIN_ACCURACY = 0.50         # 最低准确率
    MAX_PROBLEMS = 200          # 最大题目数量
    MAX_GAMES = 20              # 最大对局数量
    
    def check_timeout(self, task: Dict) -> bool:
        """检查任务是否超时"""
        created_str = task.get('created_at', datetime.now().isoformat())
        # Python 3.6 兼容
        try:
            created = datetime.fromisoformat(created_str)
        except AttributeError:
            created = datetime.strptime(created_str, "%Y-%m-%dT%H:%M:%S.%f")
            
        timeout = timedelta(hours=self.TIMEOUT_HOURS)
        
        if datetime.now() - created > timeout:
            raise TaskTimeoutError(f"任务 {task.get('task_id', 'unknown')} 已超时 {int((datetime.now() - created).total_seconds() / 3600)}小时")
        return True
        
    def check_tool_calls(self, task: Dict) -> bool:
        """检查工具调用次数"""
        tool_calls = len(task.get('tool_calls', []))
        if tool_calls > self.MAX_TOOL_CALLS:
            raise ToolLimitError(f"工具调用超过限制：{tool_calls}/{self.MAX_TOOL_CALLS}")
        return True
        
    def check_accuracy(self, result: Dict) -> bool:
        """检查准确率"""
        accuracy = result.get('accuracy', 0)
        if accuracy < self.MIN_ACCURACY:
            raise AccuracyError(f"准确率过低：{accuracy:.0%} < {self.MIN_ACCURACY:.0%}")
        return True
        
    def check_problem_count(self, task: Dict) -> bool:
        """检查题目数量"""
        problem_count = task.get('problem_count', 0)
        if problem_count > self.MAX_PROBLEMS:
            raise ProblemCountError(f"题目数量超过限制：{problem_count}/{self.MAX_PROBLEMS}")
        return True
        
    def check_game_count(self, task: Dict) -> bool:
        """检查对局数量"""
        game_count = task.get('game_count', 0)
        if game_count > self.MAX_GAMES:
            raise GameCountError(f"对局数量超过限制：{game_count}/{self.MAX_GAMES}")
        return True
        
    def validate_task(self, task: Dict) -> Dict:
        """验证任务合法性"""
        results = {
            "task_id": task.get("task_id"),
            "valid": True,
            "errors": []
        }
        
        try:
            self.check_timeout(task)
            self.check_tool_calls(task)
            self.check_problem_count(task)
            self.check_game_count(task)
        except Exception as e:
            results["valid"] = False
            results["errors"].append(str(e))
            
        return results
        
    def validate_result(self, result: Dict) -> Dict:
        """验证结果合法性"""
        results = {
            "task_id": result.get("task_id"),
            "valid": True,
            "errors": []
        }
        
        try:
            self.check_accuracy(result)
        except Exception as e:
            results["valid"] = False
            results["errors"].append(str(e))
            
        return results


class CommunicationLinter:
    """通信 Linter"""
    
    # 约束配置
    ACK_TIMEOUT_HOURS = 4       # ACK 超时时间
    MESSAGE_LENGTH_LIMIT = 2000 # 消息长度限制
    
    # 白名单工具
    ALLOWED_TOOLS = [
        "send_message",
        "receive_message",
        "ack_message"
    ]
    
    # 敏感词列表
    SENSITIVE_WORDS = [
        "机密", "秘密", "内部", "禁止", "限制"
    ]
    
    def check_ack_timeout(self, message: Dict) -> bool:
        """检查 ACK 超时"""
        sent_str = message.get('sent_at', datetime.now().isoformat())
        # Python 3.6 兼容
        try:
            sent = datetime.fromisoformat(sent_str)
        except AttributeError:
            sent = datetime.strptime(sent_str, "%Y-%m-%dT%H:%M:%S.%f")
            
        timeout = timedelta(hours=self.ACK_TIMEOUT_HOURS)
        
        if datetime.now() - sent > timeout and not message.get('acked'):
            raise AckTimeoutError(f"消息 {message.get('msg_id', 'unknown')} ACK 超时 {int((datetime.now() - sent).total_seconds() / 3600)}小时")
        return True
        
    def check_message_length(self, message: Dict) -> bool:
        """检查消息长度"""
        content = message.get('content', '')
        if len(content) > self.MESSAGE_LENGTH_LIMIT:
            raise MessageLengthError(f"消息长度超过限制：{len(content)}/{self.MESSAGE_LENGTH_LIMIT}")
        return True
        
    def check_external_message(self, message: Dict) -> bool:
        """检查外发消息合规性（三层护栏）"""
        # 第 1 层：白名单工具检查
        tool = message.get('tool', '')
        if tool not in self.ALLOWED_TOOLS:
            raise UnauthorizedToolError(f"工具 {tool} 未授权")
            
        # 第 2 层：敏感词检查
        content = message.get('content', '')
        for word in self.SENSITIVE_WORDS:
            if word in content:
                raise SensitiveContentError(f"包含敏感词：{word}")
                
        # 第 3 层：合规检查
        if not self._compliance_check(content):
            raise ComplianceError("消息内容不合规")
            
        return True
        
    def _compliance_check(self, content: str) -> bool:
        """合规检查"""
        # 检查是否包含不当承诺
        inappropriate_promises = [
            "保证", "承诺", "一定", "绝对"
        ]
        for promise in inappropriate_promises:
            if promise in content:
                return False
                
        # 检查是否暴露敏感信息
        sensitive_info = [
            "薪资", "工资", "待遇", "内部数据"
        ]
        for info in sensitive_info:
            if info in content:
                return False
                
        return True
        
    def validate_message(self, message: Dict) -> Dict:
        """验证消息合法性"""
        results = {
            "msg_id": message.get("msg_id"),
            "valid": True,
            "errors": []
        }
        
        try:
            self.check_ack_timeout(message)
            self.check_message_length(message)
            
            # 如果是外发消息，额外检查
            if message.get("direction") == "outbound":
                self.check_external_message(message)
                
        except Exception as e:
            results["valid"] = False
            results["errors"].append(str(e))
            
        return results


class ToolLinter:
    """工具调用 Linter"""
    
    # 工具签名定义
    TOOL_SIGNATURES = {
        "schedule_training": {
            "description": "调度训练任务",
            "parameters": {
                "student_id": {"type": "str", "description": "学员 ID"},
                "day": {"type": "int", "description": "训练天数"},
                "problem_count": {"type": "int", "description": "题目数量"},
                "game_count": {"type": "int", "description": "对局数量"}
            },
            "returns": {
                "task_id": "str",
                "status": "str",
                "scheduled_at": "str"
            }
        },
        "evaluate_performance": {
            "description": "评估训练表现",
            "parameters": {
                "student_id": {"type": "str", "description": "学员 ID"},
                "task_id": {"type": "str", "description": "任务 ID"}
            },
            "returns": {
                "accuracy": "float",
                "rating": "str",
                "feedback": "str"
            }
        }
    }
    
    def validate_tool_call(self, tool_name: str, parameters: Dict) -> Dict:
        """验证工具调用"""
        results = {
            "tool": tool_name,
            "valid": True,
            "errors": []
        }
        
        # 检查工具是否存在
        if tool_name not in self.TOOL_SIGNATURES:
            results["valid"] = False
            results["errors"].append(f"工具 {tool_name} 不存在")
            return results
            
        # 检查参数
        signature = self.TOOL_SIGNATURES[tool_name]
        required_params = signature["parameters"]
        
        for param, config in required_params.items():
            if param not in parameters:
                results["valid"] = False
                results["errors"].append(f"缺少必需参数：{param}")
            elif not isinstance(parameters[param], eval(config["type"])):
                results["valid"] = False
                results["errors"].append(f"参数 {param} 类型错误：期望{config['type']}，实际{type(parameters[param]).__name__}")
                
        return results


# 自定义异常类
class TaskTimeoutError(Exception):
    pass
    
class ToolLimitError(Exception):
    pass
    
class AccuracyError(Exception):
    pass
    
class ProblemCountError(Exception):
    pass
    
class GameCountError(Exception):
    pass
    
class AckTimeoutError(Exception):
    pass
    
class MessageLengthError(Exception):
    pass
    
class UnauthorizedToolError(Exception):
    pass
    
class SensitiveContentError(Exception):
    pass
    
class ComplianceError(Exception):
    pass


def main():
    """主函数"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "test_training":
            # 测试训练 Linter
            linter = TrainingLinter()
            
            # 测试用例
            test_cases = [
                {
                    "task_id": "task_001",
                    "created_at": (datetime.now() - timedelta(hours=25)).isoformat(),
                    "tool_calls": ["tool1", "tool2", "tool3", "tool4", "tool5", "tool6"],
                    "problem_count": 250,
                    "game_count": 25
                },
                {
                    "task_id": "task_002",
                    "created_at": datetime.now().isoformat(),
                    "tool_calls": ["tool1", "tool2"],
                    "problem_count": 100,
                    "game_count": 10
                }
            ]
            
            print("=== 训练 Linter 测试 ===")
            for case in test_cases:
                result = linter.validate_task(case)
                print(f"\n任务 {result['task_id']}:")
                print(f"  合法：{result['valid']}")
                if result['errors']:
                    print(f"  错误：{result['errors']}")
                    
        elif command == "test_communication":
            # 测试通信 Linter
            linter = CommunicationLinter()
            
            # 测试用例
            test_cases = [
                {
                    "msg_id": "msg_001",
                    "sent_at": (datetime.now() - timedelta(hours=5)).isoformat(),
                    "acked": False,
                    "content": "这是一条测试消息",
                    "direction": "outbound",
                    "tool": "send_message"
                },
                {
                    "msg_id": "msg_002",
                    "sent_at": datetime.now().isoformat(),
                    "acked": True,
                    "content": "包含敏感词：机密信息",
                    "direction": "outbound",
                    "tool": "send_message"
                }
            ]
            
            print("=== 通信 Linter 测试 ===")
            for case in test_cases:
                result = linter.validate_message(case)
                print(f"\n消息 {result['msg_id']}:")
                print(f"  合法：{result['valid']}")
                if result['errors']:
                    print(f"  错误：{result['errors']}")
                    
        elif command == "test_tool":
            # 测试工具 Linter
            linter = ToolLinter()
            
            # 测试用例
            test_cases = [
                {
                    "tool": "schedule_training",
                    "parameters": {
                        "student_id": "xiaochen",
                        "day": 5,
                        "problem_count": 100,
                        "game_count": 10
                    }
                },
                {
                    "tool": "unknown_tool",
                    "parameters": {}
                },
                {
                    "tool": "schedule_training",
                    "parameters": {
                        "student_id": "xiaochen",
                        "day": "5"  # 类型错误
                    }
                }
            ]
            
            print("=== 工具 Linter 测试 ===")
            for case in test_cases:
                result = linter.validate_tool_call(case["tool"], case["parameters"])
                print(f"\n工具 {result['tool']}:")
                print(f"  合法：{result['valid']}")
                if result['errors']:
                    print(f"  错误：{result['errors']}")
                    
        else:
            print(f"未知命令：{command}")
    else:
        print("=== Linter 约束系统 ===")
        print("用法：")
        print("  python3 linter_system.py test_training")
        print("  python3 linter_system.py test_communication")
        print("  python3 linter_system.py test_tool")


if __name__ == "__main__":
    main()
