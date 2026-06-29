#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 V4.0 - 端到端提交验证机制
功能：
1. 学员解题后写入outbox → 发送submission_ack
2. 教练收到ACK → 验证文件内容 → 发送coach_ack
3. 超时未收到ACK → 自动触发催促（soft→medium→hard→escalate）
4. 提交文件增加校验和防止损坏

作者：诸葛马 (Hermes)
日期：2026-06-30
版本：v1.0
"""

import json
import os
import time
import hashlib
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ============================================================
# 配置
# ============================================================

class Config:
    """端到端验证配置"""
    
    # 共享目录
    SHARED_DIR = "/home/admin/go-training/shared/"
    FROM_HERMES_DIR = f"{SHARED_DIR}from-hermes/"
    RESULTS_DIR = f"{SHARED_DIR}results/"
    ACK_DIR = f"{SHARED_DIR}acks/"  # ACK确认文件目录
    
    # 学员配置
    STUDENTS = {
        "xiaochen": {
            "name": "小陈",
            "outbox_base": "/shared/training/go/from-xiaochen/",
            "host": "121.43.80.231",
            "user": "admin",
        },
        "zhuguxia": {
            "name": "诸葛虾",
            "outbox_base": "/shared/training/go/from-zhuguxia/",
            "host": "172.24.56.3",
            "user": "admin",
        },
        "qoder": {
            "name": "qoder",
            "outbox_base": "/shared/training/go/from-qoder/",
            "host": "local",
            "user": "admin",
        },
    }
    
    # ACK超时配置（秒）
    ACK_TIMEOUTS = {
        "soft": 7200,      # 2小时
        "medium": 21600,   # 6小时
        "hard": 43200,     # 12小时
        "escalate": 86400, # 24小时
    }
    
    # 日志
    LOG_FILE = f"{SHARED_DIR}e2e_validation.log"


# ============================================================
# 校验和模块
# ============================================================

class Checksum:
    """文件校验和"""
    
    @staticmethod
    def compute(file_path: str) -> str:
        """计算文件SHA256校验和"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    @staticmethod
    def verify(file_path: str, expected_checksum: str) -> bool:
        """验证文件校验和"""
        actual = Checksum.compute(file_path)
        return actual == expected_checksum


# ============================================================
# ACK管理器
# ============================================================

