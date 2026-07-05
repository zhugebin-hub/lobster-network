"""
SSH通信通道模块 - 增强版 v2.0
添加重试、超时、错误恢复、连接池、状态监控
"""

import os
import subprocess
import json
import time
import threading
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class ChannelStats:
    """通道统计信息"""
    total_sent: int = 0
    total_received: int = 0
    total_failed: int = 0
    total_retries: int = 0
    last_success: Optional[str] = None
    last_failure: Optional[str] = None
    avg_latency_ms: float = 0.0
    latency_samples: List[float] = field(default_factory=list)
    
    def record_success(self, latency_ms: float):
        self.total_sent += 1
        self.last_success = datetime.now().isoformat()
        self.latency_samples.append(latency_ms)
        if len(self.latency_samples) > 100:
            self.latency_samples = self.latency_samples[-100:]
        self.avg_latency_ms = sum(self.latency_samples) / len(self.latency_samples)
    
    def record_failure(self):
        self.total_failed += 1
        self.last_failure = datetime.now().isoformat()
    
    def record_retry(self):
        self.total_retries += 1
    
    def to_dict(self) -> dict:
        return {
            "total_sent": self.total_sent,
            "total_received": self.total_received,
            "total_failed": self.total_failed,
            "total_retries": self.total_retries,
            "last_success": self.last_success,
            "last_failure": self.last_failure,
            "avg_latency_ms": round(self.avg_latency_ms, 2),
        }


