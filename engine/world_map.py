#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
世界地图索引引擎 (World Map Index Engine)
协议: World Map Index Protocol v0.1.0
作者: 虾尔 (lobster-001)
实现: 信电大虾 (小陈)
"""

import json
import os
import hashlib
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class WorldMap:
    """世界地图 - 小龙虾网络集体记忆引擎"""

    def __init__(self, map_id: str = "wm-001", storage_dir: str = "/shared/world_map"):
        self.map_id = map_id
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.map_file = self.storage_dir / "world_map.json"

        if self.map_file.exists():
            with open(self.map_file, "r", encoding="utf-8") as f:
                self._map = json.load(f)
        else:
            self._map = self._init_empty_map()

    def _init_empty_map(self) -> Dict:
        """初始化空世界地图"""
        now = datetime.now().isoformat()
        return {
            "world_map_id": self.map_id,
            "version": 1,
            "created_at": now,
            "updated_at": now,
            "total_chunks": 0,
            "total_treasures": 0,
            "active_agents": [],
            "domains": ["go", "poster", "protocol"],
            "chunks": {},
            "treasures": {},
            "update_log": [],
        }

    def _save(self):
        """持久化到文件"""
        self._map["updated_at"] = datetime.now().isoformat()
        self._map["version"] = self._map.get("version", 1) + 1
        with open(self.map_file, "w", encoding="utf-8") as f:
            json.dump(self._map, f, indent=2, ensure_ascii=False)

    def _log_update(self, update_type: str, agent: str, details: Dict):
        """记录更新日志"""
        entry = {
            "update_id": f"upd-{len(self._map['update_log']) + 1:03d}",
            "type": update_type,
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "details": details,
        }
        self._map["update_log"].append(entry)

    # ========== 知识碎片操作 ==========

    def add_chunk(self, chunk_data: Dict, contributor: str) -> Dict:
        """添加知识碎片"""
        chunk_id = chunk_data.get("chunk_id")
        if not chunk_id:
            raise ValueError("chunk_id is required")

        if chunk_id in self._map["chunks"]:
            raise ValueError(f"Chunk {chunk_id} already exists. Use update_chunk instead.")

        # 计算内容哈希
        content = json.dumps(chunk_data, ensure_ascii=False, sort_keys=True)
        content_hash = f"sha256:{hashlib.sha256(content.encode()).hexdigest()[:16]}"

        chunk = {
            "chunk_id": chunk_id,
            "domain": chunk_data.get("domain", "unknown"),
            "title": chunk_data.get("title", ""),
            "description": chunk_data.get("description", ""),
            "content_hash": content_hash,
            "contributor": contributor,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "tags": chunk_data.get("tags", []),
            "referenced_by": [],
            "references": chunk_data.get("references", []),
            "size_bytes": len(content.encode()),
            "format": chunk_data.get("format", "json"),
            "data": chunk_data.get("data", {}),
        }

        self._map["chunks"][chunk_id] = chunk
        self._map["total_chunks"] = len(self._map["chunks"])

        # 确保域名已注册
        domain = chunk["domain"]
        if domain not in self._map["domains"]:
            self._map["domains"].append(domain)

        self._log_update("chunk_add", contributor, {"chunk_id": chunk_id, "action": "add"})
        self._save()
        return chunk

    def update_chunk(self, chunk_id: str, new_data: Dict, agent: str) -> Dict:
        """更新知识碎片"""
        if chunk_id not in self._map["chunks"]:
            raise KeyError(f"Chunk {chunk_id} not found")

        chunk = self._map["chunks"][chunk_id]

        # 权限检查：只有贡献者或管理员可以更新
        if chunk["contributor"] != agent and agent != "admin":
            raise PermissionError(f"Only {chunk['contributor']} or admin can update this chunk")

        # 合并更新
        for key, value in new_data.items():
            if key not in ("chunk_id", "contributor", "created_at"):
                chunk[key] = value

        chunk["updated_at"] = datetime.now().isoformat()

        # 重新计算哈希
        content = json.dumps(chunk, ensure_ascii=False, sort_keys=True)
        chunk["content_hash"] = f"sha256:{hashlib.sha256(content.encode()).hexdigest()[:16]}"
        chunk["size_bytes"] = len(content.encode())

        self._log_update("chunk_update", agent, {"chunk_id": chunk_id, "action": "update"})
        self._save()
        return chunk

    def remove_chunk(self, chunk_id: str, agent: str) -> bool:
        """移除知识碎片（仅管理员）"""
        if agent != "admin":
            raise PermissionError("Only admin can remove chunks")

        if chunk_id not in self._map["chunks"]:
            return False

        # 检查引用
        referenced = self._map["chunks"][chunk_id].get("referenced_by", [])
        if referenced:
            # 延迟删除，标记为待删除
            self._map["chunks"][chunk_id]["pending_delete"] = True
            self._log_update("chunk_remove", agent, {"chunk_id": chunk_id, "action": "pending_delete", "reason": "has_references"})
        else:
            del self._map["chunks"][chunk_id]
            self._map["total_chunks"] = len(self._map["chunks"])
            self._log_update("chunk_remove", agent, {"chunk_id": chunk_id, "action": "remove"})

        self._save()
        return True

    def get_chunk(self, chunk_id: str) -> Optional[Dict]:
        """获取指定知识碎片"""
        return self._map["chunks"].get(chunk_id)

    def search_chunks(self, query: str = None, domain: str = None, tags: List[str] = None) -> List[Dict]:
        """搜索知识碎片"""
        results = []
        for chunk in self._map["chunks"].values():
            if domain and chunk["domain"] != domain:
                continue
            if tags and not any(t in chunk.get("tags", []) for t in tags):
                continue
            if query:
                query_lower = query.lower()
                if query_lower not in chunk.get("title", "").lower() and \
                   query_lower not in chunk.get("description", "").lower() and \
                   query_lower not in chunk.get("chunk_id", "").lower():
                    continue
            results.append(chunk)
        return results

    # ========== 宝藏操作 ==========

    def unlock_treasure(self, treasure_data: Dict, unlocked_by: List[str]) -> Dict:
        """解锁宝藏"""
        treasure_id = treasure_data.get("treasure_id")
        if not treasure_id:
            raise ValueError("treasure_id is required")

        if treasure_id in self._map["treasures"]:
            raise ValueError(f"Treasure {treasure_id} already exists")

        treasure = {
            "treasure_id": treasure_id,
            "title": treasure_data.get("title", ""),
            "description": treasure_data.get("description", ""),
            "rarity": treasure_data.get("rarity", "common"),
            "unlocked_by": unlocked_by,
            "unlocked_at": datetime.now().isoformat(),
            "source_dialogue_id": treasure_data.get("source_dialogue_id"),
            "related_chunks": treasure_data.get("related_chunks", []),
            "insight": treasure_data.get("insight", ""),
            "verification_status": "unlocked",
        }

        self._map["treasures"][treasure_id] = treasure
        self._map["total_treasures"] = len(self._map["treasures"])

        self._log_update("treasure_unlock", unlocked_by[0] if unlocked_by else "system", {"treasure_id": treasure_id})
        self._save()
        return treasure

    def verify_treasure(self, treasure_id: str, verifier: str) -> Dict:
        """验证宝藏"""
        if treasure_id not in self._map["treasures"]:
            raise KeyError(f"Treasure {treasure_id} not found")

        treasure = self._map["treasures"][treasure_id]
        treasure["verification_status"] = "verified"
        treasure["verified_by"] = verifier
        treasure["verified_at"] = datetime.now().isoformat()

        self._log_update("treasure_verify", verifier, {"treasure_id": treasure_id})
        self._save()
        return treasure

    def get_treasure(self, treasure_id: str) -> Optional[Dict]:
        """获取指定宝藏"""
        return self._map["treasures"].get(treasure_id)

    # ========== 同步操作 ==========

    def get_world_map(self, version: int = None) -> Dict:
        """获取完整世界地图"""
        if version and version != self._map["version"]:
            # TODO: 实现版本历史回溯
            pass
        return self._map.copy()

    def sync_incremental(self, since_version: int, since_timestamp: str = None) -> Dict:
        """增量同步"""
        new_chunks = {}
        updated_chunks = {}
        new_treasures = {}

        for chunk_id, chunk in self._map["chunks"].items():
            if chunk.get("_version", 1) > since_version:
                if chunk.get("pending_delete"):
                    continue
                # 判断是新增还是更新
                created_version = chunk.get("_created_version", 1)
                if created_version > since_version:
                    new_chunks[chunk_id] = chunk
                else:
                    updated_chunks[chunk_id] = chunk

        for tid, treasure in self._map["treasures"].items():
            if treasure.get("_version", 1) > since_version:
                new_treasures[tid] = treasure

        return {
            "type": "world_map_sync_response",
            "current_version": self._map["version"],
            "new_chunks": [{"chunk_id": k, "data": v} for k, v in new_chunks.items()],
            "updated_chunks": [{"chunk_id": k, "data": v} for k, v in updated_chunks.items()],
            "new_treasures": [{"treasure_id": k, "data": v} for k, v in new_treasures.items()],
            "removed_chunks": [],
        }

    def get_update_log(self, since_version: int = None, limit: int = 50) -> List[Dict]:
        """获取更新日志"""
        log = self._map["update_log"]
        if since_version:
            # 过滤 since_version 之后的日志
            log = [e for e in log if e.get("version", 1) >= since_version]
        return log[-limit:]

    # ========== 智能体管理 ==========

    def register_agent(self, agent_id: str) -> bool:
        """注册智能体"""
        if agent_id not in self._map["active_agents"]:
            self._map["active_agents"].append(agent_id)
            self._log_update("agent_register", agent_id, {"action": "register"})
            self._save()
            return True
        return False

    def get_active_agents(self) -> List[str]:
        """获取活跃智能体列表"""
        return self._map["active_agents"].copy()


class WorldMapManager:
    """世界地图管理员 - 处理多智能体并发写入"""

    def __init__(self, world_map: WorldMap):
        self.world_map = world_map
        self._lock_file = Path(world_map.storage_dir) / ".lock"

    def _acquire_lock(self, agent: str, timeout: int = 10) -> bool:
        """获取写锁（基于文件的简单锁）"""
        start = time.time()
        while self._lock_file.exists():
            if time.time() - start > timeout:
                return False
            time.sleep(0.1)

        try:
            with open(self._lock_file, "w") as f:
                json.dump({"locked_by": agent, "locked_at": datetime.now().isoformat()}, f)
            return True
        except:
            return False

    def _release_lock(self):
        """释放写锁"""
        if self._lock_file.exists():
            self._lock_file.unlink()

    def safe_add_chunk(self, chunk_data: Dict, contributor: str) -> Dict:
        """安全添加知识碎片（带锁）"""
        if not self._acquire_lock(contributor):
            raise RuntimeError("Failed to acquire lock")
        try:
            return self.world_map.add_chunk(chunk_data, contributor)
        finally:
            self._release_lock()

    def safe_update_chunk(self, chunk_id: str, new_data: Dict, agent: str) -> Dict:
        """安全更新知识碎片（带锁）"""
        if not self._acquire_lock(agent):
            raise RuntimeError("Failed to acquire lock")
        try:
            return self.world_map.update_chunk(chunk_id, new_data, agent)
        finally:
            self._release_lock()


# ========== 便捷函数 ==========

def create_world_map(map_id: str = "wm-001", storage_dir: str = "/shared/world_map") -> WorldMap:
    """创建世界地图实例"""
    return WorldMap(map_id, storage_dir)


def get_manager(world_map: WorldMap = None) -> WorldMapManager:
    """获取世界地图管理员"""
    if world_map is None:
        world_map = create_world_map()
    return WorldMapManager(world_map)


# ========== CLI ==========

if __name__ == "__main__":
    import sys

    cmd = sys.argv[1] if len(sys.argv) > 1 else "info"

    wm = create_world_map()

    if cmd == "info":
        m = wm.get_world_map()
        print(f"世界地图: {m['world_map_id']}")
        print(f"版本: {m['version']}")
        print(f"知识碎片: {m['total_chunks']}")
        print(f"宝藏: {m['total_treasures']}")
        print(f"活跃智能体: {', '.join(m['active_agents'])}")
        print(f"域名: {', '.join(m['domains'])}")

    elif cmd == "search":
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        domain = sys.argv[3] if len(sys.argv) > 3 else None
        results = wm.search_chunks(query, domain=domain)
        print(f"搜索结果 ({len(results)}):")
        for r in results:
            print(f"  [{r['domain']}] {r['chunk_id']}: {r['title']}")

    elif cmd == "add-chunk":
        agent = sys.argv[2] if len(sys.argv) > 2 else "unknown"
        chunk_file = sys.argv[3] if len(sys.argv) > 3 else None
        if chunk_file and os.path.exists(chunk_file):
            with open(chunk_file, "r") as f:
                chunk_data = json.load(f)
            result = wm.add_chunk(chunk_data, agent)
            print(f"✅ 已添加: {result['chunk_id']}")
        else:
            print("❌ 请提供 chunk JSON 文件路径")

    elif cmd == "unlock-treasure":
        agent = sys.argv[2] if len(sys.argv) > 2 else "unknown"
        treasure_file = sys.argv[3] if len(sys.argv) > 3 else None
        if treasure_file and os.path.exists(treasure_file):
            with open(treasure_file, "r") as f:
                treasure_data = json.load(f)
            result = wm.unlock_treasure(treasure_data, [agent])
            print(f"🏆 已解锁宝藏: {result['treasure_id']} - {result['title']}")
        else:
            print("❌ 请提供 treasure JSON 文件路径")

    else:
        print(f"未知命令: {cmd}")
        print("可用命令: info, search, add-chunk, unlock-treasure")
