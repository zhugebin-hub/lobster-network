# -*- coding: utf-8 -*-
"""
登录界面模块
负责用户登录验证
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional


class LoginWindow:
    """登录窗口类"""
    
    def __init__(self, on_login_success: Callable[[dict], None], 
                 on_admin_login: Callable[[], None] = None):
        """
        初始化登录窗口
        
        Args:
            on_login_success: 登录成功回调函数，接收学生信息字典
            on_admin_login: 管理员登录回调函数
        """
        self.on_login_success = on_login_success
        self.on_admin_login = on_admin_login
        self.root = None
        self.student_info = {}
        
    def create_window(self):
        """创建登录窗口"""
        self.root = tk.Tk()
        self.root.title("中职信息技术考试系统 - 登录")
        self.root.geometry("400x350")
        self.root.resizable(False, False)
        
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
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(
            main_frame, 
            text="中职信息技术考试系统",
            font=("Microsoft YaHei", 16, "bold")
        )
        title_label.pack(pady=(0, 30))
        
        # 姓名
        name_frame = ttk.Frame(main_frame)
        name_frame.pack(fill=tk.X, pady=5)
        ttk.Label(name_frame, text="姓名：", width=10).pack(side=tk.LEFT)
        self.name_entry = ttk.Entry(name_frame, width=20)
        self.name_entry.pack(side=tk.LEFT, padx=5)
        
        # 班级
        class_frame = ttk.Frame(main_frame)
        class_frame.pack(fill=tk.X, pady=5)
        ttk.Label(class_frame, text="班级：", width=10).pack(side=tk.LEFT)
        self.class_entry = ttk.Entry(class_frame, width=20)
        self.class_entry.pack(side=tk.LEFT, padx=5)
        
        # 身份证号
        id_frame = ttk.Frame(main_frame)
        id_frame.pack(fill=tk.X, pady=5)
        ttk.Label(id_frame, text="身份证号：", width=10).pack(side=tk.LEFT)
        self.id_entry = ttk.Entry(id_frame, width=20)
        self.id_entry.pack(side=tk.LEFT, padx=5)
        
        # 密码
        pwd_frame = ttk.Frame(main_frame)
        pwd_frame.pack(fill=tk.X, pady=5)
        ttk.Label(pwd_frame, text="密码：", width=10).pack(side=tk.LEFT)
        self.pwd_entry = ttk.Entry(pwd_frame, width=20, show="*")
        self.pwd_entry.pack(side=tk.LEFT, padx=5)
        
        # 提示标签
        hint_label = ttk.Label(
            main_frame,
            text="（默认密码为身份证末 6 位）",
            font=("Microsoft YaHei", 8),
            foreground="gray"
        )
        hint_label.pack(pady=(5, 20))
        
        # 按钮框架
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        # 登录按钮
        login_btn = ttk.Button(
            btn_frame, 
            text="登录考试", 
            command=self._verify_login,
            width=10
        )
        login_btn.pack(side=tk.LEFT, padx=10)
        
        # 管理员按钮
        admin_btn = ttk.Button(
            btn_frame,
            text="管理员登录",
            command=self._admin_login,
            width=10
        )
        admin_btn.pack(side=tk.LEFT, padx=10)
        
        # 退出按钮
        exit_btn = ttk.Button(
            btn_frame,
            text="退出",
            command=self.root.quit,
            width=10
        )
        exit_btn.pack(side=tk.LEFT, padx=10)
        
        # 绑定回车键
        self.root.bind('<Return>', lambda e: self._verify_login())
        
    def _verify_login(self):
        """验证登录信息"""
        name = self.name_entry.get().strip()
        class_name = self.class_entry.get().strip()
        id_number = self.id_entry.get().strip()
        password = self.pwd_entry.get().strip()
        
        # 验证必填字段
        if not name:
            messagebox.showerror("错误", "请输入姓名！")
            self.name_entry.focus()
            return
        
        if not class_name:
            messagebox.showerror("错误", "请输入班级！")
            self.class_entry.focus()
            return
        
        if not id_number:
            messagebox.showerror("错误", "请输入身份证号！")
            self.id_entry.focus()
            return
        
        # 验证身份证号格式（简单验证）
        if len(id_number) != 18:
            messagebox.showerror("错误", "身份证号应为 18 位！")
            self.id_entry.focus()
            return
        
        # 验证密码（默认为身份证末 6 位）
        if not password:
            messagebox.showerror("错误", "请输入密码！")
            self.pwd_entry.focus()
            return
        
        expected_pwd = id_number[-6:]
        if password != expected_pwd:
            messagebox.showerror("错误", "密码错误！\n（默认密码为身份证末 6 位）")
            self.pwd_entry.delete(0, tk.END)
            self.pwd_entry.focus()
            return
        
        # 登录成功
        self.student_info = {
            "name": name,
            "class_name": class_name,
            "id_number": id_number
        }
        
        messagebox.showinfo("成功", f"欢迎 {name} 同学！")
        self.root.destroy()
        
        # 调用回调函数
        if self.on_login_success:
            self.on_login_success(self.student_info)
    
    def _admin_login(self):
        """管理员登录"""
        # 创建管理员登录对话框
        admin_win = tk.Toplevel(self.root)
        admin_win.title("管理员登录")
        admin_win.geometry("300x150")
        admin_win.resizable(False, False)
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
                self.root.destroy()
                if self.on_admin_login:
                    self.on_admin_login()
            else:
                messagebox.showerror("错误", "管理员密码错误！")
                admin_pwd_entry.delete(0, tk.END)
                admin_pwd_entry.focus()
        
        ttk.Button(admin_win, text="确定", command=verify_admin).pack(pady=10)
        admin_win.bind('<Return>', lambda e: verify_admin())
    
    def run(self):
        """运行登录窗口"""
        self.create_window()
        self.root.mainloop()
        
        return self.student_info if self.student_info else None


def show_login(on_login_success: Callable[[dict], None], 
               on_admin_login: Callable[[], None] = None) -> Optional[dict]:
    """
    显示登录窗口
    
    Args:
        on_login_success: 登录成功回调
        on_admin_login: 管理员登录回调
    
    Returns:
        学生信息字典，如果登录成功
    """
    login = LoginWindow(on_login_success, on_admin_login)
    return login.run()
