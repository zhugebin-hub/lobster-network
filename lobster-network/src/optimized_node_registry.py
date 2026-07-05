#!/usr/bin/env python3
"""
优化版节点注册中心管理器
增强功能：
- 自动持久化
- 健康检查循环
- 节点发现 API
- 传输通道管理
"""

import json
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional

class OptimizedNodeRegistry:
    """优化版节点注册中心"""
    
    def __init__(self, workspace_dir: str = "workspace"):
        self.workspace_dir = Path(workspace_dir) / "registry"
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        
        self.state_file = self.workspace_dir / "registry_state.json"
        self.audit_log = self.workspace_dir / "audit_log.jsonl"
        
        self.nodes: Dict[str, Dict] = {}
        self._lock = threading.RLock()
        
        # 加载持久化状态
        self._load_state()
        
        # 启动健康检查线程
        self._health_check_thread = threading.Thread(
            target=self._health_check_loop,
            daemon=True
        )
        self._health_check_thread.start()
        
        print(f"[OptimizedNodeRegistry] 初始化完成，已加载 {len(self.nodes)} 个节点")
    
    def register(self, node_id: str, name: str, node_type: str = "agent",
                 capabilities: List[str] = None, transports: List[Dict] = None,
                 metadata: Dict = None, ttl_seconds: int = 300) -> Dict:
        """注册节点"""
        with self._lock:
            node_info = {
                "node_id": node_id,
                "name": name,
                "node_type": node_type,
                "capabilities": capabilities or [],
                "transports": transports or [],
                "metadata": metadata or {},
                "ttl_seconds": ttl_seconds,
                "status": "active",
                "registered_at": time.time(),
                "last_heartbeat": time.time(),
                "heartbeat_count": 0,
                "consecutive_missed": 0,
                "failed_transports": []
            }
            
            self.nodes[node_id] = node_info
            self._save_state()
            self._log_audit("register", node_id)
            
            return {"success": True, "action": "registered", "node_id": node_id}
    
    def heartbeat(self, node_id: str, status: str = None) -> Dict:
        """接收心跳"""
        with self._lock:
            if node_id not in self.nodes:
                return {"success": False, "error": f"Node {node_id} not registered"}
            
            node = self.nodes[node_id]
            node["last_heartbeat"] = time.time()
            node["heartbeat_count"] += 1
            node["consecutive_missed"] = 0
            
            if status and status in ["active", "idle", "busy", "degraded"]:
                node["status"] = status
            
            # 从 suspected/offline 恢复
            if node["status"] in ("suspected", "offline"):
                node["status"] = "active"
            
            self._save_state()
            self._log_audit("heartbeat", node_id)
            
            return {"success": True, "node_id": node_id, "heartbeat_count": node["heartbeat_count"]}
    
    def get_active_nodes(self) -> Dict[str, Dict]:
        """获取活跃节点"""
        with self._lock:
            return {
                nid: node for nid, node in self.nodes.items()
                if node["status"] in ("active", "idle", "busy", "degraded")
            }
    
    def get_nodes_by_capability(self, capability: str) -> List[Dict]:
        """按能力查找节点"""
        with self._lock:
            return [
                node for node in self.get_active_nodes().values()
                if capability in node.get("capabilities", [])
            ]
    
    def _health_check_loop(self, interval_seconds: int = 60):
        """健康检查循环"""
        while True:
            try:
                self._check_health()
            except Exception as e:
                print(f"[HealthCheck] 错误：{e}")
            time.sleep(interval_seconds)
    
    def _check_health(self):
        """执行健康检查"""
        with self._lock:
            now = time.time()
            changes = []
            
            for node_id, node in self.nodes.items():
                elapsed = now - node["last_heartbeat"]
                ttl = node.get("ttl_seconds", 300)
                
                if elapsed < ttl:
                    continue  # 正常
                
                node["consecutive_missed"] += 1
                
                if elapsed < ttl * 3:
                    # 疑似离线
                    if node["status"] != "suspected":
                        old_status = node["status"]
                        node["status"] = "suspected"
                        changes.append({
                            "node_id": node_id,
                            "old_status": old_status,
                            "new_status": "suspected",
                            "reason": f"heartbeat timeout ({elapsed:.0f}s > {ttl}s)"
                        })
                else:
                    # 确认离线
                    if node["status"] != "offline":
                        old_status = node["status"]
                        node["status"] = "offline"
                        changes.append({
                            "node_id": node_id,
                            "old_status": old_status,
                            "new_status": "offline",
                            "reason": f"extended timeout ({elapsed:.0f}s > {ttl*3}s)"
                        })
            
            if changes:
                self._save_state()
                for change in changes:
                    self._log_audit("status_change", change["node_id"], change)
                    print(f"[HealthCheck] {change['node_id']}: {change['old_status']} → {change['new_status']}")
    
    def _save_state(self):
        """持久化状态"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.nodes, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Registry] 保存状态失败：{e}")
    
    def _load_state(self):
        """加载状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    self.nodes = json.load(f)
            except Exception as e:
                print(f"[Registry] 加载状态失败：{e}")
    
    def _log_audit(self, event: str, node_id: str, details: Dict = None):
        """写入审计日志"""
        entry = {
            "timestamp": time.time(),
            "event": event,
            "node_id": node_id,
            "details": details or {}
        }
        try:
            with open(self.audit_log, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        except Exception:
            pass


# 测试代码
if __name__ == "__main__":
    print("=== 测试优化版节点注册中心 ===")
    
    registry = OptimizedNodeRegistry()
    
    # 注册测试节点
    registry.register("test-node-1", "测试节点 1", capabilities=["test", "analysis"])
    registry.register("test-node-2", "测试节点 2", capabilities=["test", "generation"])
    
    # 发送心跳
    registry.heartbeat("test-node-1")
    registry.heartbeat("test-node-2", status="busy")
    
    # 查询
    active = registry.get_active_nodes()
    print(f"活跃节点：{len(active)}")
    
    test_nodes = registry.get_nodes_by_capability("test")
    print(f"有 test 能力的节点：{len(test_nodes)}")
    
    print("✅ 测试完成")