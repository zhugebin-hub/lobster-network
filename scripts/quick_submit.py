#!/usr/bin/env python3
"""
🦞 小龙虾网络 - 学员一键提交工具
用法: python3 quick_submit.py <student_id> <day> [result_file]
"""
import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

def submit_result(student_id, day, result_file=None):
    """提交训练结果到诸葛马服务器"""
    hermes_host = "172.24.57.34"
    hermes_user = "admin"
    results_dir = "/home/admin/lobster-network/docs/training_results"
    
    if result_file:
        # 提交指定文件
        result_path = Path(result_file)
        if not result_path.exists():
            print(f"❌ 文件不存在: {result_file}")
            return False
        
        dest_name = f"{student_id}_day{day}_{result_path.name}"
        cmd = ["scp", str(result_path), f"{hermes_user}@{hermes_host}:{results_dir}/{dest_name}"]
        
        print(f"📤 提交文件: {result_path.name} → {dest_name}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ 提交成功！")
            return True
        else:
            print(f"❌ 提交失败: {result.stderr}")
            return False
    else:
        # 生成并提交默认结果
        result = {
            "student_id": student_id,
            "day": day,
            "submitted_at": datetime.now().isoformat(),
            "status": "submitted",
            "problems": 0,
            "correct": 0,
            "accuracy": 0.0,
            "games": 0,
            "wins": 0,
            "win_rate": 0.0,
        }
        
        result_file = Path(f"day{day}_result_{student_id}.json")
        with open(result_file, 'w') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        dest_name = f"{student_id}_day{day}_result.json"
        cmd = ["scp", str(result_file), f"{hermes_user}@{hermes_host}:{results_dir}/{dest_name}"]
        
        print(f"📤 提交默认结果: {dest_name}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ 提交成功！")
            return True
        else:
            print(f"❌ 提交失败: {result.stderr}")
            return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python3 quick_submit.py <student_id> <day> [result_file]")
        print("示例: python3 quick_submit.py xiaochen 3")
        print("示例: python3 quick_submit.py xiaochen 3 day3_result.json")
        sys.exit(1)
    
    student_id = sys.argv[1]
    day = int(sys.argv[2])
    result_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    submit_result(student_id, day, result_file)
