#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业微信 AI 助手实验
实验名称：基于阿里云百炼的企业微信 AI 助手构建与小龙虾智能体部署
实验者：陈政道
日期：2026 年 4 月 5 日
"""

import json
import os
import hashlib
import time
from datetime import datetime
from typing import Dict, List, Optional, Any


# ==================== 第一部分：企业微信 AI 助手核心类 ====================

class WeComAIAssistant:
    """
    企业微信 AI 助手核心类
    实现智能对话、知识库查询、任务处理等功能
    """
    
    def __init__(self, name="企业微信 AI 助手"):
        self.name = name
        self.conversations = {}  # 会话记录
        self.knowledge_base = {}  # 知识库
        self.created_at = datetime.now().isoformat()
        
    def add_knowledge(self, category: str, qa_pairs: List[Dict]):
        """
        添加知识库
        :param category: 知识分类
        :param qa_pairs: 问答对列表 [{"question": "", "answer": ""}]
        """
        if category not in self.knowledge_base:
            self.knowledge_base[category] = []
        self.knowledge_base[category].extend(qa_pairs)
        
    def search_knowledge(self, query: str, category: Optional[str] = None) -> List[Dict]:
        """
        搜索知识库
        :param query: 查询关键词
        :param category: 知识分类（可选）
        :return: 匹配的问答对
        """
        results = []
        categories = [category] if category else list(self.knowledge_base.keys())
        
        for cat in categories:
            if cat in self.knowledge_base:
                for qa in self.knowledge_base[cat]:
                    if query.lower() in qa["question"].lower() or query.lower() in qa["answer"].lower():
                        results.append({
                            "category": cat,
                            "question": qa["question"],
                            "answer": qa["answer"],
                            "score": self._calculate_similarity(query, qa["question"])
                        })
        
        # 按相似度排序
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
    
    def chat(self, user_id: str, message: str, context_size: int = 5) -> Dict:
        """
        智能对话
        :param user_id: 用户 ID
        :param message: 用户消息
        :param context_size: 上下文大小
        :return: 回复内容
        """
        # 初始化会话
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        
        # 添加用户消息到会话
        self.conversations[user_id].append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # 保持上下文大小
        if len(self.conversations[user_id]) > context_size * 2:
            self.conversations[user_id] = self.conversations[user_id][-context_size * 2:]
        
        # 生成回复
        response = self._generate_response(user_id, message)
        
        # 添加 AI 回复到会话
        self.conversations[user_id].append({
            "role": "assistant",
            "content": response["content"],
            "timestamp": datetime.now().isoformat()
        })
        
        return response
    
    def _generate_response(self, user_id: str, message: str) -> Dict:
        """
        生成回复
        """
        # 1. 尝试从知识库匹配
        knowledge_results = self.search_knowledge(message)
        if knowledge_results and knowledge_results[0]["score"] > 0.5:
            return {
                "content": knowledge_results[0]["answer"],
                "source": "knowledge_base",
                "confidence": knowledge_results[0]["score"]
            }
        
        # 2. 基于规则的回复
        response = self._rule_based_response(message)
        if response:
            return {
                "content": response,
                "source": "rule_based",
                "confidence": 0.8
            }
        
        # 3. 默认回复
        return {
            "content": "您好！我是企业微信 AI 助手，目前还在学习阶段。您可以问我关于公司制度、产品信息、技术支持等方面的问题。",
            "source": "default",
            "confidence": 0.5
        }
    
    def _rule_based_response(self, message: str) -> Optional[str]:
        """
        基于规则的回复
        """
        message_lower = message.lower()
        
        # 问候语
        if any(word in message_lower for word in ["你好", "您好", "hello", "hi", "早上好", "下午好"]):
            return "您好！我是企业微信 AI 助手，很高兴为您服务！请问有什么可以帮您？"
        
        # 自我介绍
        if any(word in message_lower for word in ["你是谁", "你是谁啊", "介绍一下自己", "self introduction"]):
            return "我是企业微信 AI 助手，基于阿里云百炼大模型构建。我可以帮助您解答公司制度、产品信息、技术支持等问题。"
        
        # 感谢
        if any(word in message_lower for word in ["谢谢", "thank you", "thanks"]):
            return "不客气！如有其他问题，随时欢迎咨询！"
        
        return None
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        计算文本相似度（简单版本）
        """
        set1 = set(text1.lower())
        set2 = set(text2.lower())
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0
    
    def get_conversation_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """
        获取会话历史
        """
        if user_id not in self.conversations:
            return []
        return self.conversations[user_id][-limit:]
    
    def export_data(self) -> Dict:
        """
        导出数据
        """
        return {
            "name": self.name,
            "created_at": self.created_at,
            "knowledge_base": self.knowledge_base,
            "total_conversations": len(self.conversations),
            "total_messages": sum(len(msgs) for msgs in self.conversations.values())
        }


# ==================== 第二部分：小龙虾智能体 ====================

