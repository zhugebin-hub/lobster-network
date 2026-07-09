#!/usr/bin/env python3
# 文档归档脚本
import os
import shutil
from datetime import datetime

def archive_documents():
    """归档旧文档"""
    base_dir = "/home/admin/lobster-network"
    archive_dir = os.path.join(base_dir, "archive")
    os.makedirs(archive_dir, exist_ok=True)
    
    # 归档daily_reports
    daily_reports_dir = os.path.join(base_dir, "docs", "daily_reports")
    if os.path.exists(daily_reports_dir):
        archive_month = datetime.now().strftime("%Y-%m")
        archive_month_dir = os.path.join(archive_dir, "daily_reports", archive_month)
        os.makedirs(archive_month_dir, exist_ok=True)
        
        # 移动30天前的文件
        for f in os.listdir(daily_reports_dir):
            filepath = os.path.join(daily_reports_dir, f)
            mtime = os.path.getmtime(filepath)
            if (datetime.now().timestamp() - mtime) > 30 * 86400:
                shutil.move(filepath, os.path.join(archive_month_dir, f))
                print(f"  已归档: {f}")
    
    # 归档training_results
    training_results_dir = os.path.join(base_dir, "docs", "training_results")
    if os.path.exists(training_results_dir):
        archive_month = datetime.now().strftime("%Y-%m")
        archive_month_dir = os.path.join(archive_dir, "training_results", archive_month)
        os.makedirs(archive_month_dir, exist_ok=True)
        
        # 移动90天前的文件
        for f in os.listdir(training_results_dir):
            filepath = os.path.join(training_results_dir, f)
            mtime = os.path.getmtime(filepath)
            if (datetime.now().timestamp() - mtime) > 90 * 86400:
                shutil.move(filepath, os.path.join(archive_month_dir, f))
                print(f"  已归档: {f}")

if __name__ == "__main__":
    archive_documents()