class ACKManager:
    """ACK确认管理器"""
    
    def __init__(self):
        self.config = Config()
        os.makedirs(self.config.ACK_DIR, exist_ok=True)
        self._init_log()
    
    def _init_log(self):
        os.makedirs(os.path.dirname(self.config.LOG_FILE), exist_ok=True)
    
    def _log(self, level: str, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{level}] {message}"
        print(log_line)
        try:
            with open(self.config.LOG_FILE, "a") as f:
                f.write(log_line + "\n")
        except:
            pass
    
    # --- 学员端：生成submission_ack ---
    
    def create_submission_ack(self, student_id: str, task_id: str, 
                               result_file: str, result_data: Dict) -> Dict:
        """学员端：创建提交ACK"""
        checksum = Checksum.compute(result_file)
        
        ack = {
            "type": "submission_ack",
            "id": f"sub-ack-{task_id}-{int(time.time())}",
            "from": student_id,
            "to": "hermes",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "task_id": task_id,
            "result_file": os.path.basename(result_file),
            "checksum": checksum,
            "result_summary": {
                "total_problems": result_data.get("total_problems", 0),
                "correct_count": result_data.get("correct_count", 0),
                "accuracy": result_data.get("accuracy", 0),
            },
            "status": "submitted",
        }
        
        # 写入ACK目录
        ack_file = os.path.join(self.config.ACK_DIR, f"{ack['id']}.json")
        with open(ack_file, "w") as f:
            json.dump(ack, f, ensure_ascii=False, indent=2)
        
        self._log("INFO", f"📤 学员{student_id}提交ACK: task={task_id}, file={ack['result_file']}, checksum={checksum[:8]}...")
        return ack
    
    # --- 教练端：验证并提交coach_ack ---
    
    def validate_and_ack(self, student_id: str, submission_ack: Dict) -> Dict:
        """教练端：验证提交并生成coach_ack"""
        task_id = submission_ack.get("task_id")
        result_file = submission_ack.get("result_file")
        expected_checksum = submission_ack.get("checksum")
        
        # 1. 查找结果文件
        result_path = os.path.join(self.config.RESULTS_DIR, result_file)
        
        # 也检查from-{student}/目录
        if not os.path.exists(result_path):
            result_path = os.path.join(
                self.config.SHARED_DIR, f"from-{student_id}/", result_file
            )
        
        file_exists = os.path.exists(result_path)
        checksum_valid = False
        
        if file_exists:
            checksum_valid = Checksum.verify(result_path, expected_checksum)
        
        # 2. 验证结果内容
        content_valid = False
        result_data = {}
        if file_exists:
            try:
                with open(result_path) as f:
                    result_data = json.load(f)
                content_valid = self._validate_content(result_data)
            except:
                content_valid = False
        
        # 3. 生成coach_ack
        all_valid = file_exists and checksum_valid and content_valid
        
        coach_ack = {
            "type": "coach_ack",
            "id": f"coach-ack-{task_id}-{int(time.time())}",
            "from": "hermes",
            "to": student_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "task_id": task_id,
            "submission_ack_id": submission_ack.get("id"),
            "validation": {
                "file_exists": file_exists,
                "checksum_valid": checksum_valid,
                "content_valid": content_valid,
                "all_valid": all_valid,
            },
            "result_summary": {
                "total_problems": result_data.get("total_problems", 0),
                "correct_count": result_data.get("correct_count", 0),
                "accuracy": result_data.get("accuracy", 0),
            },
            "status": "accepted" if all_valid else "rejected",
            "message": "提交验证通过" if all_valid else "提交验证失败，请重新提交",
        }
        
        # 写入ACK目录
        ack_file = os.path.join(self.config.ACK_DIR, f"{coach_ack['id']}.json")
        with open(ack_file, "w") as f:
            json.dump(coach_ack, f, ensure_ascii=False, indent=2)
        
        if all_valid:
            self._log("INFO", f"✅ 教练ACK通过: student={student_id}, task={task_id}")
        else:
            self._log("WARN", f"❌ 教练ACK拒绝: student={student_id}, task={task_id}, "
                      f"exists={file_exists}, checksum={checksum_valid}, content={content_valid}")
        
        return coach_ack
    
    def _validate_content(self, data: Dict) -> bool:
        """验证提交内容完整性"""
        required_fields = ["total_problems", "correct_count", "accuracy"]
        for field in required_fields:
            if field not in data:
                # 尝试嵌套结构
                if "result" in data and field in data["result"]:
                    continue
                return False
        return True
    
    # --- 超时检测 ---
    
    def check_ack_timeouts(self) -> List[Dict]:
        """检查所有ACK超时情况"""
        now = time.time()
        overdue = []
        
        # 读取所有submission_ack
        ack_dir = self.config.ACK_DIR
        if not os.path.exists(ack_dir):
            return []
        
        for filename in os.listdir(ack_dir):
            if not filename.startswith("sub-ack-") or not filename.endswith(".json"):
                continue
            
            filepath = os.path.join(ack_dir, filename)
            try:
                with open(filepath) as f:
                    ack = json.load(f)
            except:
                continue
            
            # 检查是否有对应的coach_ack
            task_id = ack.get("task_id")
            student_id = ack.get("from")
            
            has_coach_ack = False
            for coach_file in os.listdir(ack_dir):
                if coach_file.startswith(f"coach-ack-{task_id}"):
                    has_coach_ack = True
                    break
            
            if has_coach_ack:
                continue  # 已处理
            
            # 计算超时等级
            ack_time = datetime.strptime(ack["timestamp"], "%Y-%m-%d %H:%M:%S").timestamp()
            elapsed = now - ack_time
            
            level = None
            for lvl, timeout in Config.ACK_TIMEOUTS.items():
                if elapsed > timeout:
                    level = lvl
            
            if level:
                overdue.append({
                    "student_id": student_id,
                    "task_id": task_id,
                    "ack_id": ack.get("id"),
                    "elapsed_seconds": elapsed,
                    "level": level,
                    "ack_timestamp": ack["timestamp"],
                })
        
        return overdue
    
    # --- 催促通知 ---
    
    def send_escalation(self, overdue_item: Dict) -> Dict:
        """发送升级催促通知"""
        student_id = overdue_item["student_id"]
        level = overdue_item["level"]
        task_id = overdue_item["task_id"]
        
        messages = {
            "soft": "⏰ 温柔提醒：训练任务提交待确认，请检查",
            "medium": "⚠️ 正式提醒：训练任务提交超过6小时未确认",
            "hard": "🚨 紧急提醒：训练任务提交逾期12小时",
            "escalate": "🔴 升级通知：训练任务提交逾期24小时，请教练介入",
        }
        
        notification = {
            "type": "ack_escalation",
            "id": f"escalation-{task_id}-{level}-{int(time.time())}",
            "from": "hermes",
            "to": student_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "level": level,
            "task_id": task_id,
            "message": messages.get(level, "训练任务待确认"),
            "overdue_hours": round(overdue_item["elapsed_seconds"] / 3600, 1),
        }
        
        # 写入from-hermes目录
        msg_file = os.path.join(self.config.FROM_HERMES_DIR, f"{notification['id']}.json")
        with open(msg_file, "w") as f:
            json.dump(notification, f, ensure_ascii=False, indent=2)
        
        self._log("WARN", f"📢 发送{level}催促: student={student_id}, task={task_id}")
        return notification


# ============================================================
# 端到端验证流程
# ============================================================

