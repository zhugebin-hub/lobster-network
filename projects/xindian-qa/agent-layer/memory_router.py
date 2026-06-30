#!/usr/bin/env python3
"""
三级记忆路由系统
负责管理 L1 工作记忆、L2知识记忆、L3长期记忆的读写和路由
"""

import json
import os
import time
from typing import Dict, List, Optional
from datetime import datetime

class MemoryRouter:
    """三级记忆路由"""
    
    def __init__(self, workspace_dir: str = None):
        """初始化记忆路由"""
        if workspace_dir is None:
            workspace_dir = os.path.expanduser("~/.openclaw/workspace")
        
        self.workspace_dir = workspace_dir
        self.memory_dir = os.path.join(workspace_dir, "memory")
        self.l3_dir = os.path.join(workspace_dir, "xindian-qa", "l3-memory")
        
        # 创建目录
        os.makedirs(self.memory_dir, exist_ok=True)
        os.makedirs(self.l3_dir, exist_ok=True)
        
        # L1 工作记忆（会话上下文）
        self.l1_context = {
            'current_session': {},
            'recent_conversations': []
        }
        
        # L3长期记忆文件路径
        self.user_profile_path = os.path.join(self.l3_dir, "user_profiles.json")
        self.faq_stats_path = os.path.join(self.l3_dir, "faq_stats.json")
        self.conversation_summary_path = os.path.join(self.l3_dir, "conversation_summaries.json")
    
    # ========== L1 工作记忆 ==========
    
    def l1_write(self, session_id: str, data: Dict):
        """
        写入 L1 工作记忆
        
        Args:
            session_id: 会话 ID
            data: 数据（用户问题、检索片段、中间推理等）
        """
        self.l1_context['current_session'][session_id] = {
            'timestamp': time.time(),
            'data': data
        }
    
    def l1_read(self, session_id: str) -> Optional[Dict]:
        """
        读取 L1 工作记忆
        
        Args:
            session_id: 会话 ID
            
        Returns:
            会话数据
        """
        return self.l1_context['current_session'].get(session_id)
    
    def l1_cleanup(self, max_age: int = 3600):
        """
        清理过期的 L1 记忆
        
        Args:
            max_age: 最大保留时间（秒）
        """
        now = time.time()
        expired = [sid for sid, data in self.l1_context['current_session'].items() 
                   if now - data['timestamp'] > max_age]
        for sid in expired:
            del self.l1_context['current_session'][sid]
    
    # ========== L2知识记忆 ==========
    
    def l2_search(self, query: str, bailian_skill) -> List[Dict]:
        """
        搜索 L2知识记忆（百炼RAG）
        
        Args:
            query: 查询文本
            bailian_skill: 百炼 API Skill 实例
            
        Returns:
            检索结果
        """
        return bailian_skill.search(query)
    
    # ========== L3长期记忆 ==========
    
    def l3_write_user_profile(self, user_id: str, profile_data: Dict):
        """
        写入用户画像
        
        Args:
            user_id: 用户 ID
            profile_data: 用户画像数据
        """
        profiles = self._load_json(self.user_profile_path, {})
        profiles[user_id] = {
            'last_update': datetime.now().isoformat(),
            **profile_data
        }
        self._save_json(self.user_profile_path, profiles)
    
    def l3_read_user_profile(self, user_id: str) -> Optional[Dict]:
        """
        读取用户画像
        
        Args:
            user_id: 用户 ID
            
        Returns:
            用户画像数据
        """
        profiles = self._load_json(self.user_profile_path, {})
        return profiles.get(user_id)
    
    def l3_write_faq_stats(self, question: str, count: int = 1):
        """
        更新高频问题统计
        
        Args:
            question: 问题
            count: 增加次数
        """
        stats = self._load_json(self.faq_stats_path, {})
        stats[question] = stats.get(question, 0) + count
        
        # 只保留前 100 个高频问题
        sorted_stats = dict(sorted(stats.items(), key=lambda x: x[1], reverse=True)[:100])
        self._save_json(self.faq_stats_path, sorted_stats)
    
    def l3_read_faq_stats(self, top_n: int = 10) -> List[Dict]:
        """
        读取高频问题统计
        
        Args:
            top_n: 返回前 N 个
            
        Returns:
            高频问题列表
        """
        stats = self._load_json(self.faq_stats_path, {})
        sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)[:top_n]
        return [{'question': q, 'count': c} for q, c in sorted_stats]
    
    def l3_write_conversation_summary(self, session_id: str, summary: str):
        """
        写入对话摘要
        
        Args:
            session_id: 会话 ID
            summary: 对话摘要
        """
        summaries = self._load_json(self.conversation_summary_path, {})
        summaries[session_id] = {
            'timestamp': datetime.now().isoformat(),
            'summary': summary
        }
        self._save_json(self.conversation_summary_path, summaries)
    
    # ========== 记忆路由 ==========
    
    def route_query(self, query: str, session_id: str, bailian_skill) -> Dict:
        """
        路由查询到合适的记忆层级
        
        Args:
            query: 用户查询
            session_id: 会话 ID
            bailian_skill: 百炼 API Skill 实例
            
        Returns:
            路由结果
        """
        result = {
            'query': query,
            'session_id': session_id,
            'l1_context': None,
            'l2_results': [],
            'l3_user_profile': None,
            'final_answer': None
        }
        
        # 1. 读取 L1 工作记忆（会话上下文）
        l1_data = self.l1_read(session_id)
        if l1_data:
            result['l1_context'] = l1_data['data']
        
        # 2. 搜索 L2知识记忆（百炼RAG）
        l2_results = self.l2_search(query, bailian_skill)
        result['l2_results'] = l2_results
        
        # 3. 读取 L3长期记忆（用户画像）
        # 假设从 session 中获取 user_id
        user_id = l1_data['data'].get('user_id') if l1_data else None
        if user_id:
            result['l3_user_profile'] = self.l3_read_user_profile(user_id)
        
        return result
    
    # ========== 工具方法 ==========
    
    def _load_json(self, path: str, default=None):
        """加载 JSON 文件"""
        if default is None:
            default = {}
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return default
    
    def _save_json(self, path: str, data: Dict):
        """保存 JSON 文件"""
        with open(path, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

# 测试代码
if __name__ == '__main__':
    router = MemoryRouter()
    print("三级记忆路由系统初始化成功")
    print(f"L3 记忆目录：{router.l3_dir}")
