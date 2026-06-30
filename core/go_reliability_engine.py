#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 - 围棋学习可靠性引擎
功能：
1. 健康检查（NFS/SSH/进程/磁盘）
2. 自动恢复（进程重启/NFS重挂载/SSH密钥配置）
3. 重试机制（指数退避+最大重试）
4. 超时控制（分级超时+降级策略）
5. 降级策略（本地缓存→SSH传输→GitHub同步）
6. 稳定性监控（指标采集+告警）

作者：诸葛马 (Hermes)
日期：2026-06-30
版本：v1.0
"""

import json
import os
import time
import signal
import subprocess
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Callable
from pathlib import Path
from enum import Enum
import hashlib

# ============================================================
# 配置
# ============================================================

class Config:
    """可靠性引擎配置"""
    
    # 学员配置
    STUDENTS = {
        "xiaochen": {
            "name": "小陈",
            "host": "121.43.80.231",
            "user": "admin",
            "ssh_key": "/home/admin/.ssh/id_rsa_hermes",
        },
        "zhuguxia": {
            "name": "诸葛虾",
            "host": "172.24.56.3",
            "user": "admin",
            "ssh_key": "/home/admin/.ssh/id_rsa_hermes",
        },
        "qoder": {
            "name": "qoder",
            "host": "local",
            "user": "admin",
            "ssh_key": None,
        },
    }
    
    # 共享目录
    SHARED_DIR = "/home/admin/go-training/shared/"
    RESULTS_DIR = f"{SHARED_DIR}results/"
    FROM_HERMES_DIR = f"{SHARED_DIR}from-hermes/"
    ACK_DIR = f"{SHARED_DIR}acks/"
    SESSIONS_DIR = f"{SHARED_DIR}sessions/"
    MEMORY_DIR = f"{SHARED_DIR}memory/"
    WORKSPACE_DIR = f"{SHARED_DIR}workspace/"
    STATE_DIR = f"{SHARED_DIR}reliability/"
    
    # 重试配置
    RETRY_CONFIG = {
        "max_retries": 3,
        "base_delay": 2,       # 基础延迟（秒）
        "max_delay": 60,       # 最大延迟（秒）
        "backoff_factor": 2,   # 退避因子
    }
    
    # 超时配置
    TIMEOUT_CONFIG = {
        "ssh_connect": 10,      # SSH连接超时
        "ssh_command": 30,      # SSH命令超时
        "nfs_mount": 15,        # NFS挂载超时
        "file_write": 5,        # 文件写入超时
        "process_start": 10,    # 进程启动超时
    }
    
    # 降级策略
    DEGRADE_STRATEGIES = [
        "local_cache",      # 本地缓存
        "ssh_transfer",     # SSH传输
        "github_sync",      # GitHub同步
        "manual_fallback",  # 手动回退
    ]
    
    # 告警阈值
    ALERT_THRESHOLDS = {
        "disk_usage_percent": 85,
        "nfs_failure_count": 3,
        "ssh_failure_count": 5,
        "process_down_minutes": 10,
        "submission_gap_hours": 24,
        "error_rate_percent": 20,
    }
    
    # 健康检查间隔
    HEALTH_CHECK_INTERVAL = 60  # 每分钟检查一次


# ============================================================
# 健康状态枚举
# ============================================================

class HealthStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    DOWN = "down"


# ============================================================
# 重试机制（指数退避）
# ============================================================

class RetryManager:
    """重试管理器：指数退避+最大重试"""
    
    def __init__(self, config: Dict = None):
        self.config = config or Config.RETRY_CONFIG
    
    def execute_with_retry(self, func: Callable, *args, **kwargs) -> Tuple[bool, Any]:
        """
        带重试执行函数
        返回: (success, result_or_error)
        """
        max_retries = self.config["max_retries"]
        base_delay = self.config["base_delay"]
        max_delay = self.config["max_delay"]
        backoff = self.config["backoff_factor"]
        
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                result = func(*args, **kwargs)
                return True, result
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    delay = min(base_delay * (backoff ** attempt), max_delay)
                    print(f"  ⚠️ 第{attempt+1}次失败: {e}, {delay}秒后重试...")
                    time.sleep(delay)
        
        return False, last_error


# ============================================================
# 超时控制
# ============================================================

class TimeoutController:
    """超时控制器：分级超时+超时处理"""
    
    def __init__(self, config: Dict = None):
        self.config = config or Config.TIMEOUT_CONFIG
    
    def execute_with_timeout(self, func: Callable, timeout_key: str, 
                              *args, **kwargs) -> Tuple[bool, Any]:
        """
        带超时执行函数
        返回: (success, result_or_timeout_error)
        """
        timeout = self.config.get(timeout_key, 30)
        
        import threading
        result_container = [None, None]  # [result, error]
        completed = threading.Event()
        
        def target():
            try:
                result_container[0] = func(*args, **kwargs)
            except Exception as e:
                result_container[1] = e
            finally:
                completed.set()
        
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        
        if completed.wait(timeout=timeout):
            if result_container[1]:
                return False, result_container[1]
            return True, result_container[0]
        else:
            return False, TimeoutError(f"操作超时 ({timeout}秒): {timeout_key}")


# ============================================================
# 健康检查器
# ============================================================

class HealthChecker:
    """健康检查器：检查系统各组件状态"""
    
    def __init__(self):
        self.config = Config()
        self.retry = RetryManager()
        self.timeout_ctrl = TimeoutController()
    
    def check_all(self) -> Dict:
        """检查所有组件"""
        results = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "nfs": self.check_nfs(),
            "ssh": self.check_ssh(),
            "processes": self.check_processes(),
            "disk": self.check_disk(),
            "data_integrity": self.check_data_integrity(),
            "overall": HealthStatus.HEALTHY,
        }
        
        # 计算整体状态
        statuses = [v.get("status", HealthStatus.HEALTHY) 
                   for v in results.values() if isinstance(v, dict) and "status" in v]
        
        if HealthStatus.DOWN in statuses:
            results["overall"] = HealthStatus.DOWN
        elif HealthStatus.CRITICAL in statuses:
            results["overall"] = HealthStatus.CRITICAL
        elif HealthStatus.WARNING in statuses:
            results["overall"] = HealthStatus.WARNING
        
        return results
    
    def check_nfs(self) -> Dict:
        """检查NFS状态"""
        issues = []
        status = HealthStatus.HEALTHY
        
        # 检查NFS服务
        try:
            result = subprocess.run(
                ["systemctl", "is-active", "nfs-server"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                universal_newlines=True, timeout=5
            )
            if result.stdout.strip() != "active":
                issues.append("NFS服务未运行")
                status = HealthStatus.CRITICAL
        except Exception as e:
            issues.append(f"NFS服务检查失败: {e}")
            status = HealthStatus.CRITICAL
        
        # 检查端口监听
        try:
            result = subprocess.run(
                ["ss", "-tlnp"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                universal_newlines=True, timeout=5
            )
            if "2049" not in result.stdout:
                issues.append("NFS端口2049未监听")
                status = HealthStatus.CRITICAL
        except Exception as e:
            issues.append(f"端口检查失败: {e}")
        
        # 检查挂载
        try:
            result = subprocess.run(
                ["mount"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                universal_newlines=True, timeout=5
            )
            if "/shared" not in result.stdout:
                issues.append("/shared未挂载")
                status = HealthStatus.WARNING
        except Exception as e:
            issues.append(f"挂载检查失败: {e}")
        
        # 检查目录可写
        try:
            test_file = os.path.join(self.config.SHARED_DIR, ".health_check")
            with open(test_file, "w") as f:
                f.write("ok")
            os.remove(test_file)
        except Exception as e:
            issues.append(f"共享目录不可写: {e}")
            status = HealthStatus.CRITICAL
        
        return {
            "status": status,
            "issues": issues,
            "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    
    def check_ssh(self) -> Dict:
        """检查SSH连接"""
        issues = []
        warnings = []
        status = HealthStatus.HEALTHY
        
        for student_id, student_info in self.config.STUDENTS.items():
            if student_info["host"] == "local":
                continue
            
            try:
                result = subprocess.run(
                    ["ssh", "-o", "ConnectTimeout=3", 
                     "-o", "StrictHostKeyChecking=no",
                     "-i", student_info["ssh_key"],
                     f"{student_info['user']}@{student_info['host']}",
                     "echo OK"],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    universal_newlines=True, timeout=5
                )
                if result.returncode != 0 or "OK" not in result.stdout:
                    issues.append(f"{student_info['name']}({student_info['host']}) SSH连接失败")
                    status = HealthStatus.WARNING
            except subprocess.TimeoutExpired:
                warnings.append(f"{student_info['name']} SSH连接超时")
            except Exception as e:
                warnings.append(f"{student_info['name']} SSH检查异常: {e}")
        
        return {
            "status": status,
            "issues": issues,
            "warnings": warnings,
            "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    
    def check_processes(self) -> Dict:
        """检查后台进程"""
        issues = []
        status = HealthStatus.HEALTHY
        
        required_processes = [
            "sync_reminder",
            "time_protection",
            "message_poller",
        ]
        
        try:
            result = subprocess.run(
                ["ps", "aux"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                universal_newlines=True, timeout=5
            )
            ps_output = result.stdout
            
            for proc in required_processes:
                if proc not in ps_output:
                    issues.append(f"{proc} 未运行")
                    status = HealthStatus.CRITICAL
        except Exception as e:
            issues.append(f"进程检查失败: {e}")
            status = HealthStatus.WARNING
        
        return {
            "status": status,
            "issues": issues,
            "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    
    def check_disk(self) -> Dict:
        """检查磁盘空间"""
        issues = []
        status = HealthStatus.HEALTHY
        
        try:
            result = subprocess.run(
                ["df", "-h", "/"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                universal_newlines=True, timeout=5
            )
            lines = result.stdout.strip().split("\n")
            if len(lines) > 1:
                parts = lines[1].split()
                usage_percent = int(parts[4].replace("%", ""))
                
                if usage_percent >= self.config.ALERT_THRESHOLDS["disk_usage_percent"]:
                    issues.append(f"磁盘使用率{usage_percent}%超过阈值")
                    status = HealthStatus.WARNING
                
                return {
                    "status": status,
                    "usage_percent": usage_percent,
                    "issues": issues,
                    "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
        except Exception as e:
            issues.append(f"磁盘检查失败: {e}")
        
        return {
            "status": HealthStatus.WARNING,
            "issues": issues,
            "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    
    def check_data_integrity(self) -> Dict:
        """检查数据完整性"""
        issues = []
        warnings = []
        status = HealthStatus.HEALTHY
        
        # 检查关键目录
        critical_dirs = [
            self.config.RESULTS_DIR,
            self.config.FROM_HERMES_DIR,
            self.config.ACK_DIR,
        ]
        
        for dir_path in critical_dirs:
            if not os.path.exists(dir_path):
                issues.append(f"关键目录不存在: {dir_path}")
                status = HealthStatus.CRITICAL
        
        # 检查ACK文件（应该有新提交但无ACK）
        ack_dir = self.config.ACK_DIR
        if os.path.exists(ack_dir):
            ack_count = len([f for f in os.listdir(ack_dir) if f.endswith(".json")])
            if ack_count == 0:
                warnings.append("ACK目录为空（可能无新提交或ACK机制未工作）")
        
        # 检查Session文件
        sessions_dir = self.config.SESSIONS_DIR
        if os.path.exists(sessions_dir):
            session_count = len([f for f in os.listdir(sessions_dir) if f.endswith(".jsonl")])
            if session_count == 0:
                warnings.append("Session目录为空（OpenRath未使用）")
        
        # 检查Workspace
        workspace_dir = self.config.WORKSPACE_DIR
        if os.path.exists(workspace_dir):
            task_count = len([d for d in os.listdir(workspace_dir) 
                            if os.path.isdir(os.path.join(workspace_dir, d))])
            if task_count == 0:
                warnings.append("Workspace无任务（Harness未使用）")
        
        return {
            "status": status,
            "issues": issues,
            "warnings": warnings,
            "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }


# ============================================================
# 自动恢复器
# ============================================================

class AutoRecoverer:
    """自动恢复器：检测问题并自动修复"""
    
    def __init__(self):
        self.config = Config()
        self.retry = RetryManager()
        self.health_checker = HealthChecker()
    
    def recover_all(self) -> Dict:
        """执行所有恢复操作"""
        results = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "actions": [],
            "success_count": 0,
            "failure_count": 0,
        }
        
        # 1. 恢复NFS
        nfs_result = self.recover_nfs()
        results["actions"].append(nfs_result)
        results["success_count" if nfs_result["success"] else "failure_count"] += 1
        
        # 2. 恢复进程
        proc_result = self.recover_processes()
        results["actions"].append(proc_result)
        results["success_count" if proc_result["success"] else "failure_count"] += 1
        
        # 3. 恢复SSH（如果需要）
        ssh_result = self.recover_ssh()
        results["actions"].append(ssh_result)
        results["success_count" if ssh_result["success"] else "failure_count"] += 1
        
        # 4. 清理积压
        cleanup_result = self.recover_cleanup()
        results["actions"].append(cleanup_result)
        results["success_count" if cleanup_result["success"] else "failure_count"] += 1
        
        return results
    
    def recover_nfs(self) -> Dict:
        """恢复NFS挂载"""
        try:
            # 检查NFS服务
            result = subprocess.run(
                ["systemctl", "is-active", "nfs-server"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                universal_newlines=True, timeout=10
            )
            
            if result.stdout.strip() != "active":
                # 启动NFS服务
                subprocess.run(
                    ["sudo", "systemctl", "start", "nfs-server"],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    universal_newlines=True, timeout=30
                )
                subprocess.run(
                    ["sudo", "systemctl", "enable", "nfs-server"],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    universal_newlines=True, timeout=10
                )
                return {
                    "action": "nfs_start",
                    "success": True,
                    "message": "NFS服务已启动",
                }
            else:
                return {
                    "action": "nfs_check",
                    "success": True,
                    "message": "NFS服务正常运行",
                }
        except Exception as e:
            return {
                "action": "nfs_recovery",
                "success": False,
                "message": f"NFS恢复失败: {e}",
            }
    
    def recover_processes(self) -> Dict:
        """恢复后台进程"""
        recovered = []
        failed = []
        
        processes = [
            {
                "name": "sync_reminder",
                "command": ["python3", "/home/admin/lobster-network/core/sync_reminder.py", "run"],
                "description": "同步催促服务",
            },
            {
                "name": "time_protection",
                "command": ["python3", "/home/admin/lobster-network/core/time_protection_v2.py", "daemon"],
                "description": "时间保护守护进程",
            },
        ]
        
        for proc in processes:
            try:
                # 检查是否已运行
                result = subprocess.run(
                    ["ps", "aux"],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    universal_newlines=True, timeout=5
                )
                
                if proc["name"] in result.stdout:
                    recovered.append(f"{proc['name']} 已在运行")
                    continue
                
                # 后台启动
                subprocess.Popen(
                    proc["command"],
                    stdout=open(f"/tmp/{proc['name']}.log", "w"),
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                )
                recovered.append(f"{proc['name']} 已启动")
                
            except Exception as e:
                failed.append(f"{proc['name']}: {e}")
        
        return {
            "action": "process_recovery",
            "success": len(failed) == 0,
            "recovered": recovered,
            "failed": failed,
        }
    
    def recover_ssh(self) -> Dict:
        """恢复SSH连接（提供指导）"""
        issues = []
        
        for student_id, student_info in self.config.STUDENTS.items():
            if student_info["host"] == "local":
                continue
            
            try:
                result = subprocess.run(
                    ["ssh", "-o", "ConnectTimeout=3",
                     "-o", "StrictHostKeyChecking=no",
                     "-i", student_info["ssh_key"],
                     f"{student_info['user']}@{student_info['host']}",
                     "echo OK"],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    universal_newlines=True, timeout=5
                )
                
                if result.returncode != 0:
                    issues.append({
                        "student": student_info["name"],
                        "host": student_info["host"],
                        "issue": "SSH连接失败",
                        "solution": f"在{student_info['name']}节点执行: ssh-copy-id {student_info['user']}@{student_info['host']}",
                    })
            except Exception as e:
                issues.append({
                    "student": student_info["name"],
                    "host": student_info["host"],
                    "issue": str(e),
                    "solution": "检查SSH密钥和网络连接",
                })
        
        return {
            "action": "ssh_recovery",
            "success": len(issues) == 0,
            "issues": issues,
        }
    
    def recover_cleanup(self) -> Dict:
        """清理积压数据"""
        cleaned = []
        
        try:
            # 清理过期from-hermes消息（超过7天）
            from_hermes_dir = self.config.FROM_HERMES_DIR
            if os.path.exists(from_hermes_dir):
                cutoff = time.time() - (7 * 86400)
                for filename in os.listdir(from_hermes_dir):
                    if filename.endswith(".json"):
                        filepath = os.path.join(from_hermes_dir, filename)
                        if os.path.getmtime(filepath) < cutoff:
                            # 移动到archive
                            archive_dir = os.path.join(self.config.SHARED_DIR, "archive")
                            os.makedirs(archive_dir, exist_ok=True)
                            os.rename(filepath, os.path.join(archive_dir, f"old_{filename}"))
                            cleaned.append(f"归档: {filename}")
            
            return {
                "action": "cleanup",
                "success": True,
                "cleaned": cleaned,
                "cleaned_count": len(cleaned),
            }
        except Exception as e:
            return {
                "action": "cleanup",
                "success": False,
                "message": f"清理失败: {e}",
            }


# ============================================================
# 降级策略管理器
# ============================================================

class DegradeManager:
    """降级策略管理器：多级降级保障"""
    
    def __init__(self):
        self.config = Config()
        self.local_cache_dir = f"{self.config.SHARED_DIR}local_cache/"
        os.makedirs(self.local_cache_dir, exist_ok=True)
    
    def submit_with_degrade(self, student_id: str, data: Dict) -> Dict:
        """
        带降级的提交
        策略: 共享目录 → SSH传输 → GitHub同步 → 本地缓存
        """
        strategies = [
            ("shared_dir", self._submit_shared_dir),
            ("ssh_transfer", self._submit_ssh),
            ("github_sync", self._submit_github),
            ("local_cache", self._submit_local_cache),
        ]
        
        for strategy_name, strategy_fn in strategies:
            try:
                result = strategy_fn(student_id, data)
                if result.get("success"):
                    return {
                        "success": True,
                        "strategy": strategy_name,
                        "message": f"通过{strategy_name}提交成功",
                        "result": result,
                    }
            except Exception as e:
                print(f"  ⚠️ {strategy_name}失败: {e}")
                continue
        
        # 所有策略失败，保存到本地缓存
        return {
            "success": False,
            "strategy": "local_cache",
            "message": "所有策略失败，数据已保存到本地缓存",
            "cached": self._submit_local_cache(student_id, data),
        }
    
    def _submit_shared_dir(self, student_id: str, data: Dict) -> Dict:
        """通过共享目录提交"""
        results_dir = self.config.RESULTS_DIR
        os.makedirs(results_dir, exist_ok=True)
        
        filename = f"{student_id}_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(results_dir, filename)
        
        with open(filepath, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return {"success": True, "file": filepath}
    
    def _submit_ssh(self, student_id: str, data: Dict) -> Dict:
        """通过SSH传输提交"""
        student_info = self.config.STUDENTS.get(student_id)
        if not student_info or student_info["host"] == "local":
            return {"success": False, "message": "SSH不适用"}
        
        # 先写入本地临时文件
        temp_file = f"/tmp/{student_id}_submit_{int(time.time())}.json"
        with open(temp_file, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # SCP传输
        remote_path = f"/shared/training/go/from-{student_id}/"
        result = subprocess.run(
            ["scp", "-i", student_info["ssh_key"],
             "-o", "StrictHostKeyChecking=no",
             temp_file,
             f"{student_info['user']}@{student_info['host']}:{remote_path}"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True, timeout=30
        )
        
        os.remove(temp_file)
        
        if result.returncode == 0:
            return {"success": True, "method": "scp"}
        return {"success": False, "error": result.stderr}
    
    def _submit_github(self, student_id: str, data: Dict) -> Dict:
        """通过GitHub同步提交"""
        # 写入本地仓库
        local_dir = "/home/admin/lobster-network/docs/training_results/"
        os.makedirs(local_dir, exist_ok=True)
        
        filename = f"{student_id}_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(local_dir, filename)
        
        with open(filepath, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return {"success": True, "file": filepath, "note": "需手动git commit+push"}
    
    def _submit_local_cache(self, student_id: str, data: Dict) -> Dict:
        """本地缓存（最后手段）"""
        cache_file = os.path.join(
            self.local_cache_dir,
            f"{student_id}_cached_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        with open(cache_file, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return {"success": True, "file": cache_file, "note": "本地缓存，需后续处理"}


# ============================================================
# 稳定性监控器
# ============================================================

class StabilityMonitor:
    """稳定性监控器：采集指标+告警"""
    
    def __init__(self):
        self.config = Config()
        self.metrics: List[Dict] = []
        self.alerts: List[Dict] = []
    
    def collect_metrics(self) -> Dict:
        """采集当前指标"""
        metrics = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "submission_rate": self._calc_submission_rate(),
            "error_rate": self._calc_error_rate(),
            "process_uptime": self._calc_process_uptime(),
            "data_freshness": self._calc_data_freshness(),
        }
        
        self.metrics.append(metrics)
        return metrics
    
    def _calc_submission_rate(self) -> float:
        """计算提交率"""
        results_dir = self.config.RESULTS_DIR
        if not os.path.exists(results_dir):
            return 0.0
        
        # 统计最近24小时的提交
        cutoff = time.time() - 86400
        recent = 0
        total = 0
        
        for filename in os.listdir(results_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(results_dir, filename)
                total += 1
                if os.path.getmtime(filepath) > cutoff:
                    recent += 1
        
        return recent / total if total > 0 else 0.0
    
    def _calc_error_rate(self) -> float:
        """计算错误率"""
        # 检查sync_reminder日志中的错误
        log_file = "/home/admin/go-training/shared/sync_reminder.log"
        if not os.path.exists(log_file):
            return 0.0
        
        try:
            with open(log_file) as f:
                lines = f.readlines()
            
            recent_lines = [l for l in lines[-100:] if l.strip()]
            error_lines = [l for l in recent_lines if "ERROR" in l or "error" in l.lower()]
            
            return len(error_lines) / len(recent_lines) if recent_lines else 0.0
        except:
            return 0.0
    
    def _calc_process_uptime(self) -> Dict:
        """计算进程运行时间"""
        processes = ["sync_reminder", "time_protection", "message_poller"]
        uptime = {}
        
        for proc in processes:
            try:
                result = subprocess.run(
                    ["ps", "aux"],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    universal_newlines=True, timeout=5
                )
                if proc in result.stdout:
                    uptime[proc] = "running"
                else:
                    uptime[proc] = "down"
            except:
                uptime[proc] = "unknown"
        
        return uptime
    
    def _calc_data_freshness(self) -> Dict:
        """计算数据新鲜度"""
        freshness = {}
        
        dirs_to_check = {
            "results": self.config.RESULTS_DIR,
            "from_hermes": self.config.FROM_HERMES_DIR,
            "acks": self.config.ACK_DIR,
        }
        
        for name, dir_path in dirs_to_check.items():
            if os.path.exists(dir_path):
                files = [f for f in os.listdir(dir_path) if f.endswith(".json")]
                if files:
                    latest = max(
                        os.path.getmtime(os.path.join(dir_path, f)) 
                        for f in files
                    )
                    hours_ago = (time.time() - latest) / 3600
                    freshness[name] = {
                        "latest_file_hours_ago": round(hours_ago, 1),
                        "status": "fresh" if hours_ago < 24 else "stale",
                    }
                else:
                    freshness[name] = {"status": "empty"}
            else:
                freshness[name] = {"status": "missing"}
        
        return freshness
    
    def check_alerts(self, metrics: Dict) -> List[Dict]:
        """检查是否需要告警"""
        alerts = []
        thresholds = self.config.ALERT_THRESHOLDS
        
        # 提交率过低
        if metrics.get("submission_rate", 1.0) < 0.5:
            alerts.append({
                "type": "low_submission_rate",
                "severity": "warning",
                "message": f"提交率过低: {metrics['submission_rate']:.1%}",
            })
        
        # 错误率过高
        if metrics.get("error_rate", 0.0) > thresholds["error_rate_percent"] / 100:
            alerts.append({
                "type": "high_error_rate",
                "severity": "critical",
                "message": f"错误率过高: {metrics['error_rate']:.1%}",
            })
        
        # 进程宕机
        for proc, status in metrics.get("process_uptime", {}).items():
            if status == "down":
                alerts.append({
                    "type": "process_down",
                    "severity": "critical",
                    "message": f"进程{proc}宕机",
                })
        
        # 数据过期
        for name, info in metrics.get("data_freshness", {}).items():
            if info.get("status") == "stale":
                alerts.append({
                    "type": "stale_data",
                    "severity": "warning",
                    "message": f"{name}数据过期({info.get('latest_file_hours_ago', '?')}小时前)",
                })
        
        self.alerts.extend(alerts)
        return alerts
    
    def get_report(self) -> Dict:
        """获取监控报告"""
        metrics = self.collect_metrics()
        alerts = self.check_alerts(metrics)
        
        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "metrics": metrics,
            "alerts": alerts,
            "alert_count": len(alerts),
            "overall_status": "critical" if any(a["severity"] == "critical" for a in alerts) 
                            else "warning" if alerts else "healthy",
        }


# ============================================================
# 可靠性引擎（整合所有组件）
# ============================================================

class ReliabilityEngine:
    """
    围棋学习可靠性引擎
    整合：健康检查 + 自动恢复 + 重试 + 超时 + 降级 + 监控
    """
    
    def __init__(self):
        self.config = Config()
        self.health_checker = HealthChecker()
        self.auto_recoverer = AutoRecoverer()
        self.retry_manager = RetryManager()
        self.timeout_ctrl = TimeoutController()
        self.degrade_manager = DegradeManager()
        self.monitor = StabilityMonitor()
    
    def full_cycle(self) -> Dict:
        """完整可靠性周期：检查→恢复→监控"""
        print(f"\n{'='*60}")
        print(f"🔍 可靠性引擎周期检查: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        # 1. 健康检查
        print("\n📊 1. 健康检查...")
        health = self.health_checker.check_all()
        print(f"   整体状态: {health['overall'].value}")
        for component, result in health.items():
            if isinstance(result, dict) and "status" in result:
                status_icon = "✅" if result["status"] == HealthStatus.HEALTHY else "⚠️" if result["status"] == HealthStatus.WARNING else "❌"
                print(f"   {status_icon} {component}: {result['status'].value}")
                if result.get("issues"):
                    for issue in result["issues"]:
                        print(f"      - {issue}")
        
        # 2. 自动恢复（如果有问题）
        if health["overall"] in [HealthStatus.CRITICAL, HealthStatus.DOWN]:
            print(f"\n🔧 2. 自动恢复...")
            recovery = self.auto_recoverer.recover_all()
            print(f"   成功: {recovery['success_count']}, 失败: {recovery['failure_count']}")
            for action in recovery["actions"]:
                status_icon = "✅" if action.get("success") else "❌"
                print(f"   {status_icon} {action.get('action')}: {action.get('message', 'OK')}")
        else:
            print(f"\n🔧 2. 系统健康，无需恢复")
        
        # 3. 稳定性监控
        print(f"\n📈 3. 稳定性监控...")
        report = self.monitor.get_report()
        print(f"   整体状态: {report['overall_status']}")
        print(f"   告警数: {report['alert_count']}")
        for alert in report["alerts"]:
            severity_icon = "🔴" if alert["severity"] == "critical" else "🟡"
            print(f"   {severity_icon} {alert['message']}")
        
        # 4. 提交测试
        print(f"\n📤 4. 提交链路测试...")
        test_data = {
            "student_id": "test",
            "type": "reliability_test",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data": {"test": True},
        }
        submit_result = self.degrade_manager.submit_with_degrade("test", test_data)
        print(f"   策略: {submit_result['strategy']}")
        print(f"   结果: {'✅ 成功' if submit_result['success'] else '❌ 失败'}")
        
        # 保存报告
        report_dir = self.config.STATE_DIR
        os.makedirs(report_dir, exist_ok=True)
        report_file = os.path.join(report_dir, f"reliability_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        def _serialize(obj):
            if isinstance(obj, HealthStatus):
                return obj.value
            if isinstance(obj, dict):
                return {k: _serialize(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [_serialize(v) for v in obj]
            return obj
        
        with open(report_file, "w") as f:
            json.dump(_serialize({
                "health": health,
                "recovery": recovery if health["overall"] in [HealthStatus.CRITICAL, HealthStatus.DOWN] else None,
                "monitor": report,
            }), f, ensure_ascii=False, indent=2)
        
        print(f"\n📝 报告已保存: {report_file}")
        print(f"{'='*60}\n")
        
        return {
            "health": health,
            "recovery": recovery if health["overall"] in [HealthStatus.CRITICAL, HealthStatus.DOWN] else None,
            "monitor": report,
            "submit_test": submit_result,
        }


# ============================================================
# 命令行接口
# ============================================================

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="围棋学习可靠性引擎")
    parser.add_argument("action", choices=["check", "recover", "monitor", "full"],
                       help="操作: check(健康检查) | recover(自动恢复) | monitor(监控) | full(完整周期)")
    
    args = parser.parse_args()
    engine = ReliabilityEngine()
    
    if args.action == "check":
        health = engine.health_checker.check_all()
        print(json.dumps({k: (v.value if isinstance(v, HealthStatus) else v) 
                         for k, v in health.items()}, ensure_ascii=False, indent=2))
    
    elif args.action == "recover":
        recovery = engine.auto_recoverer.recover_all()
        print(json.dumps(recovery, ensure_ascii=False, indent=2))
    
    elif args.action == "monitor":
        report = engine.monitor.get_report()
        print(json.dumps(report, ensure_ascii=False, indent=2))
    
    elif args.action == "full":
        result = engine.full_cycle()


if __name__ == "__main__":
    main()
