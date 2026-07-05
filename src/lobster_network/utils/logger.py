"""
日志系统模块 V2

新增：
- 注册事件日志
- 心跳日志
- 通道状态日志
- 分级日志文件（按模块）
"""

import logging
import os
from datetime import datetime
from typing import Optional


class LobsterLogger:
    """小龙虾网络日志器 V2"""

    def __init__(
        self,
        name: str = "lobster_network",
        log_level: str = "INFO",
        log_file: Optional[str] = None,
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))

        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(getattr(logging, log_level.upper()))

            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

            if log_file:
                log_dir = os.path.dirname(log_file)
                if log_dir:
                    os.makedirs(log_dir, exist_ok=True)
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
                file_handler.setLevel(getattr(logging, log_level.upper()))
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)

    def debug(self, message: str) -> None:
        self.logger.debug(message)

    def info(self, message: str) -> None:
        self.logger.info(message)

    def warning(self, message: str) -> None:
        self.logger.warning(message)

    def error(self, message: str) -> None:
        self.logger.error(message)

    def critical(self, message: str) -> None:
        self.logger.critical(message)

    def exception(self, message: str) -> None:
        self.logger.exception(message)

    # ========== 专用日志方法 ==========

    def log_dialogue(self, from_node: str, to_node: str, emergence_score: float, new_insight: str) -> None:
        self.info(
            f"对话: {from_node} → {to_node} | "
            f"涌现值: {emergence_score:.2f} | "
            f"新见解: {new_insight}"
        )

    def log_emergence(self, event_id: str, emergence_score: float, treasure_unlocked: Optional[str] = None) -> None:
        message = f"涌现事件: {event_id} | 涌现值: {emergence_score:.2f}"
        if treasure_unlocked:
            message += f" | 解锁宝藏: {treasure_unlocked}"
        self.info(message)

    def log_ssh_event(self, event_type: str, remote_host: str, success: bool, message: str = "") -> None:
        status = "成功" if success else "失败"
        log_message = f"SSH {event_type}: {remote_host} | 状态: {status}"
        if message:
            log_message += f" | 消息: {message}"
        if success:
            self.info(log_message)
        else:
            self.error(log_message)

    def log_registry(self, event: str, node_id: str, detail: str = "") -> None:
        """注册事件日志"""
        message = f"注册中心 [{event}]: {node_id}"
        if detail:
            message += f" | {detail}"
        if event in ("REGISTER", "RE-REGISTER", "RESUME"):
            self.info(message)
        elif event in ("DEREGISTER", "CLEANUP", "SUSPEND"):
            self.warning(message)
        else:
            self.info(message)

    def log_heartbeat(self, node_id: str, success: bool, detail: str = "") -> None:
        """心跳日志"""
        status = "OK" if success else "FAIL"
        message = f"心跳 [{status}]: {node_id}"
        if detail:
            message += f" | {detail}"
        if success:
            self.debug(message)
        else:
            self.warning(message)

    def log_health(self, alive: int, dead: int, total: int) -> None:
        """健康检查日志"""
        self.info(f"健康检查: 总计={total}, 存活={alive}, 离线={dead}")

    def log_channel(self, event: str, remote_host: str, detail: str = "") -> None:
        """通道事件日志"""
        message = f"通道 [{event}]: {remote_host}"
        if detail:
            message += f" | {detail}"
        if event in ("CONNECT", "RECONNECT"):
            self.info(message)
        elif event in ("DISCONNECT", "ERROR"):
            self.error(message)
        else:
            self.debug(message)


# 全局日志器实例
_global_logger: Optional[LobsterLogger] = None


def get_logger(
    name: str = "lobster_network",
    log_level: str = "INFO",
    log_file: Optional[str] = None,
) -> LobsterLogger:
    """获取全局日志器实例"""
    global _global_logger
    if _global_logger is None:
        _global_logger = LobsterLogger(name, log_level, log_file)
    return _global_logger
