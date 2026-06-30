#!/usr/bin/env python3
"""
Prompt 模板系统
负责管理信电学院知识问答系统的各种 Prompt 模板
"""

class PromptTemplates:
    """Prompt 模板类"""
    
    # ========== 系统 Prompt ==========
    
    SYSTEM_PROMPT = """你是信电学院 AI 知识问答助手"小龙虾数字员工"。

你的职责：
1. 基于教材原文，提供准确、有据可查的专业知识问答
2. 引用原文段落，确保回答可溯源
3. 根据用户学习画像，提供个性化学习建议
4. 保持专业、友好的回答风格

回答规则：
- 如果知识片段足以回答问题，直接给出答案并引用原文
- 如果知识片段不足以回答问题，说明原因并建议用户查阅相关教材章节
- 不要编造不存在的内容
- 回答要简洁明了，避免冗长
- 对于复杂问题，可以分步骤解释"""

    # ========== 问答 Prompt ==========
    
    QA_PROMPT = """基于以下知识片段回答用户问题：

知识片段：
{context}

用户问题：{question}

请根据知识片段给出准确回答。如果知识片段不足以回答问题，请说明。

回答格式：
1. 直接给出答案
2. 引用相关原文（如有）
3. 提供进一步学习建议（如有）"""

    # ========== 意图识别 Prompt ==========
    
    INTENT_PROMPT = """请判断以下用户提问的意图类型：

用户提问：{question}

意图类型：
- course_knowledge: 课程知识问题（需要检索教材）
- system_operation: 系统操作问题（如何使用系统）
- casual_chat: 闲聊（不需要检索）

请只返回意图类型，不要返回其他内容。"""

    # ========== 摘要提取 Prompt ==========
    
    SUMMARY_PROMPT = """请对以下对话进行摘要：

对话内容：
{conversation}

请提取：
1. 用户主要问题
2. 关键知识点
3. 用户学习偏好（如有）
4. 后续建议（如有）

摘要格式：
- 主要问题：...
- 关键知识点：...
- 学习偏好：...
- 后续建议：..."""

    # ========== 用户画像更新 Prompt ==========
    
    USER_PROFILE_PROMPT = """基于以下对话，更新用户学习画像：

当前用户画像：
{current_profile}

新对话内容：
{conversation}

请更新：
1. 用户已掌握的知识点
2. 用户薄弱的知识点
3. 用户学习偏好
4. 用户提问频率

更新格式：
- 已掌握知识点：...
- 薄弱知识点：...
- 学习偏好：...
- 提问频率：..."""

    # ========== FAQ 生成 Prompt ==========
    
    FAQ_PROMPT = """基于以下对话，生成 FAQ 问答对：

对话内容：
{conversation}

请生成：
1. 标准化问题
2. 标准答案
3. 相关知识点

格式：
问题：...
答案：...
知识点：..."""

    # ========== 方法 ==========
    
    def get_system_prompt(self) -> str:
        """获取系统 Prompt"""
        return self.SYSTEM_PROMPT
    
    def get_qa_prompt(self, context: str, question: str) -> str:
        """获取问答 Prompt"""
        return self.QA_PROMPT.format(context=context, question=question)
    
    def get_intent_prompt(self, question: str) -> str:
        """获取意图识别 Prompt"""
        return self.INTENT_PROMPT.format(question=question)
    
    def get_summary_prompt(self, conversation: str) -> str:
        """获取摘要提取 Prompt"""
        return self.SUMMARY_PROMPT.format(conversation=conversation)
    
    def get_user_profile_prompt(self, current_profile: str, conversation: str) -> str:
        """获取用户画像更新 Prompt"""
        return self.USER_PROFILE_PROMPT.format(
            current_profile=current_profile,
            conversation=conversation
        )
    
    def get_faq_prompt(self, conversation: str) -> str:
        """获取 FAQ 生成 Prompt"""
        return self.FAQ_PROMPT.format(conversation=conversation)

# 测试代码
if __name__ == '__main__':
    templates = PromptTemplates()
    print("Prompt 模板系统初始化成功")
    print(f"系统 Prompt 长度：{len(templates.get_system_prompt())} 字符")
