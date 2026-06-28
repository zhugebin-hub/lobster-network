#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
围棋训练监控脚本
功能：定期检查三位学员的训练结果，生成评估报告

作者：诸葛马 (Hermes)
日期：2026-06-27
"""

import os
import json
import time
import subprocess
from datetime import datetime
from typing import Dict, List, Any

# SSH配置
SSH_KEY = "~/.ssh/id_rsa_hermes"
SSH_OPTS = "-o StrictHostKeyChecking=no"

STUDENTS = {
    "xiaochen": {
        "host": "121.43.80.231",
        "shared_dir": "/home/admin/go-training/shared",
    },
    "zhuguxia": {
        "host": "172.24.56.3",
        "shared_dir": "/home/admin/go-training/shared",
    },
    "qoder": {
        "host": "172.24.56.3",
        "shared_dir": "/home/admin/go-training/shared",
    },
}

def ssh_command(host: str, command: str) -> str:
    """执行SSH命令"""
    full_cmd = f"ssh {SSH_OPTS} -i {SSH_KEY} {host} '{command}'"
    result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
    return result.stdout

def check_results(student_id: str) -> List[str]:
    """检查学员的训练结果"""
    student = STUDENTS[student_id]
    from_dir = f"{student['shared_dir']}/from-{student_id}"
    
    # 列出结果文件
    result = ssh_command(student["host"], f"ls -la {from_dir}/")
    files = []
    for line in result.split('\n'):
        if line.endswith('.json') and not line.startswith('total') and not line.startswith('.'):
            files.append(line.split()[-1])
    
    return files

def download_result(student_id: str, filename: str) -> Dict:
    """下载训练结果"""
    student = STUDENTS[student_id]
    remote_file = f"{student['shared_dir']}/from-{student_id}/{filename}"
    local_file = f"/home/admin/go-training/shared/results/{student_id}_{filename}"
    
    # 创建本地目录
    os.makedirs("/home/admin/go-training/shared/results", exist_ok=True)
    
    # SCP下载
    full_cmd = f"scp {SSH_OPTS} -i {SSH_KEY} {student['host']}:{remote_file} {local_file}"
    subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
    
    # 读取结果
    if os.path.exists(local_file):
        with open(local_file, 'r') as f:
            return json.load(f)
    return {}

def generate_assessment_report(results: Dict[str, Any]) -> str:
    """生成评估报告"""
    md = []
    md.append("# 📊 围棋训练评估报告")
    md.append(f"\n> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    md.append("")
    
    # 学员结果汇总
    md.append("## 📈 学员训练结果")
    md.append("")
    md.append("| 学员 | 题目数 | 正确数 | 准确率 | 对局数 | 胜率 |")
    md.append("|------|--------|--------|--------|--------|------|")
    
    for student_id, result in results.items():
        problems = result.get("problems", [])
        games = result.get("games", [])
        
        correct = sum(1 for p in problems if p.get("is_correct", False))
        total = len(problems)
        accuracy = correct / total if total > 0 else 0
        
        wins = sum(1 for g in games if g.get("is_win", False))
        win_rate = wins / len(games) if games else 0
        
        md.append(f"| {student_id} | {total} | {correct} | {accuracy:.0%} | {len(games)} | {win_rate:.0%} |")
    
    md.append("")
    md.append("---")
    md.append(f"*报告由诸葛马 (Hermes) 自动生成*")
    
    return "\n".join(md)

def main():
    """主循环"""
    print("=" * 70)
    print("📊 围棋训练监控系统启动")
    print("=" * 70)
    print()
    
    max_wait = 300  # 最大等待5分钟
    check_interval = 30  # 每30秒检查一次
    
    for student_id in STUDENTS:
        print(f"👀 监控 {student_id}...")
    
    print()
    
    results = {}
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        all_done = True
        
        for student_id in STUDENTS:
            if student_id in results:
                continue
            
            files = check_results(student_id)
            if files:
                print(f"  ✓ {student_id} 有 {len(files)} 个结果文件")
                for filename in files:
                    result = download_result(student_id, filename)
                    if result:
                        results[student_id] = result
                        print(f"  ✓ {student_id} 结果已下载: {filename}")
            else:
                all_done = False
        
        if all_done:
            print("\n✅ 所有学员训练完成！")
            break
        
        print(f"\n⏳ 等待学员训练... ({int((max_wait - (time.time() - start_time)) / 60)}分钟剩余)")
        time.sleep(check_interval)
    
    # 生成评估报告
    if results:
        report = generate_assessment_report(results)
        report_path = f"/home/admin/go-training/shared/assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n📝 评估报告已保存: {report_path}")
    else:
        print("\n⚠️ 未收到训练结果")
    
    print("\n" + "=" * 70)
    print("✅ 训练监控完成")
    print("=" * 70)

if __name__ == "__main__":
    main()
