"""
主窗口界面
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
from utils.db import Database


class MainWindow:
    """主窗口类"""
    
    def __init__(self, root: tk.Tk, db: Database):
        self.root = root
        self.db = db
        
        # 创建菜单栏
        self._create_menu()
        
        # 创建主框架
        self._create_main_frame()
        
        # 创建状态栏
        self._create_status_bar()
        
        # 默认显示教师管理页面
        self.show_teachers()
    
    def _create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="新建", command=self.new_project)
        file_menu.add_command(label="打开", command=self.open_project)
        file_menu.add_command(label="保存", command=self.save_project)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        menubar.add_cascade(label="文件", menu=file_menu)
        
        # 数据管理菜单
        data_menu = tk.Menu(menubar, tearoff=0)
        data_menu.add_command(label="教师管理", command=self.show_teachers)
        data_menu.add_command(label="班级管理", command=self.show_classes)
        data_menu.add_command(label="课程设置", command=self.show_courses)
        data_menu.add_command(label="会议时间", command=self.show_meetings)
        menubar.add_cascade(label="数据管理", menu=data_menu)
        
        # 排课菜单
        schedule_menu = tk.Menu(menubar, tearoff=0)
        schedule_menu.add_command(label="自动排课", command=self.auto_schedule)
        schedule_menu.add_command(label="手动调整", command=self.manual_adjust)
        schedule_menu.add_command(label="课表查询", command=self.view_schedule)
        menubar.add_cascade(label="排课", menu=schedule_menu)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="使用说明", command=self.show_help)
        help_menu.add_command(label="关于", command=self.show_about)
        menubar.add_cascade(label="帮助", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def _create_main_frame(self):
        """创建主内容框架"""
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def _create_status_bar(self):
        """创建状态栏"""
        self.status_bar = ttk.Label(
            self.root, 
            text="就绪", 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def update_status(self, message: str):
        """更新状态栏"""
        self.status_bar.config(text=message)
    
    def clear_main_frame(self):
        """清空主内容区"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    # ==================== 菜单命令 ====================
    
    def new_project(self):
        """新建项目"""
        if messagebox.askyesno("新建", "新建将清空当前数据，确定继续？"):
            # TODO: 实现新建逻辑
            self.update_status("新建项目")
    
    def open_project(self):
        """打开项目"""
        messagebox.showinfo("提示", "功能开发中...")
    
    def save_project(self):
        """保存项目"""
        messagebox.showinfo("提示", "数据已自动保存")
    
    def show_teachers(self):
        """显示教师管理页面"""
        from ui.dialogs import TeacherManager
        self.clear_main_frame()
        TeacherManager(self.main_frame, self.db, self.update_status)
        self.update_status("教师管理")
    
    def show_classes(self):
        """显示班级管理页面"""
        from ui.dialogs import ClassManager
        self.clear_main_frame()
        ClassManager(self.main_frame, self.db, self.update_status)
        self.update_status("班级管理")
    
    def show_courses(self):
        """显示课程设置页面"""
        from ui.dialogs import CourseManager
        self.clear_main_frame()
        CourseManager(self.main_frame, self.db, self.update_status)
        self.update_status("课程设置")
    
    def show_meetings(self):
        """显示会议时间设置"""
        from ui.dialogs import MeetingManager
        self.clear_main_frame()
        MeetingManager(self.main_frame, self.db, self.update_status)
        self.update_status("会议时间设置")
    
    def auto_schedule(self):
        """自动排课"""
        from src.scheduler import Scheduler
        self.update_status("正在排课...")
        scheduler = Scheduler(self.db)
        result = scheduler.run()
        if result["success"]:
            messagebox.showinfo("排课完成", f"成功安排 {result['count']} 节课")
            self.update_status("排课完成")
        else:
            messagebox.showerror("排课失败", result["error"])
            self.update_status("排课失败")
    
    def manual_adjust(self):
        """手动调整"""
        messagebox.showinfo("提示", "功能开发中...")
    
    def view_schedule(self):
        """查看课表"""
        from ui.dialogs import ScheduleViewer
        self.clear_main_frame()
        ScheduleViewer(self.main_frame, self.db)
        self.update_status("课表查询")
    
    def show_help(self):
        """显示帮助"""
        help_text = """
学校排课系统 v1.0 使用指南

1. 数据录入顺序:
   - 先录入教师信息
   - 再录入班级信息
   - 然后设置课程
   - 最后设置会议时间

2. 排课流程:
   - 完成数据录入后点击"自动排课"
   - 系统会自动检测冲突
   - 可手动调整结果

3. 约束条件:
   - 教师时间冲突
   - 会议时间预留
   - 连堂要求
   - 特殊要求
        """
        messagebox.showinfo("帮助", help_text)
    
    def show_about(self):
        """显示关于"""
        about_text = """
学校排课系统 v1.0

一款轻量级单机版排课软件
适用于中小学及培训机构

技术栈: Python + Tkinter + SQLite

© 2026 All Rights Reserved
        """
        messagebox.showinfo("关于", about_text)
