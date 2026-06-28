"""
SSH通信通道模块 V2 — 增强版

新增：
- 自动重连（指数退避）
- 消息发送重试
- 消息去重（本地缓存已发送 ID）
- 心跳探测
- 通道状态监控
"""

import os
import subprocess
import json
import time
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta

from ..utils.message_protocol import MessageFactory


class SSHChannelV2:
    """SSH通信通道 V2"""

    def __init__(
        self,
        remote_host: str,
        remote_user: str = "admin",
        remote_port: int = 22,
        ssh_key: str = "~/.ssh/id_rsa",
        shared_dir: str = "/shared/messages",
        max_retries: int = 3,
        reconnect_base: float = 2.0,
        heartbeat_interval: int = 30,
    ):
        self.remote_host = remote_host
        self.remote_user = remote_user
        self.remote_port = remote_port
        self.ssh_key = os.path.expanduser(ssh_key)
        self.shared_dir = shared_dir
        self.to_dir = f"{shared_dir}/to_{remote_host}"
        self.from_dir = f"{shared_dir}/from_{remote_host}"
        self.max_retries = max_retries
        self.reconnect_base = reconnect_base
        self.heartbeat_interval = heartbeat_interval

        # 状态
        self._connected = False
        self._last_heartbeat: Optional[datetime] = None
        self._sent_ids: Set[str] = set()
        self._error_count = 0
        self._message_count = 0
        self._connected_at: Optional[str] = None

    # ========== 连接管理 ==========

    def connect(self) -> bool:
        """建立连接并初始化目录"""
        for attempt in range(self.max_retries):
            try:
                if self._setup_directories():
                    self._connected = True
                    self._connected_at = datetime.now().isoformat()
                    self._error_count = 0
                    return True
            except Exception as e:
                self._handle_error(f"连接尝试 {attempt+1} 失败: {e}")

            if attempt < self.max_retries - 1:
                wait = self.reconnect_base ** (attempt + 1)
                time.sleep(min(wait, 30))

        return False

    def disconnect(self) -> None:
        """断开连接"""
        self._connected = False
        self._connected_at = None

    def ensure_connected(self) -> bool:
        """确保连接可用，不可用时自动重连"""
        if self._connected and self._test_connection():
            return True
        return self.connect()

    def _setup_directories(self) -> bool:
        """创建共享目录"""
        os.makedirs(self.to_dir, exist_ok=True)
        os.makedirs(self.from_dir, exist_ok=True)

        cmd = [
            "ssh", "-i", self.ssh_key, "-p", str(self.remote_port),
            "-o", "ConnectTimeout=10",
            "-o", "StrictHostKeyChecking=no",
            f"{self.remote_user}@{self.remote_host}",
            f"mkdir -p {self.shared_dir}/to_lobster {self.shared_dir}/from_lobster",
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=15)
        return result.returncode == 0

    def _test_connection(self) -> bool:
        """测试 SSH 连接"""
        try:
            cmd = [
                "ssh", "-i", self.ssh_key, "-p", str(self.remote_port),
                "-o", "ConnectTimeout=5",
                "-o", "StrictHostKeyChecking=no",
                f"{self.remote_user}@{self.remote_host}",
                "echo ok",
            ]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
            return result.returncode == 0
        except Exception:
            return False

    # ========== 消息发送 ==========

    def send_message(self, message: Dict) -> bool:
        """
        发送消息到远程服务器（带重试）

        Returns:
            bool: 是否成功
        """
        msg_id = message.get("msg_id", "")

        # 去重
        if msg_id and msg_id in self._sent_ids:
            return True  # 已发送过，视为成功

        for attempt in range(self.max_retries):
            try:
                if not self.ensure_connected():
                    raise ConnectionError("SSH 连接不可用")

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                filename = f"msg_{timestamp}.json"
                local_path = f"{self.to_dir}/{filename}"
                remote_path = f"{self.shared_dir}/to_lobster/{filename}"

                # 写本地
                with open(local_path, 'w', encoding='utf-8') as f:
                    json.dump(message, f, ensure_ascii=False, indent=2)

                # SCP 发送
                cmd = [
                    "scp", "-i", self.ssh_key, "-P", str(self.remote_port),
                    "-o", "ConnectTimeout=10",
                    local_path,
                    f"{self.remote_user}@{self.remote_host}:{remote_path}",
                ]
                result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)

                if result.returncode == 0:
                    self._sent_ids.add(msg_id)
                    self._message_count += 1
                    self._error_count = 0
                    return True
                else:
                    raise RuntimeError(f"SCP 失败: {result.stderr.strip()}")

            except Exception as e:
                self._handle_error(f"发送消息失败 (尝试 {attempt+1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(min(self.reconnect_base ** (attempt + 1), 10))

        return False

    # ========== 消息接收 ==========

    def receive_message(self) -> Optional[Dict]:
        """从远程服务器接收消息"""
        try:
            if not self.ensure_connected():
                return None

            cmd = [
                "scp", "-i", self.ssh_key, "-P", str(self.remote_port),
                "-o", "ConnectTimeout=10",
                f"{self.remote_user}@{self.remote_host}:{self.shared_dir}/from_lobster/*.json",
                self.from_dir,
            ]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)

            if result.returncode != 0:
                return None

            files = sorted([f for f in os.listdir(self.from_dir) if f.endswith('.json')])
            if not files:
                return None

            latest_file = files[-1]
            file_path = f"{self.from_dir}/{latest_file}"

            with open(file_path, 'r', encoding='utf-8') as f:
                message = json.load(f)

            # 清理已读消息
            try:
                os.remove(file_path)
            except OSError:
                pass

            return message

        except Exception as e:
            self._handle_error(f"接收消息失败: {e}")
            return None

    # ========== 心跳 ==========

    def send_heartbeat(self, node_id: str) -> bool:
        """发送心跳消息"""
        hb = MessageFactory.heartbeat(node_id, status={
            "channel": "ssh",
            "host": self.remote_host,
        })
        return self.send_message(hb.to_dict())

    def check_heartbeat(self) -> bool:
        """检查心跳是否超时"""
        if self._last_heartbeat is None:
            return False
        return (datetime.now() - self._last_heartbeat).total_seconds() < self.heartbeat_interval * 2

    def record_heartbeat(self) -> None:
        """记录心跳"""
        self._last_heartbeat = datetime.now()

    # ========== 状态 ==========

    def get_status(self) -> Dict:
        """获取通道状态"""
        return {
            "remote_host": self.remote_host,
            "remote_user": self.remote_user,
            "remote_port": self.remote_port,
            "connected": self._connected,
            "connected_at": self._connected_at,
            "last_heartbeat": self._last_heartbeat.isoformat() if self._last_heartbeat else None,
            "heartbeat_ok": self.check_heartbeat(),
            "message_count": self._message_count,
            "error_count": self._error_count,
            "sent_ids_cached": len(self._sent_ids),
        }

    # ========== 内部方法 ==========

    def _handle_error(self, message: str) -> None:
        """处理错误"""
        self._error_count += 1
        self._connected = False
        print(f"[SSHChannel] ERROR: {message}")

    def reset_sent_cache(self) -> None:
        """清空发送去重缓存"""
        self._sent_ids.clear()
