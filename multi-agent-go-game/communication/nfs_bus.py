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
        self.game_dir = self.shared_dir / "go-game"
        self.board_file = self.game_dir / "board.json"
        self.move_queue_dir = self.game_dir / "move-queue"
        self.game_log_file = self.game_dir / "game-log.json"
        
        # 确保目录存在
        self._ensure_dirs()
    
    def _ensure_dirs(self):
        """确保所有目录存在"""
        self.from_me_dir.mkdir(parents=True, exist_ok=True)
        self.from_other_dir.mkdir(parents=True, exist_ok=True)
        self.game_dir.mkdir(parents=True, exist_ok=True)
        self.move_queue_dir.mkdir(parents=True, exist_ok=True)
    
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
    
    def save_board_state(self, board_dict: Dict):
        """保存棋盘状态"""
        with open(self.board_file, 'w', encoding='utf-8') as f:
            json.dump(board_dict, f, ensure_ascii=False, indent=2)
        print(f"💾 保存棋盘状态")
    
    def load_board_state(self) -> Optional[Dict]:
        """加载棋盘状态"""
        if not self.board_file.exists():
            return None
        
        with open(self.board_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def submit_move(self, move_data: Dict) -> str:
        """
        提交棋步到队列
        """
        move_id = f"move-{int(time.time())}-{self.agent_id}"
        move_file = self.move_queue_dir / f"{move_id}.json"
        
        move_data['move_id'] = move_id
        move_data['timestamp'] = time.time()
        move_data['agent'] = self.agent_id
        
        with open(move_file, 'w', encoding='utf-8') as f:
            json.dump(move_data, f, ensure_ascii=False, indent=2)
        
        print(f"♟️ 提交棋步: {move_id}")
        return move_id
    
    def get_pending_moves(self) -> List[Dict]:
        """获取待处理的棋步"""
        moves = []
        
        if not self.move_queue_dir.exists():
            return moves
        
        for move_file in sorted(self.move_queue_dir.glob("*.json")):
            try:
                with open(move_file, 'r', encoding='utf-8') as f:
                    move = json.load(f)
                moves.append(move)
            except Exception as e:
                print(f"⚠️ 读取棋步失败 {move_file}: {e}")
        
        return moves
    
    def log_game_event(self, event: Dict):
        """记录游戏事件"""
        events = []
        if self.game_log_file.exists():
            with open(self.game_log_file, 'r', encoding='utf-8') as f:
                events = json.load(f)
        
        event['timestamp'] = time.time()
        events.append(event)
        
        with open(self.game_log_file, 'w', encoding='utf-8') as f:
            json.dump(events, f, ensure_ascii=False, indent=2)
        
        print(f"📝 记录事件: {event.get('type', 'unknown')}")


if __name__ == '__main__':
    # 测试通信总线
    bus = NFSMessageBus()
    
    # 发送测试消息
    test_msg = {
        'type': 'game_init',
        'game_id': 'go-game-20260603',
        'black': 'lobster-001',
        'white': 'hermes',
        'board_size': 9
    }
    bus.send_message(test_msg)
    
    # 保存棋盘状态
    board_state = {
        'size': 9,
        'grid': [[0]*9 for _ in range(9)],
        'current_player': 1,
        'move_count': 0
    }
    bus.save_board_state(board_state)
    
    print("✅ 通信总线测试完成")
