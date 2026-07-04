#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 · 统一配置模块
====================
将所有硬编码路径抽象为可配置项，支持环境变量覆盖和 fallback。
"""

import os
from pathlib import Path


def _get_base_dir() -> str:
    """获取龙虾网络基础目录，环境变量 LOBSTER_HOME 优先，fallback 到 ~/.lobster-network"""
    env_home = os.environ.get("LOBSTER_HOME", "")
    if env_home:
        return env_home
    return os.path.join(str(Path.home()), ".lobster-network")


def _ensure_dir(path: str) -> str:
    """确保目录存在并返回路径"""
    os.makedirs(path, exist_ok=True)
    return path


class LobsterConfig:
    """统一配置入口 — 单例模式"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._base_dir = _get_base_dir()
        self._build_paths()

    # ==================== MQTT Broker ====================
    @property
    def mqtt_broker_host(self) -> str:
        return os.environ.get("LOBSTER_MQTT_HOST", "localhost")

    @property
    def mqtt_broker_port(self) -> int:
        return int(os.environ.get("LOBSTER_MQTT_PORT", "1883"))

    @property
    def mqtt_client_id(self) -> str:
        return os.environ.get("LOBSTER_MQTT_CLIENT_ID", "lobster-network")

    # ==================== 基础路径 ====================
    @property
    def base_dir(self) -> str:
        return self._base_dir

    @property
    def shared_dir(self) -> str:
        return self._shared_dir

    @property
    def messages_dir(self) -> str:
        return self._messages_dir

    @property
    def queue_dir(self) -> str:
        return self._queue_dir

    @property
    def training_dir(self) -> str:
        return self._training_dir

    @property
    def go_dir(self) -> str:
        return self._go_dir

    @property
    def problem_bank_dir(self) -> str:
        return self._problem_bank_dir

    @property
    def matches_dir(self) -> str:
        return self._matches_dir

    @property
    def tournament_dir(self) -> str:
        return self._tournament_dir

    @property
    def go_board_dir(self) -> str:
        return self._go_board_dir

    @property
    def go_broadcast_dir(self) -> str:
        return self._go_broadcast_dir

    # ==================== 学员队列路径 ====================
    def player_inbox(self, player: str) -> str:
        return _ensure_dir(os.path.join(self._queue_dir, player, "inbox"))

    def player_outbox(self, player: str) -> str:
        return _ensure_dir(os.path.join(self._queue_dir, player, "outbox"))

    def player_processed(self, player: str) -> str:
        return _ensure_dir(os.path.join(self._queue_dir, player, "processed"))

    def player_state(self, player: str) -> str:
        return os.path.join(self._queue_dir, player, "state.json")

    # ==================== 学员训练路径 ====================
    def player_training_dir(self, player: str) -> str:
        return _ensure_dir(os.path.join(self._training_dir, player))

    def player_profile(self, player: str) -> str:
        return os.path.join(self._training_dir, player, "profile.json")

    def player_progress(self, player: str) -> str:
        return os.path.join(self._training_dir, player, "progress.json")

    def player_wrong_book(self, player: str) -> str:
        return os.path.join(self._training_dir, player, "wrong_book.json")

    def player_daily_log(self, player: str) -> str:
        return _ensure_dir(os.path.join(self._training_dir, player, "daily_log"))

    def player_problem_history(self, player: str) -> str:
        return _ensure_dir(os.path.join(self._training_dir, player, "problem_history"))

    # ==================== 围棋引擎路径 ====================
    @property
    def go_board_file(self) -> str:
        return os.path.join(self._go_board_dir, "board.json")

    @property
    def go_move_log(self) -> str:
        return os.path.join(self._go_board_dir, "move_log.json")

    @property
    def go_timer_file(self) -> str:
        return os.path.join(self._go_board_dir, "timer.json")

    # ==================== 对局引擎存储路径 ====================
    @property
    def engine_storage_dir(self) -> str:
        return _ensure_dir(os.path.join(self._go_dir, "engine"))

    def match_storage(self, match_id: str) -> str:
        d = _ensure_dir(os.path.join(self.engine_storage_dir, match_id))
        return d

    def match_board_file(self, match_id: str) -> str:
        return os.path.join(self.match_storage(match_id), "board.json")

    def match_move_log(self, match_id: str) -> str:
        return os.path.join(self.match_storage(match_id), "move_log.json")

    def match_timer_file(self, match_id: str) -> str:
        return os.path.join(self.match_storage(match_id), "timer.json")

    def match_sgf_file(self, match_id: str) -> str:
        return os.path.join(self.match_storage(match_id), "game.sgf")

    def match_meta_file(self, match_id: str) -> str:
        return os.path.join(self.match_storage(match_id), "meta.json")

    # ==================== 调度器状态 ====================
    @property
    def status_file(self) -> str:
        return os.path.join(self._training_dir, "status.json")

    @property
    def dispatcher_log(self) -> str:
        return os.path.join(self._training_dir, "dispatcher.log")

    @property
    def brain_file(self) -> str:
        """brain.json 在仓库 config/ 下，也同步到共享路径"""
        import inspect
        try:
            frame = inspect.currentframe()
            caller = inspect.getouterframes(frame)[1]
            del frame
        except:
            return os.path.join(self._training_dir, "brain.json")
        return os.path.join(self._training_dir, "brain.json")

    # ==================== 构建路径树 ====================
    def _build_paths(self):
        self._shared_dir = _ensure_dir(os.path.join(self._base_dir, "shared"))
        self._messages_dir = _ensure_dir(os.path.join(self._shared_dir, "messages"))
        self._queue_dir = _ensure_dir(os.path.join(self._messages_dir, "queue"))
        self._training_dir = _ensure_dir(os.path.join(self._shared_dir, "training"))
        self._go_dir = _ensure_dir(os.path.join(self._training_dir, "go"))
        self._problem_bank_dir = _ensure_dir(os.path.join(self._go_dir, "problem_bank"))
        self._matches_dir = _ensure_dir(os.path.join(self._go_dir, "matches"))
        self._tournament_dir = _ensure_dir(os.path.join(self._go_dir, "tournament"))
        self._go_board_dir = _ensure_dir(os.path.join(self._go_dir, "board"))
        self._go_broadcast_dir = _ensure_dir(os.path.join(self._go_dir, "broadcasts"))

    def summary(self) -> dict:
        """返回配置摘要，供诊断用"""
        return {
            "base_dir": self._base_dir,
            "mqtt_broker": f"{self.mqtt_broker_host}:{self.mqtt_broker_port}",
            "shared_dir": self._shared_dir,
            "queue_dir": self._queue_dir,
            "training_dir": self._training_dir,
            "problem_bank": self._problem_bank_dir,
            "engine_storage": self.engine_storage_dir,
        }


# 全局单例
config = LobsterConfig()

# 以下是便捷常量，向后兼容旧代码

QUEUE_DIR = config.queue_dir
TRAINING_DIR = config.training_dir
PROBLEM_BANK_DIR = config.problem_bank_dir
MATCHES_DIR = config.matches_dir
TOURNAMENT_DIR = config.tournament_dir
GO_BOARD_FILE = config.go_board_file
GO_MOVE_LOG = config.go_move_log
GO_TIMER_FILE = config.go_timer_file
GO_BROADCAST_DIR = config.go_broadcast_dir
STATUS_FILE = config.status_file
DISPATCHER_LOG = config.dispatcher_log


if __name__ == "__main__":
    print(json.dumps(config.summary(), indent=2, ensure_ascii=False))
