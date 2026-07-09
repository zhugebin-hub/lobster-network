#!/usr/bin/env python3
"""
训练数据持久化管理器
增强功能：
- 自动保存训练结果
- 断点续传支持
- 训练进度追踪
- 数据备份与恢复
"""

import json
import time
import hashlib
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

class TrainingPersistence:
    """训练数据持久化管理器"""
    
    def __init__(self, workspace_dir: str = "workspace"):
        self.workspace_dir = Path(workspace_dir) / "training"
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        
        self.backup_dir = self.workspace_dir / "backup"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.index_file = self.workspace_dir / "training_index.json"
        self.index = self._load_index()
        
        print(f"[TrainingPersistence] 初始化完成，已加载 {len(self.index.get('agents', {}))} 个学员数据")
    
    def save_training_result(self, agent_id: str, result: Dict) -> bool:
        """保存训练结果"""
        try:
            # 确保学员目录存在
            agent_dir = self.workspace_dir / agent_id
            agent_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成文件名（带时间戳）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_file = agent_dir / f"result_{timestamp}.json"
            
            # 添加元数据
            result_with_meta = {
                **result,
                "metadata": {
                    "agent_id": agent_id,
                    "timestamp": time.time(),
                    "datetime": datetime.now().isoformat(),
                    "file_hash": hashlib.md5(json.dumps(result).encode()).hexdigest()
                }
            }
            
            # 保存结果
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result_with_meta, f, ensure_ascii=False, indent=2)
            
            # 更新索引
            self._update_index(agent_id, result_with_meta)
            
            # 自动备份
            self._auto_backup(agent_id)
            
            print(f"[TrainingPersistence] 保存训练结果：{result_file}")
            return True
            
        except Exception as e:
            print(f"[TrainingPersistence] 保存失败：{e}")
            return False
    
    def load_training_result(self, agent_id: str, latest: bool = True) -> Optional[Dict]:
        """加载训练结果"""
        try:
            agent_dir = self.workspace_dir / agent_id
            if not agent_dir.exists():
                return None
            
            # 查找结果文件
            result_files = list(agent_dir.glob("result_*.json"))
            if not result_files:
                return None
            
            # 选择最新或指定文件
            if latest:
                result_file = max(result_files, key=lambda f: f.stat().st_mtime)
            else:
                result_file = result_files[0]
            
            # 加载结果
            with open(result_file, 'r', encoding='utf-8') as f:
                result = json.load(f)
            
            print(f"[TrainingPersistence] 加载训练结果：{result_file}")
            return result
            
        except Exception as e:
            print(f"[TrainingPersistence] 加载失败：{e}")
            return None
    
    def get_training_progress(self, agent_id: str) -> Dict:
        """获取训练进度"""
        agent_dir = self.workspace_dir / agent_id
        if not agent_dir.exists():
            return {"agent_id": agent_id, "total_results": 0, "latest_result": None}
        
        result_files = list(agent_dir.glob("result_*.json"))
        latest_result = None
        if result_files:
            latest_file = max(result_files, key=lambda f: f.stat().st_mtime)
            with open(latest_file, 'r', encoding='utf-8') as f:
                latest_result = json.load(f)
        
        return {
            "agent_id": agent_id,
            "total_results": len(result_files),
            "latest_result": latest_result,
            "latest_file": str(latest_file) if result_files else None
        }
    
    def list_all_training_results(self) -> Dict[str, Dict]:
        """列出所有训练结果"""
        results = {}
        for agent_dir in self.workspace_dir.iterdir():
            if agent_dir.is_dir() and agent_dir.name != "backup":
                results[agent_dir.name] = self.get_training_progress(agent_dir.name)
        return results
    
    def _update_index(self, agent_id: str, result: Dict):
        """更新索引"""
        if "agents" not in self.index:
            self.index["agents"] = {}
        
        self.index["agents"][agent_id] = {
            "last_update": time.time(),
            "total_results": self.index["agents"].get(agent_id, {}).get("total_results", 0) + 1,
            "latest_file": str(result.get("metadata", {}).get("file_path", ""))
        }
        
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)
    
    def _auto_backup(self, agent_id: str):
        """自动备份"""
        try:
            agent_dir = self.workspace_dir / agent_id
            backup_agent_dir = self.backup_dir / agent_id
            backup_agent_dir.mkdir(parents=True, exist_ok=True)
            
            # 复制最新结果到备份
            result_files = list(agent_dir.glob("result_*.json"))
            if result_files:
                latest_file = max(result_files, key=lambda f: f.stat().st_mtime)
                backup_file = backup_agent_dir / latest_file.name
                shutil.copy2(latest_file, backup_file)
                
        except Exception as e:
            print(f"[TrainingPersistence] 备份失败：{e}")
    
    def _load_index(self) -> Dict:
        """加载索引"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {"agents": {}, "last_update": None}
    
    def restore_from_backup(self, agent_id: str) -> bool:
        """从备份恢复"""
        try:
            backup_agent_dir = self.backup_dir / agent_id
            if not backup_agent_dir.exists():
                return False
            
            agent_dir = self.workspace_dir / agent_id
            agent_dir.mkdir(parents=True, exist_ok=True)
            
            # 复制备份文件
            for backup_file in backup_agent_dir.glob("result_*.json"):
                target_file = agent_dir / backup_file.name
                shutil.copy2(backup_file, target_file)
            
            print(f"[TrainingPersistence] 从备份恢复：{agent_id}")
            return True
            
        except Exception as e:
            print(f"[TrainingPersistence] 恢复失败：{e}")
            return False


# 测试代码
if __name__ == "__main__":
    print("=== 测试训练数据持久化管理器 ===")
    
    persistence = TrainingPersistence()
    
    # 保存测试数据
    test_result = {
        "agent_id": "test_agent",
        "training_round": 1,
        "accuracy": 0.85,
        "loss": 0.15,
        "metrics": {
            "precision": 0.87,
            "recall": 0.83,
            "f1_score": 0.85
        }
    }
    
    persistence.save_training_result("test_agent", test_result)
    
    # 加载测试数据
    loaded_result = persistence.load_training_result("test_agent")
    print(f"加载结果：{loaded_result is not None}")
    
    # 获取进度
    progress = persistence.get_training_progress("test_agent")
    print(f"训练进度：{progress['total_results']} 次结果")
    
    # 列出所有结果
    all_results = persistence.list_all_training_results()
    print(f"总学员数：{len(all_results)}")
    
    print("✅ 测试完成")