class CrayfishAgent:
    """
    小龙虾智能体
    专门用于小龙虾养殖、销售、烹饪等领域的 AI 助手
    """
    
    def __init__(self):
        self.name = "小龙虾智能助手"
        self.knowledge = self._build_knowledge_base()
        
    def _build_knowledge_base(self) -> Dict:
        """
        构建小龙虾知识库
        """
        return {
            "养殖技术": [
                {
                    "question": "小龙虾养殖需要什么条件？",
                    "answer": "小龙虾养殖需要：1.水质清洁，pH 值 7-8.5；2.水温 15-30℃；3.溶氧量>5mg/L；4.水草覆盖率 30-50%；5.池塘面积 3-10 亩为宜。"
                },
                {
                    "question": "小龙虾什么时候放苗最好？",
                    "answer": "小龙虾放苗最佳时间：1.春季 3-4 月，水温稳定在 15℃以上；2.秋季 9-10 月。避免高温季节放苗，选择晴天上午进行。"
                },
                {
                    "question": "小龙虾吃什么饲料？",
                    "answer": "小龙虾是杂食性动物，饲料包括：1.植物性饲料：水草、藻类、蔬菜；2.动物性饲料：小鱼虾、螺蛳、蚯蚓；3.配合饲料：蛋白质含量 30-35%。"
                },
                {
                    "question": "小龙虾养殖周期多长？",
                    "answer": "小龙虾养殖周期一般为 2-3 个月。3-4 月放苗，5-6 月可捕捞上市。一年可养殖 2-3 茬，亩产可达 200-400 斤。"
                }
            ],
            "疾病防治": [
                {
                    "question": "小龙虾常见疾病有哪些？",
                    "answer": "小龙虾常见疾病：1.黑鳃病；2.烂尾病；3.肠炎病；4.水霉病；5.聚缩虫病。预防为主，定期消毒，保持水质清洁。"
                },
                {
                    "question": "小龙虾黑鳃病怎么治疗？",
                    "answer": "黑鳃病治疗：1.改善水质，换水 30%；2.使用二氧化氯或聚维酮碘消毒；3.饲料中添加维生素 C 和免疫多糖；4.连续治疗 5-7 天。"
                }
            ],
            "烹饪方法": [
                {
                    "question": "麻辣小龙虾怎么做？",
                    "answer": "麻辣小龙虾做法：1.小龙虾洗净去腮；2.热油爆香葱姜蒜、干辣椒、花椒；3.加入豆瓣酱炒香；4.放入小龙虾翻炒；5.加啤酒焖煮 15 分钟；6.收汁装盘。"
                },
                {"question": "小龙虾怎么清洗最干净？",
                    "answer": "小龙虾清洗步骤：1.用清水浸泡 2 小时；2.用刷子刷洗腹部和爪子；3.捏住尾部中间抽出虾线；4.剪去头部 1/3 去除腮；5.用清水冲洗 3 遍。"}
            ],
            "市场行情": [
                {
                    "question": "小龙虾什么季节最便宜？",
                    "answer": "小龙虾价格规律：1.4-5 月上市初期价格较高；2.6-8 月大量上市，价格最低；3.9 月后价格回升。建议 6-7 月购买最划算。"
                },
                {
                    "question": "小龙虾如何挑选？",
                    "answer": "挑选小龙虾：1.看活力：活动能力强；2.看外壳：完整有光泽；3.看腹部：干净无黑斑；4.闻气味：无异味；5.选大小：均匀饱满。"
                }
            ]
        }
    
    def query(self, question: str, category: Optional[str] = None) -> List[Dict]:
        """
        查询小龙虾知识
        """
        results = []
        categories = [category] if category else list(self.knowledge.keys())
        
        for cat in categories:
            if cat in self.knowledge:
                for item in self.knowledge[cat]:
                    if isinstance(item, dict) and ("question" in item):
                        if any(word in item["question"].lower() for word in question.lower()):
                            results.append({
                                "category": cat,
                                "question": item["question"],
                                "answer": item["answer"]
                            })
        
        return results
    
    def get_menu(self) -> Dict:
        """
        获取功能菜单
        """
        return {
            "name": self.name,
            "categories": list(self.knowledge.keys()),
            "commands": [
                "/help - 显示帮助信息",
                "/menu - 显示功能菜单",
                "/养殖 - 查询养殖技术",
                "/疾病 - 查询疾病防治",
                "/烹饪 - 查询烹饪方法",
                "/行情 - 查询市场行情"
            ]
        }


# ==================== 第三部分：企业微信消息处理 ====================

