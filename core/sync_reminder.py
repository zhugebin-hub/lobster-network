#!/usr/bin/env python3
"""
小龙虾网络V3.0 - 学员同步催促系统
功能: 自动同步、催促提交、验证结果、升级提醒
作者: 诸葛马 (AI教练)
版本: 1.0
"""

import json
import os
import sys
import time
import subprocess
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 活跃节点配置
ACTIVE_NODES = ["xiaochen", "zhuguxia", "qoder", "xiaowei"]

# 训练目录配置
TRAINING_DIR = "/home/admin/go-training/shared/"

# from-目录前缀
FROM_PREFIX = "from-"
# ============================================================
# 配置
# ============================================================

class Config:
    """系统配置"""
    
    # 教练服务器
    COACH_HOST = "47.93.6.57"
    COACH_USER = "admin"
    COACH_SSH_KEY = "/home/admin/.ssh/id_rsa_hermes"
    
    # 学员信息
    STUDENTS = {
        "xiaochen": {
            "name": "小陈",
            "host": "121.43.80.231",
            "type": "稳健型",
            "outbox_dir": "/home/admin/go-training/shared/queue/xiaochen/outbox/",
            "from_dir": "/home/admin/go-training/shared/from-xiaochen/",
            "training_dir": "/home/admin/go-training/shared/",
            "wechat_id": "xiaochen_wechat"
        },
        "zhuguxia": {
            "name": "诸葛虾",
            "host": "60.205.139.51",
            "type": "加速型",
            "outbox_dir": "/home/admin/go-training/shared/queue/zhuguxia/outbox/",
            "from_dir": "/home/admin/go-training/shared/from-zhuguxia/",
            "training_dir": "/home/admin/go-training/shared/",
            "wechat_id": "zhuguxia_wechat"
        },
        "qoder": {
            "name": "qoder",
            "host": "local",  # Mac本地，通过GitHub
            "type": "实战型",
            "github_repo": "https://github.com/zhugebin-hub/lobster-network",
            "local_dir": "/Users/admin/lobster-network",
            "wechat_id": "qoder_wechat"
        },
        "xiaowei": {
            "name": "小薇",
            "host": "local",  # 无服务器，通过GitHub
            "type": "基础型",
            "github_repo": "https://github.com/zhugebin-hub/lobster-network",
            "wechat_id": "xiaowei_wechat"
        }
    }
    
    # 催促策略
    REMINDER_INTERVALS = [
        {"hours": 2, "level": "soft", "message": "温柔提醒"},
        {"hours": 6, "level": "medium", "message": "正式提醒"},
        {"hours": 12, "level": "hard", "message": "紧急提醒"},
        {"hours": 24, "level": "escalate", "message": "升级提醒(通知用户)"}
    ]
    
    # 共享目录
    SHARED_DIR = "/home/admin/go-training/shared/"
    FROM_HERMES_DIR = f"{SHARED_DIR}from-hermes/"
    RESULTS_DIR = f"{SHARED_DIR}results/"
    
    # 日志
    LOG_FILE = f"{SHARED_DIR}sync_reminder.log"


# ============================================================
# SSH 通信模块
# ============================================================

