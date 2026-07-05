"""
配置管理模块 V2

新增：
- 注册中心配置
- 心跳超时配置
- 消息协议配置
- 通道重连配置
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class NetworkConfig:
    """网络配置 V2"""

    # SSH 配置
    ssh_host: str = ""
    ssh_user: str = "admin"
    ssh_port: int = 22
    ssh_key: str = "~/.ssh/id_rsa"

    # 共享目录
    shared_dir: str = "/shared/messages"

    # 涌现阈值
    emergence_threshold: float = 0.5

    # 日志配置
    log_level: str = "INFO"
    log_file: str = "lobster_network.log"

    # 网络配置
    network_name: str = "lobster-network"
    network_version: str = "0.2.0"

    # ===== 注册中心配置 =====
    heartbeat_interval: int = 30        # 心跳间隔（秒）
    heartbeat_timeout: int = 90         # 心跳超时（秒）
    auto_cleanup_interval: int = 300    # 自动清理间隔（秒）

    # ===== 消息协议配置 =====
    default_ttl_seconds: int = 300      # 默认 TTL
    max_retry_count: int = 3            # 最大重试次数
    protocol_version: str = "2.0"       # 协议版本

    # ===== 通道重连配置 =====
    max_retries: int = 3                # 最大重试次数
    reconnect_base: float = 2.0         # 重连退避基数（秒）

    def to_dict(self) -> dict:
        return {
            "ssh_host": self.ssh_host,
            "ssh_user": self.ssh_user,
            "ssh_port": self.ssh_port,
            "ssh_key": self.ssh_key,
            "shared_dir": self.shared_dir,
            "emergence_threshold": self.emergence_threshold,
            "log_level": self.log_level,
            "log_file": self.log_file,
            "network_name": self.network_name,
            "network_version": self.network_version,
            "heartbeat_interval": self.heartbeat_interval,
            "heartbeat_timeout": self.heartbeat_timeout,
            "auto_cleanup_interval": self.auto_cleanup_interval,
            "default_ttl_seconds": self.default_ttl_seconds,
            "max_retry_count": self.max_retry_count,
            "protocol_version": self.protocol_version,
            "max_retries": self.max_retries,
            "reconnect_base": self.reconnect_base,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_dict(cls, data: dict) -> "NetworkConfig":
        return cls(
            ssh_host=data.get("ssh_host", ""),
            ssh_user=data.get("ssh_user", "admin"),
            ssh_port=data.get("ssh_port", 22),
            ssh_key=data.get("ssh_key", "~/.ssh/id_rsa"),
            shared_dir=data.get("shared_dir", "/shared/messages"),
            emergence_threshold=data.get("emergence_threshold", 0.5),
            log_level=data.get("log_level", "INFO"),
            log_file=data.get("log_file", "lobster_network.log"),
            network_name=data.get("network_name", "lobster-network"),
            network_version=data.get("network_version", "0.2.0"),
            heartbeat_interval=data.get("heartbeat_interval", 30),
            heartbeat_timeout=data.get("heartbeat_timeout", 90),
            auto_cleanup_interval=data.get("auto_cleanup_interval", 300),
            default_ttl_seconds=data.get("default_ttl_seconds", 300),
            max_retry_count=data.get("max_retry_count", 3),
            protocol_version=data.get("protocol_version", "2.0"),
            max_retries=data.get("max_retries", 3),
            reconnect_base=data.get("reconnect_base", 2.0),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "NetworkConfig":
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def from_file(cls, file_path: str) -> "NetworkConfig":
        with open(file_path, 'r', encoding='utf-8') as f:
            return cls.from_json(f.read())

    def save_to_file(self, file_path: str) -> None:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(self.to_json())


class ConfigManager:
    """配置管理器"""

    def __init__(self, config: Optional[NetworkConfig] = None):
        self.config = config or NetworkConfig()

    def get_config(self) -> NetworkConfig:
        return self.config

    def update_config(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)

    def get_ssh_config(self) -> Dict:
        return {
            "host": self.config.ssh_host,
            "user": self.config.ssh_user,
            "port": self.config.ssh_port,
            "key": self.config.ssh_key,
        }

    def get_network_config(self) -> Dict:
        return {
            "name": self.config.network_name,
            "version": self.config.network_version,
            "emergence_threshold": self.config.emergence_threshold,
            "protocol_version": self.config.protocol_version,
        }

    def get_registry_config(self) -> Dict:
        """获取注册中心配置"""
        return {
            "heartbeat_interval": self.config.heartbeat_interval,
            "heartbeat_timeout": self.config.heartbeat_timeout,
            "auto_cleanup_interval": self.config.auto_cleanup_interval,
        }

    def get_channel_config(self) -> Dict:
        """获取通道配置"""
        return {
            "max_retries": self.config.max_retries,
            "reconnect_base": self.config.reconnect_base,
        }

    def export_config(self) -> str:
        return self.config.to_json()

    def save_config(self, file_path: str) -> None:
        self.config.save_to_file(file_path)

    def load_config(self, file_path: str) -> None:
        self.config = NetworkConfig.from_file(file_path)
