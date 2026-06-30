"""
对话框和数据管理界面
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional


# ==================== 教师管理 ====================

class TeacherManager(ttk.Frame):
    """教师管理界面"""
    
    def __init__(self, parent, db, update_status: Callable):
        super().__init__(parent)
        self.db = db
        self.update_status = update_status
        self.pack(fill=tk.BOTH, expand=True)
        self._create_ui()
        self._load_data()
    
    def _create_ui(self):
        """创建界面"""
        # 工具栏
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, pady=5)
        
        ttk.Button(toolbar, text="➕ 添加", command=self.add_teacher).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="✏️ 编辑", command=self.edit_teacher).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🗑️ 删除", command=self.delete_teacher).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🔄 刷新", command=self._load_data).pack(side=tk.LEFT, padx=2)
        
        # 表格
        columns = ("id", "name", "subject", "max_hours", "phone", "notes")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="姓名")
        self.tree.heading("subject", text="学科")
        self.tree.heading("max_hours", text="周课时上限")
        self.tree.heading("phone", text="电话")
        self.tree.heading("notes", text="备注")
        
        self.tree.column("id", width=50)
        self.tree.column("name", width=100)
        self.tree.column("subject", width=80)
        self.tree.column("max_hours", width=80)
        self.tree.column("phone", width=120)
        self.tree.column("notes", width=200)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _load_data(self):
        """加载数据"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        rows = self.db.fetch_all("SELECT * FROM teachers ORDER BY id")
        for row in rows:
            self.tree.insert("", tk.END, values=(
                row["id"], row["name"], row["subject"],
                row["max_weekly_hours"], row["phone"], row["notes"]
            ))
        self.update_status(f"已加载 {len(rows)} 条教师记录")
    
    def add_teacher(self):
        """添加教师"""
        dialog = TeacherDialog(self, None)
        if dialog.result:
            self.db.insert("teachers", dialog.result)
            self._load_data()
    
    def edit_teacher(self):
        """编辑教师"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择一条记录")
            return
        
        item = self.tree.item(selected[0])
        values = item["values"]
        
        # 获取完整数据
        row = self.db.fetch_one("SELECT * FROM teachers WHERE id = ?", (values[0],))
        dialog = TeacherDialog(self, dict(row))
        if dialog.result:
            self.db.update("teachers", dialog.result, "id = ?", (values[0],))
            self._load_data()
    
    def delete_teacher(self):
        """删除教师"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择一条记录")
            return
        
        if messagebox.askyesno("确认", "确定删除该教师？"):
            item = self.tree.item(selected[0])
            self.db.delete("teachers", "id = ?", (item["values"][0],))
            self._load_data()


# ==================== 班级管理 ====================

