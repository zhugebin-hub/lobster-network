"""
测试节点能力发现协议
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from lobster_network.discovery import NodeCapability, CapabilityDiscovery
from lobster_network.registry import NodeRegistry


class TestNodeCapability:
    """测试 NodeCapability 类"""
    
    def test_create_and_serialize(self):
        """测试创建和序列化"""
        cap = NodeCapability(
            node_id="test-001",
            name="测试节点",
            capabilities=["dialogue", "research"],
            knowledge_domains=["python", "ai"],
            eight_dim_scores={"understanding": 0.85, "execution": 0.90},
        )
        
        d = cap.to_dict()
        assert d["node_id"] == "test-001"
        assert d["name"] == "测试节点"
        assert "dialogue" in d["capabilities"]
        assert "python" in d["knowledge_domains"]
        assert d["eight_dim_scores"]["understanding"] == 0.85
    
    def test_deserialize(self):
        """测试反序列化"""
        data = {
            "node_id": "test-002",
            "name": "测试节点2",
            "capabilities": ["code_generation"],
            "knowledge_domains": ["go"],
            "eight_dim_scores": {"reasoning": 0.80},
            "last_updated": "2026-06-25T00:00:00",
        }
        
        cap = NodeCapability.from_dict(data)
        assert cap.node_id == "test-002"
        assert cap.name == "测试节点2"
        assert cap.eight_dim_scores["reasoning"] == 0.80
    
    def test_matches_task(self):
        """测试任务匹配度计算"""
        cap = NodeCapability(
            node_id="test-003",
            name="测试节点3",
            capabilities=["dialogue", "code_generation", "teaching"],
            knowledge_domains=["python", "ppt"],
            eight_dim_scores={
                "understanding": 0.85,
                "execution": 0.90,
                "reasoning": 0.80,
                "reflection": 0.75,
                "tooling": 0.88,
                "eq": 0.82,
                "memory": 0.78,
                "retrieval": 0.86,
            },
        )
        
        # 完全匹配
        score1 = cap.matches_task(["code_generation"], "python")
        assert score1 > 0.5
        
        # 部分匹配
        score2 = cap.matches_task(["code_generation", "research"], "python")
        assert score2 > 0.4
        
        # 不匹配
        score3 = cap.matches_task(["data_analysis"], "java")
        assert score3 < 0.5


class TestCapabilityDiscovery:
    """测试 CapabilityDiscovery 类"""
    
    def test_announce_and_save(self, tmp_path):
        """测试广播和保存能力"""
        # 创建模拟的 registry 和 messenger
        class MockRegistry:
            def list_nodes(self, status="active"):
                return []
        
        class MockMessenger:
            def send(self, **kwargs):
                return "msg_123"
        
        registry = MockRegistry()
        messenger = MockMessenger()
        
        discovery = CapabilityDiscovery(
            registry, messenger,
            node_id="test-001",
            data_dir=str(tmp_path),
        )
        
        cap = NodeCapability(
            node_id="test-001",
            name="测试节点",
            capabilities=["dialogue"],
            knowledge_domains=["python"],
            eight_dim_scores={"understanding": 0.85},
        )
        
        discovery.announce_capabilities(cap)
        
        # 检查文件是否保存
        cap_file = tmp_path / "test-001_capability.json"
        assert cap_file.exists()
        
        # 检查内容
        import json
        with open(cap_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["node_id"] == "test-001"
    
    def test_load_capability(self, tmp_path):
        """测试加载能力描述"""
        # 先保存一个能力描述
        import json
        cap_data = {
            "node_id": "test-002",
            "name": "测试节点2",
            "capabilities": ["research"],
            "knowledge_domains": ["ai"],
            "eight_dim_scores": {"reasoning": 0.80},
            "last_updated": "2026-06-25T00:00:00",
        }
        cap_file = tmp_path / "test-002_capability.json"
        with open(cap_file, "w", encoding="utf-8") as f:
            json.dump(cap_data, f, ensure_ascii=False, indent=2)
        
        # 创建 discovery 并加载
        class MockRegistry:
            def list_nodes(self, status="active"):
                return []
        
        class MockMessenger:
            def send(self, **kwargs):
                return "msg_123"
        
        discovery = CapabilityDiscovery(
            MockRegistry(), MockMessenger(),
            node_id="test-001",
            data_dir=str(tmp_path),
        )
        
        cap = discovery._load_capability("test-002")
        assert cap is not None
        assert cap.node_id == "test-002"
        assert cap.name == "测试节点2"
        assert cap.eight_dim_scores["reasoning"] == 0.80


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
