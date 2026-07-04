#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Titanic Dataset Analysis Report Generator
生成泰坦尼克号数据集分析报告
"""

import csv
import os
from collections import defaultdict
from datetime import datetime

# 配置
DATA_DIR = "/home/admin/.openclaw/workspace/dataset_project"
OUTPUT_DIR = "/home/admin/.openclaw/workspace/dataset_project"

def load_titanic_data(filepath):
    """加载泰坦尼克号数据集"""
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data

def analyze_data(data):
    """分析数据并生成统计信息"""
    stats = {
        'total': len(data),
        'survived': 0,
        'died': 0,
        'male': 0,
        'female': 0,
        'male_survived': 0,
        'female_survived': 0,
        'class_counts': defaultdict(int),
        'class_survived': defaultdict(int),
        'ages': [],
        'embarked': defaultdict(int)
    }
    
    for row in data:
        # 生存统计
        survived = row.get('Survived', '')
        if survived == '1':
            stats['survived'] += 1
        else:
            stats['died'] += 1
        
        # 性别统计
        sex = row.get('Sex', '')
        if sex == 'male':
            stats['male'] += 1
            if survived == '1':
                stats['male_survived'] += 1
        elif sex == 'female':
            stats['female'] += 1
            if survived == '1':
                stats['female_survived'] += 1
        
        # 舱位统计
        pclass = row.get('Pclass', 'Unknown')
        stats['class_counts'][pclass] += 1
        if survived == '1':
            stats['class_survived'][pclass] += 1
        
        # 年龄统计
        age = row.get('Age', '')
        if age:
            try:
                stats['ages'].append(float(age))
            except:
                pass
        
        # 登船港口统计
        embarked = row.get('Embarked', 'Unknown')
        stats['embarked'][embarked] += 1
    
    return stats

def create_simple_bar_chart(stats, output_path):
    """创建简单的 ASCII 条形图（用于文档）"""
    lines = []
    lines.append("生存率统计:")
    lines.append("-" * 50)
    
    total = stats['total']
    survived = stats['survived']
    died = stats['died']
    
    survived_pct = (survived / total * 100) if total > 0 else 0
    died_pct = (died / total * 100) if total > 0 else 0
    
    survived_bar = "█" * int(survived_pct / 2.5)
    died_bar = "█" * int(died_pct / 2.5)
    
    lines.append(f"生存者：{survived_bar} {survived} ({survived_pct:.1f}%)")
    lines.append(f"遇难者：{died_bar} {died} ({died_pct:.1f}%)")
    lines.append("")
    
    # 性别生存率
    lines.append("性别生存率:")
    lines.append("-" * 50)
    if stats['male'] > 0:
        male_rate = stats['male_survived'] / stats['male'] * 100
        male_bar = "█" * int(male_rate / 2.5)
        lines.append(f"男性：{male_bar} {stats['male_survived']}/{stats['male']} ({male_rate:.1f}%)")
    if stats['female'] > 0:
        female_rate = stats['female_survived'] / stats['female'] * 100
        female_bar = "█" * int(female_rate / 2.5)
        lines.append(f"女性：{female_bar} {stats['female_survived']}/{stats['female']} ({female_rate:.1f}%)")
    
    return "\n".join(lines)

def generate_word_report(stats, chart_text, output_path):
    """生成简单的 Word 文档（使用 XML 格式）"""
    
    # 创建简单的 Word 文档（Office Open XML 格式）
    doc_content = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<?mso-application progid="Word.Document"?>
<w:wordDocument xmlns:w="http://schemas.microsoft.com/office/word/2003/wordml">
<w:body>
<w:p>
<w:r><w:rPr><w:b/><w:sz w:val="48"/></w:rPr><w:t>泰坦尼克号数据集分析报告</w:t></w:r>
</w:p>
<w:p><w:r><w:t></w:t></w:r></w:p>
<w:p>
<w:r><w:rPr><w:b/><w:sz w:val="32"/></w:rPr><w:t>一、数据集简介</w:t></w:r>
</w:p>
<w:p>
<w:r><w:t>泰坦尼克号数据集是数据科学领域最经典的数据集之一，记录了 1912 年泰坦尼克号沉船事故中乘客的详细信息和生存情况。该数据集常用于机器学习入门教学，特别是分类问题的学习。</w:t></w:r>
</w:p>
<w:p><w:r><w:t></w:t></w:r></w:p>
<w:p>
<w:r><w:rPr><w:b/><w:sz w:val="32"/></w:rPr><w:t>二、数据集特点</w:t></w:r>
</w:p>
<w:p>
<w:r><w:t>• 数据量：{stats['total']} 条乘客记录</w:t></w:r>
</w:p>
<w:p>
<w:r><w:t>• 主要字段：乘客 ID、姓名、性别、年龄、舱位等级、票价、登船港口等</w:t></w:r>
</w:p>
<w:p>
<w:r><w:t>• 目标变量：Survived（是否生存，1=生存，0=遇难）</w:t></w:r>
</w:p>
<w:p>
<w:r><w:t>• 数据来源：Kaggle Titanic Competition</w:t></w:r>
</w:p>
<w:p><w:r><w:t></w:t></w:r></w:p>
<w:p>
<w:r><w:rPr><w:b/><w:sz w:val="32"/></w:rPr><w:t>三、应用场景</w:t></w:r>
</w:p>
<w:p>
<w:r><w:t>1. 机器学习分类算法教学（逻辑回归、决策树、随机森林等）</w:t></w:r>
</w:p>
<w:p>
<w:r><w:t>2. 特征工程实践（处理缺失值、编码分类变量等）</w:t></w:r>
</w:p>
<w:p>
<w:r><w:t>3. 数据可视化分析</w:t></w:r>
</w:p>
<w:p>
<w:r><w:t>4. 探索性数据分析（EDA）案例</w:t></w:r>
</w:p>
<w:p><w:r><w:t></w:t></w:r></w:p>
<w:p>
<w:r><w:rPr><w:b/><w:sz w:val="32"/></w:rPr><w:t>四、数据分析结果</w:t></w:r>
</w:p>
<w:p><w:r><w:t></w:t></w:r></w:p>
<w:p>
<w:r><w:rPr><w:b/></w:rPr><w:t>1. 总体生存统计</w:t></w:r>
</w:p>
<w:p>
<w:r><w:t>总乘客数：{stats['total']} 人</w:t></w:r>
</w:p>
<w:p>
<w:r><w:t>生存人数：{stats['survived']} 人 ({stats['survived']/stats['total']*100:.1f}%)</w:t></w:r>
</w:p>
<w:p>
<w:r><w:t>遇难人数：{stats['died']} 人 ({stats['died']/stats['total']*100:.1f}%)</w:t></w:r>
</w:p>
<w:p><w:r><w:t></w:t></w:r></w:p>
<w:p>
<w:r><w:rPr><w:b/></w:rPr><w:t>2. 性别与生存率</w:t></w:r>
</w:p>
<w:p>
<w:r><w:t>男性乘客：{stats['male']} 人，生存 {stats['male_survived']} 人</w:t></w:r>
</w:p>
<w:p>
<w:r><w:t>女性乘客：{stats['female']} 人，生存 {stats['female_survived']} 人</w:t></w:r>
</w:p>
'''
    
    if stats['male'] > 0:
        male_rate = stats['male_survived'] / stats['male'] * 100
        doc_content += f'<w:p><w:r><w:t>男性生存率：{male_rate:.1f}%</w:t></w:r></w:p>'
    if stats['female'] > 0:
        female_rate = stats['female_survived'] / stats['female'] * 100
        doc_content += f'<w:p><w:r><w:t>女性生存率：{female_rate:.1f}%</w:t></w:r></w:p>'
    
    doc_content += f'''
<w:p><w:r><w:t></w:t></w:r></w:p>
<w:p>
<w:r><w:rPr><w:b/></w:rPr><w:t>3. 舱位等级分布</w:t></w:r>
</w:p>
'''
    
    for pclass in sorted(stats['class_counts'].keys()):
        count = stats['class_counts'][pclass]
        survived = stats['class_survived'].get(pclass, 0)
        rate = (survived / count * 100) if count > 0 else 0
        doc_content += f'<w:p><w:r><w:t>{pclass}等舱：{count} 人，生存 {survived} 人 ({rate:.1f}%)</w:t></w:r></w:p>'
    
    # 年龄统计
    if stats['ages']:
        avg_age = sum(stats['ages']) / len(stats['ages'])
        min_age = min(stats['ages'])
        max_age = max(stats['ages'])
        doc_content += f'''
<w:p><w:r><w:t></w:t></w:r></w:p>
<w:p>
<w:r><w:rPr><w:b/></w:rPr><w:t>4. 年龄统计</w:t></w:r>
</w:p>
<w:p>
<w:r><w:t>平均年龄：{avg_age:.1f} 岁</w:t></w:r>
</w:p>
<w:p>
<w:r><w:t>最小年龄：{min_age:.1f} 岁</w:t></w:r>
</w:p>
<w:p>
<w:r><w:t>最大年龄：{max_age:.1f} 岁</w:t></w:r>
</w:p>
'''
    
    doc_content += f'''
<w:p><w:r><w:t></w:t></w:r></w:p>
<w:p>
<w:r><w:rPr><w:b/><w:sz w:val="32"/></w:rPr><w:t>五、数据可视化</w:t></w:r>
</w:p>
<w:p><w:r><w:t></w:t></w:r></w:p>
<w:p>
<w:r><w:rPr><w:b/></w:rPr><w:t>生存率条形图:</w:t></w:r>
</w:p>
<w:p>
<w:r><w:t>{chart_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")}</w:t></w:r>
</w:p>
<w:p><w:r><w:t></w:t></w:r></w:p>
<w:p>
<w:r><w:rPr><w:b/><w:sz w:val="32"/></w:rPr><w:t>六、结论</w:t></w:r>
</w:p>
<w:p>
<w:r><w:t>通过分析泰坦尼克号数据集，我们发现：</w:t></w:r>
</w:p>
<w:p>
<w:r><w:t>1. 女性生存率显著高于男性，体现了"女士优先"的救援原则</w:t></w:r>
</w:p>
<w:p>
<w:r><w:t>2. 高等舱位乘客生存率更高，反映了社会阶层对救援优先级的影响</w:t></w:r>
</w:p>
<w:p>
<w:r><w:t>3. 该数据集是学习数据科学和机器学习的优秀入门材料</w:t></w:r>
</w:p>
<w:p><w:r><w:t></w:t></w:r></w:p>
<w:p>
<w:r><w:t>报告生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</w:t></w:r>
</w:p>
</w:body>
</w:wordDocument>
'''
    
    # 保存为 .doc 文件（Word 2003 XML 格式，兼容性好）
    output_file = os.path.join(output_path, "泰坦尼克号数据集分析报告.doc")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(doc_content)
    
    return output_file

def main():
    print("正在加载泰坦尼克号数据集...")
    data_path = os.path.join(DATA_DIR, "train.csv")
    
    if not os.path.exists(data_path):
        print(f"错误：找不到数据文件 {data_path}")
        return
    
    data = load_titanic_data(data_path)
    print(f"成功加载 {len(data)} 条记录")
    
    print("正在分析数据...")
    stats = analyze_data(data)
    
    print("正在生成图表...")
    chart_text = create_simple_bar_chart(stats, None)
    
    print("正在生成 Word 报告...")
    output_file = generate_word_report(stats, chart_text, OUTPUT_DIR)
    
    print(f"\n✓ 报告已生成：{output_file}")
    print(f"✓ 数据文件：{data_path}")
    
    # 打印统计摘要
    print("\n=== 数据统计摘要 ===")
    print(f"总乘客数：{stats['total']}")
    print(f"生存：{stats['survived']} ({stats['survived']/stats['total']*100:.1f}%)")
    print(f"遇难：{stats['died']} ({stats['died']/stats['total']*100:.1f}%)")
    print(f"男性：{stats['male']}, 女性：{stats['female']}")

if __name__ == "__main__":
    main()
