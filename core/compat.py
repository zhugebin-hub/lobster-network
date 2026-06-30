#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
路径自适应与版本兼容层
解决 P0-问题 3：硬编码路径导致脚本不可移植

功能：
1. 自动检测 BASE_DIR（消除硬编码）
2. Python 3.6-3.9 兼容性处理
3. subprocess 跨版本兼容
4. JSON 统一编码处理

作者：信电大虾 (小龙虾网络)
日期：2026-07-01
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, Union

# === 1. 路径自适应 ===
# 所有脚本应使用 REPO_ROOT 替代硬编码路径
CURRENT_FILE = Path(__file__).resolve()
REPO_ROOT = CURRENT_FILE.parent.parent  # core/ -> lobster-network/

# 共享目录路径
SHARED_DIR = REPO_ROOT / ".shared" / "training" / "go"
QUEUE_DIR = REPO_ROOT / "lobster-data" / "messages" / "queue"
DOCS_DIR = REPO_ROOT / "docs" / "training_results"

# 确保目录存在
for dir_path in [SHARED_DIR, QUEUE_DIR, DOCS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)


# === 2. Python 3.6 兼容层 ===
def run_subprocess(cmd: list, timeout: int = 300) -> subprocess.CompletedProcess:
    """
    跨版本 subprocess 运行器
    解决 Python 3.6 不支持 capture_output=True 的问题
    """
    # Python 3.6 使用 stdout/stderr PIPE
    return subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        timeout=timeout
    )


def json_load(file_path: Union[str, Path]) -> Any:
    """安全加载 JSON"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def json_dump(data: Any, file_path: Union[str, Path], indent: int = 2) -> None:
    """安全保存 JSON"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def get_python_version() -> tuple:
    """获取 Python 版本"""
    return sys.version_info[:2]


def is_python_36() -> bool:
    """检查是否为 Python 3.6"""
    return get_python_version() == (3, 6)


# === 3. 日志兼容 ===
import logging

def setup_logger(name: str, log_file: Union[str, Path] = None, level: int = logging.INFO) -> logging.Logger:
    """配置兼容日志"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 控制台输出
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # 文件输出（可选）
        if log_file:
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
    return logger


# === 导出 ===
__all__ = [
    'REPO_ROOT', 'SHARED_DIR', 'QUEUE_DIR', 'DOCS_DIR',
    'run_subprocess', 'json_load', 'json_dump',
    'get_python_version', 'is_python_36',
    'setup_logger'
]