class ClassManager(ttk.Frame):
    """班级管理界面"""
    
    def __init__(self, parent, db, update_status: Callable):
        super().__init__(parent)
        self.db = db
        self.update_status = update_status
        self.pack(fill=tk.BOTH, expand=True)
        self._create_ui()
        self._load_data()
    
    def _create_ui(self):
        """创建界面"""
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, pady=5)
        
        ttk.Button(toolbar, text="➕ 添加", command=self.add_class).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="✏️ 编辑", command=self.edit_class).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🗑️ 删除", command=self.delete_class).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🔄 刷新", command=self._load_data).pack(side=tk.LEFT, padx=2)
        
        columns = ("id", "name", "grade", "student_count", "homeroom_teacher")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="班级名称")
        self.tree.heading("grade", text="年级")
        self.tree.heading("student_count", text="学生数")
        self.tree.heading("homeroom_teacher", text="班主任")
        
        self.tree.column("id", width=50)
        self.tree.column("name", width=150)
        self.tree.column("grade", width=100)
        self.tree.column("student_count", width=80)
        self.tree.column("homeroom_teacher", width=150)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
    
    def _load_data(self):
        """加载数据"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        rows = self.db.fetch_all("""
            SELECT c.id, c.name, c.grade, c.student_count, t.name as teacher_name
            FROM classes c
            LEFT JOIN teachers t ON c.homeroom_teacher_id = t.id
            ORDER BY c.grade, c.name
        """)
        for row in rows:
            self.tree.insert("", tk.END, values=(
                row["id"], row["name"], row["grade"],
                row["student_count"], row["teacher_name"] or "-"
            ))
        self.update_status(f"已加载 {len(rows)} 条班级记录")
    
    def add_class(self):
        """添加班级"""
        dialog = ClassDialog(self, None)
        if dialog.result:
            self.db.insert("classes", dialog.result)
            self._load_data()
    
    def edit_class(self):
        """编辑班级"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择一条记录")
            return
        
        item = self.tree.item(selected[0])
        row = self.db.fetch_one("SELECT * FROM classes WHERE id = ?", (item["values"][0],))
        dialog = ClassDialog(self, dict(row))
        if dialog.result:
            self.db.update("classes", dialog.result, "id = ?", (item["values"][0],))
            self._load_data()
    
    def delete_class(self):
        """删除班级"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择一条记录")
            return
        
        if messagebox.askyesno("确认", "确定删除该班级？"):
            item = self.tree.item(selected[0])
            self.db.delete("classes", "id = ?", (item["values"][0],))
            self._load_data()


# ==================== 课程管理 ====================

class CourseManager(ttk.Frame):
    """课程设置界面"""
    
    def __init__(self, parent, db, update_status: Callable):
        super().__init__(parent)
        self.db = db
        self.update_status = update_status
        self.pack(fill=tk.BOTH, expand=True)
        self._create_ui()
        self._load_data()
    
    def _create_ui(self):
        """创建界面"""
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, pady=5)
        
        ttk.Button(toolbar, text="➕ 添加", command=self.add_course).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="✏️ 编辑", command=self.edit_course).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🗑️ 删除", command=self.delete_course).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🔄 刷新", command=self._load_data).pack(side=tk.LEFT, padx=2)
        
        columns = ("id", "class_name", "teacher_name", "subject", "weekly_hours", "consecutive", "requirements")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("class_name", text="班级")
        self.tree.heading("teacher_name", text="教师")
        self.tree.heading("subject", text="科目")
        self.tree.heading("weekly_hours", text="周课时")
        self.tree.heading("consecutive", text="连堂")
        self.tree.heading("requirements", text="特殊要求")
        
        self.tree.column("id", width=50)
        self.tree.column("class_name", width=120)
        self.tree.column("teacher_name", width=100)
        self.tree.column("subject", width=80)
        self.tree.column("weekly_hours", width=60)
        self.tree.column("consecutive", width=60)
        self.tree.column("requirements", width=200)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
    
    def _load_data(self):
        """加载数据"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        rows = self.db.fetch_all("""
            SELECT c.id, cl.name as class_name, t.name as teacher_name, 
                   c.subject, c.weekly_hours, c.consecutive, c.requirements
            FROM courses c
            JOIN classes cl ON c.class_id = cl.id
            JOIN teachers t ON c.teacher_id = t.id
            ORDER BY cl.name, c.subject
        """)
        for row in rows:
            self.tree.insert("", tk.END, values=(
                row["id"], row["class_name"], row["teacher_name"],
                row["subject"], row["weekly_hours"], row["consecutive"],
                row["requirements"] or "-"
            ))
        self.update_status(f"已加载 {len(rows)} 条课程记录")
    
    def add_course(self):
        """添加课程"""
        dialog = CourseDialog(self, None, self.db)
        if dialog.result:
            self.db.insert("courses", dialog.result)
            self._load_data()
    
    def edit_course(self):
        """编辑课程"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择一条记录")
            return
        
        item = self.tree.item(selected[0])
        row = self.db.fetch_one("SELECT * FROM courses WHERE id = ?", (item["values"][0],))
        dialog = CourseDialog(self, dict(row), self.db)
        if dialog.result:
            self.db.update("courses", dialog.result, "id = ?", (item["values"][0],))
            self._load_data()
    
    def delete_course(self):
        """删除课程"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择一条记录")
            return
        
        if messagebox.askyesno("确认", "确定删除该课程？"):
            item = self.tree.item(selected[0])
            self.db.delete("courses", "id = ?", (item["values"][0],))
            self._load_data()


# ==================== 会议时间管理 ====================

class MeetingManager(ttk.Frame):
    """会议时间管理界面"""
    
    def __init__(self, parent, db, update_status: Callable):
        super().__init__(parent)
        self.db = db
        self.update_status = update_status
        self.pack(fill=tk.BOTH, expand=True)
        self._create_ui()
        self._load_data()
    
    def _create_ui(self):
        """创建界面"""
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, pady=5)
        
        ttk.Button(toolbar, text="➕ 添加", command=self.add_meeting).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🗑️ 删除", command=self.delete_meeting).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🔄 刷新", command=self._load_data).pack(side=tk.LEFT, padx=2)
        
        columns = ("id", "name", "day", "period", "recurring")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="会议名称")
        self.tree.heading("day", text="星期")
        self.tree.heading("period", text="节次")
        self.tree.heading("recurring", text="每周重复")
        
        self.tree.column("id", width=50)
        self.tree.column("name", width=200)
        self.tree.column("day", width=80)
        self.tree.column("period", width=60)
        self.tree.column("recurring", width=80)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
    
    def _load_data(self):
        """加载数据"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        days = ["", "周一", "周二", "周三", "周四", "周五"]
        rows = self.db.fetch_all("SELECT * FROM meetings ORDER BY day_of_week, period")
        for row in rows:
            self.tree.insert("", tk.END, values=(
                row["id"], row["name"], days[row["day_of_week"]],
                row["period"], "是" if row["recurring"] else "否"
            ))
        self.update_status(f"已加载 {len(rows)} 条会议记录")
    
    def add_meeting(self):
        """添加会议"""
        dialog = MeetingDialog(self, None)
        if dialog.result:
            self.db.insert("meetings", dialog.result)
            self._load_data()
    
    def delete_meeting(self):
        """删除会议"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择一条记录")
            return
        
        if messagebox.askyesno("确认", "确定删除该会议时间？"):
            item = self.tree.item(selected[0])
            self.db.delete("meetings", "id = ?", (item["values"][0],))
            self._load_data()


# ==================== 课表查看 ====================

class ScheduleViewer(ttk.Frame):
    """课表查看界面"""
    
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.pack(fill=tk.BOTH, expand=True)
        self._create_ui()
    
    def _create_ui(self):
        """创建界面"""
        # 选择班级
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, pady=5)
        
        ttk.Label(toolbar, text="选择班级:").pack(side=tk.LEFT, padx=5)
        
        self.class_var = tk.StringVar()
        classes = self.db.fetch_all("SELECT id, name FROM classes ORDER BY name")
        self.class_combo = ttk.Combobox(toolbar, textvariable=self.class_var, width=30)
        self.class_combo["values"] = [f"{c['id']}-{c['name']}" for c in classes]
        self.class_combo.pack(side=tk.LEFT, padx=5)
        self.class_combo.bind("<<ComboboxSelected>>", self.load_schedule)
        
        ttk.Button(toolbar, text="🔄 刷新", command=self.load_schedule).pack(side=tk.LEFT, padx=5)
        
        # 课表框架
        self.schedule_frame = ttk.Frame(self)
        self.schedule_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    def load_schedule(self, event=None):
        """加载课表"""
        for widget in self.schedule_frame.winfo_children():
            widget.destroy()
        
        if not self.class_var.get():
            return
        
        class_id = int(self.class_var.get().split("-")[0])
        
        # 创建课表网格
        periods = ["节次", "1", "2", "3", "4", "5", "6", "7", "8"]
        days = ["班级", "周一", "周二", "周三", "周四", "周五"]
        
        # 表头
        for i, day in enumerate(days):
            label = ttk.Label(self.schedule_frame, text=day, relief=tk.RIDGE, padding=10)
            label.grid(row=0, column=i, sticky="nsew")
        
        # 节次行
        for i, period in enumerate(periods):
            label = ttk.Label(self.schedule_frame, text=period, relief=tk.RIDGE, padding=5)
            label.grid(row=i+1, column=0, sticky="nsew")
        
        # 填充课表
        rows = self.db.fetch_all("""
            SELECT day_of_week, period, subject, teacher_name
            FROM schedules s
            JOIN teachers t ON s.teacher_id = t.id
            WHERE s.class_id = ?
            ORDER BY day_of_week, period
        """, (class_id,))
        
        # 创建字典便于查找
        schedule_dict = {}
        for row in rows:
            key = (row["day_of_week"], row["period"])
            schedule_dict[key] = f"{row['subject']}\n({row['teacher_name']})"
        
        # 填充单元格
        for day in range(1, 6):
            for period in range(1, 9):
                content = schedule_dict.get((day, period), "")
                label = ttk.Label(
                    self.schedule_frame, 
                    text=content, 
                    relief=tk.SOLID, 
                    padding=10,
                    background="#f0f0f0" if not content else "#e6f3ff"
                )
                label.grid(row=period+1, column=day, sticky="nsew")
        
        # 设置行列权重
        for i in range(6):
            self.schedule_frame.grid_columnconfigure(i, weight=1)
        for i in range(9):
            self.schedule_frame.grid_rowconfigure(i+1, weight=1)


# ==================== 对话框类 ====================

class TeacherDialog(tk.Toplevel):
    """教师编辑对话框"""
    
    def __init__(self, parent, data: Optional[dict]):
        super().__init__(parent)
        self.result = None
        self.data = data
        
        self.title("编辑教师" if data else "添加教师")
        self.geometry("400x350")
        self.resizable(False, False)
        
        self._create_widgets()
        self._load_data()
        
        self.transient(parent)
        self.grab_set()
        self.wait_window(self)
    
    def _create_widgets(self):
        """创建控件"""
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 姓名
        ttk.Label(frame, text="姓名:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.name_var, width=30).grid(row=0, column=1, pady=5)
        
        # 学科
        ttk.Label(frame, text="学科:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.subject_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.subject_var, width=30).grid(row=1, column=1, pady=5)
        
        # 周课时上限
        ttk.Label(frame, text="周课时上限:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.max_hours_var = tk.StringVar(value="16")
        ttk.Entry(frame, textvariable=self.max_hours_var, width=30).grid(row=2, column=1, pady=5)
        
        # 电话
        ttk.Label(frame, text="电话:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.phone_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.phone_var, width=30).grid(row=3, column=1, pady=5)
        
        # 备注
        ttk.Label(frame, text="备注:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.notes_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.notes_var, width=30).grid(row=4, column=1, pady=5)
        
        # 按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="确定", command=self.on_ok).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="取消", command=self.destroy).pack(side=tk.LEFT, padx=10)
    
    def _load_data(self):
        """加载数据"""
        if self.data:
            self.name_var.set(self.data.get("name", ""))
            self.subject_var.set(self.data.get("subject", ""))
            self.max_hours_var.set(str(self.data.get("max_weekly_hours", 16)))
            self.phone_var.set(self.data.get("phone", ""))
            self.notes_var.set(self.data.get("notes", ""))
    
    def on_ok(self):
        """确定按钮"""
        if not self.name_var.get() or not self.subject_var.get():
            messagebox.showwarning("提示", "姓名和学科不能为空")
            return
        
        self.result = {
            "name": self.name_var.get(),
            "subject": self.subject_var.get(),
            "max_weekly_hours": int(self.max_hours_var.get()),
            "phone": self.phone_var.get(),
            "notes": self.notes_var.get()
        }
        self.destroy()


class ClassDialog(tk.Toplevel):
    """班级编辑对话框"""
    
    def __init__(self, parent, data: Optional[dict]):
        super().__init__(parent)
        self.result = None
        self.data = data
        
        self.title("编辑班级" if data else "添加班级")
        self.geometry("400x300")
        self.resizable(False, False)
        
        self._create_widgets()
        self._load_data()
        
        self.transient(parent)
        self.grab_set()
        self.wait_window(self)
    
    def _create_widgets(self):
        """创建控件"""
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 班级名称
        ttk.Label(frame, text="班级名称:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.name_var, width=30).grid(row=0, column=1, pady=5)
        
        # 年级
        ttk.Label(frame, text="年级:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.grade_var = tk.StringVar()
        grade_combo = ttk.Combobox(frame, textvariable=self.grade_var, width=27)
        grade_combo["values"] = ["高一", "高二", "高三", "初一", "初二", "初三"]
        grade_combo.grid(row=1, column=1, pady=5)
        
        # 学生数
        ttk.Label(frame, text="学生数:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.student_count_var = tk.StringVar(value="45")
        ttk.Entry(frame, textvariable=self.student_count_var, width=30).grid(row=2, column=1, pady=5)
        
        # 按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="确定", command=self.on_ok).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="取消", command=self.destroy).pack(side=tk.LEFT, padx=10)
    
    def _load_data(self):
        """加载数据"""
        if self.data:
            self.name_var.set(self.data.get("name", ""))
            self.grade_var.set(self.data.get("grade", ""))
            self.student_count_var.set(str(self.data.get("student_count", 45)))
    
    def on_ok(self):
        """确定按钮"""
        if not self.name_var.get() or not self.grade_var.get():
            messagebox.showwarning("提示", "班级名称和年级不能为空")
            return
        
        self.result = {
            "name": self.name_var.get(),
            "grade": self.grade_var.get(),
            "student_count": int(self.student_count_var.get())
        }
        self.destroy()


class CourseDialog(tk.Toplevel):
    """课程编辑对话框"""
    
    def __init__(self, parent, data: Optional[dict], db: Database):
        super().__init__(parent)
        self.result = None
        self.data = data
        self.db = db
        
        self.title("编辑课程" if data else "添加课程")
        self.geometry("450x400")
        self.resizable(False, False)
        
        self._create_widgets()
        self._load_data()
        
        self.transient(parent)
        self.grab_set()
        self.wait_window(self)
    
    def _create_widgets(self):
        """创建控件"""
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 班级
        ttk.Label(frame, text="班级:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.class_var = tk.StringVar()
        classes = self.db.fetch_all("SELECT id, name FROM classes ORDER BY name")
        self.class_combo = ttk.Combobox(frame, textvariable=self.class_var, width=30)
        self.class_combo["values"] = [f"{c['id']}-{c['name']}" for c in classes]
        self.class_combo.grid(row=0, column=1, pady=5)
        
        # 教师
        ttk.Label(frame, text="教师:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.teacher_var = tk.StringVar()
        teachers = self.db.fetch_all("SELECT id, name FROM teachers ORDER BY name")
        self.teacher_combo = ttk.Combobox(frame, textvariable=self.teacher_var, width=30)
        self.teacher_combo["values"] = [f"{t['id']}-{t['name']}" for t in teachers]
        self.teacher_combo.grid(row=1, column=1, pady=5)
        
        # 科目
        ttk.Label(frame, text="科目:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.subject_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.subject_var, width=30).grid(row=2, column=1, pady=5)
        
        # 周课时
        ttk.Label(frame, text="周课时:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.weekly_hours_var = tk.StringVar(value="2")
        ttk.Entry(frame, textvariable=self.weekly_hours_var, width=30).grid(row=3, column=1, pady=5)
        
        # 连堂
        ttk.Label(frame, text="连堂:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.consecutive_var = tk.StringVar(value="1")
        ttk.Entry(frame, textvariable=self.consecutive_var, width=30).grid(row=4, column=1, pady=5)
        
        # 特殊要求
        ttk.Label(frame, text="特殊要求:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.requirements_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.requirements_var, width=30).grid(row=5, column=1, pady=5)
        
        # 按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="确定", command=self.on_ok).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="取消", command=self.destroy).pack(side=tk.LEFT, padx=10)
    
    def _load_data(self):
        """加载数据"""
        if self.data:
            self.class_var.set(f"{self.data.get('class_id', '')}-{self.db.fetch_one('SELECT name FROM classes WHERE id = ?', (self.data.get('class_id'),))['name']}")
            self.teacher_var.set(f"{self.data.get('teacher_id', '')}-{self.db.fetch_one('SELECT name FROM teachers WHERE id = ?', (self.data.get('teacher_id'),))['name']}")
            self.subject_var.set(self.data.get("subject", ""))
            self.weekly_hours_var.set(str(self.data.get("weekly_hours", 2)))
            self.consecutive_var.set(str(self.data.get("consecutive", 1)))
            self.requirements_var.set(self.data.get("requirements", ""))
    
    def on_ok(self):
        """确定按钮"""
        if not all([self.class_var.get(), self.teacher_var.get(), self.subject_var.get()]):
            messagebox.showwarning("提示", "班级、教师、科目不能为空")
            return
        
        class_id = int(self.class_var.get().split("-")[0])
        teacher_id = int(self.teacher_var.get().split("-")[0])
        
        self.result = {
            "class_id": class_id,
            "teacher_id": teacher_id,
            "subject": self.subject_var.get(),
            "weekly_hours": int(self.weekly_hours_var.get()),
            "consecutive": int(self.consecutive_var.get()),
            "requirements": self.requirements_var.get()
        }
        self.destroy()


class MeetingDialog(tk.Toplevel):
    """会议时间对话框"""
    
    def __init__(self, parent, data: Optional[dict]):
        super().__init__(parent)
        self.result = None
        self.data = data
        
        self.title("添加会议时间")
        self.geometry("350x250")
        self.resizable(False, False)
        
        self._create_widgets()
        self._load_data()
        
        self.transient(parent)
        self.grab_set()
        self.wait_window(self)
    
    def _create_widgets(self):
        """创建控件"""
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 会议名称
        ttk.Label(frame, text="会议名称:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.name_var, width=30).grid(row=0, column=1, pady=5)
        
        # 星期
        ttk.Label(frame, text="星期:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.day_var = tk.StringVar()
        day_combo = ttk.Combobox(frame, textvariable=self.day_var, width=27)
        day_combo["values"] = ["周一", "周二", "周三", "周四", "周五"]
        day_combo.grid(row=1, column=1, pady=5)
        
        # 节次
        ttk.Label(frame, text="节次:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.period_var = tk.StringVar()
        period_combo = ttk.Combobox(frame, textvariable=self.period_var, width=27)
        period_combo["values"] = [str(i) for i in range(1, 9)]
        period_combo.grid(row=2, column=1, pady=5)
        
        # 每周重复
        self.recurring_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="每周重复", variable=self.recurring_var).grid(row=3, column=1, sticky=tk.W, pady=10)
        
        # 按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="确定", command=self.on_ok).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="取消", command=self.destroy).pack(side=tk.LEFT, padx=10)
    
    def _load_data(self):
        """加载数据"""
        if self.data:
            self.name_var.set(self.data.get("name", ""))
            days = ["", "周一", "周二", "周三", "周四", "周五"]
            self.day_var.set(days[self.data.get("day_of_week", 1)])
            self.period_var.set(str(self.data.get("period", 1)))
            self.recurring_var.set(bool(self.data.get("recurring", True)))
    
    def on_ok(self):
        """确定按钮"""
        if not self.name_var.get():
            messagebox.showwarning("提示", "会议名称不能为空")
            return
        
        day_map = {"周一": 1, "周二": 2, "周三": 3, "周四": 4, "周五": 5}
        
        self.result = {
            "name": self.name_var.get(),
            "day_of_week": day_map.get(self.day_var.get(), 1),
            "period": int(self.period_var.get()),
            "recurring": 1 if self.recurring_var.get() else 0
        }
        self.destroy()
