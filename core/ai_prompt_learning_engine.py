#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 - AI绘画提示词工程师学习技能
功能：
1. 培养AI绘画提示词工程师
2. 4周学习路径（基础→风格→商业→模板库）
3. 淘宝商业变现准备

作者：诸葛马 (Hermes)
日期：2026-06-30
版本：v1.0
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

# ============================================================
# 配置
# ============================================================

class Config:
    """AI绘画提示词工程师配置"""
    
    # 学习路径
    LEARNING_PATH = {
        "week1": {
            "name": "提示词基础语法",
            "duration_days": 7,
            "modules": [
                {
                    "module_id": "w1_basic_syntax",
                    "name": "基础语法结构",
                    "description": "掌握提示词基本结构：subject, style, mood, lighting, composition",
                    "problem_count": 20,
                    "practice_count": 10,
                    "topics": [
                        "主体描述（subject）：人物/场景/物品",
                        "风格定义（style）：写实/插画/3D/艺术",
                        "氛围营造（mood）：温馨/神秘/史诗/科幻",
                        "光线设置（lighting）：自然光/studio/戏剧/霓虹",
                        "构图技巧（composition）：rule_of_thirds/close_up/wide_angle",
                    ],
                    "learning_resources": [
                        "Midjourney官方文档提示词指南",
                        "PromptHero提示词结构解析",
                        "Civitai社区热门提示词分析",
                    ],
                    "practice_tasks": [
                        "生成5张不同主体的图片",
                        "生成5张不同风格的图片",
                        "对比不同光线设置的效果",
                    ],
                },
                {
                    "module_id": "w1_parameters",
                    "name": "参数理解与应用",
                    "description": "掌握Midjourney核心参数：--ar, --v, --style, --chaos, --seed",
                    "problem_count": 15,
                    "practice_count": 10,
                    "topics": [
                        "宽高比（--ar）：16:9/9:16/1:1/4:3",
                        "版本（--v）：v5/v6/niji",
                        "风格化（--style）：raw/vivid",
                        "随机性（--chaos）：0-100",
                        "种子（--seed）：固定/随机",
                        "质量（--quality）：.25/.5/1",
                    ],
                    "practice_tasks": [
                        "用不同宽高比生成同一主题",
                        "对比v5和v6的效果差异",
                        "用不同chaos值生成系列图",
                    ],
                },
                {
                    "module_id": "w1_weight_control",
                    "name": "权重控制与负面提示词",
                    "description": "掌握权重控制语法和负面提示词",
                    "problem_count": 15,
                    "practice_count": 10,
                    "topics": [
                        "权重语法（::）：cat::1.5 dog::0.5",
                        "强调括号（()）：(beautiful) face",
                        "弱化括号（[]）：[blurry] background",
                        "负面提示词（--no）：--no text, watermark",
                        "负面提示词（--negprompt）：高级用法",
                    ],
                    "practice_tasks": [
                        "用权重控制生成混合主题",
                        "用强调/弱化调整细节",
                        "用负面提示词排除不需要的元素",
                    ],
                },
            ],
            "total_problems": 50,
            "total_practice": 30,
            "target": "掌握Midjourney基础语法和参数",
        },
        "week2": {
            "name": "风格与参数进阶",
            "duration_days": 7,
            "modules": [
                {
                    "module_id": "w2_realistic",
                    "name": "写实风格",
                    "description": "掌握photorealistic和cinematic风格",
                    "problem_count": 10,
                    "practice_count": 10,
                    "topics": [
                        "photorealistic：超写实人物/风景",
                        "cinematic：电影感光影和构图",
                        "product photography：商业产品摄影",
                        "portrait photography：人像摄影",
                    ],
                    "practice_tasks": [
                        "生成5张超写实人像",
                        "生成5张电影感场景",
                        "生成5张商业产品图",
                    ],
                },
                {
                    "module_id": "w2_illustration",
                    "name": "插画风格",
                    "description": "掌握illustration/anime/watercolor风格",
                    "problem_count": 10,
                    "practice_count": 10,
                    "topics": [
                        "illustration：商业插画/绘本风格",
                        "anime：日本动漫风格",
                        "watercolor：水彩画风格",
                        "pixel art：像素艺术风格",
                    ],
                    "practice_tasks": [
                        "生成5张商业插画",
                        "生成5张动漫风格图",
                        "生成5张水彩画风格图",
                    ],
                },
                {
                    "module_id": "w2_3d_art",
                    "name": "3D与数字艺术",
                    "description": "掌握3D render和digital art风格",
                    "problem_count": 10,
                    "practice_count": 10,
                    "topics": [
                        "3D render：Blender/Octane渲染",
                        "digital art：数字绘画",
                        "concept art：概念设计",
                        "isometric：等距视角",
                    ],
                    "practice_tasks": [
                        "生成5张3D渲染图",
                        "生成5张数字艺术图",
                        "生成5张概念设计图",
                    ],
                },
                {
                    "module_id": "w2_commercial",
                    "name": "商业视觉设计",
                    "description": "掌握商业级视觉设计提示词",
                    "problem_count": 10,
                    "practice_count": 10,
                    "topics": [
                        "logo design：极简/渐变/3D logo",
                        "packaging design：包装设计",
                        "poster design：海报设计",
                        "brand identity：品牌视觉",
                    ],
                    "practice_tasks": [
                        "生成5个logo设计",
                        "生成5个包装设计",
                        "生成5个海报设计",
                    ],
                },
            ],
            "total_problems": 40,
            "total_practice": 40,
            "target": "掌握10种主流AI绘画风格",
        },
        "week3": {
            "name": "商业级提示词",
            "duration_days": 7,
            "modules": [
                {
                    "module_id": "w3_taobao",
                    "name": "淘宝商品图",
                    "description": "生成淘宝级商品图提示词",
                    "problem_count": 10,
                    "practice_count": 15,
                    "topics": [
                        "服装商品图：模特展示/平铺/挂拍",
                        "数码产品图：科技感和细节展示",
                        "家居用品图：场景化展示",
                        "美妆产品图：精致质感和光影",
                        "食品商品图：食欲感和色彩",
                    ],
                    "practice_tasks": [
                        "生成5张服装商品图",
                        "生成5张数码产品图",
                        "生成5张家居用品图",
                    ],
                },
                {
                    "module_id": "w3_social_media",
                    "name": "社交媒体配图",
                    "description": "生成小红书/抖音/Instagram配图",
                    "problem_count": 10,
                    "practice_count": 15,
                    "topics": [
                        "小红书封面：吸引眼球的视觉设计",
                        "抖音背景：动态感和视觉冲击",
                        "Instagram配图：ins风和美学",
                        "微博配图：信息图和海报",
                    ],
                    "practice_tasks": [
                        "生成5张小红书封面",
                        "生成5张抖音背景",
                        "生成5张Instagram配图",
                    ],
                },
                {
                    "module_id": "w3_avatar",
                    "name": "AI头像定制",
                    "description": "生成各类AI头像提示词",
                    "problem_count": 10,
                    "practice_count": 20,
                    "topics": [
                        "写实头像：超写实人像",
                        "卡通头像：Q版/日系/欧美",
                        "二次元头像：动漫风格",
                        "商务头像：职业形象",
                        "情侣头像：配对设计",
                    ],
                    "practice_tasks": [
                        "生成5张写实头像",
                        "生成5张卡通头像",
                        "生成5张二次元头像",
                        "生成5张商务头像",
                    ],
                },
            ],
            "total_problems": 30,
            "total_practice": 50,
            "target": "生成淘宝级商业提示词",
        },
        "week4": {
            "name": "模板库建设",
            "duration_days": 7,
            "modules": [
                {
                    "module_id": "w4_template_library",
                    "name": "提示词模板库",
                    "description": "整理和分类提示词模板",
                    "problem_count": 10,
                    "practice_count": 30,
                    "topics": [
                        "分类整理：按风格/用途/难度分类",
                        "标签系统：便于搜索的标签体系",
                        "使用教程：买家指南和示例",
                        "定价策略：9.9-49元/套",
                    ],
                    "practice_tasks": [
                        "整理50个基础提示词模板",
                        "整理50个风格提示词模板",
                        "整理50个商业提示词模板",
                        "编写使用教程",
                    ],
                },
                {
                    "module_id": "w4_taobao_prep",
                    "name": "淘宝上架准备",
                    "description": "准备淘宝商品上架",
                    "problem_count": 5,
                    "practice_count": 20,
                    "topics": [
                        "商品标题优化：关键词和搜索优化",
                        "主图设计：吸引点击的视觉设计",
                        "详情页设计：展示商品价值",
                        "定价策略：竞争力定价",
                        "客服话术：常见问题解答",
                    ],
                    "practice_tasks": [
                        "设计3个商品标题",
                        "设计3张主图",
                        "设计3个详情页",
                        "编写客服话术",
                    ],
                },
            ],
            "total_problems": 15,
            "total_practice": 50,
            "target": "完成100+提示词模板库，准备淘宝上架",
        },
    }
    
    # 学员配置
    STUDENTS = {
        "xiaochen": {
            "name": "小陈",
            "focus": "商业级提示词和模板库建设",
            "strengths": ["基础扎实", "稳定性好"],
            "weaknesses": ["推理力不足", "需要分步指导"],
        },
        "zhuguxia": {
            "name": "诸葛虾",
            "focus": "风格多样性和快速生成",
            "strengths": ["解题速度快", "工具力强"],
            "weaknesses": ["反思力不足", "需要深度练习"],
        },
        "qoder": {
            "name": "qoder",
            "focus": "系统性学习和模板库建设",
            "strengths": ["实战能力强", "质量高"],
            "weaknesses": ["训练量偏少", "缺乏系统性"],
        },
    }
    
    # 共享目录
    SHARED_DIR = "/home/admin/go-training/shared/"
    AI_PROMPT_DIR = f"{SHARED_DIR}ai_prompt_training/"
    TEMPLATE_DIR = f"{AI_PROMPT_DIR}templates/"
    PRACTICE_DIR = f"{AI_PROMPT_DIR}practice/"


