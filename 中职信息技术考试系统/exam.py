# -*- coding: utf-8 -*-
"""
考试界面模块
负责显示题目、答题和交卷
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Dict, List, Any, Callable
import random
import time


class ExamWindow:
    """考试窗口类"""
    
    def __init__(self, student_info: Dict[str, str], 
                 questions: Dict[str, List[Dict[str, Any]]],
                 on_exam_complete: Callable[[Dict[str, Any]], None] = None):
        """
        初始化考试窗口
        
        Args:
            student_info: 学生信息
            questions: 题库（包含 single_choice, multiple_choice, true_false）
            on_exam_complete: 考试完成回调函数
        """
        self.student_info = student_info
        self.questions = questions
        self.on_exam_complete = on_exam_complete
        
        self.root = None
        self.notebook = None  # 选项卡
        
        # 当前答题情况
        self.user_answers = {
            "single_choice": {},
            "multiple_choice": {},
            "true_false": {}
        }
        
        # 题目显示（每种题型最多显示 10 题每页）
        self.single_page_size = 10
        self.multiple_page_size = 5
        self.true_false_page_size = 5
        
        # 当前页码
        self.current_pages = {
            "single_choice": 0,
            "multiple_choice": 0,
            "true_false": 0
        }
        
        # 计时器
        self.start_time = None
        self.timer_id = None
        self.exam_duration = 60  # 考试时长（分钟）
        
    def create_window(self):
        """创建考试窗口"""
        self.root = tk.Tk()
        self.root.title("中职信息技术考试系统 - 考试界面")
        self.root.geometry("900x700")
        
        # 设置窗口居中
        self._center_window()
        
        # 记录开始时间
        self.start_time = time.time()
        
        self._create_widgets()
        self._start_timer()
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
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
        
        # 顶部信息栏
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 学生信息
        student_label = ttk.Label(
            info_frame,
            text=f"姓名：{self.student_info['name']}  |  "
                 f"班级：{self.student_info['class_name']}  |  "
                 f"身份证号：{self.student_info['id_number']}",
            font=("Microsoft YaHei", 10)
        )
        student_label.pack(side=tk.LEFT)
        
        # 计时器
        self.timer_label = ttk.Label(
            info_frame,
            text="剩余时间：60:00",
            font=("Microsoft YaHei", 12, "bold"),
            foreground="blue"
        )
        self.timer_label.pack(side=tk.RIGHT)
        
        # 选项卡
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 单选题页面
        self.single_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.single_frame, text="单选题 (30 题，每题 2 分)")
        self._create_single_choice_page()
        
        # 多选题页面
        self.multiple_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.multiple_frame, text="多选题 (10 题，每题 3 分)")
        self._create_multiple_choice_page()
        
        # 判断题页面
        self.true_false_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.true_false_frame, text="判断题 (10 题，每题 2 分)")
        self._create_true_false_page()
        
        # 底部按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            btn_frame,
            text="上一题",
            command=self._prev_question,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="下一题",
            command=self._next_question,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(btn_frame, text="").pack(side=tk.LEFT, expand=True)
        
        ttk.Button(
            btn_frame,
            text="交卷",
            command=self._submit_exam,
            width=10
        ).pack(side=tk.RIGHT, padx=5)
        
    def _create_single_choice_page(self):
        """创建单选题页面"""
        # 清空框架
        for widget in self.single_frame.winfo_children():
            widget.destroy()
        
        # 获取单选题
        single_questions = self.questions.get("single_choice", [])
        
        if not single_questions:
            ttk.Label(self.single_frame, text="暂无题目").pack()
            return
        
        # 创建滚动区域
        canvas = tk.Canvas(self.single_frame)
        scrollbar = ttk.Scrollbar(self.single_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 显示题目
        self._display_questions(
            scrollable_frame,
            single_questions,
            "single_choice",
            self.single_page_size
        )
        
    def _create_multiple_choice_page(self):
        """创建多选题页面"""
        # 清空框架
        for widget in self.multiple_frame.winfo_children():
            widget.destroy()
        
        # 获取多选题
        multiple_questions = self.questions.get("multiple_choice", [])
        
        if not multiple_questions:
            ttk.Label(self.multiple_frame, text="暂无题目").pack()
            return
        
        # 创建滚动区域
        canvas = tk.Canvas(self.multiple_frame)
        scrollbar = ttk.Scrollbar(self.multiple_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 显示题目
        self._display_questions(
            scrollable_frame,
            multiple_questions,
            "multiple_choice",
            self.multiple_page_size
        )
        
    def _create_true_false_page(self):
        """创建判断题页面"""
        # 清空框架
        for widget in self.true_false_frame.winfo_children():
            widget.destroy()
        
        # 获取判断题
        true_false_questions = self.questions.get("true_false", [])
        
        if not true_false_questions:
            ttk.Label(self.true_false_frame, text="暂无题目").pack()
            return
        
        # 创建滚动区域
        canvas = tk.Canvas(self.true_false_frame)
        scrollbar = ttk.Scrollbar(self.true_false_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 显示题目
        self._display_questions(
            scrollable_frame,
            true_false_questions,
            "true_false",
            self.true_false_page_size
        )
        
    def _display_questions(self, parent, questions: List[Dict[str, Any]], 
                          question_type: str, page_size: int):
        """
        显示题目
        
        Args:
            parent: 父容器
            questions: 题目列表
            question_type: 题目类型
            page_size: 每页显示数量
        """
        current_page = self.current_pages[question_type]
        start_idx = current_page * page_size
        end_idx = min(start_idx + page_size, len(questions))
        
        # 题目编号变量存储
        if not hasattr(self, f'{question_type}_vars'):
            setattr(self, f'{question_type}_vars', {})
        
        vars_dict = getattr(self, f'{question_type}_vars')
        
        for i, q in enumerate(questions[start_idx:end_idx], start_idx):
            # 题目框架
            q_frame = ttk.Frame(parent)
            q_frame.pack(fill=tk.X, pady=10, padx=10)
            
            # 题号
            q_num = i + 1
            ttk.Label(
                q_frame,
                text=f"{q_num}. {q['question']}",
                font=("Microsoft YaHei", 10),
                wraplength=700
            ).pack(anchor=tk.W, pady=(0, 5))
            
            # 选项
            if question_type in ["single_choice", "multiple_choice"]:
                # 单选题和多选题使用复选框（多选可以选多个）
                for option in q["options"]:
                    option_letter = option[0]  # A, B, C, D
                    var_key = f"{q['id']}_{option_letter}"
                    
                    if question_type == "single_choice":
                        # 单选题使用 Radio
                        if var_key not in vars_dict:
                            vars_dict[var_key] = tk.StringVar(value="")
                        
                        radio = ttk.Radiobutton(
                            q_frame,
                            text=option,
                            variable=vars_dict[var_key],
                            value=option_letter,
                            command=lambda qt=question_type, qid=q['id']: 
                                self._save_answer(qt, qid)
                        )
                        radio.pack(anchor=tk.W, padx=20)
                    else:
                        # 多选题使用 Checkbutton
                        if var_key not in vars_dict:
                            vars_dict[var_key] = tk.BooleanVar(value=False)
                        
                        check = ttk.Checkbutton(
                            q_frame,
                            text=option,
                            variable=vars_dict[var_key],
                            command=lambda qt=question_type, qid=q['id']: 
                                self._save_answer(qt, qid)
                        )
                        check.pack(anchor=tk.W, padx=20)
            else:
                # 判断题
                if q['id'] not in vars_dict:
                    vars_dict[q['id']] = tk.StringVar(value="")
                
                tf_frame = ttk.Frame(q_frame)
                tf_frame.pack(anchor=tk.W, padx=20)
                
                ttk.Radiobutton(
                    tf_frame,
                    text="正确",
                    variable=vars_dict[q['id']],
                    value="正确",
                    command=lambda qt=question_type, qid=q['id']: 
                        self._save_answer(qt, qid)
                ).pack(side=tk.LEFT, padx=10)
                
                ttk.Radiobutton(
                    tf_frame,
                    text="错误",
                    variable=vars_dict[q['id']],
                    value="错误",
                    command=lambda qt=question_type, qid=q['id']: 
                        self._save_answer(qt, qid)
                ).pack(side=tk.LEFT, padx=10)
            
            # 分隔线
            ttk.Separator(parent, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # 页码显示
        total_pages = (len(questions) + page_size - 1) // page_size
        page_label = ttk.Label(
            parent,
            text=f"第 {current_page + 1}/{total_pages} 页",
            font=("Microsoft YaHei", 9)
        )
        page_label.pack(pady=10)
    
    def _save_answer(self, question_type: str, question_id: int):
        """
        保存答案
        
        Args:
            question_type: 题目类型
            question_id: 题目 ID
        """
        vars_dict = getattr(self, f'{question_type}_vars', {})
        
        if question_type == "single_choice":
            # 单选题
            for key, var in vars_dict.items():
                if key.startswith(f"{question_id}_"):
                    answer = var.get()
                    if answer:
                        self.user_answers[question_type][question_id] = answer
                    break
        elif question_type == "multiple_choice":
            # 多选题
            answers = []
            for key, var in vars_dict.items():
                if key.startswith(f"{question_id}_"):
                    if var.get():
                        answers.append(key.split("_")[1])  # 获取 A, B, C, D
            if answers:
                self.user_answers[question_type][question_id] = "".join(sorted(answers))
            else:
                self.user_answers[question_type].pop(question_id, None)
        else:
            # 判断题
            if question_id in vars_dict:
                answer = vars_dict[question_id].get()
                if answer:
                    self.user_answers[question_type][question_id] = answer
                else:
                    self.user_answers[question_type].pop(question_id, None)
    
    def _prev_question(self):
        """上一页"""
        current_tab = self.notebook.index(self.notebook.select())
        question_types = ["single_choice", "multiple_choice", "true_false"]
        question_type = question_types[current_tab]
        
        if self.current_pages[question_type] > 0:
            self.current_pages[question_type] -= 1
            self._refresh_page(question_type)
    
    def _next_question(self):
        """下一页"""
        current_tab = self.notebook.index(self.notebook.select())
        question_types = ["single_choice", "multiple_choice", "true_false"]
        question_type = question_types[current_tab]
        
        questions = self.questions.get(question_type, [])
        page_size = getattr(self, f'{question_type}_page_size')
        max_page = (len(questions) + page_size - 1) // page_size
        
        if self.current_pages[question_type] < max_page - 1:
            self.current_pages[question_type] += 1
            self._refresh_page(question_type)
    
    def _refresh_page(self, question_type: str):
        """刷新页面"""
        if question_type == "single_choice":
            self._create_single_choice_page()
        elif question_type == "multiple_choice":
            self._create_multiple_choice_page()
        else:
            self._create_true_false_page()
    
    def _start_timer(self):
        """启动计时器"""
        self._update_timer()
    
    def _update_timer(self):
        """更新计时器"""
        elapsed = time.time() - self.start_time
        remaining_seconds = self.exam_duration * 60 - int(elapsed)
        
        if remaining_seconds <= 0:
            remaining_seconds = 0
            self.timer_label.configure(text="时间到！", foreground="red")
            self._submit_exam()
            return
        
        minutes = remaining_seconds // 60
        seconds = remaining_seconds % 60
        self.timer_label.configure(
            text=f"剩余时间：{minutes:02d}:{seconds:02d}",
            foreground="blue" if remaining_seconds > 300 else "red"
        )
        
        # 继续计时
        self.timer_id = self.root.after(1000, self._update_timer)
    
    def _submit_exam(self):
        """交卷"""
        # 停止计时器
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        
        # 确认交卷
        if not messagebox.askyesno("确认", "确定要交卷吗？\n交卷后将无法修改答案！"):
            self._start_timer()
            return
        
        # 计算成绩
        scores = self._calculate_scores()
        
        # 显示成绩
        self._show_result(scores)
        
        # 调用回调
        if self.on_exam_complete:
            self.on_exam_complete({
                "student_info": self.student_info,
                "scores": scores,
                "user_answers": self.user_answers,
                "exam_duration": self.exam_duration * 60 - (time.time() - self.start_time)
            })
    
    def _calculate_scores(self) -> Dict[str, Any]:
        """
        计算成绩
        
        Returns:
            成绩字典
        """
        single_score = 0
        multiple_score = 0
        true_false_score = 0
        
        # 单选题（每题 2 分）
        for q in self.questions.get("single_choice", []):
            user_answer = self.user_answers["single_choice"].get(q["id"])
            if user_answer == q["answer"]:
                single_score += 2
        
        # 多选题（每题 3 分）
        for q in self.questions.get("multiple_choice", []):
            user_answer = self.user_answers["multiple_choice"].get(q["id"])
            if user_answer == q["answer"]:
                multiple_score += 3
        
        # 判断题（每题 2 分）
        for q in self.questions.get("true_false", []):
            user_answer = self.user_answers["true_false"].get(q["id"])
            if user_answer == q["answer"]:
                true_false_score += 2
        
        total_score = single_score + multiple_score + true_false_score
        
        return {
            "single_score": single_score,
            "multiple_score": multiple_score,
            "true_false_score": true_false_score,
            "total_score": total_score,
            "max_score": 100
        }
    
    def _show_result(self, scores: Dict[str, Any]):
        """
        显示成绩
        
        Args:
            scores: 成绩字典
        """
        result_win = tk.Toplevel(self.root)
        result_win.title("考试成绩")
        result_win.geometry("400x300")
        result_win.transient(self.root)
        result_win.grab_set()
        
        frame = ttk.Frame(result_win, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        ttk.Label(
            frame,
            text="考试成绩单",
            font=("Microsoft YaHei", 16, "bold")
        ).pack(pady=(0, 20))
        
        # 学生信息
        ttk.Label(
            frame,
            text=f"姓名：{self.student_info['name']}",
            font=("Microsoft YaHei", 11)
        ).pack(anchor=tk.W, pady=2)
        
        ttk.Label(
            frame,
            text=f"班级：{self.student_info['class_name']}",
            font=("Microsoft YaHei", 11)
        ).pack(anchor=tk.W, pady=2)
        
        ttk.Separator(frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # 成绩详情
        ttk.Label(
            frame,
            text=f"单选题得分：{scores['single_score']}/60",
            font=("Microsoft YaHei", 11)
        ).pack(anchor=tk.W, pady=2)
        
        ttk.Label(
            frame,
            text=f"多选题得分：{scores['multiple_score']}/30",
            font=("Microsoft YaHei", 11)
        ).pack(anchor=tk.W, pady=2)
        
        ttk.Label(
            frame,
            text=f"判断题得分：{scores['true_false_score']}/20",
            font=("Microsoft YaHei", 11)
        ).pack(anchor=tk.W, pady=2)
        
        ttk.Separator(frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # 总分
        total_color = "green" if scores['total_score'] >= 60 else "red"
        ttk.Label(
            frame,
            text=f"总分：{scores['total_score']}/100",
            font=("Microsoft YaHei", 14, "bold"),
            foreground=total_color
        ).pack(pady=10)
        
        # 评价
        if scores['total_score'] >= 90:
            comment = "优秀！"
        elif scores['total_score'] >= 80:
            comment = "良好！"
        elif scores['total_score'] >= 60:
            comment = "及格！"
        else:
            comment = "不及格，请继续努力！"
        
        ttk.Label(
            frame,
            text=comment,
            font=("Microsoft YaHei", 12),
            foreground=total_color
        ).pack(pady=10)
        
        # 确定按钮
        ttk.Button(
            frame,
            text="确定",
            command=result_win.destroy
        ).pack(pady=10)
    
    def _on_closing(self):
        """窗口关闭事件"""
        if messagebox.askyesno("确认", "考试尚未完成，确定要退出吗？\n退出后成绩将不会保存！"):
            if self.timer_id:
                self.root.after_cancel(self.timer_id)
            self.root.destroy()
    
    def run(self):
        """运行考试窗口"""
        self.create_window()
        self.root.mainloop()


def start_exam(student_info: Dict[str, str], 
               questions: Dict[str, List[Dict[str, Any]]],
               on_exam_complete: Callable[[Dict[str, Any]], None] = None):
    """
    开始考试
    
    Args:
        student_info: 学生信息
        questions: 题库
        on_exam_complete: 考试完成回调
    """
    exam = ExamWindow(student_info, questions, on_exam_complete)
    exam.run()
