"""
SSH 传输通道（集成诸葛马版 ssh_channel_v2）
"""

import os
import time
from typing import Tuple, Optional
from dataclasses import dataclass

try:
    import paramiko
    HAS_PARAMIKO = True
except ImportError:
    HAS_PARAMIKO = False
    paramiko = None

from ..messenger import Transport, ReliableMessage
from ..registry import TransportConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class SSHConfig:
    """SSH 连接配置"""
    hostname: str
    username: str
    port: int = 22
    password: Optional[str] = None
    key_filename: Optional[str] = None
    timeout: int = 10


class SSHTransport(Transport):
    """SSH 文件传输通道"""
    
    def __init__(self, ssh_config: SSHConfig):
        super().__init__("ssh")
        self.ssh_config = ssh_config
        self._client = None
    
    def _connect(self):
        """建立 SSH 连接"""
        if not HAS_PARAMIKO:
            raise ImportError("paramiko 未安装，无法使用 SSH 传输通道")
        
        if self._client and self._client.get_transport() and self._client.get_transport().is_active():
            return self._client
        
        client = paramiko.SSHClient()
        # 安全策略：拒绝未知主机密钥，防止中间人攻击
        # 使用 RejectPolicy 替代 AutoAddPolicy，已知主机需预先配置在 known_hosts
        client.set_missing_host_key_policy(paramiko.RejectPolicy())
        
        connect_kwargs = {
            "hostname": self.ssh_config.hostname,
            "port": self.ssh_config.port,
            "username": self.ssh_config.username,
            "timeout": self.ssh_config.timeout,
        }
        
        if self.ssh_config.password:
            connect_kwargs["password"] = self.ssh_config.password
        elif self.ssh_config.key_filename:
            connect_kwargs["key_filename"] = self.ssh_config.key_filename
        
        client.connect(**connect_kwargs)
        self._client = client
        return client
    
    def send(self, message: ReliableMessage, config: TransportConfig) -> Tuple[bool, Optional[str], Optional[float]]:
        """通过 SSH 发送消息文件"""
        start = time.time()
        try:
            client = self._connect()
            sftp = client.open_sftp()
            
            # 解析目标目录
            target_dir = config.endpoint or f"/tmp/lobster-messages/from-{message.from_node}"
            
            # 创建目录（递归）
            try:
                sftp.mkdir(target_dir)
            except IOError:
                pass  # 目录可能已存在
            
            # 上传文件
            filename = f"{message.msg_id}.json"
            remote_path = os.path.join(target_dir, filename)
            
            import json
            content = json.dumps(message.to_dict(), ensure_ascii=False, indent=2).encode('utf-8')
            
            with sftp.file(remote_path, 'w') as f:
                f.write(content.decode('utf-8'))
            
            sftp.close()
            latency = (time.time() - start) * 1000
            
            logger.debug(f"SSH send: {remote_path} ({latency:.1f}ms)")
            return True, None, latency
            
        except Exception as e:
            latency = (time.time() - start) * 1000
            error = f"SSH send failed: {e}"
            logger.error(error)
            
            # 重置连接以便下次重试
            if self._client:
                try:
                    self._client.close()
                except:
                    pass
                self._client = None
            
            return False, error, latency
    
    def can_use(self, config: TransportConfig) -> bool:
        """检查 SSH 通道是否可用"""
        if not config.enabled:
            return False
        try:
            client = self._connect()
            # 快速测试 SFTP
            sftp = client.open_sftp()
            sftp.close()
            return True
        except Exception as e:
            logger.debug(f"SSH channel unavailable: {e}")
            return False
    
    def close(self):
        """关闭 SSH 连接"""
        if self._client:
            try:
                self._client.close()
            except:
                pass
            self._client = None
