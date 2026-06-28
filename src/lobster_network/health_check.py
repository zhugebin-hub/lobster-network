#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
健康检查系统 (Health Check) - 小龙虾网络 V3.1
集成系统资源监控 + 服务连通性检测

功能:
- CPU / 内存 / 磁盘监控
- Signal Arena / MeYo 连通性检测
- 健康评分与告警
- 定期巡检报告生成
"""

import os
import sys
import time
import json
import logging
import subprocess
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class HealthStatus:
    """健康状态"""
    healthy: bool = True
    score: float = 100.0          # 0-100, 100=完全健康
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    checks: Dict[str, Any] = field(default_factory=dict)
    checked_at: str = ""

    def __post_init__(self):
        if not self.checked_at:
            self.checked_at = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return {
            "healthy": self.healthy,
            "score": round(self.score, 1),
            "issues": self.issues,
            "warnings": self.warnings,
            "checks": self.checks,
            "checked_at": self.checked_at,
        }


class SystemMonitor:
    """系统资源监控"""

    @staticmethod
    def get_cpu_percent(interval: float = 0.5) -> float:
        """获取 CPU 使用率"""
        try:
            import psutil
            return psutil.cpu_percent(interval=interval)
        except ImportError:
            # 降级方案: 读取 /proc/stat
            try:
                with open('/proc/loadavg', 'r') as f:
                    load = float(f.read().split()[1])  # 1分钟负载
                    cpu_count = os.cpu_count() or 1
                    return min((load / cpu_count) * 100, 100.0)
            except Exception:
                return -1.0

    @staticmethod
    def get_memory_info() -> Dict:
        """获取内存信息"""
        try:
            import psutil
            mem = psutil.virtual_memory()
            return {
                "total_mb": round(mem.total / 1024 / 1024, 1),
                "used_mb": round(mem.used / 1024 / 1024, 1),
                "available_mb": round(mem.available / 1024 / 1024, 1),
                "percent": mem.percent,
            }
        except ImportError:
            # 降级方案: 读取 /proc/meminfo
            try:
                info = {}
                with open('/proc/meminfo', 'r') as f:
                    for line in f:
                        parts = line.split()
                        key = parts[0].rstrip(':')
                        value = int(parts[1])  # kB
                        info[key] = value
                total = info.get('MemTotal', 1)
                available = info.get('MemAvailable', total)
                used = total - available
                return {
                    "total_mb": round(total / 1024, 1),
                    "used_mb": round(used / 1024, 1),
                    "available_mb": round(available / 1024, 1),
                    "percent": round(used / total * 100, 1),
                }
            except Exception:
                return {"error": "无法获取内存信息"}

    @staticmethod
    def get_disk_info(path: str = "/") -> Dict:
        """获取磁盘信息"""
        try:
            import psutil
            disk = psutil.disk_usage(path)
            return {
                "total_gb": round(disk.total / 1024 / 1024 / 1024, 1),
                "used_gb": round(disk.used / 1024 / 1024 / 1024, 1),
                "free_gb": round(disk.free / 1024 / 1024 / 1024, 1),
                "percent": disk.percent,
            }
        except Exception:
            # 降级方案: df 命令
            try:
                result = subprocess.run(['df', '-B1', path], capture_output=True, text=True)
                lines = result.stdout.strip().split('\n')
                if len(lines) >= 2:
                    parts = lines[1].split()
                    total = int(parts[1])
                    used = int(parts[2])
                    free = int(parts[3])
                    return {
                        "total_gb": round(total / 1024 / 1024 / 1024, 1),
                        "used_gb": round(used / 1024 / 1024 / 1024, 1),
                        "free_gb": round(free / 1024 / 1024 / 1024, 1),
                        "percent": float(parts[4].rstrip('%')),
                    }
            except Exception:
                pass
        return {"error": "无法获取磁盘信息"}

    @staticmethod
    def get_uptime() -> str:
        """获取系统运行时间"""
        try:
            with open('/proc/uptime', 'r') as f:
                seconds = float(f.read().split()[0])
                days = int(seconds // 86400)
                hours = int((seconds % 86400) // 3600)
                minutes = int((seconds % 3600) // 60)
                return f"{days}天{hours}时{minutes}分"
        except Exception:
            return "未知"


class ConnectivityChecker:
    """服务连通性检测"""

    @staticmethod
    def check_http(url: str, timeout: float = 5.0) -> Dict:
        """HTTP 连通性检测"""
        import urllib.request
        import urllib.error

        start = time.time()
        try:
            req = urllib.request.Request(url, method='GET')
            req.add_header('User-Agent', 'LobsterNetwork-HealthCheck/3.1')
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                elapsed = time.time() - start
                return {
                    "status": "ok",
                    "code": resp.status,
                    "latency_ms": round(elapsed * 1000, 1),
                    "url": url,
                }
        except urllib.error.HTTPError as e:
            elapsed = time.time() - start
            return {
                "status": "error",
                "code": e.code,
                "latency_ms": round(elapsed * 1000, 1),
                "url": url,
                "error": str(e),
            }
        except Exception as e:
            elapsed = time.time() - start
            return {
                "status": "down",
                "code": 0,
                "latency_ms": round(elapsed * 1000, 1),
                "url": url,
                "error": str(e),
            }

    @staticmethod
    def check_tcp(host: str, port: int, timeout: float = 3.0) -> Dict:
        """TCP 端口连通性检测"""
        import socket
        start = time.time()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((host, port))
            sock.close()
            elapsed = time.time() - start
            return {
                "status": "ok",
                "host": host,
                "port": port,
                "latency_ms": round(elapsed * 1000, 1),
            }
        except Exception as e:
            elapsed = time.time() - start
            return {
                "status": "down",
                "host": host,
                "port": port,
                "latency_ms": round(elapsed * 1000, 1),
                "error": str(e),
            }


class HealthChecker:
    """健康检查主类"""

    # 告警阈值
    CPU_WARNING = 80.0
    CPU_CRITICAL = 95.0
    MEM_WARNING = 80.0
    MEM_CRITICAL = 95.0
    DISK_WARNING = 85.0
    DISK_CRITICAL = 95.0
    LATENCY_WARNING = 500.0   # ms
    LATENCY_CRITICAL = 2000.0  # ms

    def __init__(self, name: str = "lobster-node"):
        self.name = name
        self.system = SystemMonitor()
        self.connectivity = ConnectivityChecker()
        self._history: List[Dict] = []
        self._max_history = 100

    def check_system(self) -> Dict:
        """系统资源检查"""
        result = {}

        # CPU
        cpu = self.system.get_cpu_percent()
        result["cpu"] = {"value": cpu, "unit": "%"}
        if cpu >= self.CPU_CRITICAL:
            result["cpu"]["level"] = "critical"
        elif cpu >= self.CPU_WARNING:
            result["cpu"]["level"] = "warning"
        else:
            result["cpu"]["level"] = "ok"

        # 内存
        mem = self.system.get_memory_info()
        if "percent" in mem:
            mem["level"] = ("critical" if mem["percent"] >= self.MEM_CRITICAL
                           else "warning" if mem["percent"] >= self.MEM_WARNING
                           else "ok")
        result["memory"] = mem

        # 磁盘
        disk = self.system.get_disk_info()
        if "percent" in disk:
            disk["level"] = ("critical" if disk["percent"] >= self.DISK_CRITICAL
                            else "warning" if disk["percent"] >= self.DISK_WARNING
                            else "ok")
        result["disk"] = disk

        # 运行时间
        result["uptime"] = self.system.get_uptime()

        return result

    def check_services(self, services: Optional[List[Dict]] = None) -> Dict:
        """服务连通性检查"""
        if services is None:
            services = [
                {"name": "signal_arena", "type": "http", "url": "https://world.coze.site"},
                {"name": "meyo", "type": "http", "url": "https://www.meyo123.com"},
            ]

        result = {}
        for svc in services:
            if svc["type"] == "http":
                result[svc["name"]] = self.connectivity.check_http(
                    svc["url"], svc.get("timeout", 5.0)
                )
            elif svc["type"] == "tcp":
                result[svc["name"]] = self.connectivity.check_tcp(
                    svc["host"], svc["port"], svc.get("timeout", 3.0)
                )
        return result

    def compute_score(self, system: Dict, services: Dict) -> HealthStatus:
        """计算健康评分"""
        status = HealthStatus()
        score = 100.0
        status.checks["system"] = system
        status.checks["services"] = services

        # CPU 扣分
        cpu = system.get("cpu", {})
        if cpu.get("level") == "critical":
            score -= 30
            status.issues.append(f"CPU 使用率过高: {cpu.get('value')}%")
        elif cpu.get("level") == "warning":
            score -= 10
            status.warnings.append(f"CPU 使用率偏高: {cpu.get('value')}%")

        # 内存扣分
        mem = system.get("memory", {})
        if mem.get("level") == "critical":
            score -= 30
            status.issues.append(f"内存使用率过高: {mem.get('percent')}%")
        elif mem.get("level") == "warning":
            score -= 10
            status.warnings.append(f"内存使用率偏高: {mem.get('percent')}%")

        # 磁盘扣分
        disk = system.get("disk", {})
        if disk.get("level") == "critical":
            score -= 20
            status.issues.append(f"磁盘使用率过高: {disk.get('percent')}%")
        elif disk.get("level") == "warning":
            score -= 5
            status.warnings.append(f"磁盘使用率偏高: {disk.get('percent')}%")

        # 服务扣分
        for name, info in services.items():
            if info.get("status") == "down":
                score -= 15
                status.issues.append(f"服务 {name} 不可达")
            elif info.get("status") == "error":
                score -= 5
                status.warnings.append(f"服务 {name} 返回错误: {info.get('code')}")
            elif info.get("latency_ms", 0) > self.LATENCY_CRITICAL:
                score -= 10
                status.warnings.append(f"服务 {name} 延迟过高: {info['latency_ms']}ms")

        status.score = max(0.0, min(100.0, score))
        status.healthy = len(status.issues) == 0

        return status

    def run_full_check(self, services: Optional[List[Dict]] = None) -> HealthStatus:
        """执行完整健康检查"""
        logger.info(f"[健康检查:{self.name}] 开始巡检...")
        system = self.check_system()
        svc_status = self.check_services(services)
        status = self.compute_score(system, svc_status)
        status.checked_at = datetime.now().isoformat()

        # 记录历史
        self._history.append(status.to_dict())
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

        level = "✅ 健康" if status.healthy else ("⚠️ 警告" if status.warnings else "🔴 异常")
        logger.info(f"[健康检查:{self.name}] {level} 评分: {status.score:.1f}/100 "
                     f"问题: {len(status.issues)} 警告: {len(status.warnings)}")

        return status

    def get_history(self, count: int = 10) -> List[Dict]:
        """获取历史检查结果"""
        return self._history[-count:]

    def save_report(self, path: str, status: HealthStatus):
        """保存健康报告到文件"""
        report = {
            "node": self.name,
            "status": status.to_dict(),
            "history": self.get_history(5),
        }
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        logger.info(f"[健康检查:{self.name}] 报告已保存到 {path}")


# ========== 便捷函数 ==========

def quick_check(name: str = "lobster-node") -> Dict:
    """快速健康检查，返回字典"""
    checker = HealthChecker(name)
    status = checker.run_full_check()
    return status.to_dict()


def check_and_alert(name: str = "lobster-node", threshold: float = 60.0) -> Optional[Dict]:
    """检查并返回需要告警的信息（评分低于阈值）"""
    checker = HealthChecker(name)
    status = checker.run_full_check()
    if status.score < threshold:
        return status.to_dict()
    return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    result = quick_check()
    print(json.dumps(result, ensure_ascii=False, indent=2))
