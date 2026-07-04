"""
NFS 共享目录通信总线
用于虾尔和诸葛马之间的消息传递
"""

import os
import json
import time
from typing import Optional, Dict, List
from pathlib import Path


class NFSMessageBus:
    """基于 NFS 共享目录的消息总线"""
    
    def __init__(self, shared_dir: str = "/shared", agent_id: str = "lobster-001"):
        self.shared_dir = Path(shared_dir)
        self.agent_id = agent_id
        
        # 消息目录
        self.from_me_dir = self.shared_dir / "messages" / "from-lobster"
        self.from_other_dir = self.shared_dir / "messages" / "from-hermes"
        
        # 游戏状态目录
        self.game_dir = self.shared_dir / "escape-room"
        self.room_state_file = self.game_dir / "room-state.json"
        self.clue_queue_dir = self.game_dir / "clue-queue"
        self.puzzle_log_file = self.game_dir / "puzzle-log.json"
        
        # 确保目录存在
        self._ensure_dirs()
    
    def _ensure_dirs(self):
        """确保所有目录存在"""
        self.from_me_dir.mkdir(parents=True, exist_ok=True)
        self.from_other_dir.mkdir(parents=True, exist_ok=True)
        self.game_dir.mkdir(parents=True, exist_ok=True)
        self.clue_queue_dir.mkdir(parents=True, exist_ok=True)
    
    def send_message(self, message: Dict) -> str:
        """
        发送消息到共享目录
        返回消息 ID
        """
        msg_id = f"{int(time.time())}-{self.agent_id}"
        msg_file = self.from_me_dir / f"{msg_id}.json"
        
        message['msg_id'] = msg_id
        message['timestamp'] = time.time()
        message['sender'] = self.agent_id
        
        with open(msg_file, 'w', encoding='utf-8') as f:
            json.dump(message, f, ensure_ascii=False, indent=2)
        
        print(f"📤 发送消息: {msg_id}")
        return msg_id
    
    def receive_messages(self) -> List[Dict]:
        """
        接收对方发送的消息
        返回消息列表
        """
        messages = []
        
        if not self.from_other_dir.exists():
            return messages
        
        for msg_file in sorted(self.from_other_dir.glob("*.json")):
            try:
                with open(msg_file, 'r', encoding='utf-8') as f:
                    message = json.load(f)
                messages.append(message)
                
                # 移动到归档目录
                archive_dir = self.shared_dir / "messages" / "archive"
                archive_dir.mkdir(parents=True, exist_ok=True)
                msg_file.rename(archive_dir / msg_file.name)
                
                print(f"📥 接收消息: {message.get('msg_id', 'unknown')}")
            except Exception as e:
                print(f"⚠️ 读取消息失败 {msg_file}: {e}")
        
        return messages
    
    def save_room_state(self, room_state: Dict):
        """保存密室状态"""
        with open(self.room_state_file, 'w', encoding='utf-8') as f:
            json.dump(room_state, f, ensure_ascii=False, indent=2)
        print(f"💾 保存密室状态")
    
    def load_room_state(self) -> Optional[Dict]:
        """加载密室状态"""
        if not self.room_state_file.exists():
            return None
        
        with open(self.room_state_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def submit_clue(self, clue_data: Dict) -> str:
        """
        提交线索到队列
        """
        clue_id = f"clue-{int(time.time())}-{self.agent_id}"
        clue_file = self.clue_queue_dir / f"{clue_id}.json"
        
        clue_data['clue_id'] = clue_id
        clue_data['timestamp'] = time.time()
        clue_data['agent'] = self.agent_id
        
        with open(clue_file, 'w', encoding='utf-8') as f:
            json.dump(clue_data, f, ensure_ascii=False, indent=2)
        
        print(f"🔍 提交线索: {clue_id}")
        return clue_id
    
    def get_pending_clues(self) -> List[Dict]:
        """获取待处理的线索"""
        clues = []
        
        if not self.clue_queue_dir.exists():
            return clues
        
        for clue_file in sorted(self.clue_queue_dir.glob("*.json")):
            try:
                with open(clue_file, 'r', encoding='utf-8') as f:
                    clue = json.load(f)
                clues.append(clue)
            except Exception as e:
                print(f"⚠️ 读取线索失败 {clue_file}: {e}")
        
        return clues
    
    def log_puzzle_event(self, event: Dict):
        """记录谜题事件"""
        events = []
        if self.puzzle_log_file.exists():
            with open(self.puzzle_log_file, 'r', encoding='utf-8') as f:
                events = json.load(f)
        
        event['timestamp'] = time.time()
        events.append(event)
        
        with open(self.puzzle_log_file, 'w', encoding='utf-8') as f:
            json.dump(events, f, ensure_ascii=False, indent=2)
        
        print(f"📝 记录事件: {event.get('type', 'unknown')}")


if __name__ == '__main__':
    # 测试通信总线
    bus = NFSMessageBus()
    
    # 发送测试消息
    test_msg = {
        'type': 'room_init',
        'room_id': 'escape-room-20260603',
        'size': 5,
        'players': ['lobster-001', 'hermes']
    }
    bus.send_message(test_msg)
    
    # 保存密室状态
    room_state = {
        'size': 5,
        'players_visited': 0,
        'puzzles_solved': 0,
        'clues_collected': 0
    }
    bus.save_room_state(room_state)
    
    print("✅ 通信总线测试完成")
