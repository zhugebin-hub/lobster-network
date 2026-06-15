#!/usr/bin/env python3
"""
2025 学年第二学期 课表生成器
根据教师任课安排，自动生成班级课表和教师课表
"""

import zipfile
import xml.etree.ElementTree as ET
import json
from collections import defaultdict
import random

# 配置
DAYS = ['周一', '周二', '周三', '周四', '周五']
PERIODS = list(range(1, 9))  # 每天 8 节课
WEEKLY_PERIODS = len(DAYS) * len(PERIODS)  # 40 节课

# 学科配置
SUBJECTS = {
    '语文': {'periods': 5, 'priority': 'high', 'can_double': False, 'no_afternoon_last': True},
    '数学': {'periods': 5, 'priority': 'high', 'can_double': False, 'no_afternoon_last': True},
    '英语': {'periods': 5, 'priority': 'high', 'can_double': False, 'no_afternoon_last': True},
    '科学': {'periods': 5, 'priority': 'high', 'can_double': True, 'no_afternoon_last': True},
    '历史与社会': {'periods': 5, 'priority': 'high', 'can_double': True, 'no_afternoon_last': True},
    '体育': {'periods': 3, 'priority': 'medium', 'can_double': False, 'no_afternoon_last': False},
    '音乐': {'periods': 1, 'priority': 'low', 'can_double': False, 'no_afternoon_last': False},
    '美术': {'periods': 1, 'priority': 'low', 'can_double': False, 'no_afternoon_last': False},
    '劳动': {'periods': 1, 'priority': 'low', 'can_double': False, 'no_afternoon_last': False},
    '综合实践': {'periods': 1, 'priority': 'low', 'can_double': False, 'no_afternoon_last': False},
    '班队心理': {'periods': 1, 'priority': 'low', 'can_double': False, 'no_afternoon_last': False},
    '地方课程': {'periods': 1, 'priority': 'low', 'can_double': False, 'no_afternoon_last': False},
}

# 上午节次 (1-4 节) 和 下午非最后两节 (5-6 节)
MORNING_PERIODS = [1, 2, 3, 4]
AFTERNOON_EARLY_PERIODS = [5, 6]
AFTERNOON_LAST_PERIODS = [7, 8]  # 主科不排这些节次
PREFERRED_PERIODS = [1, 2, 3, 4, 5, 6, 7]  # 优先使用 1-7 节，第 8 节尽量不用
SKILL_SUBJECTS = ['体育', '音乐', '美术', '劳动', '综合实践', '班队心理', '地方课程']

# 列映射
COL_MAP = {
    'D': '语文', 'E': '数学', 'F': '英语', 'G': '科学',
    'H': '历史与社会', 'I': '体育', 'J': '音乐', 'K': '美术',
    'L': '劳动', 'M': '综合实践', 'N': '班队心理', 'O': '地方课程'
}

