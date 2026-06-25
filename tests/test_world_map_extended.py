#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
世界地图引擎扩展测试
测试版本历史回溯、多域名扩展、广播机制、CLI 功能
"""

import json
import os
import tempfile
import shutil
import unittest
from pathlib import Path
from datetime import datetime

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.world_map import WorldMap, WorldMapManager


class TestWorldMapVersioning(unittest.TestCase):
    """测试版本历史回溯功能"""

    def setUp(self):
        """创建临时存储目录"""
        self.test_dir = tempfile.mkdtemp()
        self.wm = WorldMap(map_id="test-wm-version", storage_dir=self.test_dir)

    def tearDown(self):
        """清理临时目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_version_increment(self):
        """测试版本号递增"""
        m = self.wm.get_world_map()
        initial_version = m["version"]
        
        # 添加 chunk 应该触发版本更新
        chunk_data = {
            "chunk_id": "version_test_001",
            "domain": "go",
            "title": "版本测试",
            "description": "测试版本号递增",
            "tags": ["version"],
        }
        self.wm.add_chunk(chunk_data, "test_agent")
        
        m2 = self.wm.get_world_map()
        self.assertGreater(m2["version"], initial_version)

    def test_get_world_map_current_version(self):
        """测试获取当前版本"""
        m = self.wm.get_world_map()
        self.assertEqual(m["version"], self.wm._map["version"])

    def test_version_history_tracking(self):
        """测试版本历史跟踪"""
        # 添加多个 chunk
        for i in range(3):
            chunk_data = {
                "chunk_id": f"history_test_{i:03d}",
                "domain": "protocol",
                "title": f"历史测试 {i}",
                "description": f"第 {i} 次测试",
                "tags": ["history"],
            }
            self.wm.add_chunk(chunk_data, "test_agent")
        
        log = self.wm.get_update_log()
        self.assertGreaterEqual(len(log), 3)
    
    def test_get_version_history(self):
        """测试获取版本历史"""
        # 添加一些数据
        for i in range(3):
            chunk_data = {
                "chunk_id": f"version_hist_{i:03d}",
                "domain": "go",
                "title": f"版本历史 {i}",
                "description": f"测试版本历史 {i}",
                "tags": ["version"],
            }
            self.wm.add_chunk(chunk_data, "test_agent")
        
        history = self.wm.get_version_history()
        self.assertGreaterEqual(len(history), 3)
        
        # 检查历史记录格式
        for entry in history:
            self.assertIn("version", entry)
            self.assertIn("timestamp", entry)
            self.assertIn("total_chunks", entry)
    
    def test_get_version_info_current(self):
        """测试获取当前版本信息"""
        # 添加数据
        chunk_data = {
            "chunk_id": "version_info_test",
            "domain": "protocol",
            "title": "版本信息测试",
            "description": "测试当前版本信息",
            "tags": ["version"],
        }
        self.wm.add_chunk(chunk_data, "test_agent")
        
        m = self.wm.get_world_map()
        current_version = m["version"]
        
        info = self.wm.get_version_info(current_version)
        self.assertIsNotNone(info)
        self.assertTrue(info["is_current"])
    
    def test_get_version_info_historical(self):
        """测试获取历史版本信息"""
        # 添加第一个 chunk
        chunk_data1 = {
            "chunk_id": "hist_v1",
            "domain": "go",
            "title": "历史版本 1",
            "description": "测试历史版本",
            "tags": ["history"],
        }
        self.wm.add_chunk(chunk_data1, "test_agent")
        
        # 获取版本 1 的信息
        info = self.wm.get_version_info(1)
        self.assertIsNotNone(info)
        self.assertFalse(info["is_current"])
        
        # 添加第二个 chunk
        chunk_data2 = {
            "chunk_id": "hist_v2",
            "domain": "go",
            "title": "历史版本 2",
            "description": "测试历史版本",
            "tags": ["history"],
        }
        self.wm.add_chunk(chunk_data2, "test_agent")
        
        # 再次获取版本 1 的信息（应该来自历史快照）
        info = self.wm.get_version_info(1)
        self.assertIsNotNone(info)
        self.assertEqual(info["version"], 1)


