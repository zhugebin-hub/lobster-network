"""
测试 Clawvard 学习器
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from lobster_network.learning import ClawvardLearner
from lobster_network.assessment.clawvard_bridge import PracticeSession, PracticeQuestion


class TestClawvardLearner:
    """测试 ClawvardLearner 类"""
    
    def test_init(self, tmp_path):
        """测试初始化"""
        learner = ClawvardLearner(
            node_id="test-001",
            agent_name="测试节点",
            data_dir=str(tmp_path),
        )
        
        assert learner.node_id == "test-001"
        assert learner.agent_name == "测试节点"
        assert learner.data_dir.exists()
    
    def test_create_mock_practice(self, tmp_path):
        """测试创建模拟练习"""
        learner = ClawvardLearner(
            node_id="test-001",
            agent_name="测试节点",
            data_dir=str(tmp_path),
        )
        
        session = learner._create_mock_practice_session(dimensions=["reasoning", "execution"])
        
        assert session.practice_id != ""
        assert len(session.questions) == 2  # reasoning + execution
        assert session.agent_name == "测试节点"
    
    def test_save_and_load(self, tmp_path):
        """测试保存和加载"""
        learner = ClawvardLearner(
            node_id="test-001",
            agent_name="测试节点",
            data_dir=str(tmp_path),
        )
        
        # 创建模拟会话
        session = learner._create_mock_practice_session(["reasoning"])
        
        # 保存会话
        learner._save_practice_session(session)
        
        # 检查文件是否存在
        practice_file = tmp_path / f"practice_{session.practice_id}.json"
        assert practice_file.exists()
        
        # 加载并检查内容
        import json
        with open(practice_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        assert data["practice_id"] == session.practice_id
        assert data["agent_name"] == "测试节点"
        assert len(data["questions"]) == 1


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
