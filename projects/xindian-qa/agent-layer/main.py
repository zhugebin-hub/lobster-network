#!/usr/bin/env python3
"""
信电学院 AI 知识问答系统 - 主入口
整合百炼 API Skill、三级记忆路由、Prompt 模板
"""

import json
import os
import sys
from typing import Dict, Optional

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bailian_api_skill import BailianAPISkill
from memory_router import MemoryRouter
from prompt_templates import PromptTemplates

class XindianQASystem:
    """信电学院 AI 知识问答系统"""
    
    def __init__(self, config_path: str = None):
        """初始化系统"""
        self.bailian_skill = BailianAPISkill(config_path)
        self.memory_router = MemoryRouter()
        self.prompt_templates = PromptTemplates()
        
        print("✅ 信电学院 AI 知识问答系统初始化成功")
        print(f"   知识库 ID: {self.bailian_skill.kb_id}")
        print(f"   大模型：{self.bailian_skill.llm_model}")
    
    def process_query(self, query: str, session_id: str, user_id: str = None) -> Dict:
        """
        处理用户查询
        
        Args:
            query: 用户问题
            session_id: 会话 ID
            user_id: 用户 ID（可选）
            
        Returns:
            处理结果
        """
        print(f"\n🔍 处理查询：{query}")
        print(f"   会话 ID: {session_id}")
        print(f"   用户 ID: {user_id}")
        
        # 1. 意图识别
        intent = self._identify_intent(query)
        print(f"   意图：{intent}")
        
        # 2. 根据意图路由
        if intent == 'course_knowledge':
            result = self._handle_course_knowledge(query, session_id, user_id)
        elif intent == 'system_operation':
            result = self._handle_system_operation(query)
        else:  # casual_chat
            result = self._handle_casual_chat(query)
        
        # 3. 记忆沉淀
        self._memory_sediment(query, result, session_id, user_id)
        
        return result
    
    def _identify_intent(self, query: str) -> str:
        """识别用户意图"""
        # 简单规则匹配（后续可替换为 LLM 识别）
        if any(keyword in query for keyword in ['怎么', '如何', '使用', '帮助']):
            return 'system_operation'
        elif any(keyword in query for keyword in ['你好', '谢谢', '再见', '哈哈']):
            return 'casual_chat'
        else:
            return 'course_knowledge'
    
    def _handle_course_knowledge(self, query: str, session_id: str, user_id: str) -> Dict:
        """处理课程知识问题"""
        print("   📚 处理课程知识问题...")
        
        # 1. 路由查询到三级记忆
        route_result = self.memory_router.route_query(query, session_id, self.bailian_skill)
        
        # 2. 获取检索结果
        l2_results = route_result['l2_results']
        if not l2_results:
            return {
                'answer': '抱歉，知识库中未找到相关内容。请尝试其他关键词或联系管理员补充教材。',
                'sources': [],
                'intent': 'course_knowledge'
            }
        
        # 3. 构建知识片段
        context = self._build_context(l2_results)
        
        # 4. 生成答案（优先使用本地 RAG）
        prompt = self.prompt_templates.get_qa_prompt(context, query)
        if self.bailian_skill.use_local_rag and self.bailian_skill.local_rag:
            answer = self.bailian_skill.local_rag.generate_answer(query, context)
        else:
            answer = self.bailian_skill.generate_answer(query, context)
        
        # 5. 更新 L1 工作记忆
        self.memory_router.l1_write(session_id, {
            'query': query,
            'l2_results': l2_results,
            'user_id': user_id
        })
        
        return {
            'answer': answer,
            'sources': [{'title': r.get('title', ''), 'content': r.get('content', '')} for r in l2_results[:3]],
            'intent': 'course_knowledge'
        }
    
    def _handle_system_operation(self, query: str) -> Dict:
        """处理系统操作问题"""
        print("   ⚙️ 处理系统操作问题...")
        
        # 简单规则匹配
        if '怎么' in query or '如何' in query:
            answer = """信电学院 AI 知识问答系统使用说明：

1. 在钉钉群中直接提问，系统会自动回答
2. 问题应围绕信电学院课程内容
3. 可以追问，系统会结合上下文回答
4. 回答会引用教材原文，确保准确性

如需帮助，请联系管理员。"""
        else:
            answer = "请直接提出您的课程问题，我会基于教材为您解答。"
        
        return {
            'answer': answer,
            'sources': [],
            'intent': 'system_operation'
        }
    
    def _handle_casual_chat(self, query: str) -> Dict:
        """处理闲聊"""
        print("   💬 处理闲聊...")
        
        # 简单规则匹配
        if '你好' in query:
            answer = "你好！我是信电学院 AI 知识问答助手，有什么课程问题需要帮助吗？"
        elif '谢谢' in query:
            answer = "不客气！如有其他问题，随时提问。"
        else:
            answer = "我是信电学院 AI 知识问答助手，主要回答课程相关问题。请提出您的课程问题。"
        
        return {
            'answer': answer,
            'sources': [],
            'intent': 'casual_chat'
        }
    
    def _build_context(self, l2_results: list) -> str:
        """构建知识片段"""
        context_parts = []
        for i, result in enumerate(l2_results[:5], 1):
            content = result.get('content', '')
            title = result.get('title', f'片段{i}')
            context_parts.append(f"[{title}]\n{content}")
        
        return '\n\n'.join(context_parts)
    
    def _memory_sediment(self, query: str, result: Dict, session_id: str, user_id: str):
        """记忆沉淀"""
        print("   💾 记忆沉淀...")
        
        # 更新 L3 高频问题统计
        self.memory_router.l3_write_faq_stats(query)
        
        # 更新用户画像（如有 user_id）
        if user_id:
            profile = self.memory_router.l3_read_user_profile(user_id) or {}
            # 简单更新：记录提问次数
            profile['question_count'] = profile.get('question_count', 0) + 1
            self.memory_router.l3_write_user_profile(user_id, profile)
        
        # 写入对话摘要（简化版）
        summary = f"用户提问：{query}\n回答类型：{result['intent']}"
        self.memory_router.l3_write_conversation_summary(session_id, summary)
    
    def search_knowledge(self, query: str) -> list:
        """直接搜索知识库"""
        return self.bailian_skill.search(query)

# 测试代码
if __name__ == '__main__':
    # 初始化系统
    system = XindianQASystem()
    
    # 测试查询
    test_query = "电路分析基础中的基尔霍夫定律是什么？"
    test_session = "test_session_001"
    test_user = "test_user_001"
    
    result = system.process_query(test_query, test_session, test_user)
    
    print("\n" + "="*50)
    print("📝 查询结果：")
    print(f"意图：{result['intent']}")
    print(f"回答：{result['answer'][:200]}...")
    print(f"来源：{len(result['sources'])} 个片段")
    print("="*50)