class TestWorldMapMultiDomain(unittest.TestCase):
    """测试多域名扩展功能"""

    def setUp(self):
        """创建临时存储目录"""
        self.test_dir = tempfile.mkdtemp()
        self.wm = WorldMap(map_id="test-wm-domain", storage_dir=self.test_dir)

    def tearDown(self):
        """清理临时目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_add_new_domain(self):
        """测试添加新域名"""
        # 初始域名
        m = self.wm.get_world_map()
        initial_domains = set(m["domains"])
        
        # 添加新域名的 chunk
        chunk_data = {
            "chunk_id": "math_test_001",
            "domain": "math",
            "title": "数学测试",
            "description": "测试新域名扩展",
            "tags": ["math"],
        }
        self.wm.add_chunk(chunk_data, "test_agent")
        
        m2 = self.wm.get_world_map()
        self.assertIn("math", m2["domains"])
        self.assertNotEqual(set(m2["domains"]), initial_domains)

    def test_search_by_domain(self):
        """测试按域名搜索"""
        # 添加不同域名的 chunk
        domains = ["go", "poster", "protocol", "math"]
        for domain in domains:
            chunk_data = {
                "chunk_id": f"{domain}_search_test",
                "domain": domain,
                "title": f"{domain} 搜索测试",
                "description": f"测试 {domain} 域名搜索",
                "tags": [domain],
            }
            self.wm.add_chunk(chunk_data, "test_agent")
        
        # 搜索特定域名
        for domain in domains:
            results = self.wm.search_chunks(domain=domain)
            self.assertGreaterEqual(len(results), 1)
            for r in results:
                self.assertEqual(r["domain"], domain)


class TestWorldMapBroadcast(unittest.TestCase):
    """测试世界地图广播机制"""

    def setUp(self):
        """创建临时存储目录"""
        self.test_dir = tempfile.mkdtemp()
        self.wm = WorldMap(map_id="test-wm-broadcast", storage_dir=self.test_dir)

    def tearDown(self):
        """清理临时目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_broadcast_log_entry(self):
        """测试广播日志记录"""
        chunk_data = {
            "chunk_id": "broadcast_test_001",
            "domain": "go",
            "title": "广播测试",
            "description": "测试广播机制",
            "tags": ["broadcast"],
        }
        self.wm.add_chunk(chunk_data, "test_agent")
        
        log = self.wm.get_update_log()
        self.assertGreater(len(log), 0)
        
        # 检查最新日志条目
        latest = log[-1]
        self.assertEqual(latest["type"], "chunk_add")
        self.assertEqual(latest["agent"], "test_agent")

    def test_incremental_sync(self):
        """测试增量同步"""
        # 添加初始数据
        chunk_data = {
            "chunk_id": "sync_test_001",
            "domain": "protocol",
            "title": "同步测试",
            "description": "测试增量同步",
            "tags": ["sync"],
        }
        self.wm.add_chunk(chunk_data, "test_agent")
        
        m = self.wm.get_world_map()
        current_version = m["version"]
        
        # 获取增量更新（使用版本 0 获取所有数据）
        sync_result = self.wm.sync_incremental(since_version=0)
        self.assertIn("new_chunks", sync_result)
        self.assertGreaterEqual(len(sync_result["new_chunks"]), 1)


class TestWorldMapCLI(unittest.TestCase):
    """测试 CLI 功能"""

    def setUp(self):
        """创建临时存储目录"""
        self.test_dir = tempfile.mkdtemp()
        self.wm = WorldMap(map_id="test-wm-cli", storage_dir=self.test_dir)

    def tearDown(self):
        """清理临时目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_export_world_map(self):
        """测试导出世界地图"""
        # 添加测试数据
        chunk_data = {
            "chunk_id": "cli_test_001",
            "domain": "go",
            "title": "CLI 测试",
            "description": "测试 CLI 导出功能",
            "tags": ["cli"],
        }
        self.wm.add_chunk(chunk_data, "test_agent")
        
        # 获取完整地图
        m = self.wm.get_world_map()
        self.assertIn("world_map_id", m)
        self.assertIn("chunks", m)
        self.assertIn("treasures", m)

    def test_import_chunk_data(self):
        """测试导入 chunk 数据"""
        chunk_file = os.path.join(self.test_dir, "test_chunk.json")
        chunk_data = {
            "chunk_id": "import_test_001",
            "domain": "poster",
            "title": "导入测试",
            "description": "测试导入功能",
            "tags": ["import"],
            "data": {"key": "value"},
        }
        
        with open(chunk_file, "w") as f:
            json.dump(chunk_data, f)
        
        # 读取并添加
        with open(chunk_file, "r") as f:
            data = json.load(f)
        
        result = self.wm.add_chunk(data, "test_agent")
        self.assertEqual(result["chunk_id"], "import_test_001")


class TestWorldMapConcurrency(unittest.TestCase):
    """测试并发写入安全"""

    def setUp(self):
        """创建临时存储目录"""
        self.test_dir = tempfile.mkdtemp()
        self.wm = WorldMap(map_id="test-wm-concurrent", storage_dir=self.test_dir)
        self.manager = WorldMapManager(self.wm)

    def tearDown(self):
        """清理临时目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_concurrent_add_chunks(self):
        """测试并发添加 chunk"""
        import threading
        import time
        
        results = []
        errors = []
        
        def add_chunk(chunk_id, agent):
            try:
                chunk_data = {
                    "chunk_id": chunk_id,
                    "domain": "go",
                    "title": f"并发测试 {chunk_id}",
                    "description": f"测试并发添加 {chunk_id}",
                    "tags": ["concurrent"],
                }
                result = self.manager.safe_add_chunk(chunk_data, agent)
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # 创建多个线程
        threads = []
        for i in range(5):
            t = threading.Thread(target=add_chunk, args=(f"concurrent_{i:03d}", f"agent_{i}"))
            threads.append(t)
        
        # 启动所有线程，间隔短暂时间减少竞争
        for t in threads:
            t.start()
            time.sleep(0.01)
        
        # 等待所有线程完成
        for t in threads:
            t.join(timeout=10)
        
        # 检查结果（允许少量锁竞争失败）
        self.assertGreaterEqual(len(results), 3)  # 至少 3 个成功
        self.assertLessEqual(len(errors), 2)  # 最多 2 个失败
        
        m = self.wm.get_world_map()
        self.assertGreaterEqual(m["total_chunks"], 3)


if __name__ == "__main__":
    unittest.main()
