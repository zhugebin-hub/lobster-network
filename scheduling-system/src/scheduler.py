"""
排课算法模块
使用约束满足问题 (CSP) 算法
"""
from typing import Dict, List, Set, Tuple, Optional
from utils.db import Database


class Scheduler:
    """排课器"""
    
    def __init__(self, db: Database):
        self.db = db
        self.time_slots = []  # 可用时间槽 [(day, period), ...]
        self.meetings = set()  # 会议时间 {(day, period), ...}
        self.schedules = []  # 排课结果
        
    def run(self) -> dict:
        """
        执行排课
        返回：{"success": bool, "count": int, "error": str}
        """
        try:
            # 1. 初始化
            self._init_time_slots()
            self._load_meetings()
            
            # 2. 获取所有课程
            courses = self._load_courses()
            if not courses:
                return {"success": False, "error": "没有可排的课程"}
            
            # 3. 执行排课算法
            self.schedules = []
            success = self._schedule_courses(courses)
            
            if not success:
                return {"success": False, "error": "无法完成排课，存在冲突"}
            
            # 4. 保存结果
            self._save_schedules()
            
            return {
                "success": True,
                "count": len(self.schedules)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _init_time_slots(self):
        """初始化时间槽（5 天 × 8 节 = 40 个时间槽）"""
        self.time_slots = []
        for day in range(1, 6):  # 周一至周五
            for period in range(1, 9):  # 8 节课
                self.time_slots.append((day, period))
    
    def _load_meetings(self):
        """加载会议时间（这些时间不能排课）"""
        self.meetings = set()
        rows = self.db.fetch_all("SELECT day_of_week, period FROM meetings WHERE recurring = 1")
        for row in rows:
            self.meetings.add((row["day_of_week"], row["period"]))
    
    def _load_courses(self) -> List[dict]:
        """加载所有课程"""
        rows = self.db.fetch_all("""
            SELECT c.id, c.class_id, c.teacher_id, c.subject, 
                   c.weekly_hours, c.consecutive, c.requirements,
                   cl.name as class_name, t.name as teacher_name
            FROM courses c
            JOIN classes cl ON c.class_id = cl.id
            JOIN teachers t ON c.teacher_id = t.id
            ORDER BY c.weekly_hours DESC  -- 周课时多的优先排
        """)
        return [dict(row) for row in rows]
    
    def _schedule_courses(self, courses: List[dict]) -> bool:
        """
        排课主算法
        使用贪心算法 + 回溯
        """
        # 记录已占用的时间槽
        # key: (class_id, day, period) -> 班级时间占用
        # key: (teacher_id, day, period) -> 教师时间占用
        class_occupied: Set[Tuple[int, int, int]] = set()
        teacher_occupied: Set[Tuple[int, int, int]] = set()
        
        for course in courses:
            success = self._schedule_single_course(
                course, class_occupied, teacher_occupied
            )
            if not success:
                return False
        
        return True
    
    def _schedule_single_course(
        self, 
        course: dict, 
        class_occupied: Set[Tuple[int, int, int]],
        teacher_occupied: Set[Tuple[int, int, int]]
    ) -> bool:
        """
        排单门课程
        """
        class_id = course["class_id"]
        teacher_id = course["teacher_id"]
        weekly_hours = course["weekly_hours"]
        consecutive = course["consecutive"]
        requirements = course.get("requirements", "")
        
        scheduled_count = 0
        attempts = []  # 记录尝试过的位置
        
        while scheduled_count < weekly_hours:
            # 寻找可用时间槽
            slot = self._find_available_slot(
                class_id, teacher_id, consecutive,
                class_occupied, teacher_occupied,
                requirements, attempts
            )
            
            if slot is None:
                # 无法找到合适位置，回溯
                return False
            
            day, period = slot
            
            # 占用时间槽
            for p in range(period, period + consecutive):
                class_occupied.add((class_id, day, p))
                teacher_occupied.add((teacher_id, day, p))
                self.schedules.append({
                    "class_id": class_id,
                    "teacher_id": teacher_id,
                    "course_id": course["id"],
                    "day_of_week": day,
                    "period": p,
                    "room": ""
                })
            
            scheduled_count += consecutive
            attempts.append(slot)
        
        return True
    
    def _find_available_slot(
        self,
        class_id: int,
        teacher_id: int,
        consecutive: int,
        class_occupied: Set[Tuple[int, int, int]],
        teacher_occupied: Set[Tuple[int, int, int]],
        requirements: str,
        attempts: List[Tuple[int, int]]
    ) -> Optional[Tuple[int, int]]:
        """
        查找可用时间槽
        返回：(day, period) 或 None
        """
        for day in range(1, 6):
            for period in range(1, 9 - consecutive + 1):
                slot = (day, period)
                
                # 检查是否已尝试过
                if slot in attempts:
                    continue
                
                # 检查是否是会议时间
                if slot in self.meetings:
                    continue
                
                # 检查连堂时间是否都可用
                all_available = True
                for p in range(period, period + consecutive):
                    check_slot = (day, p)
                    
                    # 检查会议
                    if check_slot in self.meetings:
                        all_available = False
                        break
                    
                    # 检查班级冲突
                    if (class_id, day, p) in class_occupied:
                        all_available = False
                        break
                    
                    # 检查教师冲突
                    if (teacher_id, day, p) in teacher_occupied:
                        all_available = False
                        break
                
                if all_available:
                    # 检查特殊要求
                    if self._check_requirements(slot, requirements):
                        return slot
        
        return None
    
    def _check_requirements(self, slot: Tuple[int, int], requirements: str) -> bool:
        """
        检查特殊要求
        例如："不排周一第一节"
        """
        if not requirements:
            return True
        
        day, period = slot
        days = ["", "周一", "周二", "周三", "周四", "周五"]
        day_name = days[day]
        
        # 解析要求（简单实现）
        if "不排" in requirements:
            if day_name in requirements and f"第{period}节" in requirements:
                return False
        
        return True
    
    def _save_schedules(self):
        """保存排课结果到数据库"""
        # 先清空旧数据
        self.db.execute("DELETE FROM schedules")
        
        # 插入新数据
        for schedule in self.schedules:
            self.db.insert("schedules", schedule)
        
        self.db.commit()
