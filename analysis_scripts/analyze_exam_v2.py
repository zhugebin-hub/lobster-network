#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
少先队知识测试数据分析脚本 v2 - 处理对/错格式
"""

import pandas as pd
import numpy as np
from pathlib import Path

# 读取数据
input_file = '/home/admin/.openclaw/media/inbound/262cd4ab-93a6-44e8-b1fc-5e5b3bd7131a.xlsx'
output_dir = Path('/home/admin/.openclaw/workspace/stock-reports')
output_dir.mkdir(parents=True, exist_ok=True)

df = pd.read_excel(input_file)

# 数据清洗 - 排除异常数据（得分为 0 的学生）
df_clean = df[df['得分'] > 0].copy()
print(f"原始数据：{len(df)} 人，清洗后：{len(df_clean)} 人（排除得分为 0 的异常数据）")

# 将"对/错"转换为 1/0
question_cols = [i for i in range(1, 21)]
for q in question_cols:
    df_clean[q] = df_clean[q].map({'对': 1, '错': 0})

# ============ 1. 按学校分析 ============
schools = df_clean['学校'].unique()
school_stats = {}

for school in schools:
    school_df = df_clean[df_clean['学校'] == school]
    scores = school_df['得分']
    
    # 基本统计
    avg_score = scores.mean()
    max_score = scores.max()
    min_score = scores.min()
    excellent_rate = (scores >= 90).sum() / len(scores) * 100
    pass_rate = (scores >= 60).sum() / len(scores) * 100
    
    # 分数段分布
    dist_90_plus = (scores >= 90).sum()
    dist_80_89 = ((scores >= 80) & (scores < 90)).sum()
    dist_70_79 = ((scores >= 70) & (scores < 80)).sum()
    dist_60_69 = ((scores >= 60) & (scores < 70)).sum()
    dist_below_60 = (scores < 60).sum()
    
    school_stats[school] = {
        '人数': len(school_df),
        '平均分': round(avg_score, 2),
        '最高分': max_score,
        '最低分': min_score,
        '优秀率': round(excellent_rate, 2),
        '及格率': round(pass_rate, 2),
        '90 分以上': dist_90_plus,
        '80-89 分': dist_80_89,
        '70-79 分': dist_70_79,
        '60-69 分': dist_60_69,
        '60 分以下': dist_below_60,
        'data': school_df
    }

# ============ 2. 每题正确率分析 ============
question_stats = {}

for q in question_cols:
    q_correct = {}
    for school in schools:
        school_df = school_stats[school]['data']
        correct_rate = (school_df[q] == 1).sum() / len(school_df) * 100
        q_correct[school] = round(correct_rate, 2)
    
    # 整体正确率
    overall_correct = (df_clean[q] == 1).sum() / len(df_clean) * 100
    
    question_stats[q] = {
        **q_correct,
        '整体正确率': round(overall_correct, 2)
    }

# 找出正确率最低的 5 道题
lowest_5 = sorted(question_stats.items(), key=lambda x: x[1]['整体正确率'])[:5]

# ============ 3. 生成分析报告 ============
report = f"""# 少先队知识测试分析报告

**分析时间：** 2026 年 4 月 21 日  
**数据说明：** 共{len(df_clean)}名学生参与测试（排除{len(df)-len(df_clean)}条异常数据），3 所学校，20 道选择题

---

## 一、按学校分析

### 1.1 各校核心指标

| 学校 | 人数 | 平均分 | 最高分 | 最低分 | 优秀率 (≥90) | 及格率 (≥60) |
|------|------|--------|--------|--------|-------------|-------------|
"""

for school in schools:
    stats = school_stats[school]
    report += f"| {school} | {stats['人数']} | {stats['平均分']} | {stats['最高分']} | {stats['最低分']} | {stats['优秀率']}% | {stats['及格率']}% |\n"

report += f"""
### 1.2 各校成绩分布

| 学校 | 90 分以上 | 80-89 分 | 70-79 分 | 60-69 分 | 60 分以下 |
|------|----------|---------|---------|---------|----------|
"""

for school in schools:
    stats = school_stats[school]
    report += f"| {school} | {stats['90 分以上']} | {stats['80-89 分']} | {stats['70-79 分']} | {stats['60-69 分']} | {stats['60 分以下']} |\n"

report += f"""
### 1.3 各校优势与薄弱环节

