#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钉钉聊天记录导出 - 案例文档生成脚本

功能：
1. 从对话记录生成案例文档
2. 自动识别主题模块
3. 生成教学分析建议
4. 输出 Markdown 格式文档
"""

import os
import json
from datetime import datetime
from pathlib import Path

def generate_case_document(conversation_history, modules_analysis, output_path):
    """
    生成案例文档
    
    参数：
    - conversation_history: 对话历史（列表）
    - modules_analysis: 模块分析（字典）
    - output_path: 输出路径
    """
    
    # 读取模板
    template_path = Path(__file__).parent.parent / 'templates' / 'case_template.md'
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # 提取基本信息
    case_info = extract_case_info(conversation_history)
    
    # 生成模块内容
    modules_content = generate_modules_content(conversation_history, modules_analysis)
    
    # 生成技巧提炼
    tips_content = generate_tips_content(conversation_history)
    
    # 生成产出物清单
    outputs_content = generate_outputs_content(conversation_history)
    
    # 填充模板
    document = template.replace('[案例名称]', case_info['case_name'])
    document = document.replace('[副标题]', case_info['subtitle'])
    document = document.replace('DH-LLM-YYYY-NNN', case_info['case_number'])
    document = document.replace('YYYY 年 MM 月 DD 日', case_info['date'])
    document = document.replace('[约 X 小时]', case_info['duration'])
    
    # 替换模块内容
    document = document.replace('[重复以上模块结构，直到所有模块完成]', modules_content)
    
    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(document)
    
    print(f"✅ 案例文档生成完成：{output_path}")
    return output_path


def extract_case_info(conversation_history):
    """
    提取案例基本信息
    """
    
    first_msg = conversation_history[0]
    last_msg = conversation_history[-1]
    
    # 计算时长
    start_time = datetime.fromisoformat(first_msg['timestamp'])
    end_time = datetime.fromisoformat(last_msg['timestamp'])
    duration = end_time - start_time
    duration_str = f"约 {int(duration.total_seconds() / 60)} 分钟"
    
    return {
        'case_number': f"DH-LLM-2026-{get_case_number()}",
        'case_name': '人机协作设计数字人文课程',
        'subtitle': '浙江工商大学通识课教学设计实录',
        'date': start_time.strftime('%Y 年 %m 月 %d 日'),
        'duration': duration_str
    }


def get_case_number():
    """
    获取下一个案例编号
    """
    cases_dir = Path(__file__).parent.parent.parent.parent / 'teaching_cases'
    
    if not cases_dir.exists():
        return '001'
    
    existing_cases = list(cases_dir.glob('*_*'))
    next_num = len(existing_cases) + 1
    return f'{next_num:03d}'


def generate_modules_content(conversation_history, modules_analysis):
    """
    生成模块内容
    """
    
    modules_content = ""
    
    for module_id, module_info in modules_analysis.items():
        module_content = f"""
### 模块{module_id}: {module_info['title']}

**时间**: {module_info.get('time', 'N/A')}

**主题**: {module_info['theme']}

**对话内容**:

---

{module_info['dialog']}

---

**📌 教学分析**:

| 维度 | 分析 |
|------|------|
| **AI 能力展示** | {module_info.get('ai_capability', 'N/A')} |
| **提问技巧** | {module_info.get('questioning_skill', 'N/A')} |
| **输出质量** | {module_info.get('output_quality', 'N/A')} |
| **教学价值** | {module_info.get('teaching_value', 'N/A')} |

**💡 关键技巧**:
{format_list(module_info.get('tips', []))}

**⚠️ 验证点**:
{format_list(module_info.get('verification', []))}

---
"""
        modules_content += module_content
    
    return modules_content


def generate_tips_content(conversation_history):
    """
    生成技巧提炼内容
    """
    
    # TODO: 实现自动分析
    return """
| 技巧 | 示例 | 效果 |
|------|------|------|
| **情境铺垫** | 先分享照片，再要求写诗 | AI 理解更准确 |
| **概念纠正** | "小龙虾就是你自己" | 建立有效比喻 |
| **逐步细化** | 6 轮迭代完善方案 | 产出更精准 |
"""


def generate_outputs_content(conversation_history):
    """
    生成产出物清单
    """
    
    # TODO: 实现自动分析
    return """
| 产出物 | 说明 | 文件 |
|--------|------|------|
| 11 周教学方案 | 完整课程设计 | digital_humanities_11weeks.docx |
| 第 5 周材料包 | 7 个教学文件 | week5_package_word.zip |
| 教学案例文档 | 本案例 | 01_案例文档.docx |
"""


def format_list(items):
    """
    格式化列表为 Markdown
    """
    if not items:
        return "- [待补充]"
    
    return '\n'.join([f"- {item}" for item in items])


if __name__ == "__main__":
    # 示例用法
    print("案例文档生成脚本 - 示例")
    print("请在实际使用时传入对话历史和模块分析")
