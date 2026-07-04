# -*- coding: utf-8 -*-
"""
题库管理界面模块
负责题库的增删改查
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Dict, List, Any
from database import QuestionDatabase


class AdminWindow:
    """管理员窗口类"""
    
    def __init__(self):
        """初始化管理员窗口"""
        self.root = None
        self.db = QuestionDatabase()
        self.current_type = "single_choice"
        
    def create_window(self):
        """创建管理员窗口"""
        self.root = tk.Tk()
        self.root.title("中职信息技术考试系统 - 题库管理")
        self.root.geometry("1000x700")
        
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
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 顶部标题
        title_label = ttk.Label(
            main_frame,
            text="题库管理系统",
            font=("Microsoft YaHei", 16, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # 题型选择
        type_frame = ttk.Frame(main_frame)
        type_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(type_frame, text="选择题型：").pack(side=tk.LEFT, padx=5)
        
        self.type_var = tk.StringVar(value="single_choice")
        type_combo = ttk.Combobox(
            type_frame,
            textvariable=self.type_var,
            values=["single_choice", "multiple_choice", "true_false"],
            width=20,
            state="readonly"
        )
        type_combo.pack(side=tk.LEFT, padx=5)
        type_combo.bind('<<ComboboxSelected>>', lambda e: self._refresh_question_list())
        
        ttk.Label(type_frame, text="（单选题/多选题/判断题）").pack(side=tk.LEFT, padx=5)
        
        # 按钮区域
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            btn_frame,
            text="添加题目",
            command=self._add_question,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="编辑题目",
            command=self._edit_question,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="删除题目",
            command=self._delete_question,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="刷新列表",
            command=self._refresh_question_list,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="保存题库",
            command=self._save_questions,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(btn_frame, text="").pack(side=tk.LEFT, expand=True)
        
        ttk.Button(
            btn_frame,
            text="返回登录",
            command=self._back_to_login,
            width=10
        ).pack(side=tk.RIGHT, padx=5)
        
        # 统计信息
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill=tk.X, pady=10)
        
        self.stats_label = ttk.Label(stats_frame, text="")
        self.stats_label.pack(side=tk.LEFT)
        
        # 题目列表
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建 Treeview
        columns = ("ID", "题目", "答案", "分类")
        self.question_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            height=20
        )
        
        self.question_tree.heading("ID", text="ID")
        self.question_tree.heading("题目", text="题目内容")
        self.question_tree.heading("答案", text="答案")
        self.question_tree.heading("分类", text="分类")
        
        self.question_tree.column("ID", width=50)
        self.question_tree.column("题目", width=500)
        self.question_tree.column("答案", width=100)
        self.question_tree.column("分类", width=100)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.question_tree.yview)
        self.question_tree.configure(yscrollcommand=scrollbar.set)
        
        self.question_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 双击编辑
        self.question_tree.bind('<Double-1>', lambda e: self._edit_question())
        
        # 初始加载
        self._refresh_question_list()
        
    def _refresh_question_list(self):
        """刷新题目列表"""
        # 清空列表
        for item in self.question_tree.get_children():
            self.question_tree.delete(item)
        
        # 获取当前题型
        self.current_type = self.type_var.get()
        questions = self.db.get_questions(self.current_type)
        
        # 填充列表
        for q in questions:
            self.question_tree.insert("", tk.END, values=(
                q.get("id", ""),
                q.get("question", "")[:50] + "..." if len(q.get("question", "")) > 50 else q.get("question", ""),
                q.get("answer", ""),
                q.get("category", "")
            ))
        
        # 更新统计
        type_names = {
            "single_choice": "单选题",
            "multiple_choice": "多选题",
            "true_false": "判断题"
        }
        total = self.db.get_total_count()
        current_count = len(questions)
        
        self.stats_label.configure(
            text=f"当前：{type_names.get(self.current_type, '')} {current_count} 道 | "
                 f"总计：{total} 道"
        )
    
    def _add_question(self):
        """添加题目"""
        # 创建添加对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("添加题目")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # ID
        ttk.Label(frame, text="题目 ID：").grid(row=0, column=0, sticky=tk.W, pady=5)
        id_entry = ttk.Entry(frame, width=40)
        id_entry.grid(row=0, column=1, pady=5)
        
        # 题目
        ttk.Label(frame, text="题目内容：").grid(row=1, column=0, sticky=tk.W, pady=5)
        question_text = tk.Text(frame, width=40, height=4)
        question_text.grid(row=1, column=1, pady=5)
        
        # 选项
        ttk.Label(frame, text="选项 A：").grid(row=2, column=0, sticky=tk.W, pady=5)
        option_a = ttk.Entry(frame, width=40)
        option_a.grid(row=2, column=1, pady=5)
        
        ttk.Label(frame, text="选项 B：").grid(row=3, column=0, sticky=tk.W, pady=5)
        option_b = ttk.Entry(frame, width=40)
        option_b.grid(row=3, column=1, pady=5)
        
        ttk.Label(frame, text="选项 C：").grid(row=4, column=0, sticky=tk.W, pady=5)
        option_c = ttk.Entry(frame, width=40)
        option_c.grid(row=4, column=1, pady=5)
        
        ttk.Label(frame, text="选项 D：").grid(row=5, column=0, sticky=tk.W, pady=5)
        option_d = ttk.Entry(frame, width=40)
        option_d.grid(row=5, column=1, pady=5)
        
        # 答案
        ttk.Label(frame, text="答案：").grid(row=6, column=0, sticky=tk.W, pady=5)
        answer_entry = ttk.Entry(frame, width=40)
        answer_entry.grid(row=6, column=1, pady=5)
        ttk.Label(frame, text="（单选/多选填字母，如：A 或 ABC；判断填：正确/错误）").grid(
            row=7, column=1, sticky=tk.W, pady=5
        )
        
        # 分类
        ttk.Label(frame, text="分类：").grid(row=8, column=0, sticky=tk.W, pady=5)
        category_var = tk.StringVar()
        category_combo = ttk.Combobox(
            frame,
            textvariable=category_var,
            values=["计算机基础", "Windows 操作", "网络基础", "信息安全", "Office 应用"],
            width=37,
            state="readonly"
        )
        category_combo.grid(row=8, column=1, pady=5)
        
        def save_question():
            try:
                q_id = int(id_entry.get().strip())
                question = question_text.get("1.0", tk.END).strip()
                answer = answer_entry.get().strip()
                category = category_var.get().strip()
                
                if not question or not answer:
                    messagebox.showerror("错误", "题目内容和答案不能为空！")
                    return
                
                # 构建选项
                options = []
                if self.current_type != "true_false":
                    opts = [option_a.get(), option_b.get(), option_c.get(), option_d.get()]
                    options = [f"{chr(65+i)}. {opt}" for i, opt in enumerate(opts) if opt.strip()]
                else:
                    options = ["正确", "错误"]
                
                new_question = {
                    "id": q_id,
                    "question": question,
                    "options": options,
                    "answer": answer,
                    "category": category
                }
                
                if self.db.add_question(self.current_type, new_question):
                    messagebox.showinfo("成功", "题目添加成功！")
                    dialog.destroy()
                    self._refresh_question_list()
                else:
                    messagebox.showerror("错误", "添加题目失败！")
            except Exception as e:
                messagebox.showerror("错误", f"添加题目失败：{e}")
        
        ttk.Button(frame, text="保存", command=save_question).grid(row=9, column=0, pady=20)
        ttk.Button(frame, text="取消", command=dialog.destroy).grid(row=9, column=1, pady=20)
    
    def _edit_question(self):
        """编辑题目"""
        selected = self.question_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要编辑的题目！")
            return
        
        item = self.question_tree.item(selected[0])
        q_id = item["values"][0]
        
        # 查找题目
        questions = self.db.get_questions(self.current_type)
        question = None
        for q in questions:
            if q["id"] == q_id:
                question = q
                break
        
        if not question:
            messagebox.showerror("错误", "未找到该题目！")
            return
        
        # 创建编辑对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("编辑题目")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # ID
        ttk.Label(frame, text="题目 ID：").grid(row=0, column=0, sticky=tk.W, pady=5)
        id_entry = ttk.Entry(frame, width=40)
        id_entry.grid(row=0, column=1, pady=5)
        id_entry.insert(0, question["id"])
        id_entry.configure(state="readonly")
        
        # 题目
        ttk.Label(frame, text="题目内容：").grid(row=1, column=0, sticky=tk.W, pady=5)
        question_text = tk.Text(frame, width=40, height=4)
        question_text.grid(row=1, column=1, pady=5)
        question_text.insert("1.0", question["question"])
        
        # 选项
        options = question.get("options", [])
        
        ttk.Label(frame, text="选项 A：").grid(row=2, column=0, sticky=tk.W, pady=5)
        option_a = ttk.Entry(frame, width=40)
        option_a.grid(row=2, column=1, pady=5)
        if len(options) > 0:
            option_a.insert(0, options[0][3:] if len(options[0]) > 2 else options[0])
        
        ttk.Label(frame, text="选项 B：").grid(row=3, column=0, sticky=tk.W, pady=5)
        option_b = ttk.Entry(frame, width=40)
        option_b.grid(row=3, column=1, pady=5)
        if len(options) > 1:
            option_b.insert(0, options[1][3:] if len(options[1]) > 2 else options[1])
        
        ttk.Label(frame, text="选项 C：").grid(row=4, column=0, sticky=tk.W, pady=5)
        option_c = ttk.Entry(frame, width=40)
        option_c.grid(row=4, column=1, pady=5)
        if len(options) > 2:
            option_c.insert(0, options[2][3:] if len(options[2]) > 2 else options[2])
        
        ttk.Label(frame, text="选项 D：").grid(row=5, column=0, sticky=tk.W, pady=5)
        option_d = ttk.Entry(frame, width=40)
        option_d.grid(row=5, column=1, pady=5)
        if len(options) > 3:
            option_d.insert(0, options[3][3:] if len(options[3]) > 2 else options[3])
        
        # 答案
        ttk.Label(frame, text="答案：").grid(row=6, column=0, sticky=tk.W, pady=5)
        answer_entry = ttk.Entry(frame, width=40)
        answer_entry.grid(row=6, column=1, pady=5)
        answer_entry.insert(0, question["answer"])
        
        # 分类
        ttk.Label(frame, text="分类：").grid(row=8, column=0, sticky=tk.W, pady=5)
        category_var = tk.StringVar(value=question.get("category", ""))
        category_combo = ttk.Combobox(
            frame,
            textvariable=category_var,
            values=["计算机基础", "Windows 操作", "网络基础", "信息安全", "Office 应用"],
            width=37
        )
        category_combo.grid(row=8, column=1, pady=5)
        
        def update_question():
            try:
                question_content = question_text.get("1.0", tk.END).strip()
                answer = answer_entry.get().strip()
                category = category_var.get().strip()
                
                if not question_content or not answer:
                    messagebox.showerror("错误", "题目内容和答案不能为空！")
                    return
                
                # 构建选项
                opts_list = [option_a.get(), option_b.get(), option_c.get(), option_d.get()]
                if self.current_type != "true_false":
                    options = [f"{chr(65+i)}. {opt}" for i, opt in enumerate(opts_list) if opt.strip()]
                else:
                    options = ["正确", "错误"]
                
                updated_question = {
                    "id": question["id"],
                    "question": question_content,
                    "options": options,
                    "answer": answer,
                    "category": category
                }
                
                if self.db.update_question(self.current_type, question["id"], updated_question):
                    messagebox.showinfo("成功", "题目更新成功！")
                    dialog.destroy()
                    self._refresh_question_list()
                else:
                    messagebox.showerror("错误", "更新题目失败！")
            except Exception as e:
                messagebox.showerror("错误", f"更新题目失败：{e}")
        
        ttk.Button(frame, text="保存", command=update_question).grid(row=9, column=0, pady=20)
        ttk.Button(frame, text="取消", command=dialog.destroy).grid(row=9, column=1, pady=20)
    
    def _delete_question(self):
        """删除题目"""
        selected = self.question_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要删除的题目！")
            return
        
        item = self.question_tree.item(selected[0])
        q_id = item["values"][0]
        
        if messagebox.askyesno("确认", f"确定要删除题目 ID={q_id} 吗？"):
            if self.db.delete_question(self.current_type, q_id):
                messagebox.showinfo("成功", "题目删除成功！")
                self._refresh_question_list()
            else:
                messagebox.showerror("错误", "删除题目失败！")
    
    def _save_questions(self):
        """保存题库"""
        if self.db.save():
            messagebox.showinfo("成功", "题库保存成功！")
        else:
            messagebox.showerror("错误", "题库保存失败！")
    
    def _back_to_login(self):
        """返回登录界面"""
        if messagebox.askyesno("确认", "确定要返回登录界面吗？"):
            self.root.destroy()
            # 重新启动主程序
            import main
            main.main()
    
    def run(self):
        """运行管理员窗口"""
        self.create_window()
        self.root.mainloop()


def show_admin():
    """显示管理员界面"""
    admin = AdminWindow()
    admin.run()
