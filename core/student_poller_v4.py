#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 V4.0 - 学员端消息轮询器
部署到学员服务器，每30秒轮询 to-{student}/ 目录，自动消费消息

作者：诸葛马 (Hermes)
日期：2026-07-01
版本：v4.0
"""

import json
import os
import sys
import time
import hashlib
import subprocess
import signal
import logging
from datetime import datetime
from pathlib import Path

# ============================================================
# 配置
# ============================================================

class PollerConfig:
    """轮询器配置"""
    POLL_INTERVAL = 30  # 轮询间隔(秒)
    SHARED_BASE = "/home/admin/go-training/shared"
    PROCESSED_DIR = "processed"  # 已处理消息目录
    LOG_FILE = "poller.log"
    STATE_FILE = "poller_state.json"
    MAX_RETRIES = 3
    RETRY_DELAY = 10

# ============================================================
# 消息处理器
# ============================================================

class MessageHandler:
    """消息处理器 - 根据消息类型分发"""
    
    def __init__(self, student_id, config):
        self.student_id = student_id
        self.config = config
        self.shared_base = config.SHARED_BASE
        self.processed_dir = os.path.join(self.shared_base, "processed", student_id)
        os.makedirs(self.processed_dir, exist_ok=True)
        
        # 日志
        log_dir = os.path.join(self.shared_base, "logs")
        os.makedirs(log_dir, exist_ok=True)
        logging.basicConfig(
            filename=os.path.join(log_dir, f"{student_id}_poller.log"),
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s'
        )
        self.logger = logging.getLogger(student_id)
    
    def process_message(self, filename):
        """处理单条消息"""
        filepath = os.path.join(self.shared_base, f"to-{self.student_id}", filename)
        if not os.path.exists(filepath):
            return False
        
        try:
            with open(filepath, 'r') as f:
                msg = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            self.logger.error(f"读取消息失败: {filename} - {e}")
            return False
        
        msg_type = msg.get("type", "unknown")
        msg_id = msg.get("id", filename)
        
        self.logger.info(f"处理消息: type={msg_type}, id={msg_id}")
        
        # 根据类型分发
        result = self._dispatch(msg_type, msg, filename)
        
        # 移动到已处理目录
        processed_path = os.path.join(self.processed_dir, filename)
        try:
            os.rename(filepath, processed_path)
            self.logger.info(f"消息已处理并归档: {filename}")
        except OSError as e:
            self.logger.warning(f"归档失败: {filename} - {e}")
        
        return result
    
    def _dispatch(self, msg_type, msg, filename):
        """消息分发"""
        handlers = {
            "training_task": self._handle_training_task,
            "go_match_notify": self._handle_go_match,
            "go_move": self._handle_go_move,
            "reminder": self._handle_reminder,
            "assessment": self._handle_assessment,
            "system": self._handle_system,
        }
        
        handler = handlers.get(msg_type, self._handle_unknown)
        try:
            return handler(msg, filename)
        except Exception as e:
            self.logger.error(f"处理失败: {msg_type} - {e}")
            return False
    
    def _handle_training_task(self, msg, filename):
        """处理训练任务"""
        day = msg.get("day", "?")
        focus = msg.get("focus", "未知")
        problem_count = msg.get("problem_count", 0)
        
        self.logger.info(f"训练任务: Day{day} - {focus} ({problem_count}题)")
        
        # 写入训练任务到学员工作目录
        work_dir = os.path.join(self.shared_base, "training", self.student_id, "inbox")
        os.makedirs(work_dir, exist_ok=True)
        task_file = os.path.join(work_dir, filename)
        with open(task_file, 'w') as f:
            json.dump(msg, f, indent=2, ensure_ascii=False)
        
        # 发送ACK到教练
        self._send_ack(msg.get("id", filename), "training_task", "received")
        return True
    
    def _handle_go_match(self, msg, filename):
        """处理围棋对局通知"""
        role = msg.get("role", "?")
        opponent = msg.get("opponent", "?")
        board_size = msg.get("board_size", 19)
        
        self.logger.info(f"对局通知: 你是{role}方, 对手={opponent}, 棋盘={board_size}x{board_size}")
        
        # 保存对局信息
        match_dir = os.path.join(self.shared_base, "training", "go", "matches")
        os.makedirs(match_dir, exist_ok=True)
        match_file = os.path.join(match_dir, f"local_match_{self.student_id}.json")
        with open(match_file, 'w') as f:
            json.dump(msg, f, indent=2, ensure_ascii=False)
        
        self._send_ack(msg.get("id", filename), "go_match", "received")
        return True
    
    def _handle_go_move(self, msg, filename):
        """处理围棋落子通知"""
        move = msg.get("move", "?")
        move_num = msg.get("move_num", "?")
        
        self.logger.info(f"对手落子: 第{move_num}手 → {move}")
        
        # 保存落子信息供学员参考
        match_dir = os.path.join(self.shared_base, "training", "go", "matches")
        os.makedirs(match_dir, exist_ok=True)
        move_file = os.path.join(match_dir, f"last_move_{self.student_id}.json")
        with open(move_file, 'w') as f:
            json.dump(msg, f, indent=2, ensure_ascii=False)
        
        self._send_ack(msg.get("id", filename), "go_move", "received")
        return True
    
    def _handle_reminder(self, msg, filename):
        """处理催促提醒"""
        level = msg.get("level", "soft")
        self.logger.info(f"催促提醒: level={level}")
        self._send_ack(msg.get("id", filename), "reminder", "received")
        return True
    
    def _handle_assessment(self, msg, filename):
        """处理评估通知"""
        self.logger.info(f"评估通知: {msg.get('assessment_type', '?')}")
        self._send_ack(msg.get("id", filename), "assessment", "received")
        return True
    
    def _handle_system(self, msg, filename):
        """处理系统消息"""
        self.logger.info(f"系统消息: {msg.get('action', '?')}")
        self._send_ack(msg.get("id", filename), "system", "received")
        return True
    
    def _handle_unknown(self, msg, filename):
        """处理未知类型消息"""
        self.logger.warning(f"未知消息类型: {msg.get('type', 'none')}")
        self._send_ack(msg.get("id", filename), "unknown", "received")
        return True
    
    def _send_ack(self, msg_id, msg_type, status):
        """发送ACK到教练"""
        ack = {
            "id": f"ack_{msg_id}_{int(time.time())}",
            "type": "ack",
            "original_id": msg_id,
            "original_type": msg_type,
            "status": status,
            "student_id": self.student_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "poller_version": "4.0"
        }
        
        ack_dir = os.path.join(self.shared_base, "from-" + self.student_id)
        os.makedirs(ack_dir, exist_ok=True)
        ack_file = os.path.join(ack_dir, f"ack_{msg_id}_{int(time.time())}.json")
        with open(ack_file, 'w') as f:
            json.dump(ack, f, indent=2)
        
        self.logger.info(f"ACK已发送: {msg_id}")

# ============================================================
# 轮询器主类
# ============================================================

class StudentPoller:
    """学员端消息轮询器"""
    
    def __init__(self, student_id):
        self.student_id = student_id
        self.config = PollerConfig()
        self.handler = MessageHandler(student_id, self.config)
        self.running = False
        self.processed_count = 0
        self.error_count = 0
        
        # 状态文件
        self.state_dir = os.path.join(self.config.SHARED_BASE, "poller_state")
        os.makedirs(self.state_dir, exist_ok=True)
        self.state_file = os.path.join(self.state_dir, f"{student_id}_state.json")
        
        # 加载状态
        self.state = self._load_state()
    
    def _load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {"last_poll": None, "processed": 0, "errors": 0, "started": None}
    
    def _save_state(self):
        self.state["last_poll"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.state["processed"] = self.processed_count
        self.state["errors"] = self.error_count
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def run(self, max_iterations=None):
        """启动轮询"""
        self.running = True
        self.state["started"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._save_state()
        
        print(f"🔄 学员端消息轮询器 v4.0 启动")
        print(f"📋 学员: {self.student_id}")
        print(f"📂 监听目录: {self.config.SHARED_BASE}/to-{self.student_id}/")
        print(f"⏱ 轮询间隔: {self.config.POLL_INTERVAL}秒")
        print(f"🚀 开始轮询...\n")
        
        iteration = 0
        while self.running:
            if max_iterations and iteration >= max_iterations:
                print(f"✅ 完成 {max_iterations} 次轮询，退出")
                break
            
            try:
                self._poll_once()
                iteration += 1
                time.sleep(self.config.POLL_INTERVAL)
            except KeyboardInterrupt:
                print("\n⏹ 收到中断信号，退出轮询")
                break
            except Exception as e:
                self.error_count += 1
                print(f"❌ 轮询错误: {e}")
                time.sleep(5)
        
        self._save_state()
        print(f"\n📊 统计: 处理={self.processed_count}, 错误={self.error_count}")
    
    def _poll_once(self):
        """单次轮询"""
        inbox_dir = os.path.join(self.config.SHARED_BASE, f"to-{self.student_id}")
        if not os.path.exists(inbox_dir):
            os.makedirs(inbox_dir, exist_ok=True)
            return
        
        files = sorted(os.listdir(inbox_dir))
        if not files:
            return
        
        print(f"📬 发现 {len(files)} 条新消息")
        for filename in files:
            if filename.endswith('.json'):
                try:
                    success = self.handler.process_message(filename)
                    if success:
                        self.processed_count += 1
                        print(f"  ✅ {filename}")
                    else:
                        self.error_count += 1
                        print(f"  ❌ {filename}")
                except Exception as e:
                    self.error_count += 1
                    print(f"  ❌ {filename}: {e}")
        
        self._save_state()
    
    def stop(self):
        self.running = False

# ============================================================
# 主入口
# ============================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 student_poller_v4.py <student_id> [--daemon] [--iterations N]")
        print("示例: python3 student_poller_v4.py xiaochen --daemon")
        sys.exit(1)
    
    student_id = sys.argv[1]
    daemon = "--daemon" in sys.argv
    iterations = None
    if "--iterations" in sys.argv:
        idx = sys.argv.index("--iterations")
        iterations = int(sys.argv[idx + 1])
    
    poller = StudentPoller(student_id)
    
    if daemon:
        poller.run()  # 无限轮询
    else:
        poller.run(max_iterations=iterations or 1)  # 默认1次
