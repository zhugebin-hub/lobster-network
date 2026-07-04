#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
少先队知识测试深度分析 - 结合题目内容
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json

# 题目内容（根据 docx 文件整理）
questions = {
    1: {"content": "少先队是（ ）创立和领导的", "answer": "D", "category": "少先队组织"},
    2: {"content": "队旗红旗象征（ ）", "answer": "C", "category": "少先队标志"},
    3: {"content": "少先队集会时由谁带领呼号", "answer": "C", "category": "少先队礼仪"},
    4: {"content": "队会中呼号的口号是", "answer": "C", "category": "少先队礼仪"},
    5: {"content": "10 月 13 日纪念什么", "answer": "B", "category": "少先队知识"},
    6: {"content": "小队一般由几人组成", "answer": "B", "category": "少先队组织"},
    7: {"content": "什么是少先队的生命", "answer": "B", "category": "少先队活动"},
    8: {"content": "不属于少先队作风的是", "answer": "B", "category": "少先队作风"},
    9: {"content": "加入少先队的年龄", "answer": "A", "category": "少先队知识"},
    10: {"content": "红领巾代表什么的一角", "answer": "A", "category": "少先队标志"},
    11: {"content": "维护国家荣誉是", "answer": "A", "category": "公民责任"},
    12: {"content": "社会主义核心价值观个人层面", "answer": "C", "category": "价值观"},
    13: {"content": "不是传统美德的是", "answer": "C", "category": "传统美德"},
    14: {"content": "属于社会公德表现的是", "answer": "B", "category": "社会公德"},
    15: {"content": "小组合作正确做法", "answer": "B", "category": "团队合作"},
    16: {"content": "看到乱涂乱画怎么做", "answer": "D", "category": "社会公德"},
    17: {"content": "答应同学的事情应该", "answer": "C", "category": "诚信"},
    18: {"content": "不属于传统节日的是", "answer": "B", "category": "传统文化"},
    19: {"content": "升国旗奏国歌时应该", "answer": "D", "category": "礼仪规范"},
    20: {"content": "班规制定正确说法", "answer": "B", "category": "民主参与"},
}

# 读取成绩数据
input_file = '/home/admin/.openclaw/media/inbound/262cd4ab-93a6-44e8-b1fc-5e5b3bd7131a.xlsx'
df = pd.read_excel(input_file)
df_clean = df[df['得分'] > 0].copy()

# 将"对/错"转换为 1/0
question_cols = [i for i in range(1, 21)]
for q in question_cols:
    df_clean[q] = df_clean[q].map({'对': 1, '错': 0})

# 按知识点分类统计
category_stats = {}
for q_num, q_info in questions.items():
    cat = q_info['category']
    if cat not in category_stats:
        category_stats[cat] = []
    category_stats[cat].append(q_num)

# 计算各知识点正确率
category_results = {}
for cat, q_nums in category_stats.items():
    cat_correct_rates = []
    for q in q_nums:
        correct_rate = (df_clean[q] == 1).sum() / len(df_clean) * 100
        cat_correct_rates.append(correct_rate)
    category_results[cat] = {
        '题目数': len(q_nums),
        '题号': q_nums,
        '平均正确率': round(np.mean(cat_correct_rates), 2),
        '各题正确率': [round((df_clean[q] == 1).sum() / len(df_clean) * 100, 2) for q in q_nums]
    }

# 生成深度分析报告
report = f"""# 少先队知识与道德素养测试 - 深度分析报告

**分析时间：** 2026 年 4 月 21 日  
**样本数量：** {len(df_clean)} 名学生（3 所学校）  
**测试内容：** 20 道选择题（少先队知识 + 道德素养）

---

## 一、知识点分类统计

### 1.1 各知识点掌握情况

| 知识点 | 题目数 | 题号 | 平均正确率 | 掌握程度 |
|--------|--------|------|-----------|----------|
"""

for cat, results in category_results.items():
    rate = results['平均正确率']
    if rate >= 90:
        level = "优秀 ✅"
    elif rate >= 70:
        level = "良好 ✓"
    elif rate >= 60:
        level = "合格 △"
    else:
        level = "待加强 ⚠️"
    report += f"| {cat} | {results['题目数']} | {results['题号']} | {rate}% | {level} |\n"

report += f"""
### 1.2 知识点正确率排序

"""

sorted_cats = sorted(category_results.items(), key=lambda x: x[1]['平均正确率'], reverse=True)
for i, (cat, results) in enumerate(sorted_cats, 1):
    report += f"**第{i}名：{cat}** - {results['平均正确率']}%（{results['题目数']}题）\n"

