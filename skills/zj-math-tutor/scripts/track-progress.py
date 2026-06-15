#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
浙江初中数学学习助手 - 学习进度跟踪脚本
功能：记录学生学习进度、知识掌握度、错题本
"""

import json
import os
from datetime import datetime
from pathlib import Path

# 配置文件路径
WORKSPACE = Path.home() / ".openclaw" / "workspace"
PROGRESS_FILE = WORKSPACE / "learning-progress.md"

def load_progress():
    """加载学习进度数据"""
    if not PROGRESS_FILE.exists():
        return {
            "student_name": "",
            "grade": "",
            "start_date": "",
            "chapters": [],
            "weak_points": [],
            "error_book": [],
            "statistics": {
                "total_hours": 0,
                "total_problems": 0,
                "correct_rate": 0
            }
        }
    
    # 简单解析 Markdown 文件（实际使用可更完善）
    data = {
        "student_name": "",
        "grade": "",
        "start_date": "",
        "chapters": [],
        "weak_points": [],
        "error_book": [],
        "statistics": {
            "total_hours": 0,
            "total_problems": 0,
            "correct_rate": 0
        }
    }
    
    with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
        # 简单解析逻辑，可根据需要完善
        if "**学生姓名：**" in content:
            data["student_name"] = content.split("**学生姓名：**")[1].split("\n")[0].strip()
        if "**年级：**" in content:
            data["grade"] = content.split("**年级：**")[1].split("\n")[0].strip()
    
    return data

def save_progress(data):
    """保存学习进度为 Markdown 格式"""
    markdown = f"""# 学习档案

**学生姓名：** {data.get('student_name', '')}
**年级：** {data.get('grade', '')}
**开始日期：** {data.get('start_date', datetime.now().strftime('%Y-%m-%d'))}
**最后更新：** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 已学章节
"""
    
    for chapter in data.get('chapters', []):
        status = "✓" if chapter.get('status') == 'mastered' else "○"
        proficiency = chapter.get('proficiency', 3)
        stars = "★" * proficiency + "☆" * (5 - proficiency)
        markdown += f"- [{status}] {chapter.get('name', '')}（掌握度：{stars}）\n"
    
    markdown += "\n## 薄弱知识点\n"
    for point in data.get('weak_points', []):
        markdown += f"- {point}\n"
    
    markdown += "\n## 错题本\n| 日期 | 题目 | 错误原因 | 知识点 |\n|------|------|----------|--------|\n"
    for error in data.get('error_book', [])[-10:]:  # 最近 10 道错题
        markdown += f"| {error.get('date', '')} | {error.get('problem', '')[:20]}... | {error.get('reason', '')} | {error.get('topic', '')} |\n"
    
    stats = data.get('statistics', {})
    markdown += f"""
