#!/usr/bin/env python3
"""
ARD 协议测试脚本

功能：
- 测试 ARD 协议基本功能
- 测试 Agent 发现
- 测试资源发现
- 测试任务协同

使用方法：
    python3 tests/test_ard_protocol.py [--verbose]
"""

import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from src.lobster_network.ard_protocol import ARDProtocol, ARDMessage
    from src.lobster_network.ard_gateway import ARDGateway
    from src.lobster_network.ard_match import ARDMatcher
    from src.lobster_network.ard_security import ARDSecurity
    ARD_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  ARD 模块导入失败：{e}")
    ARD_AVAILABLE = False

VERBOSE = False

def parse_args():
    """解析命令行参数"""
    global VERBOSE
    for arg in sys.argv[1:]:
        if arg == "--verbose":
            VERBOSE = True

def test_ard_protocol():
    """测试 ARD 协议基本功能"""
    print("\n📡 测试 ARD 协议基本功能...")
    
    if not ARD_AVAILABLE:
        print("  ⚠️  ARD 模块不可用，跳过测试")
        return True
    
    try:
        # 创建 ARD 协议实例
        protocol = ARDProtocol()
        
        # 创建测试消息
        message = ARDMessage(
            message_id="test-001",
            sender_id="xiaochen",
            receiver_id="hermes",
            message_type="discovery",
            payload={
                "agent_type": "assistant",
                "capabilities": ["code", "analysis"],
                "knowledge": ["AI", "blockchain"]
            }
        )
        
        # 序列化消息
        serialized = protocol.serialize(message)
        if VERBOSE:
            print(f"  序列化消息：{serialized[:100]}...")
        
        # 反序列化消息
        deserialized = protocol.deserialize(serialized)
        if deserialized.message_id == message.message_id:
            print("  ✅ 消息序列化/反序列化测试通过")
            return True
        else:
            print("  ❌ 消息序列化/反序列化测试失败")
            return False
            
    except Exception as e:
        print(f"  ❌ ARD 协议测试失败：{e}")
        return False

def test_agent_discovery():
    """测试 Agent 发现"""
    print("\n🔍 测试 Agent 发现...")
    
    if not ARD_AVAILABLE:
        print("  ⚠️  ARD 模块不可用，跳过测试")
        return True
    
    try:
        gateway = ARDGateway()
        
        # 注册测试 Agent
        agents = [
            {
                "id": "xiaochen",
                "name": "小陈",
                "type": "agent",
                "capabilities": ["code", "analysis"],
                "knowledge": ["AI", "blockchain"]
            },
            {
                "id": "hermes",
                "name": "诸葛马",
                "type": "coach",
                "capabilities": ["management", "architecture"],
                "knowledge": ["project", "system"]
            }
        ]
        
        for agent in agents:
            gateway.register_agent(agent)
        
        # 测试发现
        discovered = gateway.discover_agents({"capabilities": ["code"]})
        if len(discovered) > 0:
            print(f"  ✅ 发现 {len(discovered)} 个 Agent")
            if VERBOSE:
                for agent in discovered:
                    print(f"    - {agent['name']} ({agent['id']})")
            return True
        else:
            print("  ❌ 未发现 Agent")
            return False
            
    except Exception as e:
        print(f"  ❌ Agent 发现测试失败：{e}")
        return False

def test_resource_discovery():
    """测试资源发现"""
    print("\n📦 测试资源发现...")
    
    if not ARD_AVAILABLE:
        print("  ⚠️  ARD 模块不可用，跳过测试")
        return True
    
    try:
        gateway = ARDGateway()
        
        # 注册测试资源
        resources = [
            {
                "id": "resource-001",
                "name": "代码库",
                "type": "repository",
                "url": "https://github.com/zhugebin-hub/lobster-network",
                "capabilities": ["code", "documentation"]
            },
            {
                "id": "resource-002",
                "name": "数据集",
                "type": "dataset",
                "url": "https://example.com/dataset",
                "capabilities": ["data", "analysis"]
            }
        ]
        
        for resource in resources:
            gateway.register_resource(resource)
        
        # 测试发现
        discovered = gateway.discover_resources({"type": "repository"})
        if len(discovered) > 0:
            print(f"  ✅ 发现 {len(discovered)} 个资源")
            if VERBOSE:
                for resource in discovered:
                    print(f"    - {resource['name']} ({resource['type']})")
            return True
        else:
            print("  ❌ 未发现资源")
            return False
            
    except Exception as e:
        print(f"  ❌ 资源发现测试失败：{e}")
        return False

def test_task_collaboration():
    """测试任务协同"""
    print("\n🤝 测试任务协同...")
    
    if not ARD_AVAILABLE:
        print("  ⚠️  ARD 模块不可用，跳过测试")
        return True
    
    try:
        matcher = ARDMatcher()
        
        # 创建测试任务
        task = {
            "id": "task-001",
            "name": "代码审查",
            "type": "code_review",
            "requirements": {
                "capabilities": ["code", "review"],
                "knowledge": ["python", "architecture"]
            }
        }
        
        # 创建测试 Agent
        agent = {
            "id": "xiaochen",
            "name": "小陈",
            "capabilities": ["code", "review", "analysis"],
            "knowledge": ["python", "architecture", "AI"]
        }
        
        # 测试匹配
        match = matcher.match_task(task, agent)
        if match["score"] > 0.5:
            print(f"  ✅ 任务匹配成功（得分：{match['score']:.2f}）")
            if VERBOSE:
                print(f"    匹配详情：{match}")
            return True
        else:
            print(f"  ❌ 任务匹配失败（得分：{match['score']:.2f}）")
            return False
            
    except Exception as e:
        print(f"  ❌ 任务协同测试失败：{e}")
        return False

def generate_test_report(results: dict):
    """生成测试报告"""
    print("\n" + "="*60)
    print("🦞 ARD 协议测试报告")
    print("="*60)
    print(f"测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed
    
    print(f"总测试数：{total}")
    print(f"通过：{passed}")
    print(f"失败：{failed}")
    print()
    
    for test_name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print("="*60)
    
    return failed == 0

def main():
    """主函数"""
    parse_args()
    
    print("🧪 开始 ARD 协议测试...")
    
    results = {}
    
    # 运行测试
    results["ARD 协议基本功能"] = test_ard_protocol()
    results["Agent 发现"] = test_agent_discovery()
    results["资源发现"] = test_resource_discovery()
    results["任务协同"] = test_task_collaboration()
    
    # 生成报告
    all_passed = generate_test_report(results)
    
    # 返回状态码
    if all_passed:
        print("\n🎉 所有测试通过！")
        sys.exit(0)
    else:
        print("\n⚠️  部分测试失败")
        sys.exit(1)

if __name__ == "__main__":
    main()