def parse_xlsx(filepath):
    """解析 xlsx 文件"""
    with zipfile.ZipFile(filepath, 'r') as z:
        strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            with z.open('xl/sharedStrings.xml') as f:
                tree = ET.parse(f)
                root = tree.getroot()
                ns = {'ss': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                for si in root.findall('.//ss:si', ns):
                    t = si.find('ss:t', ns)
                    if t is not None:
                        strings.append(t.text if t.text else '')
        
        sheets_data = {}
        for idx, sheet_name in enumerate(['sheet1', 'sheet2', 'sheet3']):
            sheet_path = f'xl/worksheets/{sheet_name}.xml'
            if sheet_path in z.namelist():
                with z.open(sheet_path) as f:
                    tree = ET.parse(f)
                    root = tree.getroot()
                    ns = {'ss': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                    
                    rows = []
                    for row in root.findall('.//ss:row', ns):
                        row_data = {}
                        for cell in row.findall('ss:c', ns):
                            cell_ref = cell.get('r', '')
                            cell_type = cell.get('t', 'n')
                            v = cell.find('ss:v', ns)
                            value = v.text if v is not None else ''
                            
                            if cell_type == 's' and value.isdigit():
                                value = strings[int(value)] if int(value) < len(strings) else value
                            
                            row_data[cell_ref] = value
                        if row_data:
                            rows.append(row_data)
                    
                    sheets_data[f'sheet{idx+1}'] = rows
        
        return sheets_data, strings

def extract_assignments(sheets_data):
    """提取任课安排"""
    grade_names = {'sheet1': '九年级', 'sheet2': '八年级', 'sheet3': '七年级'}
    assignments = {}  # {class_name: {subject: teacher}}
    teacher_load = defaultdict(list)  # {teacher: [(grade, class, subject)]}
    
    for sheet_key, grade_name in grade_names.items():
        if sheet_key not in sheets_data:
            continue
        
        rows = sheets_data[sheet_key]
        for i, row in enumerate(rows):
            if i < 3:
                continue
            
            class_name = row.get(f'A{i+1}', '')
            if not class_name or not class_name.isdigit():
                continue
            
            assignments[class_name] = {'grade': grade_name}
            
            for col, subject in COL_MAP.items():
                teacher = row.get(f'{col}{i+1}', '').strip()
                if teacher:
                    assignments[class_name][subject] = teacher
                    teacher_load[teacher].append((grade_name, class_name, subject))
    
    return assignments, teacher_load

def generate_schedule(assignments, teacher_load):
    """生成课表 - 优化版：主科每天 1 节 + 文化课连堂 + 技能课同年级连堂"""
    class_schedules = {}  # {class_name: {day: {period: subject}}}
    teacher_schedules = defaultdict(lambda: defaultdict(dict))  # {teacher: {day: {period: class}}}
    teacher_day_load = defaultdict(lambda: defaultdict(int))  # {teacher: {day: count}}
    
    classes = list(assignments.keys())
    CULTURE_SUBJECTS = ['语文', '数学', '英语', '科学', '历史与社会']
    SKILL_SUBJECTS_LIST = ['体育', '音乐', '美术', '劳动', '综合实践', '班队心理', '地方课程']
    
    # 按年级分组班级
    grade_classes = defaultdict(list)
    for class_name in classes:
        grade = assignments[class_name].get('grade', '')
        grade_classes[grade].append(class_name)
    
    # 先安排所有班级的文化课
    for class_name in classes:
        class_schedule = {day: {} for day in DAYS}
        class_assignments = assignments[class_name]
        grade = class_assignments.get('grade', '')
        
        # 安排文化课 - 每天 1 节，尽量连堂
        for subject, config in SUBJECTS.items():
            if subject not in CULTURE_SUBJECTS:
                continue
            
            teacher = class_assignments.get(subject, '')
            if not teacher:
                continue
            
            periods_needed = config['periods']  # 5 节
            scheduled = 0
            attempts = 0
            max_attempts = 200
            
            # 主科必须每天 1 节（周一至周五各 1 节）
            days_to_schedule = DAYS.copy()  # 必须覆盖所有 5 天
            random.shuffle(days_to_schedule)  # 打乱顺序增加随机性
            
            for day in days_to_schedule:
                if scheduled >= periods_needed:
                    break
                
                attempts = 0
                while attempts < 50:
                    attempts += 1
                    
                    # 寻找可用的节次（1-6 节，避免 7-8 节）
                    available_periods = []
                    for period in range(1, 7):
                        if period in class_schedule[day]:
                            continue
                        if period in teacher_schedules[teacher][day]:
                            continue
                        available_periods.append(period)
                    
                    if not available_periods:
                        continue
                    
                    # 优先选择能连堂的节次
                    teacher_periods = [p for p in teacher_schedules[teacher][day].keys()]
                    best_period = None
                    
                    for period in available_periods:
                        if (period - 1) in teacher_periods or (period + 1) in teacher_periods:
                            best_period = period
                            break
                    
                    if best_period is None:
                        best_period = random.choice(available_periods)
                    
                    period = best_period
                    
                    class_schedule[day][period] = {
                        'subject': subject,
                        'teacher': teacher
                    }
                    teacher_schedules[teacher][day][period] = class_name
                    teacher_day_load[teacher][day] += 1
                    scheduled += 1
                    break
        
        class_schedules[class_name] = class_schedule
    
    # 按年级批量安排技能课（促进同年级连堂）
    for grade, grade_cls in grade_classes.items():
        # 收集该年级所有技能课老师
        skill_teachers = defaultdict(list)  # {teacher: [(class_name, subject, periods_needed)]}
        
        for class_name in grade_cls:
            class_assignments = assignments[class_name]
            for subject in SKILL_SUBJECTS_LIST:
                teacher = class_assignments.get(subject, '')
                if teacher:
                    periods = SUBJECTS.get(subject, {}).get('periods', 1)
                    skill_teachers[teacher].append((class_name, subject, periods))
        
        # 为每个技能课老师安排课程（同年级尽量连堂）
        for teacher, class_subjects in skill_teachers.items():
            # 按科目分组
            subject_classes = defaultdict(list)
            for class_name, subject, periods in class_subjects:
                subject_classes[subject].append((class_name, periods))
            
            # 为每个科目安排课程
            for subject, classes_periods in subject_classes.items():
                # 班会课（班队心理）固定在周五第 7 节
                if subject == '班队心理':
                    for class_name, periods_needed in classes_periods:
                        class_schedule = class_schedules[class_name]
                        day = '周五'
                        period = 7
                        
                        # 检查周五第 7 节是否可用
                        if period not in class_schedule[day] and period not in teacher_schedules[teacher][day]:
                            class_schedule[day][period] = {
                                'subject': subject,
                                'teacher': teacher
                            }
                            teacher_schedules[teacher][day][period] = class_name
                            teacher_day_load[teacher][day] += 1
                        else:
                            # 如果不可用，尝试其他天第 7 节
                            for attempt_day in ['周四', '周三', '周二', '周一']:
                                if period not in class_schedule[attempt_day] and period not in teacher_schedules[teacher][attempt_day]:
                                    class_schedule[attempt_day][period] = {
                                        'subject': subject,
                                        'teacher': teacher
                                    }
                                    teacher_schedules[teacher][attempt_day][period] = class_name
                                    teacher_day_load[teacher][attempt_day] += 1
                                    break
                else:
                    # 其他技能课正常安排
                    # 尝试在同一天安排同年级的多个班级
                    day = random.choice(DAYS)
                    
                    for class_name, periods_needed in classes_periods:
                        class_schedule = class_schedules[class_name]
                        scheduled = 0
                        attempts = 0
                        max_attempts = 100
                        
                        while scheduled < periods_needed and attempts < max_attempts:
                            attempts += 1
                            
                            # 优先选择老师已有该年级课的天
                            weighted_days = [day] * 3 + DAYS  # 权重偏向已选天
                            
                            attempt_day = random.choice(weighted_days)
                            
                            # 寻找可用节次（优先 3-7 节，第 8 节尽量不用）
                            available_periods = []
                            # 先找 3-7 节
                            for period in range(3, 8):
                                if period in class_schedule[attempt_day]:
                                    continue
                                if period in teacher_schedules[teacher][attempt_day]:
                                    continue
                                available_periods.append(period)
                            
                            # 如果 3-7 节没有空位，才考虑第 8 节
                            if not available_periods:
                                for period in range(8, 9):
                                    if period in class_schedule[attempt_day]:
                                        continue
                                    if period in teacher_schedules[teacher][attempt_day]:
                                        continue
                                    available_periods.append(period)
                            
                            if not available_periods:
                                continue
                            
                            # 优先选择能连堂的节次
                            teacher_periods = [p for p in teacher_schedules[teacher][attempt_day].keys()]
                            best_period = None
                            
                            for period in available_periods:
                                if (period - 1) in teacher_periods or (period + 1) in teacher_periods:
                                    best_period = period
                                    break
                            
                            if best_period is None:
                                best_period = random.choice(available_periods)
                            
                            period = best_period
                            
                            class_schedule[attempt_day][period] = {
                                'subject': subject,
                                'teacher': teacher
                            }
                            teacher_schedules[teacher][attempt_day][period] = class_name
                            teacher_day_load[teacher][attempt_day] += 1
                            scheduled += 1
    
    return class_schedules, teacher_schedules

def export_class_schedule(class_schedules, assignments, output_file):
    """导出班级课表"""
    lines = []
    lines.append("=" * 120)
    lines.append("2025 学年第二学期 班级课表")
    lines.append("=" * 120)
    
    for class_name in sorted(class_schedules.keys()):
        schedule = class_schedules[class_name]
        grade = assignments[class_name].get('grade', '')
        
        lines.append(f"\n【{grade} {class_name}班】")
        lines.append("-" * 80)
        
        # 表头
        header = f"{'节次':<8}"
        for day in DAYS:
            header += f"{day:<16}"
        lines.append(header)
        lines.append("-" * 80)
        
        # 每节课
        for period in PERIODS:
            row = f"第{period}节".ljust(8)
            for day in DAYS:
                if period in schedule[day]:
                    info = schedule[day][period]
                    cell = f"{info['subject']}({info['teacher']})"
                else:
                    cell = "-"
                row += cell.ljust(16)
            lines.append(row)
        
        lines.append("-" * 80)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"班级课表已导出：{output_file}")

def export_teacher_schedule(teacher_schedules, output_file):
    """导出教师课表"""
    lines = []
    lines.append("=" * 120)
    lines.append("2025 学年第二学期 教师任课课表")
    lines.append("=" * 120)
    
    for teacher in sorted(teacher_schedules.keys()):
        schedule = teacher_schedules[teacher]
        
        lines.append(f"\n【教师：{teacher}】")
        lines.append("-" * 80)
        
        # 表头
        header = f"{'节次':<8}"
        for day in DAYS:
            header += f"{day:<16}"
        lines.append(header)
        lines.append("-" * 80)
        
        # 每节课
        has_class = False
        for period in PERIODS:
            row = f"第{period}节".ljust(8)
            for day in DAYS:
                if period in schedule[day]:
                    class_name = schedule[day][period]
                    cell = f"{class_name}班"
                    has_class = True
                else:
                    cell = "-"
                row += cell.ljust(16)
            lines.append(row)
        
        if not has_class:
            lines.append("(无任课安排)")
        
        lines.append("-" * 80)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"教师课表已导出：{output_file}")

def main():
    print("开始解析任课表...")
    filepath = '/home/admin/.openclaw/media/inbound/61567064-d9e7-4034-aafd-86a2a4067022.xlsx'
    
    sheets_data, strings = parse_xlsx(filepath)
    print(f"解析完成，共 {len(strings)} 个字符串")
    
    print("提取任课安排...")
    assignments, teacher_load = extract_assignments(sheets_data)
    print(f"共 {len(assignments)} 个班级，{len(teacher_load)} 位教师")
    
    print("生成课表...")
    random.seed(42)  # 固定随机种子，保证结果可复现
    class_schedules, teacher_schedules = generate_schedule(assignments, teacher_load)
    
    print("导出课表...")
    export_class_schedule(class_schedules, assignments, '/home/admin/.openclaw/workspace/schedule/class_schedules.txt')
    export_teacher_schedule(teacher_schedules, '/home/admin/.openclaw/workspace/schedule/teacher_schedules.txt')
    
    print("\n✅ 课表生成完成！")

if __name__ == '__main__':
    main()