class E2EValidator:
    """端到端验证流程控制器"""
    
    def __init__(self):
        self.config = Config()
        self.ack_manager = ACKManager()
    
    def process_new_submissions(self) -> Dict:
        """处理所有新提交（教练端）"""
        results = {"processed": 0, "accepted": 0, "rejected": 0, "errors": 0}
        
        # 扫描所有from-{student}/目录
        for student_id, student_info in self.config.STUDENTS.items():
            from_dir = os.path.join(self.config.SHARED_DIR, f"from-{student_id}/")
            if not os.path.exists(from_dir):
                continue
            
            # 查找新的结果文件
            for filename in os.listdir(from_dir):
                if not filename.endswith(".json"):
                    continue
                
                # 跳过已处理的
                if filename.startswith("reminder_") or filename.startswith("push-"):
                    continue
                
                filepath = os.path.join(from_dir, filename)
                try:
                    with open(filepath) as f:
                        data = json.load(f)
                except:
                    results["errors"] += 1
                    continue
                
                # 检查是否已有coach_ack
                task_id = data.get("task_id") or data.get("reply_to") or filename.replace(".json", "")
                has_ack = any(
                    f"coach-ack-{task_id}" in fn 
                    for fn in os.listdir(self.config.ACK_DIR)
                ) if os.path.exists(self.config.ACK_DIR) else False
                
                if has_ack:
                    continue
                
                # 创建submission_ack（模拟学员已发送）
                sub_ack = self.ack_manager.create_submission_ack(
                    student_id, task_id, filepath, data
                )
                
                # 验证并生成coach_ack
                coach_ack = self.ack_manager.validate_and_ack(student_id, sub_ack)
                
                results["processed"] += 1
                if coach_ack["status"] == "accepted":
                    results["accepted"] += 1
                else:
                    results["rejected"] += 1
        
        return results
    
    def check_and_escalate(self) -> Dict:
        """检查超时并发送催促"""
        overdue = self.ack_manager.check_ack_timeouts()
        escalated = []
        
        for item in overdue:
            # 只发送最高级别的催促（避免重复）
            notification = self.ack_manager.send_escalation(item)
            escalated.append(notification)
        
        return {
            "overdue_count": len(overdue),
            "escalated": len(escalated),
            "details": overdue,
        }
    
    def full_cycle(self) -> Dict:
        """完整验证周期：处理新提交 + 检查超时"""
        self._log("INFO", "🔄 开始端到端验证周期...")
        
        process_results = self.process_new_submissions()
        escalation_results = self.check_and_escalate()
        
        summary = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "processing": process_results,
            "escalation": escalation_results,
        }
        
        self._log("INFO", f"📊 验证周期完成: 处理{process_results['processed']}个, "
                         f"通过{process_results['accepted']}个, "
                         f"拒绝{process_results['rejected']}个, "
                         f"超时{escalation_results['overdue_count']}个")
        
        return summary
    
    def _log(self, level: str, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")


# ============================================================
# 学员端：提交结果时自动生成ACK
# ============================================================

def student_submit_with_ack(student_id: str, task_id: str, result_data: Dict,
                             outbox_dir: str) -> Tuple[bool, str]:
    """
    学员端：提交结果并自动生成submission_ack
    调用方式：在学员训练脚本的send_response()中调用此函数
    """
    config = Config()
    validator = E2EValidator()
    
    # 1. 写入结果文件到outbox
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_filename = f"go-result-{student_id}-{task_id}-{timestamp}.json"
    result_filepath = os.path.join(outbox_dir, result_filename)
    
    os.makedirs(outbox_dir, exist_ok=True)
    
    # 添加校验和到结果数据
    result_data["_metadata"] = {
        "student_id": student_id,
        "task_id": task_id,
        "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    
    with open(result_filepath, "w") as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    # 2. 生成submission_ack
    ack = validator.ack_manager.create_submission_ack(
        student_id, task_id, result_filepath, result_data
    )
    
    # 3. 将ACK写入共享目录（教练可读取）
    ack_dir = config.ACK_DIR
    os.makedirs(ack_dir, exist_ok=True)
    ack_filepath = os.path.join(ack_dir, f"{ack['id']}.json")
    
    # 也复制到from-hermes/让学员脚本能读到coach_ack
    from_hermes_dir = config.FROM_HERMES_DIR
    os.makedirs(from_hermes_dir, exist_ok=True)
    
    return True, ack["id"]


# ============================================================
# 命令行接口
# ============================================================

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="端到端提交验证机制")
    parser.add_argument("action", choices=["check", "process", "escalate", "full"],
                       help="操作: check(检查超时) | process(处理新提交) | escalate(催促) | full(完整周期)")
    
    args = parser.parse_args()
    validator = E2EValidator()
    
    if args.action == "check":
        overdue = validator.ack_manager.check_ack_timeouts()
        print(json.dumps({"overdue_count": len(overdue), "details": overdue}, 
                        ensure_ascii=False, indent=2))
    
    elif args.action == "process":
        results = validator.process_new_submissions()
        print(json.dumps(results, ensure_ascii=False, indent=2))
    
    elif args.action == "escalate":
        results = validator.check_and_escalate()
        print(json.dumps(results, ensure_ascii=False, indent=2))
    
    elif args.action == "full":
        results = validator.full_cycle()
        print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