class WeComMessageHandler:
    """
    企业微信消息处理器
    处理企业微信 API 消息格式
    """
    
    def __init__(self, assistant: WeComAIAssistant):
        self.assistant = assistant
        self.crayfish_agent = CrayfishAgent()
        
    def parse_message(self, data: Dict) -> Dict:
        """
        解析企业微信消息
        """
        return {
            "user_id": data.get("UserID", ""),
            "message": data.get("Content", ""),
            "message_type": data.get("MsgType", "text"),
            "timestamp": data.get("CreateTime", int(time.time())),
            "agent_id": data.get("AgentID", "")
        }
    
    def process_text_message(self, parsed_msg: Dict) -> Dict:
        """
        处理文本消息
        """
        user_id = parsed_msg["user_id"]
        message = parsed_msg["message"]
        
        # 检查是否是小龙虾相关查询
        if any(word in message for word in ["小龙虾", "龙虾", "养殖", "烹饪", "麻辣"]):
            results = self.crayfish_agent.query(message)
            if results:
                response_text = f"🦞 小龙虾智能助手为您解答：\n\n"
                for r in results[:2]:
                    response_text += f"【{r['category']}】\n"
                    response_text += f"问：{r['question']}\n"
                    response_text += f"答：{r['answer']}\n\n"
                return {
                    "msgtype": "text",
                    "text": {
                        "content": response_text
                    }
                }
        
        # 普通 AI 助手回复
        response = self.assistant.chat(user_id, message)
        return {
            "msgtype": "text",
            "text": {
                "content": response["content"]
            }
        }
    
    def format_response(self, response: Dict) -> str:
        """
        格式化响应为 JSON
        """
        return json.dumps(response, ensure_ascii=False, indent=2)


# ==================== 第四部分：实验演示 ====================

def run_demo():
    """
    运行实验演示
    """
    print("=" * 70)
    print("企业微信 AI 助手实验")
    print("实验名称：基于阿里云百炼的企业微信 AI 助手构建与小龙虾智能体部署")
    print("实验者：陈政道")
    print("日期：2026 年 4 月 5 日")
    print("=" * 70)
    print()
    
    # 1. 创建 AI 助手
    print("【步骤 1】创建企业微信 AI 助手...")
    assistant = WeComAIAssistant("企业微信 AI 助手")
    
    # 添加企业知识库
    assistant.add_knowledge("公司制度", [
        {"question": "上班时间是什么？", "answer": "公司上班时间：周一至周五 9:00-18:00，午休 12:00-13:30。"},
        {"question": "如何请假？", "answer": "请假流程：1.提前在企业微信提交申请；2.直属领导审批；3.人事备案。"},
        {"question": "工资什么时候发？", "answer": "工资发放时间：每月 15 日发放上月工资，遇节假日提前。"}
    ])
    
    assistant.add_knowledge("产品信息", [
        {"question": "公司有哪些产品？", "answer": "公司主要产品：1.企业微信 AI 助手；2.知识图谱系统；3.智能客服平台。"},
        {"question": "如何购买产品？", "answer": "购买流程：1.联系销售顾问；2.需求沟通；3.签订合同；4.部署实施。"}
    ])
    
    print(f"✓ AI 助手已创建")
    print(f"✓ 知识库分类：{list(assistant.knowledge_base.keys())}")
    print()
    
    # 2. 创建小龙虾智能体
    print("【步骤 2】创建小龙虾智能体...")
    crayfish = CrayfishAgent()
    menu = crayfish.get_menu()
    print(f"✓ 小龙虾智能体已创建")
    print(f"✓ 知识分类：{menu['categories']}")
    print()
    
    # 3. 创建消息处理器
    print("【步骤 3】创建消息处理器...")
    handler = WeComMessageHandler(assistant)
    print("✓ 消息处理器已就绪")
    print()
    
    # 4. 模拟对话测试
    print("【步骤 4】模拟对话测试...")
    print()
    
    test_messages = [
        ("user001", "你好"),
        ("user001", "上班时间是什么？"),
        ("user002", "小龙虾怎么养殖？"),
        ("user002", "麻辣小龙虾怎么做？"),
        ("user001", "谢谢"),
    ]
    
    for user_id, message in test_messages:
        print(f"用户 [{user_id}]: {message}")
        parsed = handler.parse_message({
            "UserID": user_id,
            "Content": message,
            "MsgType": "text",
            "CreateTime": int(time.time()),
            "AgentID": "1000001"
        })
        response = handler.process_text_message(parsed)
        print(f"AI 助手：{response['text']['content'].strip()}")
        print("-" * 50)
    
    # 5. 导出数据
    print("【步骤 5】导出实验数据...")
    data = assistant.export_data()
    print(f"✓ 总会话数：{data['total_conversations']}")
    print(f"✓ 总消息数：{data['total_messages']}")
    print()
    
    # 6. 保存数据
    print("【步骤 6】保存实验数据...")
    
    with open("wecom_assistant_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("✓ 助手数据已保存：wecom_assistant_data.json")
    
    with open("crayfish_knowledge.json", "w", encoding="utf-8") as f:
        json.dump(crayfish.knowledge, f, ensure_ascii=False, indent=2)
    print("✓ 小龙虾知识库已保存：crayfish_knowledge.json")
    
    with open("conversation_logs.json", "w", encoding="utf-8") as f:
        logs = {}
        for user_id, msgs in assistant.conversations.items():
            logs[user_id] = msgs
        json.dump(logs, f, ensure_ascii=False, indent=2)
    print("✓ 会话记录已保存：conversation_logs.json")
    
    print()
    print("=" * 70)
    print("实验完成！")
    print("=" * 70)
    
    return assistant, crayfish, handler


if __name__ == "__main__":
    run_demo()
