# -*- coding: utf-8 -*-
"""
中职信息技术考试系统 - 主程序入口
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# 确保可以导入同目录模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import QuestionDatabase
from score import ScoreManager
from login import LoginWindow
from exam import ExamWindow
from admin import AdminWindow


class MainApplication:
    """主应用程序类"""
    
    def __init__(self):
        """初始化应用程序"""
        self.root = None
        self.student_info = None
        self.db = QuestionDatabase()
        self.score_manager = ScoreManager()
        
    def create_main_menu(self):
        """创建主菜单"""
        self.root = tk.Tk()
        self.root.title("中职信息技术考试系统")
        self.root.geometry("500x400")
        
        # 设置窗口居中
        self._center_window()
        
        self._create_widgets()
        
    def _center_window(self):
        """设置窗口居中"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def _create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="30")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(
            main_frame,
            text="中职信息技术考试系统",
            font=("Microsoft YaHei", 20, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ttk.Label(
            main_frame,
            text="欢迎使用考试系统",
            font=("Microsoft YaHei", 12)
        )
        subtitle_label.pack(pady=(0, 30))
        
        # 按钮框架
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        # 开始考试按钮
        start_btn = ttk.Button(
            btn_frame,
            text="开始考试",
            command=self._start_exam_flow,
            width=20
        )
        start_btn.pack(pady=10)
        
        # 成绩查询按钮
        query_btn = ttk.Button(
            btn_frame,
            text="成绩查询",
            command=self._show_score_query,
            width=20
        )
        query_btn.pack(pady=10)
        
        # 管理员入口按钮
        admin_btn = ttk.Button(
            btn_frame,
            text="管理员入口",
            command=self._admin_login,
            width=20
        )
        admin_btn.pack(pady=10)
        
        # 退出按钮
        exit_btn = ttk.Button(
            btn_frame,
            text="退出系统",
            command=self.root.quit,
            width=20
        )
        exit_btn.pack(pady=10)
        
        # 版本信息
        version_label = ttk.Label(
            main_frame,
            text="版本：1.0.0",
            font=("Microsoft YaHei", 8),
            foreground="gray"
        )
        version_label.pack(side=tk.BOTTOM, pady=(20, 0))
    
    def _start_exam_flow(self):
        """开始考试流程"""
        # 创建登录窗口
        login_window = LoginWindow(
            on_login_success=self._on_login_success,
            on_admin_login=self._admin_login
        )
        login_window.create_window()
        
        # 隐藏主窗口
        self.root.withdraw()
        
        # 等待登录完成
        login_window.root.wait_window()
        
        # 如果登录成功，显示考试界面
        if login_window.student_info:
            self.student_info = login_window.student_info
            self._start_exam()
        else:
            # 登录取消，显示主窗口
            self.root.deiconify()
    
    def _on_login_success(self, student_info: dict):
        """登录成功回调"""
        self.student_info = student_info
    
    def _start_exam(self):
        """开始考试"""
        # 获取题库
        questions = self.db.get_all_questions()
        
        # 创建考试窗口
        exam_window = ExamWindow(
            student_info=self.student_info,
            questions=questions,
            on_exam_complete=self._on_exam_complete
        )
        
        # 隐藏主窗口
        self.root.withdraw()
        
        # 运行考试
        exam_window.create_window()
        exam_window.root.wait_window()
        
        # 考试结束，返回主窗口
        self.root.deiconify()
    
    def _on_exam_complete(self, exam_result: dict):
        """考试完成回调"""
        # 保存成绩
        student_info = exam_result["student_info"]
        scores = exam_result["scores"]
        
        self.score_manager.save_score(student_info, scores)
        
        # 显示保存成功提示
        messagebox.showinfo(
            "成绩保存",
            f"成绩已保存！\n总分：{scores['total_score']}/100"
        )
    
    def _show_score_query(self):
        """显示成绩查询"""
        query_win = tk.Toplevel(self.root)
        query_win.title("成绩查询")
        query_win.geometry("600x400")
        query_win.transient(self.root)
        
        frame = ttk.Frame(query_win, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        ttk.Label(
            frame,
            text="成绩查询",
            font=("Microsoft YaHei", 16, "bold")
        ).pack(pady=(0, 20))
        
        # 搜索框
        search_frame = ttk.Frame(frame)
        search_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(search_frame, text="身份证号：").pack(side=tk.LEFT)
        id_entry = ttk.Entry(search_frame, width=20)
        id_entry.pack(side=tk.LEFT, padx=5)
        
        def search():
            # 清空列表
            for item in score_tree.get_children():
                score_tree.delete(item)
            
            id_number = id_entry.get().strip()
            if id_number:
                scores = self.score_manager.get_student_scores(id_number)
            else:
                scores = self.score_manager.get_all_scores()
            
            for score in scores:
                score_tree.insert("", tk.END, values=(
                    score.get("姓名", ""),
                    score.get("班级", ""),
                    score.get("身份证号", ""),
                    score.get("考试日期", ""),
                    score.get("总分", "")
                ))
        
        ttk.Button(search_frame, text="查询", command=search).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="显示全部", command=lambda: [id_entry.delete(0, tk.END), search()]).pack(side=tk.LEFT, padx=5)
        
        # 成绩列表
        columns = ("姓名", "班级", "身份证号", "考试日期", "总分")
        score_tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            score_tree.heading(col, text=col)
            score_tree.column(col, width=100)
        
        score_tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 导出按钮
        export_frame = ttk.Frame(frame)
        export_frame.pack(fill=tk.X)
        
        def export_csv():
            import csv
            from datetime import datetime
            
            scores = self.score_manager.get_all_scores()
            if not scores:
                messagebox.showwarning("提示", "没有成绩数据可导出！")
                return
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"成绩导出_{timestamp}.csv"
            
            try:
                with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=scores[0].keys())
                    writer.writeheader()
                    writer.writerows(scores)
                messagebox.showinfo("成功", f"成绩已导出到：{filename}")
            except Exception as e:
                messagebox.showerror("错误", f"导出失败：{e}")
        
        ttk.Button(export_frame, text="导出 CSV", command=export_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="关闭", command=query_win.destroy).pack(side=tk.RIGHT)
        
        # 初始加载全部
        search()
    
    def _admin_login(self):
        """管理员登录"""
        # 创建管理员登录对话框
        admin_win = tk.Toplevel(self.root)
        admin_win.title("管理员登录")
        admin_win.geometry("300x150")
        admin_win.transient(self.root)
        
        ttk.Label(admin_win, text="管理员密码：").pack(pady=10)
        admin_pwd_entry = ttk.Entry(admin_win, show="*", width=20)
        admin_pwd_entry.pack(pady=5)
        admin_pwd_entry.focus()
        
        def verify_admin():
            pwd = admin_pwd_entry.get().strip()
            # 默认管理员密码：admin123
            if pwd == "admin123":
                admin_win.destroy()
                self.root.withdraw()
                
                # 打开管理员界面
                admin_window = AdminWindow()
                admin_window.create_window()
                admin_window.root.wait_window()
                
                self.root.deiconify()
            else:
                messagebox.showerror("错误", "管理员密码错误！")
                admin_pwd_entry.delete(0, tk.END)
                admin_pwd_entry.focus()
        
        ttk.Button(admin_win, text="确定", command=verify_admin).pack(pady=10)
        admin_win.bind('<Return>', lambda e: verify_admin())
    
    def run(self):
        """运行应用程序"""
        self.create_main_menu()
        self.root.mainloop()


def main():
    """主函数"""
    app = MainApplication()
    app.run()


if __name__ == "__main__":
    main()