report += f"""
---

## 二、重点题目分析

### 2.1 正确率最低的 5 道题

| 排名 | 题号 | 知识点 | 题目内容 | 正确率 |
|------|------|--------|----------|--------|
"""

# 计算每题正确率
q_rates = []
for q in question_cols:
    rate = (df_clean[q] == 1).sum() / len(df_clean) * 100
    q_rates.append((q, rate, questions[q]['content'], questions[q]['category']))

lowest_5 = sorted(q_rates, key=lambda x: x[1])[:5]
for i, (q, rate, content, cat) in enumerate(lowest_5, 1):
    report += f"| {i} | 第{q}题 | {cat} | {content[:30]}... | {rate}% |\n"

report += f"""
### 2.2 正确率最高的 5 道题

| 排名 | 题号 | 知识点 | 题目内容 | 正确率 |
|------|------|--------|----------|--------|
"""

highest_5 = sorted(q_rates, key=lambda x: x[1], reverse=True)[:5]
for i, (q, rate, content, cat) in enumerate(highest_5, 1):
    report += f"| {i} | 第{q}题 | {cat} | {content[:30]}... | {rate}% |\n"

report += f"""
---

## 三、分学校知识点分析

"""

schools = df_clean['学校'].unique()

for school in schools:
    school_df = df_clean[df_clean['学校'] == school]
    report += f"### {school}（{len(school_df)}人）\n\n"
    report += "| 知识点 | 平均正确率 | 最薄弱题目 |\n"
    report += "|--------|-----------|------------|\n"
    
    for cat, q_nums in category_stats.items():
        cat_rates = [(df_clean[df_clean['学校']==school][q] == 1).sum() / len(school_df) * 100 for q in q_nums]
        avg_rate = np.mean(cat_rates)
        min_q = q_nums[np.argmin(cat_rates)]
        min_rate = min(cat_rates)
        report += f"| {cat} | {round(avg_rate, 1)}% | 第{min_q}题 ({round(min_rate, 1)}%) |\n"
    report += "\n"

report += f"""
---

## 四、教学建议

### 4.1 重点讲解内容（正确率<60%）

"""

weak_cats = [cat for cat, res in category_results.items() if res['平均正确率'] < 60]
if weak_cats:
    for cat in weak_cats:
        report += f"**{cat}**（{category_results[cat]['平均正确率']}%）\n"
        report += f"- 涉及题目：第{category_results[cat]['题号']}题\n"
        for q in category_results[cat]['题号']:
            report += f"  - 第{q}题：{questions[q]['content']}\n"
        report += "\n"
else:
    report += "所有知识点正确率均在 60% 以上，整体掌握良好。\n"

report += f"""
### 4.2 针对性教学策略

**少先队组织知识：**
- 开展"少先队知识知多少"主题班会
- 制作少先队知识卡片，学生随身携带记忆
- 组织高年级队员给低年级队员讲解队史

**礼仪规范：**
- 每周升旗仪式后进行礼仪点评
- 拍摄标准礼仪示范视频，班级循环播放
- 开展"礼仪小标兵"评选活动

**道德素养：**
- 结合生活实例进行情景教学
- 组织"我身边的好人好事"分享会
- 开展志愿服务活动，实践道德行为

**传统文化：**
- 传统节日前开展主题文化活动
- 邀请家长进课堂讲述传统故事
- 组织经典诵读比赛

---

## 五、附件

- 错题统计表.xlsx
- 图表数据模板.csv
- 教师分析报告.txt

---

**报告生成：** 小龙虾 AI 助手  
**生成时间：** 2026 年 4 月 21 日
"""

# 保存报告
output_dir = Path('/home/admin/.openclaw/workspace/stock-reports')
report_file = output_dir / '深度分析报告.md'
with open(report_file, 'w', encoding='utf-8') as f:
    f.write(report)

print(f"✓ 深度分析报告已保存：{report_file}")

# 保存题目对照表
qa_data = []
for q in question_cols:
    rate = (df_clean[q] == 1).sum() / len(df_clean) * 100
    qa_data.append({
        '题号': q,
        '题目内容': questions[q]['content'],
        '正确答案': questions[q]['answer'],
        '知识点': questions[q]['category'],
        '整体正确率': round(rate, 2)
    })

qa_df = pd.DataFrame(qa_data)
qa_file = output_dir / '题目对照表.xlsx'
qa_df.to_excel(qa_file, index=False)
print(f"✓ 题目对照表已保存：{qa_file}")

print("\n===== 深度分析完成 =====")