class SSHClient:
    """SSH客户端"""
    
    def __init__(self, host: str, user: str = "admin", key: str = Config.COACH_SSH_KEY):
        self.host = host
        self.user = user
        self.key = key
    
    def run(self, command: str, timeout: int = 30) -> Tuple[bool, str]:
        """执行SSH命令"""
        ssh_cmd = [
            "ssh", "-i", self.key,
            "-o", "ConnectTimeout=10",
            "-o", "StrictHostKeyChecking=no",
            f"{self.user}@{self.host}",
            command
        ]
        try:
            result = subprocess.run(
                ssh_cmd,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                universal_newlines=True,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout or result.stderr
        except subprocess.TimeoutExpired:
            return False, "SSH连接超时"
        except Exception as e:
            return False, str(e)
    
    def scp_upload(self, local_path: str, remote_path: str) -> Tuple[bool, str]:
        """SCP上传"""
        scp_cmd = [
            "scp", "-i", self.key,
            "-o", "StrictHostKeyChecking=no",
            local_path,
            f"{self.user}@{self.host}:{remote_path}"
        ]
        try:
            result = subprocess.run(scp_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=30)
            return result.returncode == 0, result.stdout or result.stderr
        except Exception as e:
            return False, str(e)
    
    def scp_download(self, remote_path: str, local_path: str) -> Tuple[bool, str]:
        """SCP下载"""
        scp_cmd = [
            "scp", "-i", self.key,
            "-o", "StrictHostKeyChecking=no",
            f"{self.user}@{self.host}:{remote_path}",
            local_path
        ]
        try:
            result = subprocess.run(scp_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=30)
            return result.returncode == 0, result.stdout or result.stderr
        except Exception as e:
            return False, str(e)


# ============================================================
# 同步引擎
# ============================================================

class SyncEngine:
    """同步引擎 - 自动同步学员提交"""
    
    def __init__(self):
        self.config = Config()
        self.logger = Logger()
    
    def sync_all_students(self) -> Dict:
        """同步所有学员"""
        results = {}
        for student_id, student_info in self.config.STUDENTS.items():
            self.logger.info(f"🔄 同步学员: {student_info['name']} ({student_id})")
            
            if student_info["host"] == "local" and "github" in str(student_info.get("github_repo", "")):
                results[student_id] = self.sync_github_student(student_id, student_info)
            else:
                results[student_id] = self.sync_ssh_student(student_id, student_info)
        
        return results
    
    def sync_ssh_student(self, student_id: str, student_info: Dict) -> Dict:
        """SSH同步学员"""
        host = student_info["host"]
        client = SSHClient(host)
        
        # 1. 检查outbox目录
        success, output = client.run(f"ls -la {student_info['outbox_dir']} 2>/dev/null || echo 'DIR_NOT_FOUND'")
        
        if "DIR_NOT_FOUND" in output:
            # 创建目录
            client.run(f"mkdir -p {student_info['outbox_dir']}")
            client.run(f"mkdir -p {student_info['from_dir']}")
            return {"status": "dir_created", "message": "目录已创建"}
        
        # 2. 列出outbox文件
        success, files = client.run(f"find {student_info['outbox_dir']} -name '*.json' -type f")
        
        if not files.strip():
            return {"status": "empty", "message": "outbox无新文件"}
        
        # 3. 同步文件到from-{name}/
        synced = []
        for file_path in files.strip().split("\n"):
            if not file_path:
                continue
            filename = os.path.basename(file_path)
            dest_path = f"{student_info['from_dir']}{filename}"
            
            # 下载文件
            local_temp = f"/tmp/sync_{student_id}_{filename}"
            success, _ = client.scp_download(file_path, local_temp)
            
            if success:
                # 上传到教练服务器
                coach_dest = f"{self.config.RESULTS_DIR}{student_id}_{filename}"
                coach_client = SSHClient(self.config.COACH_HOST)
                coach_client.scp_upload(local_temp, coach_dest)
                synced.append(filename)
                
                # 清理临时文件
                os.remove(local_temp)
        
        return {
            "status": "synced",
            "files": synced,
            "count": len(synced)
        }
    
    def sync_github_student(self, student_id: str, student_info: Dict) -> Dict:
        """GitHub同步学员"""
        # 使用本地仓库检查
        local_repo = "/home/admin/lobster-network"
        if not os.path.exists(f"{local_repo}/.git"):
            return {"status": "no_repo", "message": "本地仓库不存在"}
        
        try:
            # 检查最近提交
            result = subprocess.run(
                ["git", "log", "--oneline", "-5", "--since=24 hours"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                universal_newlines=True,
                timeout=10,
                cwd=local_repo
            )
            
            if result.returncode == 0:
                commits = result.stdout.strip().split("\n")
                return {
                    "status": "checked",
                    "message": f"最近24小时有{len(commits)}次提交",
                    "recent_commits": commits
                }
            else:
                return {
                    "status": "error",
                    "message": "无法读取仓库"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }


# ============================================================
# 催促引擎
# ============================================================

class ReminderEngine:
    """催促引擎 - 多通道催促提交"""
    
    def __init__(self):
        self.config = Config()
        self.logger = Logger()
    
    def check_submissions(self) -> Dict:
        """检查所有学员提交状态"""
        results = {}
        current_day = self.get_current_day()
        
        for student_id, student_info in self.config.STUDENTS.items():
            submitted = self.check_student_submission(student_id, current_day)
            results[student_id] = {
                "name": student_info["name"],
                "submitted": submitted,
                "day": current_day,
                "needs_reminder": not submitted
            }
        
        return results
    
    def get_current_day(self) -> int:
        """获取当前训练天数"""
        # 从任务文件推断
        task_files = list(Path(self.config.FROM_HERMES_DIR).glob("day*_*.json"))
        if not task_files:
            return 1
        
        # 找到最大的day数
        max_day = 0
        for f in task_files:
            if "day" in f.name:
                try:
                    day = int(f.name.split("day")[1].split("_")[0])
                    max_day = max(max_day, day)
                except:
                    pass
        
        return max_day
    
    def check_student_submission(self, student_id: str, day: int) -> bool:
        """检查学员是否已提交"""
        results_dir = Path(self.config.RESULTS_DIR)
        
        # 检查提交文件
        patterns = [
            f"{student_id}_day{day}_*.json",
            f"{student_id}_*w*d*.json",
            f"go-result-{student_id}*.json"
        ]
        
        for pattern in patterns:
            files = list(results_dir.glob(pattern))
            if files:
                return True
        
        return False
    
    def send_reminder(self, student_id: str, level: str = "soft") -> bool:
        """发送催促提醒"""
        student_info = self.config.STUDENTS.get(student_id)
        if not student_info:
            return False
        
        self.logger.info(f"📢 发送{level}提醒: {student_info['name']}")
        
        if level == "soft":
            return self.send_soft_reminder(student_id, student_info)
        elif level == "medium":
            return self.send_medium_reminder(student_id, student_info)
        elif level == "hard":
            return self.send_hard_reminder(student_id, student_info)
        elif level == "escalate":
            return self.send_escalate_reminder(student_id, student_info)
        
        return False
    
    def send_soft_reminder(self, student_id: str, student_info: Dict) -> bool:
        """温柔提醒 - SSH消息"""
        if student_info["host"] == "local":
            return self.send_github_reminder(student_id, student_info)
        
        client = SSHClient(student_info["host"])
        message = {
            "type": "reminder",
            "level": "soft",
            "message": "⏰ 温柔提醒：今日训练任务待完成，加油！",
            "task": self.get_current_task(student_id),
            "deadline": "22:00",
            "timestamp": datetime.now().isoformat()
        }
        
        # 写入共享目录
        msg_file = f"{self.config.FROM_HERMES_DIR}/reminder_{student_id}_{int(time.time())}.json"
        with open(msg_file, "w") as f:
            json.dump(message, f, ensure_ascii=False, indent=2)
        
        return True
    
    def send_medium_reminder(self, student_id: str, student_info: Dict) -> bool:
        """正式提醒 - SSH + 共享目录"""
        if student_info["host"] == "local":
            return self.send_github_reminder(student_id, student_info)
        
        client = SSHClient(student_info["host"])
        message = {
            "type": "reminder",
            "level": "medium",
            "message": "⚠️ 正式提醒：训练任务即将截止，请尽快提交",
            "task": self.get_current_task(student_id),
            "deadline": "22:00",
            "timestamp": datetime.now().isoformat()
        }
        
        msg_file = f"{self.config.FROM_HERMES_DIR}/reminder_{student_id}_{int(time.time())}.json"
        with open(msg_file, "w") as f:
            json.dump(message, f, ensure_ascii=False, indent=2)
        
        # SSH通知
        client.run(f"echo '{json.dumps(message, ensure_ascii=False)}' > {student_info['outbox_dir']}/reminder_from_coach.json")
        
        return True
    
    def send_hard_reminder(self, student_id: str, student_info: Dict) -> bool:
        """紧急提醒 - 多通道"""
        # SSH + 共享目录 + 微信(通过用户)
        self.send_medium_reminder(student_id, student_info)
        
        message = {
            "type": "reminder",
            "level": "hard",
            "message": "🚨 紧急提醒：训练任务已逾期，请立即提交！",
            "task": self.get_current_task(student_id),
            "overdue_hours": 2,
            "timestamp": datetime.now().isoformat()
        }
        
        msg_file = f"{self.config.FROM_HERMES_DIR}/urgent_{student_id}_{int(time.time())}.json"
        with open(msg_file, "w") as f:
            json.dump(message, f, ensure_ascii=False, indent=2)
        
        return True
    
    def send_escalate_reminder(self, student_id: str, student_info: Dict) -> bool:
        """升级提醒 - 通知用户"""
        self.send_hard_reminder(student_id, student_info)
        
        # 通过微信通知用户
        message = f"🚨 学员 {student_info['name']} 训练任务逾期24小时未提交\n"
        message += f"任务: {self.get_current_task(student_id)}\n"
        message += f"请协调学员尽快完成"
        
        # 写入通知文件
        notify_file = f"{self.config.RESULTS_DIR}/escalate_{student_id}_{int(time.time())}.json"
        with open(notify_file, "w") as f:
            json.dump({"message": message, "student": student_id}, f, ensure_ascii=False, indent=2)
        
        return True
    
    def send_github_reminder(self, student_id: str, student_info: Dict) -> bool:
        """GitHub提醒"""
        message = {
            "type": "reminder",
            "level": "soft",
            "message": "⏰ GitHub提醒：训练任务待完成",
            "task": self.get_current_task(student_id),
            "timestamp": datetime.now().isoformat()
        }
        
        msg_file = f"{self.config.FROM_HERMES_DIR}/github_reminder_{student_id}_{int(time.time())}.json"
        with open(msg_file, "w") as f:
            json.dump(message, f, ensure_ascii=False, indent=2)
        
        return True
    
    def get_current_task(self, student_id: str) -> str:
        """获取当前任务"""
        task_file = f"{self.config.FROM_HERMES_DIR}/day3_{student_id}.json"
        if os.path.exists(task_file):
            with open(task_file) as f:
                task = json.load(f)
                return f"{task.get('problems', 'N/A')}题 + {task.get('games', 'N/A')}局"
        return "Day3训练任务"


# ============================================================
# 验证引擎
# ============================================================

class ValidationEngine:
    """验证引擎 - 检查提交完整性"""
    
    def __init__(self):
        self.config = Config()
        self.logger = Logger()
    
    def validate_submission(self, student_id: str, day: int) -> Dict:
        """验证提交完整性"""
        results_dir = Path(self.config.RESULTS_DIR)
        
        # 查找提交文件
        files = list(results_dir.glob(f"{student_id}_day{day}_*.json"))
        if not files:
            files = list(results_dir.glob(f"go-result-{student_id}*.json"))
        
        if not files:
            return {
                "status": "missing",
                "message": "未找到提交文件",
                "completeness": 0
            }
        
        # 验证内容
        for file in files:
            try:
                with open(file) as f:
                    data = json.load(f)
                
                validation = self.validate_content(data, student_id, day)
                return validation
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"文件解析失败: {str(e)}",
                    "completeness": 0
                }
        
        return {"status": "unknown", "message": "无法验证", "completeness": 0}
    
    def validate_content(self, data: Dict, student_id: str, day: int) -> Dict:
        """验证提交内容"""
        required_fields = ["problems", "games", "reflection"]
        missing = [f for f in required_fields if f not in data]
        
        problems = data.get("problems", [])
        games = data.get("games", [])
        
        # 计算完整性
        completeness = 100
        if missing:
            completeness -= len(missing) * 20
        
        # 检查题目数量
        expected_problems = 150 if day == 3 else 120
        problem_ratio = min(len(problems) / expected_problems, 1.0) * 40
        
        # 检查对局数量
        expected_games = 12 if day == 3 else 10
        game_ratio = min(len(games) / expected_games, 1.0) * 30
        
        completeness = int(problem_ratio + game_ratio + (30 if not missing else 0))
        
        return {
            "status": "validated",
            "completeness": completeness,
            "problems_count": len(problems),
            "games_count": len(games),
            "missing_fields": missing,
            "accuracy": self.calculate_accuracy(problems)
        }
    
    def calculate_accuracy(self, problems: List[Dict]) -> float:
        """计算准确率"""
        if not problems:
            return 0.0
        correct = sum(1 for p in problems if p.get("is_correct", False))
        return round(correct / len(problems) * 100, 1)


# ============================================================
# 日志模块
# ============================================================

class Logger:
    """日志模块"""
    
    def __init__(self, log_file: str = Config.LOG_FILE):
        self.log_file = log_file
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    def info(self, message: str):
        self._log("INFO", message)
    
    def warn(self, message: str):
        self._log("WARN", message)
    
    def error(self, message: str):
        self._log("ERROR", message)
    
    def _log(self, level: str, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{level}] {message}\n"
        
        print(log_line.strip())
        
        with open(self.log_file, "a") as f:
            f.write(log_line)


# ============================================================
# 主调度器
# ============================================================

class SyncReminderScheduler:
    """同步催促调度器"""
    
    def __init__(self):
        self.sync_engine = SyncEngine()
        self.reminder_engine = ReminderEngine()
        self.validation_engine = ValidationEngine()
        self.logger = Logger()
    
    def run_cycle(self) -> Dict:
        """运行一个完整周期"""
        self.logger.info("=" * 60)
        self.logger.info("🔄 开始同步催促周期")
        self.logger.info("=" * 60)
        
        # 1. 同步所有学员
        self.logger.info("📥 步骤1: 同步学员提交")
        sync_results = self.sync_engine.sync_all_students()
        
        # 2. 检查提交状态
        self.logger.info("📊 步骤2: 检查提交状态")
        submission_status = self.reminder_engine.check_submissions()
        
        # 3. 发送催促提醒
        self.logger.info("📢 步骤3: 发送催促提醒")
        reminder_results = {}
        for student_id, status in submission_status.items():
            if status["needs_reminder"]:
                # 根据逾期时间决定提醒级别
                level = self.determine_reminder_level(student_id)
                success = self.reminder_engine.send_reminder(student_id, level)
                reminder_results[student_id] = {
                    "level": level,
                    "success": success
                }
        
        # 4. 验证已提交结果
        self.logger.info("✅ 步骤4: 验证提交结果")
        validation_results = {}
        for student_id, status in submission_status.items():
            if not status["needs_reminder"]:
                day = status["day"]
                validation = self.validation_engine.validate_submission(student_id, day)
                validation_results[student_id] = validation
        
        # 5. 生成报告
        report = {
            "timestamp": datetime.now().isoformat(),
            "sync_results": sync_results,
            "submission_status": submission_status,
            "reminder_results": reminder_results,
            "validation_results": validation_results
        }
        
        # 保存报告
        report_file = f"{Config.RESULTS_DIR}/sync_reminder_report_{int(time.time())}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"📄 报告已保存: {report_file}")
        self.logger.info("=" * 60)
        
        return report
    
    def determine_reminder_level(self, student_id: str) -> str:
        """根据逾期时间决定提醒级别"""
        # 简化版本：默认soft
        # 实际应根据最后提交时间计算
        return "soft"


# ============================================================
# 命令行接口
# ============================================================

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="小龙虾网络V3.0 - 学员同步催促系统")
    parser.add_argument("action", choices=["sync", "remind", "validate", "run"],
                       help="操作: sync(同步) | remind(催促) | validate(验证) | run(完整周期)")
    parser.add_argument("--student", type=str, help="指定学员ID")
    parser.add_argument("--level", type=str, default="soft",
                       choices=["soft", "medium", "hard", "escalate"],
                       help="提醒级别")
    
    args = parser.parse_args()
    
    scheduler = SyncReminderScheduler()
    
    if args.action == "run":
        # 运行完整周期
        report = scheduler.run_cycle()
        print(json.dumps(report, ensure_ascii=False, indent=2))
    
    elif args.action == "sync":
        # 仅同步
        if args.student:
            student_info = Config.STUDENTS.get(args.student)
            if student_info:
                if student_info["host"] == "local":
                    result = scheduler.sync_engine.sync_github_student(args.student, student_info)
                else:
                    result = scheduler.sync_engine.sync_ssh_student(args.student, student_info)
                print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            results = scheduler.sync_engine.sync_all_students()
            print(json.dumps(results, ensure_ascii=False, indent=2))
    
    elif args.action == "remind":
        # 仅催促
        if args.student:
            success = scheduler.reminder_engine.send_reminder(args.student, args.level)
            print(f"提醒发送: {'✅ 成功' if success else '❌ 失败'}")
        else:
            status = scheduler.reminder_engine.check_submissions()
            for student_id, s in status.items():
                if s["needs_reminder"]:
                    scheduler.reminder_engine.send_reminder(student_id, args.level)
    
    elif args.action == "validate":
        # 仅验证
        if args.student:
            day = scheduler.reminder_engine.get_current_day()
            result = scheduler.validation_engine.validate_submission(args.student, day)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            day = scheduler.reminder_engine.get_current_day()
            for student_id in Config.STUDENTS:
                result = scheduler.validation_engine.validate_submission(student_id, day)
                print(f"{student_id}: {result['status']} (完整性: {result.get('completeness', 0)}%)")


if __name__ == "__main__":
    main()
