#!/usr/bin/env python3
"""
学校排课系统 - 主程序入口
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.db import Database
from ui.main_window import MainWindow


def main():
    """主函数"""
    # 初始化数据库
    db = Database("data/school.db")
    db.connect()
    
    # 创建主窗口
    root = tk.Tk()
    root.title("学校排课系统 v1.0")
    root.geometry("1200x800")
    
    # 设置窗口图标（可选）
    # root.iconbitmap("icon.ico")
    
    app = MainWindow(root, db)
    
    # 窗口关闭时清理资源
    def on_closing():
        if messagebox.askokcancel("退出", "确定要退出系统吗？"):
            db.close()
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