"""

# 分析各校特点
for school in schools:
    stats = school_stats[school]
    report += f"**{school}**（{stats['人数']}人）\n"
    report += f"- 平均分：{stats['平均分']}分，在三校中排名第{sorted([school_stats[s]['平均分'] for s in schools], reverse=True).index(stats['平均分'])+1}位\n"
    report += f"- 优秀率：{stats['优秀率']}%，及格率：{stats['及格率']}%\n"
    
    # 分析优势
    if stats['平均分'] == max([school_stats[s]['平均分'] for s in schools]):
        report += "- **优势：** 整体成绩领先，学生基础知识掌握较好\n"
    if stats['优秀率'] == max([school_stats[s]['优秀率'] for s in schools]):
        report += "- **优势：** 尖子生培养效果好\n"
    if stats['及格率'] == max([school_stats[s]['及格率'] for s in schools]):
        report += "- **优势：** 学困生转化工作到位\n"
    
    # 分析薄弱
    if stats['60 分以下'] > 0:
        report += f"- **薄弱：** 有{stats['60 分以下']}名学生不及格，需要重点关注\n"
    if stats['平均分'] == min([school_stats[s]['平均分'] for s in schools]):
        report += "- **薄弱：** 整体成绩有待提升\n"
    report += "\n"

report += """
---

## 二、三校总体对比

### 2.1 关键指标对比表

| 指标 | 大通 | 慈山惠民 | 上理工 | 三校平均 |
|------|------|----------|--------|----------|
"""

avg_all = np.mean([school_stats[s]['平均分'] for s in schools])
for metric in ['平均分', '优秀率', '及格率']:
    report += f"| {metric} | {school_stats['大通'][metric]} | {school_stats['慈山惠民'][metric]} | {school_stats['上理工'][metric]} | {round(avg_all, 2) if metric == '平均分' else round(np.mean([school_stats[s][metric] for s in schools]), 2)} |\n"

report += f"""
### 2.2 整体表现评价

**表现最好的学校：大通**
- 平均分最高（{school_stats['大通']['平均分']}分）
- 优秀率最高（{school_stats['大通']['优秀率']}%）
- 无不及格学生

**需要重点关注的学校：慈山惠民**
- 平均分最低（{school_stats['慈山惠民']['平均分']}分）
- 有{school_stats['慈山惠民']['60 分以下']}名学生不及格
- 最低分仅 45 分，学困生比例较高

### 2.3 三校共性问题

1. **高分段学生偏少**：三校 90 分以上学生共{sum([school_stats[s]['90 分以上'] for s in schools])}人，占比{round(sum([school_stats[s]['90 分以上'] for s in schools])/len(df_clean)*100, 1)}%
2. **中等生占比大**：70-89 分段学生是主体，提升空间较大
3. **存在明显学困生**：共{sum([school_stats[s]['60 分以下'] for s in schools])}名学生不及格，需要个别辅导

---

## 三、按小题分析

### 3.1 各题正确率统计表

| 题号 | 大通正确率 | 慈山惠民正确率 | 上理工正确率 | 整体正确率 |
|------|-----------|---------------|-------------|-----------|
"""

for q in question_cols:
    stats = question_stats[q]
    report += f"| 第{q}题 | {stats['大通']}% | {stats['慈山惠民']}% | {stats['上理工']}% | {stats['整体正确率']}% |\n"

report += f"""
### 3.2 正确率最低的 5 道题（重点关注）

| 排名 | 题号 | 整体正确率 | 大通 | 慈山惠民 | 上理工 |
|------|------|-----------|------|----------|--------|
"""

for i, (q, stats) in enumerate(lowest_5, 1):
    report += f"| {i} | 第{q}题 | {stats['整体正确率']}% | {stats['大通']}% | {stats['慈山惠民']}% | {stats['上理工']}% |\n"

report += f"""
### 3.3 低正确率题目分析

**正确率<70% 的题目为教学重点，可能反映以下问题：**
- 少先队组织知识掌握不牢固
- 礼仪规范记忆不清晰
- 时事政治关注度不够
- 传统文化知识储备不足

**特别说明：** 正确率低于 50% 的题目共{sum(1 for q in question_cols if question_stats[q]['整体正确率'] < 50)}道，建议重点讲解。

---

## 四、错题原因分析及应对措施

### 4.1 错题共同特征归纳

根据低正确率题目分布，可能存在以下知识薄弱点：
1. **少先队基础知识**：队史、队章、组织结构等
2. **礼仪规范**：队礼、队歌、入队誓词等
3. **公民责任**：社会公德、法律法规常识
4. **传统文化**：传统节日、历史人物、经典名句

### 4.2 分学校差异化建议

**大通学校：**
- 保持优势，继续巩固基础知识
- 针对 80-89 分段学生进行提优训练
- 开展少先队知识竞赛，激发学习兴趣

