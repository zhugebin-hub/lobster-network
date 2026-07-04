#!/usr/bin/env python3
"""
硬护栏系统
基于 Agent Harness工程实践设计（借鉴悟空 AI 招聘经验）

三层硬护栏：
- 第 1 层：白名单工具（只能调发消息工具，禁用撤回/群发）
- 第 2 层：Linter 拦截（所有外发消息先过敏感词/合规规则）
- 第 3 层：第二个 Agent 审稿（独立 Context 判断是否冒犯/暴露敏感信息）
"""

import json
import os
import re
import time
from pathlib import Path
from typing import Dict, List, Optional


class ToolWhitelist:
    """
    第 1 层：白名单工具
    限制 Agent 只能调用特定工具
    """
    
    def __init__(self, allowed_tools: List[str]):
        self.allowed_tools = allowed_tools
    
    def is_allowed(self, tool_name: str) -> bool:
        """检查工具是否在白名单中"""
        return tool_name in self.allowed_tools
    
    def get_allowed_tools(self) -> List[str]:
        """获取允许的工具列表"""
        return self.allowed_tools.copy()


class ContentLinter:
    """
    第 2 层：内容 Linter
    检查敏感词、合规规则
    """
    
    def __init__(self, config: Dict = None):
        if config is None:
            config = {
                "sensitive_words": ["密码", "账号", "薪资", "录用", "承诺"],
                "max_length": 500,
                "require_review": True
            }
        
        self.config = config
        self.sensitive_pattern = re.compile(
            "|".join(re.escape(word) for word in config.get("sensitive_words", []))
        )
    
    def check(self, content: str) -> Dict:
        """
        检查内容
        
        Args:
            content: 待检查内容
            
        Returns:
            Dict: 检查结果
        """
        issues = []
        
        # 检查敏感词
        sensitive_matches = self.sensitive_pattern.findall(content)
        if sensitive_matches:
            issues.append({
                "type": "sensitive_word",
                "message": f"包含敏感词: {', '.join(sensitive_matches)}",
                "severity": "high"
            })
        
        # 检查长度
        max_length = self.config.get("max_length", 500)
        if len(content) > max_length:
            issues.append({
                "type": "length_exceeded",
                "message": f"内容长度 {len(content)} 超过限制 {max_length}",
                "severity": "medium"
            })
        
        # 检查是否需要审核
        require_review = self.config.get("require_review", True)
        if require_review and issues:
            issues.append({
                "type": "requires_review",
                "message": "内容需要人工审核",
                "severity": "info"
            })
        
        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "checked_at": time.time()
        }


class ReviewAgent:
    """
    第 3 层：审核 Agent
    独立 Context 审核内容
    """
    
    def __init__(self, workspace_dir: str):
        self.workspace_dir = Path(workspace_dir) / "review_agent"
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        
        # 审核规则
        self.review_rules = [
            "不冒犯用户",
            "不暴露薪资信息",
            "不暗示录用",
            "不承诺无法保证的事项",
            "使用礼貌用语"
        ]
    
    def review(self, content: str, context: Dict = None) -> Dict:
        """
        审核内容
        
        Args:
            content: 待审核内容
            context: 上下文信息
            
        Returns:
            Dict: 审核结果
        """
        print(f"[ReviewAgent] 审核内容: {content[:50]}...")
        
        issues = []
        
        # 检查是否冒犯
        if self._check_offensive(content):
            issues.append({
                "type": "offensive",
                "message": "内容可能冒犯用户",
                "severity": "high"
            })
        
        # 检查是否暴露敏感信息
        if self._check_sensitive_info(content):
            issues.append({
                "type": "sensitive_info",
                "message": "内容可能暴露敏感信息",
                "severity": "high"
            })
        
        # 检查是否暗示录用
        if self._check_hiring_hint(content):
            issues.append({
                "type": "hiring_hint",
                "message": "内容可能暗示录用",
                "severity": "medium"
            })
        
        # 保存审核记录
        self._save_review_record(content, issues)
        
        return {
            "approved": len(issues) == 0,
            "issues": issues,
            "reviewed_at": time.time()
        }
    
    def _check_offensive(self, content: str) -> bool:
        """检查是否冒犯"""
        offensive_words = ["笨", "傻", "蠢", "白痴", "智商"]
        return any(word in content for word in offensive_words)
    
    def _check_sensitive_info(self, content: str) -> bool:
        """检查是否暴露敏感信息"""
        sensitive_patterns = [
            r"薪资\s*[:：]\s*\d+",
            r"工资\s*[:：]\s*\d+",
            r"密码\s*[:：]\s*\S+",
            r"账号\s*[:：]\s*\S+"
        ]
        return any(re.search(pattern, content) for pattern in sensitive_patterns)
    
    def _check_hiring_hint(self, content: str) -> bool:
        """检查是否暗示录用"""
        hiring_words = ["录用", "录取", "通过", "合格", "确定"]
        return any(word in content for word in hiring_words)
    
    def _save_review_record(self, content: str, issues: List[Dict]):
        """保存审核记录"""
        record_file = self.workspace_dir / f"review_{int(time.time())}.json"
        with open(record_file, 'w', encoding='utf-8') as f:
            json.dump({
                "content": content,
                "issues": issues,
                "reviewed_at": time.time()
            }, f, ensure_ascii=False, indent=2)