# ============================================================
# AI绘画提示词学习引擎
# ============================================================

class AIPromptLearningEngine:
    """AI绘画提示词学习引擎"""
    
    def __init__(self):
        self.config = Config()
        self._init_dirs()
    
    def _init_dirs(self):
        os.makedirs(self.config.AI_PROMPT_DIR, exist_ok=True)
        os.makedirs(self.config.TEMPLATE_DIR, exist_ok=True)
        os.makedirs(self.config.PRACTICE_DIR, exist_ok=True)
    
    def generate_week_plan(self, week: str) -> Dict:
        """生成周学习计划"""
        week_plan = self.config.LEARNING_PATH.get(week)
        if not week_plan:
            return {"error": f"未找到{week}的学习计划"}
        
        return {
            "week": week,
            "name": week_plan["name"],
            "duration_days": week_plan["duration_days"],
            "modules": week_plan["modules"],
            "total_problems": week_plan["total_problems"],
            "total_practice": week_plan["total_practice"],
            "target": week_plan["target"],
        }
    
    def generate_full_plan(self) -> Dict:
        """生成完整4周学习计划"""
        plan = {
            "skill_name": "AI绘画提示词工程师",
            "version": "v1.0",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_weeks": 4,
            "total_problems": 0,
            "total_practice": 0,
            "weeks": [],
        }
        
        for week_key in ["week1", "week2", "week3", "week4"]:
            week_plan = self.generate_week_plan(week_key)
            plan["weeks"].append(week_plan)
            plan["total_problems"] += week_plan["total_problems"]
            plan["total_practice"] += week_plan["total_practice"]
        
        return plan
    
    def generate_training_task(self, student_id: str, week: str, module_id: str) -> Dict:
        """生成训练任务"""
        week_plan = self.config.LEARNING_PATH.get(week)
        if not week_plan:
            return {"error": f"未找到{week}的学习计划"}
        
        module = None
        for m in week_plan["modules"]:
            if m["module_id"] == module_id:
                module = m
                break
        
        if not module:
            return {"error": f"未找到{module_id}的训练模块"}
        
        student = self.config.STUDENTS[student_id]
        
        task = {
            "id": f"ai-prompt-{week}-{module_id}-{int(datetime.now().timestamp())}",
            "type": "ai_prompt_training_task",
            "from": "hermes",
            "to": student_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "skill": "AI绘画提示词工程师",
            "week": week,
            "module": module,
            "student": student,
            "task": {
                "title": module["name"],
                "description": module["description"],
                "problem_count": module["problem_count"],
                "practice_count": module["practice_count"],
                "topics": module["topics"],
                "practice_tasks": module["practice_tasks"],
            },
            "submission_requirements": {
                "require_prompt_examples": True,
                "require_generated_images": True,
                "require_reflection": True,
            },
        }
        
        return task
    
    def generate_template_catalog(self) -> Dict:
        """生成提示词模板目录"""
        catalog = {
            "template_library": "AI绘画提示词模板库",
            "version": "v1.0",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "categories": {
                "basic": {
                    "name": "基础提示词",
                    "count": 50,
                    "price": "9.9元",
                    "templates": [
                        {"id": "basic_001", "name": "超写实人像", "prompt": "photorealistic portrait, professional photography, studio lighting, 85mm lens, shallow depth of field, --ar 4:5 --v 6 --style raw"},
                        {"id": "basic_002", "name": "电影感风景", "prompt": "cinematic landscape, golden hour, dramatic clouds, wide angle, rule of thirds, --ar 16:9 --v 6"},
                        {"id": "basic_003", "name": "商业产品图", "prompt": "product photography, clean background, studio lighting, professional, commercial, --ar 1:1 --v 6 --style raw"},
                    ],
                },
                "style": {
                    "name": "风格提示词",
                    "count": 100,
                    "price": "19.9元",
                    "templates": [
                        {"id": "style_001", "name": "日系插画", "prompt": "anime style illustration, vibrant colors, detailed, masterpiece, --ar 16:9 --v 6 --niji 6"},
                        {"id": "style_002", "name": "水彩画", "prompt": "watercolor painting, soft colors, artistic, flowing, --ar 3:4 --v 6"},
                        {"id": "style_003", "name": "3D渲染", "prompt": "3D render, octane render, blender, realistic lighting, --ar 16:9 --v 6"},
                    ],
                },
                "commercial": {
                    "name": "商业提示词",
                    "count": 200,
                    "price": "29.9元",
                    "templates": [
                        {"id": "comm_001", "name": "淘宝服装图", "prompt": "fashion photography, model wearing clothing, studio lighting, white background, commercial, --ar 3:4 --v 6 --style raw"},
                        {"id": "comm_002", "name": "小红书封面", "prompt": "instagram aesthetic, lifestyle photography, bright and airy, soft lighting, --ar 4:5 --v 6"},
                        {"id": "comm_003", "name": "AI头像定制", "prompt": "professional headshot, studio lighting, neutral background, high quality, --ar 1:1 --v 6 --style raw"},
                    ],
                },
            },
            "total_templates": 350,
            "total_value": "9.9+19.9+29.9=59.7元",
        }
        
        return catalog
    
    def generate_taobao_product_plan(self) -> Dict:
        """生成淘宝商品上架计划"""
        plan = {
            "product_plan": "AI绘画提示词淘宝商品计划",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "products": [
                {
                    "product_id": "ai_prompt_basic",
                    "name": "AI绘画基础提示词50套",
                    "description": "包含超写实/插画/3D/艺术等基础提示词模板，附使用教程",
                    "price": "9.9元",
                    "expected_monthly_sales": 500,
                    "expected_monthly_revenue": "4,950元",
                    "content": [
                        "50个基础提示词",
                        "使用教程PDF",
                        "示例图50张",
                    ],
                },
                {
                    "product_id": "ai_prompt_style",
                    "name": "AI绘画风格提示词100套",
                    "description": "包含10种主流风格提示词，覆盖写实/插画/3D/商业等",
                    "price": "19.9元",
                    "expected_monthly_sales": 300,
                    "expected_monthly_revenue": "5,970元",
                    "content": [
                        "100个风格提示词",
                        "风格对比指南",
                        "示例图100张",
                    ],
                },
                {
                    "product_id": "ai_prompt_commercial",
                    "name": "AI绘画商业提示词200套",
                    "description": "淘宝商品图/社交媒体/头像定制等商业级提示词",
                    "price": "29.9元",
                    "expected_monthly_sales": 200,
                    "expected_monthly_revenue": "5,980元",
                    "content": [
                        "200个商业提示词",
                        "商业应用指南",
                        "示例图200张",
                    ],
                },
                {
                    "product_id": "ai_prompt_full",
                    "name": "AI绘画全套提示词库500+套",
                    "description": "完整提示词库+教程+示例，一站式解决方案",
                    "price": "49.9元",
                    "expected_monthly_sales": 100,
                    "expected_monthly_revenue": "4,990元",
                    "content": [
                        "500+提示词",
                        "完整使用教程",
                        "示例图500+张",
                        "定期更新",
                    ],
                },
                {
                    "product_id": "ai_prompt_custom",
                    "name": "AI绘画提示词定制服务",
                    "description": "根据客户需求定制专属提示词",
                    "price": "99-199元",
                    "expected_monthly_sales": 50,
                    "expected_monthly_revenue": "7,450元",
                    "content": [
                        "专属提示词定制",
                        "多次修改",
                        "使用指导",
                    ],
                },
            ],
            "total_expected_monthly_revenue": "29,340元",
        }
        
        return plan


# ============================================================
# 命令行接口
# ============================================================

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI绘画提示词工程师学习技能")
    parser.add_argument("action", choices=["plan", "task", "catalog", "taobao"],
                       help="操作: plan(学习计划) | task(训练任务) | catalog(模板目录) | taobao(淘宝计划)")
    parser.add_argument("--student", type=str, help="学员ID")
    parser.add_argument("--week", type=str, help="周次（week1-week4）")
    parser.add_argument("--module", type=str, help="模块ID")
    
    args = parser.parse_args()
    engine = AIPromptLearningEngine()
    
    if args.action == "plan":
        plan = engine.generate_full_plan()
        print(json.dumps(plan, ensure_ascii=False, indent=2))
    
    elif args.action == "task":
        if args.student and args.week and args.module:
            task = engine.generate_training_task(args.student, args.week, args.module)
            print(json.dumps(task, ensure_ascii=False, indent=2))
        else:
            print("❌ 请提供 --student, --week, --module 参数")
    
    elif args.action == "catalog":
        catalog = engine.generate_template_catalog()
        print(json.dumps(catalog, ensure_ascii=False, indent=2))
    
    elif args.action == "taobao":
        plan = engine.generate_taobao_product_plan()
        print(json.dumps(plan, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