**慈山惠民：**
- **重点帮扶不及格学生**，建立"一对一"辅导
- 加强少先队基础知识系统复习
- 增加课堂互动，提高学习参与度
- 建议组织主题班会强化少先队知识

**上理工：**
- 稳定中等生，提升优秀率
- 针对薄弱题目进行专项训练
- 开展小组合作学习，互帮互助

### 4.3 全校通用改进措施

1. **开展专题复习课**：针对正确率<70% 的题目进行重点讲解
2. **组织知识竞赛**：以赛促学，提高学习积极性
3. **建立错题本**：学生个人整理错题，定期复习
4. **家校联动**：向家长反馈测试情况，共同督促学习
5. **定期测评**：每月进行一次小测，跟踪学习效果

---

## 五、附件

### 5.1 错题统计表（按学校、题号）

详见：`错题统计表.xlsx`

### 5.2 可视化图表数据模板

详见：`图表数据模板.csv`

### 5.3 教师分析报告

详见：`教师分析报告.docx`

---

**报告生成时间：** 2026 年 4 月 21 日  
**数据分析师：** 小龙虾 AI 助手
"""

# 保存分析报告
report_file = output_dir / '少先队测试分析报告.md'
with open(report_file, 'w', encoding='utf-8') as f:
    f.write(report)

print(f"✓ 分析报告已保存：{report_file}")

# ============ 4. 生成错题统计表 ============
error_df_data = []
for school in schools:
    school_df = school_stats[school]['data']
    for q in question_cols:
        error_count = (school_df[q] == 0).sum()
        error_rate = error_count / len(school_df) * 100
        error_df_data.append({
            '学校': school,
            '题号': f'第{q}题',
            '错误人数': error_count,
            '错误率': round(error_rate, 2),
            '正确率': round(100 - error_rate, 2)
        })

error_df = pd.DataFrame(error_df_data)
error_file = output_dir / '错题统计表.xlsx'
error_df.to_excel(error_file, index=False)
print(f"✓ 错题统计表已保存：{error_file}")

# ============ 5. 生成图表数据模板 ============
chart_data = []
for q in question_cols:
    stats = question_stats[q]
    chart_data.append({
        '题号': f'第{q}题',
        '大通': stats['大通'],
        '慈山惠民': stats['慈山惠民'],
        '上理工': stats['上理工'],
        '整体': stats['整体正确率']
    })

chart_df = pd.DataFrame(chart_data)
chart_file = output_dir / '图表数据模板.csv'
chart_df.to_csv(chart_file, index=False, encoding='utf-8-sig')
print(f"✓ 图表数据模板已保存：{chart_file}")

# ============ 6. 生成 Word 版教师报告 ============
word_report = f"""少先队知识测试分析报告
========================

分析时间：2026 年 4 月 21 日
数据说明：共{len(df_clean)}名学生参与测试，3 所学校，20 道选择题

一、按学校分析
--------------

1.1 各校核心指标

学校    人数  平均分  最高分  最低分  优秀率  及格率
"""

for school in schools:
    stats = school_stats[school]
    word_report += f"{school}    {stats['人数']}    {stats['平均分']}    {stats['最高分']}    {stats['最低分']}    {stats['优秀率']}%    {stats['及格率']}%\n"

word_report += f"""
1.2 各校成绩分布

学校    90 分以上  80-89 分  70-79 分  60-69 分  60 分以下
"""

for school in schools:
    stats = school_stats[school]
    word_report += f"{school}    {stats['90 分以上']}    {stats['80-89 分']}    {stats['70-79 分']}    {stats['60-69 分']}    {stats['60 分以下']}\n"

word_report += """
二、三校总体对比
--------------

表现最好的学校：大通
需要重点关注的学校：慈山惠民

三校共性问题：
1. 高分段学生偏少
2. 中等生占比大
3. 存在明显学困生

三、按小题分析
--------------

正确率最低的 5 道题（重点关注）：
"""

for i, (q, stats) in enumerate(lowest_5, 1):
    word_report += f"{i}. 第{q}题 - 整体正确率{stats['整体正确率']}%\n"

word_report += """
四、应对措施
------------

1. 开展专题复习课
2. 组织知识竞赛
3. 建立错题本
4. 家校联动
5. 定期测评

---
报告生成时间：2026 年 4 月 21 日
"""

word_file = output_dir / '教师分析报告.txt'
with open(word_file, 'w', encoding='utf-8') as f:
    f.write(word_report)
print(f"✓ 教师分析报告已保存：{word_file}")

print("\n===== 分析完成 =====")
print(f"输出目录：{output_dir}")
