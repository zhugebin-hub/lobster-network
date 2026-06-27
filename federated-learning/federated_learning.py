#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🦞 小龙虾网络 · 联邦学习系统
版本: V1.0 | 日期: 2026-06-27
功能: 智能体间知识共享的联邦学习机制
"""

import json
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
import random

class FederatedClient:
    """联邦学习客户端"""
    
    def __init__(self, client_id: str, name: str):
        self.client_id = client_id
        self.name = name
        self.local_data = []
        self.local_model = {}
        self.training_history = []
    
    def add_data(self, data: Dict):
        """添加本地数据"""
        self.local_data.append(data)
    
    def train_local(self, epochs: int = 1) -> Dict:
        """本地训练"""
        if not self.local_data:
            return {"status": "error", "message": "无训练数据"}
        
        # 模拟训练过程
        model_updates = {
            "client_id": self.client_id,
            "epochs": epochs,
            "data_size": len(self.local_data),
            "updates": {}
        }
        
        # 根据数据生成模型更新
        for data in self.local_data:
            topic = data.get("topic", "unknown")
            accuracy = data.get("accuracy", 0)
            
            if topic not in model_updates["updates"]:
                model_updates["updates"][topic] = []
            model_updates["updates"][topic].append(accuracy)
        
        # 计算平均准确率
        all_accuracies = []
        for accuracies in model_updates["updates"].values():
            all_accuracies.extend(accuracies)
        
        if all_accuracies:
            model_updates["avg_accuracy"] = sum(all_accuracies) / len(all_accuracies)
        else:
            model_updates["avg_accuracy"] = 0
        
        self.training_history.append(model_updates)
        return model_updates
    
    def get_model_update(self) -> Dict:
        """获取模型更新"""
        if self.training_history:
            return self.training_history[-1]
        return {}

class FederatedServer:
    """联邦学习服务器"""
    
    def __init__(self, storage_path: str = "/shared/training/go/federated-learning"):
        self.storage_path = storage_path
        self.clients = {}
        self.global_model = {}
        self.training_rounds = []
        self._ensure_storage()
    
    def _ensure_storage(self):
        """确保存储目录存在"""
        os.makedirs(self.storage_path, exist_ok=True)
    
    def register_client(self, client: FederatedClient):
        """注册客户端"""
        self.clients[client.client_id] = client
    
    def select_clients(self, num_clients: int = None) -> List[FederatedClient]:
        """选择参与训练的客户端"""
        if num_clients is None:
            num_clients = len(self.clients)
        
        selected = list(self.clients.values())[:num_clients]
        return selected
    
    def aggregate_models(self, client_updates: List[Dict]) -> Dict:
        """聚合模型更新 (FedAvg算法)"""
        if not client_updates:
            return {}
        
        aggregated = {
            "round": len(self.training_rounds) + 1,
            "num_clients": len(client_updates),
            "global_updates": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # 聚合各主题的准确率
        topic_accuracies = {}
        for update in client_updates:
            if "updates" in update:
                for topic, accuracies in update["updates"].items():
                    if topic not in topic_accuracies:
                        topic_accuracies[topic] = []
                    topic_accuracies[topic].extend(accuracies)
        
        # 计算全局平均
        for topic, accuracies in topic_accuracies.items():
            if accuracies:
                aggregated["global_updates"][topic] = sum(accuracies) / len(accuracies)
        
        # 计算全局平均准确率
        all_accuracies = []
        for accuracies in topic_accuracies.values():
            all_accuracies.extend(accuracies)
        
        if all_accuracies:
            aggregated["global_accuracy"] = sum(all_accuracies) / len(all_accuracies)
        else:
            aggregated["global_accuracy"] = 0
        
        self.global_model = aggregated
        self.training_rounds.append(aggregated)
        
        return aggregated
    
    def run_federated_round(self, num_clients: int = None, epochs: int = 1) -> Dict:
        """运行一轮联邦学习"""
        # 选择客户端
        selected_clients = self.select_clients(num_clients)
        
        if not selected_clients:
            return {"status": "error", "message": "无可用客户端"}
        
        # 本地训练
        client_updates = []
        for client in selected_clients:
            update = client.train_local(epochs)
            if update.get("status") != "error":
                client_updates.append(update)
        
        # 聚合模型
        if client_updates:
            global_model = self.aggregate_models(client_updates)
            return global_model
        
        return {"status": "error", "message": "无有效模型更新"}
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            "total_clients": len(self.clients),
            "training_rounds": len(self.training_rounds),
            "global_model": self.global_model
        }

if __name__ == "__main__":
    # 测试联邦学习系统
    server = FederatedServer()
    
    print("🦞 联邦学习系统测试")
    print(f"   存储路径: {server.storage_path}")
    
    # 创建客户端
    print("\n📝 创建客户端...")
    xiaochen = FederatedClient("xiaochen", "小陈")
    xiaochen.add_data({"topic": "死活", "accuracy": 0.875})
    xiaochen.add_data({"topic": "手筋", "accuracy": 1.0})
    xiaochen.add_data({"topic": "定式", "accuracy": 1.0})
    xiaochen.add_data({"topic": "官子", "accuracy": 0.5})
    xiaochen.add_data({"topic": "布局", "accuracy": 0.5})
    
    zhuguxia = FederatedClient("zhuguxia", "诸葛虾")
    zhuguxia.add_data({"topic": "死活", "accuracy": 0.625})
    zhuguxia.add_data({"topic": "手筋", "accuracy": 0.625})
    zhuguxia.add_data({"topic": "定式", "accuracy": 1.0})
    zhuguxia.add_data({"topic": "官子", "accuracy": 1.0})
    zhuguxia.add_data({"topic": "布局", "accuracy": 1.0})
    
    qoder = FederatedClient("qoder", "qoder小龙虾")
    qoder.add_data({"topic": "死活", "accuracy": 0.95})
    qoder.add_data({"topic": "手筋", "accuracy": 0.85})
    qoder.add_data({"topic": "定式", "accuracy": 0.75})
    qoder.add_data({"topic": "官子", "accuracy": 0.65})
    qoder.add_data({"topic": "布局", "accuracy": 0.80})
    
    # 注册客户端
    server.register_client(xiaochen)
    server.register_client(zhuguxia)
    server.register_client(qoder)
    print(f"   已注册3个客户端")
    
    # 运行联邦学习
    print("\n🔄 运行联邦学习...")
    for round_num in range(3):
        print(f"\n  轮次 {round_num + 1}:")
        result = server.run_federated_round()
        print(f"    全局准确率: {result.get('global_accuracy', 0):.3f}")
        print(f"    各主题准确率:")
        for topic, acc in result.get("global_updates", {}).items():
            print(f"      {topic}: {acc:.3f}")
    
    # 状态
    print("\n📊 状态:")
    status = server.get_status()
    print(f"   客户端数: {status['total_clients']}")
    print(f"   训练轮数: {status['training_rounds']}")
    
    print("\n✅ 联邦学习系统测试完成")