class HardGuardrail:
    """
    硬护栏系统
    三层审核机制
    """
    
    def __init__(self, workspace_dir: str = None):
        if workspace_dir is None:
            workspace_dir = os.path.join(os.path.dirname(__file__), "..", "workspace")
        
        self.workspace_dir = Path(workspace_dir)
        
        # 第 1 层：白名单工具
        self.tool_whitelist = ToolWhitelist([
            "send_message",
            "send_notification",
            "query_data",
            "generate_report"
        ])
        
        # 第 2 层：内容 Linter
        self.content_linter = ContentLinter()
        
        # 第 3 层：审核 Agent
        self.review_agent = ReviewAgent(str(self.workspace_dir))
    
    def validate_tool_call(self, tool_name: str) -> bool:
        """
        验证工具调用（第 1 层）
        
        Args:
            tool_name: 工具名称
            
        Returns:
            bool: 是否允许调用
        """
        return self.tool_whitelist.is_allowed(tool_name)
    
    def validate_content(self, content: str) -> Dict:
        """
        验证内容（第 2 层 + 第 3 层）
        
        Args:
            content: 待验证内容
            
        Returns:
            Dict: 验证结果
        """
        # 第 2 层：Linter 检查
        linter_result = self.content_linter.check(content)
        
        if not linter_result["passed"]:
            return {
                "passed": False,
                "layer": "linter",
                "issues": linter_result["issues"]
            }
        
        # 第 3 层：审核 Agent
        review_result = self.review_agent.review(content)
        
        if not review_result["approved"]:
            return {
                "passed": False,
                "layer": "review_agent",
                "issues": review_result["issues"]
            }
        
        return {
            "passed": True,
            "layer": "all",
            "issues": []
        }
    
    def validate_and_execute(self, tool_name: str, content: str) -> Dict:
        """
        验证并执行
        
        Args:
            tool_name: 工具名称
            content: 内容
            
        Returns:
            Dict: 执行结果
        """
        # 第 1 层：工具白名单
        if not self.validate_tool_call(tool_name):
            return {
                "status": "blocked",
                "layer": "tool_whitelist",
                "message": f"工具 {tool_name} 不在白名单中"
            }
        
        # 第 2+3 层：内容审核
        content_result = self.validate_content(content)
        if not content_result["passed"]:
            return {
                "status": "blocked",
                "layer": content_result["layer"],
                "issues": content_result["issues"]
            }
        
        # 所有检查通过，执行
        return {
            "status": "executed",
            "tool": tool_name,
            "message": "内容审核通过，已执行"
        }


if __name__ == "__main__":
    # 测试硬护栏系统
    guardrail = HardGuardrail()
    
    # 测试 1：允许的工具 + 安全内容
    print("\n=== 测试 1: 允许的工具 + 安全内容 ===")
    result = guardrail.validate_and_execute("send_message", "您好，请问有什么可以帮助您的？")
    print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    # 测试 2：禁止的工具
    print("\n=== 测试 2: 禁止的工具 ===")
    result = guardrail.validate_and_execute("delete_user", "删除用户")
    print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    # 测试 3：敏感内容
    print("\n=== 测试 3: 敏感内容 ===")
    result = guardrail.validate_and_execute("send_message", "您的薪资是 10000 元，我们决定录用您")
    print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    # 测试 4：冒犯内容
    print("\n=== 测试 4: 冒犯内容 ===")
    result = guardrail.validate_and_execute("send_message", "你真笨，这都不会")
    print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
EOF

echo "硬护栏系统已创建"