## 学习统计
- 总学习时长：{stats.get('total_hours', 0)} 小时
- 完成题目：{stats.get('total_problems', 0)} 道
- 正确率：{stats.get('correct_rate', 0)}%
"""
    
    # 确保目录存在
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    print(f"✓ 学习进度已保存到：{PROGRESS_FILE}")

def add_chapter(student_name, chapter_name, status='learning', proficiency=3):
    """添加或更新章节学习记录"""
    data = load_progress()
    
    if not data.get('student_name'):
        data['student_name'] = student_name
        data['start_date'] = datetime.now().strftime('%Y-%m-%d')
    
    # 查找是否已存在该章节
    chapters = data.get('chapters', [])
    found = False
    for chapter in chapters:
        if chapter.get('name') == chapter_name:
            chapter['status'] = status
            chapter['proficiency'] = proficiency
            found = True
            break
    
    if not found:
        chapters.append({
            'name': chapter_name,
            'status': status,
            'proficiency': proficiency,
            'learned_date': datetime.now().strftime('%Y-%m-%d')
        })
        data['chapters'] = chapters
    
    save_progress(data)
    print(f"✓ 已记录章节：{chapter_name}（状态：{status}，掌握度：{proficiency}/5）")

def add_error_record(student_name, problem, reason, topic):
    """添加错题记录"""
    data = load_progress()
    
    if not data.get('student_name'):
        data['student_name'] = student_name
    
    error_book = data.get('error_book', [])
    error_book.append({
        'date': datetime.now().strftime('%Y-%m-%d'),
        'problem': problem,
        'reason': reason,
        'topic': topic
    })
    data['error_book'] = error_book[-50:]  # 保留最近 50 道错题
    
    save_progress(data)
    print(f"✓ 已记录错题：{problem[:30]}...（原因：{reason}）")

def update_statistics(student_name, hours=0, problems=0, correct=0):
    """更新学习统计"""
    data = load_progress()
    
    if not data.get('student_name'):
        data['student_name'] = student_name
    
    stats = data.get('statistics', {})
    stats['total_hours'] = stats.get('total_hours', 0) + hours
    stats['total_problems'] = stats.get('total_problems', 0) + problems
    
    # 计算正确率
    if problems > 0:
        total_correct = stats.get('total_problems', 0) * stats.get('correct_rate', 0) / 100 + correct
        stats['correct_rate'] = round(total_correct / stats['total_problems'] * 100, 1) if stats['total_problems'] > 0 else 0
    
    data['statistics'] = stats
    save_progress(data)
    print(f"✓ 学习统计已更新：总时长{stats['total_hours']}h，题目{stats['total_problems']}道，正确率{stats['correct_rate']}%")

def generate_report(student_name=None):
    """生成学习报告"""
    data = load_progress()
    
    if student_name and data.get('student_name') != student_name:
        print(f"未找到学生 {student_name} 的学习记录")
        return
    
    print("\n" + "="*50)
    print(f"📊 {data.get('student_name', '未知')} 的学习报告")
    print("="*50)
    print(f"年级：{data.get('grade', '未设置')}")
    print(f"开始日期：{data.get('start_date', '未设置')}")
    
    print(f"\n📚 已学章节：{len(data.get('chapters', []))}个")
    mastered = sum(1 for c in data.get('chapters', []) if c.get('status') == 'mastered')
    print(f"   已掌握：{mastered}个")
    
    print(f"\n⚠️  薄弱知识点：{len(data.get('weak_points', []))}个")
    for point in data.get('weak_points', [])[:5]:
        print(f"   - {point}")
    
    print(f"\n📝 错题本：{len(data.get('error_book', []))}道")
    
    stats = data.get('statistics', {})
    print(f"\n📈 学习统计:")
    print(f"   总学习时长：{stats.get('total_hours', 0)} 小时")
    print(f"   完成题目：{stats.get('total_problems', 0)} 道")
    print(f"   正确率：{stats.get('correct_rate', 0)}%")
    print("="*50 + "\n")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='浙江初中数学学习助手 - 学习进度跟踪')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # add-chapter 命令
    chapter_parser = subparsers.add_parser('add-chapter', help='添加章节学习记录')
    chapter_parser.add_argument('--student', required=True, help='学生姓名')
    chapter_parser.add_argument('--chapter', required=True, help='章节名称')
    chapter_parser.add_argument('--status', default='learning', choices=['learning', 'mastered'], help='学习状态')
    chapter_parser.add_argument('--proficiency', type=int, default=3, choices=[1,2,3,4,5], help='掌握度 (1-5)')
    
    # add-error 命令
    error_parser = subparsers.add_parser('add-error', help='添加错题记录')
    error_parser.add_argument('--student', required=True, help='学生姓名')
    error_parser.add_argument('--problem', required=True, help='题目内容')
    error_parser.add_argument('--reason', required=True, help='错误原因')
    error_parser.add_argument('--topic', required=True, help='知识点')
    
    # update-stats 命令
    stats_parser = subparsers.add_parser('update-stats', help='更新学习统计')
    stats_parser.add_argument('--student', required=True, help='学生姓名')
    stats_parser.add_argument('--hours', type=float, default=0, help='学习时长 (小时)')
    stats_parser.add_argument('--problems', type=int, default=0, help='完成题目数')
    stats_parser.add_argument('--correct', type=int, default=0, help='正确题目数')
    
    # report 命令
    report_parser = subparsers.add_parser('report', help='生成学习报告')
    report_parser.add_argument('--student', help='学生姓名')
    
    args = parser.parse_args()
    
    if args.command == 'add-chapter':
        add_chapter(args.student, args.chapter, args.status, args.proficiency)
    elif args.command == 'add-error':
        add_error_record(args.student, args.problem, args.reason, args.topic)
    elif args.command == 'update-stats':
        update_statistics(args.student, args.hours, args.problems, args.correct)
    elif args.command == 'report':
        generate_report(args.student)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