class SSHChannel:
    """SSH通信通道 - 增强版"""
    
    def __init__(
        self,
        remote_host: str,
        remote_user: str = "admin",
        remote_port: int = 22,
        ssh_key: str = "~/.ssh/id_rsa",
        shared_dir: str = "/shared/messages",
        max_retries: int = 3,
        timeout: int = 30,
        retry_delay: float = 2.0,
    ):
        """
        初始化SSH通道
        
        Args:
            remote_host: 远程服务器地址
            remote_user: 远程用户名
            remote_port: SSH端口
            ssh_key: SSH密钥路径
            shared_dir: 共享消息目录
            max_retries: 最大重试次数
            timeout: 超时时间（秒）
            retry_delay: 重试延迟（秒）
        """
        self.remote_host = remote_host
        self.remote_user = remote_user
        self.remote_port = remote_port
        self.ssh_key = os.path.expanduser(ssh_key)
        self.shared_dir = shared_dir
        self.to_dir = f"{shared_dir}/to_{remote_host}"
        self.from_dir = f"{shared_dir}/from_{remote_host}"
        self.max_retries = max_retries
        self.timeout = timeout
        self.retry_delay = retry_delay
        
        self.stats = ChannelStats()
        self._lock = threading.Lock()
        self._connected = False
        self._connection_time: Optional[datetime] = None
    
    def setup_directories(self) -> bool:
        """
        创建共享目录
        
        Returns:
            bool: 是否成功
        """
        try:
            os.makedirs(self.to_dir, exist_ok=True)
            os.makedirs(self.from_dir, exist_ok=True)
            
            # 在远程服务器创建目录
            cmd = [
                "ssh", "-i", self.ssh_key,
                "-p", str(self.remote_port),
                "-o", "ConnectTimeout=10",
                "-o", "StrictHostKeyChecking=accept-new",
                f"{self.remote_user}@{self.remote_host}",
                f"mkdir -p {self.shared_dir}/to_lobster {self.shared_dir}/from_lobster"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout)
            return result.returncode == 0
        except Exception as e:
            print(f"创建目录失败: {e}")
            return False
    
    def send_message(self, message: Dict) -> bool:
        """
        发送消息到远程服务器（带重试）
        
        Args:
            message: 消息字典
        
        Returns:
            bool: 是否成功
        """
        for attempt in range(self.max_retries + 1):
            try:
                start_time = time.time()
                
                # 生成消息文件名
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                filename = f"msg_{timestamp}.json"
                local_path = f"{self.to_dir}/{filename}"
                remote_path = f"{self.shared_dir}/to_lobster/{filename}"
                
                # 写入本地文件（原子写入）
                tmp_path = local_path + ".tmp"
                with open(tmp_path, 'w', encoding='utf-8') as f:
                    json.dump(message, f, ensure_ascii=False, indent=2)
                os.rename(tmp_path, local_path)  # 原子操作，避免读取不完整文件
                
                # 通过SCP发送到远程服务器
                cmd = [
                    "scp", "-i", self.ssh_key,
                    "-P", str(self.remote_port),
                    "-o", "ConnectTimeout=10",
                    "-o", "ServerAliveInterval=5",
                    "-o", "ServerAliveCountMax=2",
                    local_path,
                    f"{self.remote_user}@{self.remote_host}:{remote_path}"
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout)
                
                if result.returncode == 0:
                    latency = (time.time() - start_time) * 1000
                    with self._lock:
                        self.stats.record_success(latency)
                        self._connected = True
                        self._connection_time = datetime.now()
                    return True
                else:
                    with self._lock:
                        self.stats.record_failure()
                    print(f"发送失败 (尝试 {attempt+1}/{self.max_retries+1}): {result.stderr}")
            
            except subprocess.TimeoutExpired:
                with self._lock:
                    self.stats.record_failure()
                print(f"发送超时 (尝试 {attempt+1}/{self.max_retries+1})")
            
            except Exception as e:
                with self._lock:
                    self.stats.record_failure()
                print(f"发送异常 (尝试 {attempt+1}/{self.max_retries+1}): {e}")
            
            # 重试延迟（指数退避）
            if attempt < self.max_retries:
                delay = self.retry_delay * (2 ** attempt)
                with self._lock:
                    self.stats.record_retry()
                time.sleep(delay)
        
        return False
    
    def receive_message(self) -> Optional[Dict]:
        """
        从远程服务器接收消息
        
        Returns:
            Optional[Dict]: 消息字典，如果没有消息返回None
        """
        try:
            # 从远程服务器拉取消息
            cmd = [
                "scp", "-i", self.ssh_key,
                "-P", str(self.remote_port),
                "-o", "ConnectTimeout=10",
                f"{self.remote_user}@{self.remote_host}:{self.shared_dir}/from_lobster/*.json",
                self.from_dir
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout)
            
            if result.returncode != 0:
                return None
            
            # 读取最新消息
            files = sorted([f for f in os.listdir(self.from_dir) if f.endswith('.json')])
            if not files:
                return None
            
            latest_file = files[-1]
            file_path = f"{self.from_dir}/{latest_file}"
            
            # 原子读取
            with open(file_path, 'r', encoding='utf-8') as f:
                message = json.load(f)
            
            # 删除已读取的消息文件
            os.remove(file_path)
            
            with self._lock:
                self.stats.total_received += 1
            
            return message
        except Exception as e:
            print(f"接收消息失败: {e}")
            return None
    
    def test_connection(self) -> bool:
        """
        测试SSH连接
        
        Returns:
            bool: 连接是否成功
        """
        try:
            start_time = time.time()
            cmd = [
                "ssh", "-i", self.ssh_key,
                "-p", str(self.remote_port),
                "-o", "ConnectTimeout=10",
                "-o", "StrictHostKeyChecking=accept-new",
                f"{self.remote_user}@{self.remote_host}",
                "echo 'Connection successful'"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout)
            
            if result.returncode == 0:
                latency = (time.time() - start_time) * 1000
                with self._lock:
                    self._connected = True
                    self._connection_time = datetime.now()
                    self.stats.record_success(latency)
                return True
            else:
                with self._lock:
                    self.stats.record_failure()
                return False
        except Exception as e:
            print(f"连接测试失败: {e}")
            with self._lock:
                self.stats.record_failure()
            return False
    
    def get_status(self) -> Dict:
        """
        获取通道状态
        
        Returns:
            Dict: 通道状态信息
        """
        with self._lock:
            return {
                "remote_host": self.remote_host,
                "remote_user": self.remote_user,
                "remote_port": self.remote_port,
                "shared_dir": self.shared_dir,
                "to_dir": self.to_dir,
                "from_dir": self.from_dir,
                "connected": self._connected,
                "connection_time": self._connection_time.isoformat() if self._connection_time else None,
                "max_retries": self.max_retries,
                "timeout": self.timeout,
                "retry_delay": self.retry_delay,
                "stats": self.stats.to_dict(),
            }
    
    def get_health(self) -> Dict:
        """
        获取健康状态
        
        Returns:
            Dict: 健康状态
        """
        with self._lock:
            success_rate = (
                self.stats.total_sent / (self.stats.total_sent + self.stats.total_failed)
                if (self.stats.total_sent + self.stats.total_failed) > 0
                else 0
            )
            
            return {
                "healthy": self._connected and success_rate > 0.5,
                "connected": self._connected,
                "success_rate": round(success_rate, 3),
                "avg_latency_ms": round(self.stats.avg_latency_ms, 2),
                "total_failed": self.stats.total_failed,
                "total_retries": self.stats.total_retries,
            }
