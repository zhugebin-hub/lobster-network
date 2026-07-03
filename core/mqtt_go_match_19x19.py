#!/usr/bin/env python3
"""
19×19 围棋实战对局脚本
小龙虾网络 - 诸葛马教练组织
小陈 (黑) vs 诸葛虾 (白)
"""

import json
import time
import random
import sys
import os
import signal
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.mqtt_client_base import MqttClientBase as MQTTClientBase
from core.mqtt_go_match_sync import GoBoard, GoMatchSync as GoMoveValidator

class Match19x19:
    """19×19围棋实战对局管理器"""
    
    def __init__(self, broker_host='47.93.6.57', broker_port=1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.match_id = f"19x19_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 创建教练端MQTT客户端
        self.client = MQTTClientBase(
            node_id=f"coach_match_{self.match_id}",
            broker_host=broker_host,
            broker_port=broker_port
        )
        
        # 棋盘和规则验证器
        self.board = GoBoard(19)
        self.validator = GoMoveValidator()
        
        # 对局状态
        self.current_turn = "black"  # 黑先
        self.moves = []
        self.pass_count = 0
        self.game_over = False
        self.start_time = None
        self.move_times = {}
        
        # 结果存储
        self.results = {
            "match_id": self.match_id,
            "black_player": "小陈",
            "white_player": "诸葛虾",
            "board_size": 19,
            "moves": [],
            "final_score": None,
            "winner": None,
            "duration": None
        }
        
        # 信号处理
        signal.signal(signal.SIGINT, self._handle_exit)
        signal.signal(signal.SIGTERM, self._handle_exit)
        
    def _handle_exit(self, signum, frame):
        """优雅退出"""
        print("\n🛑 收到退出信号，正在保存对局数据...")
        self._save_match_data()
        self.client.disconnect()
        sys.exit(0)
        
    def _on_message(self, client, userdata, msg):
        """处理MQTT消息"""
        topic = msg.topic
        payload = json.loads(msg.payload.decode())
        
        print(f"\n📡 收到消息: {topic}")
        print(f"   内容: {json.dumps(payload, ensure_ascii=False)}")
        
        if "move" in topic:
            self._handle_move(payload)
        elif "ack" in topic:
            self._handle_ack(payload)
        elif "status" in topic:
            self._handle_status(payload)
            
    def _handle_move(self, payload):
        """处理落子"""
        player = payload.get("player")
        coord = payload.get("coord")
        timestamp = payload.get("timestamp")
        
        if self.game_over:
            print("⚠️ 对局已结束，忽略落子")
            return
            
        # 验证回合
        if player != self.current_turn:
            print(f"⚠️ 回合错误: 期望{self.current_turn}，收到{player}")
            return
            
        # 验证落子
        if coord == "PASS":
            self.pass_count += 1
            if self.pass_count >= 2:
                self._end_game()
                return
        else:
            self.pass_count = 0
            if not self.validator.is_valid_move(self.board, coord, self.current_turn):
                print(f"⚠️ 无效落子: {coord}")
                return
                
            # 更新棋盘
            self.board.place_stone(coord, self.current_turn)
            
        # 记录移动
        move_record = {
            "move_number": len(self.moves) + 1,
            "player": self.current_turn,
            "coord": coord,
            "timestamp": timestamp,
            "duration": time.time() - self.move_times.get(self.current_turn, time.time())
        }
        self.moves.append(move_record)
        self.results["moves"].append(move_record)
        
        # 更新回合
        self.current_turn = "white" if self.current_turn == "black" else "black"
        self.move_times[self.current_turn] = time.time()
        
        # 广播落子
        self._broadcast_move(move_record)
        
        # 打印棋盘
        self._print_board()
        
        # 检查是否结束
        if len(self.moves) >= 361:  # 19×19最大手数
            self._end_game()
            
    def _handle_ack(self, payload):
        """处理ACK"""
        print(f"✅ ACK: {payload.get('player')} - {payload.get('message', 'OK')}")
        
    def _handle_status(self, payload):
        """处理状态更新"""
        player = payload.get("player")
        status = payload.get("status")
        print(f"📊 {player} 状态: {status}")
        
    def _broadcast_move(self, move_record):
        """广播落子到所有订阅者"""
        topic = f"lobster/match/{self.match_id}/move"
        payload = json.dumps(move_record, ensure_ascii=False)
        self.client.publish(topic, payload, qos=1)
        
    def _print_board(self):
        """打印棋盘"""
        print("\n" + "="*60)
        print(f"🦞 小龙虾网络 19×19 围棋实战")
        print(f"   对局ID: {self.match_id}")
        print(f"   手数: {len(self.moves)}")
        print(f"   当前: {'黑方(小陈)' if self.current_turn == 'black' else '白方(诸葛虾)'}")
        print("="*60)
        
        # 打印坐标
        header = "    " + " ".join([f"{chr(65+i)}" for i in range(19)])
        print(header)
        print("   " + "-"*57)
        
        # 打印棋盘
        for row in range(19):
            row_str = f"{19-row:2d} |"
            for col in range(19):
                stone = self.board.get_stone((row, col))
                if stone == "black":
                    row_str += " ● "
                elif stone == "white":
                    row_str += " ○ "
                else:
                    row_str += " · "
            row_str += "|"
            print(row_str)
            
        print("   " + "-"*57)
        print()
        
    def _end_game(self):
        """结束对局"""
        self.game_over = True
        end_time = time.time()
        duration = end_time - (self.start_time or end_time)
        
        # 计算结果
        score = self.validator.calculate_score(self.board)
        winner = "黑方(小陈)" if score > 0 else "白方(诸葛虾)" if score < 0 else "平局"
        
        self.results["final_score"] = score
        self.results["winner"] = winner
        self.results["duration"] = duration
        self.results["total_moves"] = len(self.moves)
        
        # 广播结果
        topic = f"lobster/match/{self.match_id}/result"
        payload = json.dumps(self.results, ensure_ascii=False)
        self.client.publish(topic, payload, qos=2)
        
        # 保存数据
        self._save_match_data()
        
        # 打印结果
        print("\n" + "="*60)
        print("🏁 对局结束!")
        print(f"   总手数: {len(self.moves)}")
        print(f"   用时: {duration:.1f}秒")
        print(f"   胜者: {winner}")
        print(f"   分差: {abs(score)}目")
        print("="*60)
        
    def _save_match_data(self):
        """保存对局数据"""
        os.makedirs("/home/admin/lobster-network/data/matches/", exist_ok=True)
        filepath = f"/home/admin/lobster-network/data/matches/{self.match_id}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"💾 对局数据已保存: {filepath}")
        
    def start(self):
        """启动对局"""
        print("🚀 启动19×19围棋实战对局")
        print(f"   对局ID: {self.match_id}")
        print(f"   黑方: 小陈 (AI)")
        print(f"   白方: 诸葛虾 (AI)")
        print(f"   Broker: {self.broker_host}:{self.broker_port}")
        print()
        
        # 连接MQTT
        self.client.connect()
        self.client.subscribe(f"lobster/match/{self.match_id}/move", qos=1)
        self.client.subscribe(f"lobster/match/{self.match_id}/ack", qos=1)
        self.client.subscribe(f"lobster/match/{self.match_id}/status", qos=1)
        self.client.on_message = self._on_message
        
        # 发布对局开始消息
        start_payload = {
            "type": "match_start",
            "match_id": self.match_id,
            "board_size": 19,
            "black_player": "小陈",
            "white_player": "诸葛虾",
            "komi": 6.5,
            "rules": "中国规则",
            "timestamp": datetime.now().isoformat()
        }
        topic = f"lobster/match/{self.match_id}/start"
        self.client.publish(topic, json.dumps(start_payload, ensure_ascii=False), qos=2)
        
        self.start_time = time.time()
        self.move_times["black"] = time.time()
        
        print("✅ 对局已开始，等待落子...")
        print()
        
        # 保持运行
        try:
            while not self.game_over:
                time.sleep(1)
        except KeyboardInterrupt:
            self._handle_exit(None, None)
            
if __name__ == "__main__":
    match = Match19x19()
    match.start()
