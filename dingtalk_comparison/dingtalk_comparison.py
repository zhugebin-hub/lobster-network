#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钉钉 AI 助手对比实验
实验名称：钉钉原生 AI 助理与自建 AI 助手对比体验
实验者：陈政道
日期：2026 年 4 月 5 日
"""

import json
from datetime import datetime
from typing import Dict, List


# ==================== 第一部分：测试场景设计 ====================

TEST_SCENARIOS = [
    {
        "id": 1,
        "name": "日常问候",
        "questions": ["你好", "早上好", "在吗"],
        "expectation": "友好问候，引导用户提问"
    },
    {
        "id": 2,
        "name": "知识问答",
        "questions": ["什么是人工智能？", "Python 和 Java 有什么区别？"],
        "expectation": "准确回答概念性问题"
    },
    {
        "id": 3,
        "name": "任务处理",
        "questions": ["帮我写一封邮件", "创建一个待办事项"],
        "expectation": "理解任务意图，提供协助"
    },
    {
        "id": 4,
        "name": "专业咨询",
        "questions": ["小龙虾养殖需要什么条件？", "糖尿病有哪些症状？"],
        "expectation": "提供专业领域知识"
    },
    {
        "id": 5,
        "name": "多轮对话",
        "questions": ["推荐几本书", "第一本多少钱？", "在哪里可以买到？"],
        "expectation": "保持上下文连贯性"
    },
    {
        "id": 6,
        "name": "创意生成",
        "questions": ["帮我写一首诗", "想一个产品 slogan"],
        "expectation": "展现创造力和想象力"
    }
]


# ==================== 第二部分：体验记录类 ====================

class ExperienceRecorder:
    """体验记录器"""
    
    def __init__(self):
        self.records = []
        self.start_time = datetime.now()
        
    def add_record(self, assistant_type: str, scenario: Dict, 
                   question: str, response: str, rating: int, notes: str):
        """
        添加体验记录
        :param assistant_type: 助手类型（钉钉原生/自建）
        :param scenario: 测试场景
        :param question: 问题
        :param response: 回复
        :param rating: 评分（1-5）
        :param notes: 备注
        """
        self.records.append({
            "timestamp": datetime.now().isoformat(),
            "assistant_type": assistant_type,
            "scenario_id": scenario["id"],
            "scenario_name": scenario["name"],
            "question": question,
            "response": response,
            "rating": rating,
            "notes": notes
        })
    
    def calculate_scores(self) -> Dict:
        """计算各项得分"""
        scores = {
            "钉钉原生 AI 助理": {"total": 0, "count": 0, "avg": 0},
            "自建 AI 助手": {"total": 0, "count": 0, "avg": 0}
        }
        
        for record in self.records:
            atype = record["assistant_type"]
            scores[atype]["total"] += record["rating"]
            scores[atype]["count"] += 1
        
        for atype in scores:
            if scores[atype]["count"] > 0:
                scores[atype]["avg"] = scores[atype]["total"] / scores[atype]["count"]
        
        return scores
    
    def export_data(self) -> Dict:
        """导出数据"""
        return {
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "total_records": len(self.records),
            "scores": self.calculate_scores(),
            "records": self.records
        }


# ==================== 第三部分：模拟体验数据 ====================

def generate_mock_responses():
    """
    生成模拟体验数据
    实际使用时应替换为真实交互记录
    """
    return {
        "钉钉原生 AI 助理": {
            "日常问候": [
                {
                    "question": "你好",
                    "response": "您好！我是钉钉 AI 助理，很高兴为您服务！请问有什么可以帮您？我可以帮您查询信息、处理任务、解答问题等。",
                    "rating": 5,
                    "notes": "回复热情友好，主动引导用户提问"
                },
                {
                    "question": "早上好",
                    "response": "早上好！☀️ 新的一天开始了，祝您工作顺利！有什么我可以帮您的吗？",
                    "rating": 5,
                    "notes": "带表情符号，语气亲切自然"
                }
            ],
            "知识问答": [
                {
                    "question": "什么是人工智能？",
                    "response": "人工智能（AI）是计算机科学的一个分支，致力于创造能够模拟、延伸和扩展人类智能的理论、方法、技术及应用系统。主要包括：1.机器学习；2.深度学习；3.自然语言处理；4.计算机视觉等。当前 AI 已广泛应用于语音助手、图像识别、自动驾驶等领域。",
                    "rating": 5,
                    "notes": "回答准确全面，结构清晰"
                }
            ],
            "任务处理": [
                {
                    "question": "帮我写一封邮件",
                    "response": "好的，我来帮您写邮件。请告诉我：1.收件人是谁？2.邮件主题是什么？3.主要想表达什么内容？我会根据您的要求生成邮件草稿。",
                    "rating": 4,
                    "notes": "主动询问关键信息，引导用户完成"
                }
            ],
            "专业咨询": [
                {
                    "question": "小龙虾养殖需要什么条件？",
                    "response": "小龙虾养殖需要以下条件：1.水质要求：pH 值 7-8.5，溶氧量>5mg/L；2.水温：15-30℃为宜；3.池塘：面积 3-10 亩，水深 1-1.5 米；4.水草：覆盖率 30-50%；5.防逃设施：池埂四周设置防逃网。建议您咨询当地水产技术推广站获取更详细的指导。",
                    "rating": 5,
                    "notes": "专业知识准确，给出实用建议"
                }
            ],
            "多轮对话": [
                {
                    "question": "推荐几本书",
                    "response": "好的，为您推荐几本好书：1.《人类简史》- 了解人类历史；2.《思考快与慢》- 理解决策心理；3.《三体》- 科幻经典。您对哪类书籍更感兴趣呢？",
                    "rating": 5,
                    "notes": "推荐多样化，主动询问偏好"
                },
                {
                    "question": "第一本多少钱？",
                    "response": "《人类简史》的价格因版本不同有所差异：精装版约 68 元，平装版约 48 元，电子版约 19.9 元。您可以在京东、当当、亚马逊等平台购买。需要我帮您查询具体购买链接吗？",
                    "rating": 5,
                    "notes": "理解上下文，准确回答"
                }
            ],
            "创意生成": [
                {
                    "question": "帮我写一首诗",
                    "response": "《春日》\n春风拂面柳丝轻，\n花开满园蝶自鸣。\n岁月如歌人未老，\n且行且唱且从容。\n\n希望您喜欢！需要我调整风格或主题吗？",
                    "rating": 5,
                    "notes": "有一定文学素养，主动询问反馈"
                }
            ]
        },
        "自建 AI 助手": {
            "日常问候": [
                {
                    "question": "你好",
                    "response": "您好！我是企业微信 AI 助手，很高兴为您服务！请问有什么可以帮您？",
                    "rating": 4,
                    "notes": "回复规范但略显单调"
                },
                {
                    "question": "早上好",
                    "response": "您好！我是企业微信 AI 助手，目前还在学习阶段。您可以问我关于公司制度、产品信息、技术支持等方面的问题。",
                    "rating": 3,
                    "notes": "未能识别问候语境，回复模板化"
                }
            ],
            "知识问答": [
                {
                    "question": "什么是人工智能？",
                    "response": "您好！我是企业微信 AI 助手，目前还在学习阶段。您可以问我关于公司制度、产品信息、技术支持等方面的问题。",
                    "rating": 2,
                    "notes": "知识库未覆盖通用知识，回复默认内容"
                }
            ],
            "任务处理": [
                {
                    "question": "帮我写一封邮件",
                    "response": "您好！我是企业微信 AI 助手，目前还在学习阶段。您可以问我关于公司制度、产品信息、技术支持等方面的问题。",
                    "rating": 2,
                    "notes": "无法处理复杂任务"
                }
            ],
            "专业咨询": [
                {
                    "question": "小龙虾养殖需要什么条件？",
                    "response": "🦞 小龙虾智能助手为您解答：\n\n【养殖技术】\n问：小龙虾养殖需要什么条件？\n答：小龙虾养殖需要：1.水质清洁，pH 值 7-8.5；2.水温 15-30℃；3.溶氧量>5mg/L；4.水草覆盖率 30-50%；5.池塘面积 3-10 亩为宜。",
                    "rating": 5,
                    "notes": "垂直领域知识准确，格式清晰"
                }
            ],
            "多轮对话": [
                {
                    "question": "推荐几本书",
                    "response": "您好！我是企业微信 AI 助手，目前还在学习阶段。您可以问我关于公司制度、产品信息、技术支持等方面的问题。",
                    "rating": 2,
                    "notes": "无上下文理解能力"
                },
                {
                    "question": "第一本多少钱？",
                    "response": "您好！我是企业微信 AI 助手，目前还在学习阶段。您可以问我关于公司制度、产品信息、技术支持等方面的问题。",
                    "rating": 1,
                    "notes": "完全丢失上下文"
                }
            ],
            "创意生成": [
                {
                    "question": "帮我写一首诗",
                    "response": "您好！我是企业微信 AI 助手，目前还在学习阶段。您可以问我关于公司制度、产品信息、技术支持等方面的问题。",
                    "rating": 1,
                    "notes": "无创意生成能力"
                }
            ]
        }
    }


# ==================== 第四部分：对比分析 ====================

def analyze_differences(mock_data: Dict) -> Dict:
    """
    分析两者差异
    """
    analysis = {
        "响应速度": {
            "钉钉原生": "快速，几乎即时响应",
            "自建": "快速，本地处理无延迟",
            "差异": "相当"
        },
        "知识广度": {
            "钉钉原生": "覆盖通用知识、专业知识、生活常识等",
            "自建": "仅限预设知识库（企业制度 + 小龙虾）",
            "差异": "钉钉原生明显更广"
        },
        "对话连贯性": {
            "钉钉原生": "支持多轮对话，理解上下文",
            "自建": "单轮对话，无上下文记忆",
            "差异": "钉钉原生优势明显"
        },
        "专业深度": {
            "钉钉原生": "各领域均衡，专业领域准确",
            "自建": "垂直领域（小龙虾）专业准确",
            "差异": "自建在特定领域可媲美"
        },
        "个性化": {
            "钉钉原生": "语气自然，使用表情符号",
            "自建": "模板化回复，较为机械",
            "差异": "钉钉原生更友好"
        },
        "任务处理": {
            "钉钉原生": "可处理写邮件、创待办等复杂任务",
            "自建": "仅支持简单问答",
            "差异": "钉钉原生功能更强"
        },
        "可定制性": {
            "钉钉原生": "有限定制，依赖平台能力",
            "自建": "完全可控，可深度定制",
            "差异": "自建更灵活"
        },
        "部署成本": {
            "钉钉原生": "开箱即用，零开发成本",
            "自建": "需开发维护，时间成本高",
            "差异": "钉钉原生更经济"
        }
    }
    return analysis


# ==================== 第五部分：实验报告生成 ====================

def run_comparison_experiment():
    """
    运行对比实验
    """
    print("=" * 70)
    print("钉钉 AI 助手对比体验实验")
    print("实验名称：钉钉原生 AI 助理与自建 AI 助手对比体验")
    print("实验者：陈政道")
    print("日期：2026 年 4 月 5 日")
    print("=" * 70)
    print()
    
    # 1. 创建记录器
    print("【步骤 1】创建体验记录器...")
    recorder = ExperienceRecorder()
    print("✓ 记录器已就绪")
    print()
    
    # 2. 加载模拟数据
    print("【步骤 2】加载体验数据...")
    mock_data = generate_mock_responses()
    print(f"✓ 钉钉原生 AI 助理：{len(mock_data['钉钉原生 AI 助理'])} 个场景")
    print(f"✓ 自建 AI 助手：{len(mock_data['自建 AI 助手'])} 个场景")
    print()
    
    # 3. 记录体验
    print("【步骤 3】记录体验数据...")
    for assistant_type, scenarios in mock_data.items():
        for scenario_name, records in scenarios.items():
            scenario = next((s for s in TEST_SCENARIOS if s["name"] == scenario_name), None)
            if scenario:
                for record in records:
                    recorder.add_record(
                        assistant_type=assistant_type,
                        scenario=scenario,
                        question=record["question"],
                        response=record["response"],
                        rating=record["rating"],
                        notes=record["notes"]
                    )
    print(f"✓ 共记录 {len(recorder.records)} 条体验数据")
    print()
    
    # 4. 计算得分
    print("【步骤 4】计算评分...")
    scores = recorder.calculate_scores()
    for atype, score in scores.items():
        print(f"{atype}: 平均 {score['avg']:.1f} 分（总分{score['total']}, 记录{score['count']}条）")
    print()
    
    # 5. 差异分析
    print("【步骤 5】差异分析...")
    analysis = analyze_differences(mock_data)
    for dimension, details in analysis.items():
        print(f"\n【{dimension}】")
        print(f"  钉钉原生：{details['钉钉原生']}")
        print(f"  自建：{details['自建']}")
        print(f"  差异：{details['差异']}")
    print()
    
    # 6. 保存数据
    print("【步骤 6】保存实验数据...")
    data = recorder.export_data()
    with open("comparison_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("✓ 对比数据已保存：comparison_data.json")
    
    with open("experience_records.json", "w", encoding="utf-8") as f:
        json.dump(recorder.records, f, ensure_ascii=False, indent=2)
    print("✓ 体验记录已保存：experience_records.json")
    
    print()
    print("=" * 70)
    print("实验完成！")
    print("=" * 70)
    
    return recorder, analysis


if __name__ == "__main__":
    run_comparison_experiment()
