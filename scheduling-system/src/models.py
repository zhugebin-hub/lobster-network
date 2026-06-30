"""
数据模型定义
"""
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class Teacher:
    """教师信息"""
    id: int
    name: str
    subject: str  # 任教学科
    max_weekly_hours: int = 16  # 最大周课时
    email: str = ""
    phone: str = ""
    notes: str = ""


@dataclass
class ClassGrade:
    """班级信息"""
    id: int
    name: str  # 如：高一 (1) 班
    grade: str  # 年级：高一/高二/高三
    student_count: int = 45
    homeroom_teacher_id: Optional[int] = None


@dataclass
class Course:
    """课程设置"""
    id: int
    class_id: int  # 所属班级
    teacher_id: int  # 任课教师
    subject: str  # 科目
    weekly_hours: int = 2  # 周课时
    consecutive: int = 1  # 连堂数（1=单节，2=连堂）
    requirements: str = ""  # 特殊要求（如：不排周一第一节）


@dataclass
class Meeting:
    """会议/活动时间（该时段不排课）"""
    id: int
    name: str
    day_of_week: int  # 1-5 (周一至周五)
    period: int  # 节次 (1-8)
    recurring: bool = True  # 是否每周重复


@dataclass
class Schedule:
    """课表记录"""
    id: int
    class_id: int
    teacher_id: int
    course_id: int
    day_of_week: int  # 1-5
    period: int  # 1-8
    room: str = ""  # 教室


@dataclass
class TimeSlot:
    """时间槽（用于排课算法）"""
    day: int  # 1-5
    period: int  # 1-8
    
    def __str__(self):
        days = ["", "周一", "周二", "周三", "周四", "周五"]
        return f"{days[self.day]} 第{self.period}节"
