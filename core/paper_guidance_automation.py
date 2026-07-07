#!/usr/bin/env python3
"""
论文撰写引导自动化脚本
自动为所有学员分配任务、监控进度、生成报告
"""
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

# 路径配置
REPO_ROOT = Path("/home/admin/lobster-network")
PAPER_DIR = REPO_ROOT / "domains" / "paper"
TRAINER = PAPER_DIR / "trainers" / "paper_trainer.py"

# 学员列表
STUDENTS = ["qoder", "xiaochen", "zhuguxia", "hermes"]

def run_command(cmd):
    """运行命令并返回输出"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode

def assign_tasks(day):
    """为所有学员分配任务"""
    print(f"\n{'='*60}")
    print(f"📝 Day {day} 任务分配")
    print(f"{'='*60}")
    
    for student in STUDENTS:
        print(f"\n👤 {student}:")
        cmd = f"python3 {TRAINER} --node {student} --action assign --day {day}"
        stdout, stderr, code = run_command(cmd)
        if code == 0:
            print(f"  ✅ 任务分配成功")
            # 打印任务摘要
            for line in stdout.split('\n')[2:5]:
                if line.strip():
                    print(f"     {line.strip()}")
        else:
            print(f"  ❌ 任务分配失败: {stderr}")

def check_progress():
    """检查所有学员进度"""
    print(f"\n{'='*60}")
    print(f"📊 进度检查")
    print(f"{'='*60}")
    
    cmd = f"python3 {TRAINER} --action status"
    stdout, stderr, code = run_command(cmd)
    if code == 0:
        print(stdout)
    else:
        print(f"❌ 进度检查失败: {stderr}")

def generate_report():
    """生成训练报告"""
    print(f"\n{'='*60}")
    print(f"📋 训练报告")
    print(f"{'='*60}")
    
    for student in STUDENTS:
        print(f"\n👤 {student}:")
        cmd = f"python3 {TRAINER} --node {student} --action weekly-report"
        stdout, stderr, code = run_command(cmd)
        if code == 0:
            print(stdout[:500])  # 只打印前500字符
        else:
            print(f"  ❌ 报告生成失败: {stderr}")

def main():
    """主函数"""
    print("🦞 小龙虾网络 · 论文撰写引导自动化")
    print(f"📅 日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 步骤1: 分配任务
    assign_tasks(1)
    
    # 步骤2: 检查进度
    check_progress()
    
    # 步骤3: 生成报告
    generate_report()
    
    print(f"\n{'='*60}")
    print("✅ 引导流程完成")
    print(f"{'='*60}")
    print("\n📝 下一步:")
    print("1. 学员开始精读论文")
    print("2. 完成写作练习")
    print("3. 提交学习进度")
    print("4. 参加论文研讨会")

if __name__ == "__main__":
    main()
