#!/usr/bin/env python3
"""
19×19 围棋实战对局 - 简化版
直接使用paho-mqtt，不依赖复杂封装
"""

import json
import time
import random
import sys
import os
import signal
from datetime import datetime

try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("❌ 请安装 paho-mqtt: pip install paho-mqtt")
    sys.exit(1)

class Simple19x19Match:
    """简化版19×19对局"""
    
    def __init__(self, broker_host='47.93.6.57', broker_port=1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.match_id = f"19x19_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 创建MQTT客户端
        self.client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=f"coach_19x19_{self.match_id}",
            clean_session=True,
            protocol=mqtt.MQTTv311,
        )
        
        # 回调
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        
        # 对局状态
        self.board = [['.' for _ in range(19)] for _ in range(19)]
        self.current_turn = 'black'
        self.moves = []
        self.game_over = False
        self.connected = False
        
        # 结果
        self.results = {
            "match_id": self.match_id,
            "black_player": "小陈",
            "white_player": "诸葛虾",
            "board_size": 19,
            "moves": [],
            "winner": None,
            "duration": None
        }
        
        self.start_time = None
        
    def _on_connect(self, client, userdata, flags, rc, properties=None):
        """连接成功"""
        if rc == 0:
            self.connected = True
            print(f"✅ 已连接到MQTT Broker")
            
            # 订阅主题
            topics = [
                f"lobster/match/{self.match_id}/move",
                f"lobster/match/{self.match_id}/ack",
                f"lobster/match/{self.match_id}/status"
            ]
            for topic in topics:
                client.subscribe(topic, qos=1)
                print(f"📡 订阅: {topic}")
                
            # 发布对局开始
            self._publish_start()
        else:
            print(f"❌ 连接失败: {rc}")
            
    def _on_message(self, client, userdata, msg):
        """处理消息"""
        try:
            payload = json.loads(msg.payload.decode())
            topic = msg.topic
            
            print(f"\n📡 收到: {topic}")
            print(f"   {json.dumps(payload, ensure_ascii=False)}")
            
            if '/move' in topic:
                self._handle_move(payload)
            elif '/ack' in topic:
                print(f"✅ ACK: {payload.get('player', 'unknown')}")
            elif '/status' in topic:
                print(f"📊 状态: {payload.get('player', 'unknown')} - {payload.get('status', 'unknown')}")
                
        except Exception as e:
            print(f"⚠️ 消息处理错误: {e}")
            
    def _on_disconnect(self, client, userdata, rc, properties=None):
        """断开连接"""
        self.connected = False
        print(f"🔌 断开连接: {rc}")
        
    def _publish(self, topic, payload, qos=1):
        """发布消息"""
        if not self.connected:
            print(f"⚠️ 未连接，无法发布")
            return False
        try:
            if isinstance(payload, dict):
                payload = json.dumps(payload, ensure_ascii=False)
            self.client.publish(topic, payload, qos=qos)
            return True
        except Exception as e:
            print(f"❌ 发布失败: {e}")
            return False
            
    def _publish_start(self):
        """发布对局开始"""
        topic = f"lobster/match/{self.match_id}/start"
        payload = {
            "type": "match_start",
            "match_id": self.match_id,
            "board_size": 19,
            "black_player": "小陈",
            "white_player": "诸葛虾",
            "komi": 6.5,
            "rules": "中国规则",
            "timestamp": datetime.now().isoformat()
        }
        self._publish(topic, payload, qos=2)
        self.start_time = time.time()
        print(f"\n🚀 对局已开始: {self.match_id}")
        self._print_board()
        
    def _handle_move(self, payload):
        """处理落子"""
        if self.game_over:
            return
            
        player = payload.get('player')
        coord = payload.get('coord')
        
        # 验证回合
        expected = 'black' if len(self.moves) % 2 == 0 else 'white'
        if player != expected:
            print(f"⚠️ 回合错误: 期望{expected}，收到{player}")
            return
            
        # 处理落子
        if coord == 'PASS':
            print(f"🏳️ {player} 弃权")
            self.moves.append({'player': player, 'coord': 'PASS', 'move': len(self.moves)+1})
        else:
            # 解析坐标 (如 "D4" -> (15, 3))
            try:
                col_letter = coord[0].upper()
                row_num = int(coord[1:])
                col = ord(col_letter) - ord('A')
                row = 19 - row_num
                
                if 0 <= row < 19 and 0 <= col < 19:
                    if self.board[row][col] == '.':
                        self.board[row][col] = '●' if player == 'black' else '○'
                        self.moves.append({'player': player, 'coord': coord, 'row': row, 'col': col, 'move': len(self.moves)+1})
                        print(f"♟️ {player} 落子: {coord}")
                    else:
                        print(f"⚠️ 位置已有棋子: {coord}")
                        return
                else:
                    print(f"⚠️ 坐标越界: {coord}")
                    return
            except:
                print(f"⚠️ 坐标格式错误: {coord}")
                return
                
        # 广播落子
        self._broadcast_move()
        self._print_board()
        
        # 检查结束条件
        if len(self.moves) >= 361:
            self._end_game()
            
    def _broadcast_move(self):
        """广播落子"""
        topic = f"lobster/match/{self.match_id}/move"
        last_move = self.moves[-1]
        self._publish(topic, last_move, qos=1)
        
    def _print_board(self):
        """打印棋盘"""
        print("\n" + "="*60)
        print(f"🦞 小龙虾网络 19×19 围棋实战")
        print(f"   对局ID: {self.match_id}")
        print(f"   手数: {len(self.moves)}")
        print(f"   当前: {'黑方(小陈)' if len(self.moves) % 2 == 0 else '白方(诸葛虾)'}")
        print("="*60)
        
        # 坐标
        header = "    " + " ".join([f"{chr(65+i)}" for i in range(19)])
        print(header)
        print("   " + "-"*57)
        
        # 棋盘
        for row in range(19):
            row_str = f"{19-row:2d} |"
            for col in range(19):
                stone = self.board[row][col]
                if stone == '●':
                    row_str += " ● "
                elif stone == '○':
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
        
        # 简单计分
        black_count = sum(row.count('●') for row in self.board)
        white_count = sum(row.count('○') for row in self.board)
        
        winner = "黑方(小陈)" if black_count > white_count else "白方(诸葛虾)" if white_count > black_count else "平局"
        
        self.results["winner"] = winner
        self.results["duration"] = duration
        self.results["total_moves"] = len(self.moves)
        self.results["black_score"] = black_count
        self.results["white_score"] = white_count
        
        # 广播结果
        topic = f"lobster/match/{self.match_id}/result"
        self._publish(topic, self.results, qos=2)
        
        # 保存
        self._save_results()
        
        # 打印结果
        print("\n" + "="*60)
        print("🏁 对局结束!")
        print(f"   总手数: {len(self.moves)}")
        print(f"   用时: {duration:.1f}秒")
        print(f"   黑方: {black_count}子")
        print(f"   白方: {white_count}子")
        print(f"   胜者: {winner}")
        print("="*60)
        
    def _save_results(self):
        """保存结果"""
        os.makedirs("/home/admin/lobster-network/data/matches/", exist_ok=True)
        filepath = f"/home/admin/lobster-network/data/matches/{self.match_id}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"💾 结果已保存: {filepath}")
        
    def start(self):
        """启动对局"""
        print("🚀 启动19×19围棋实战对局")
        print(f"   对局ID: {self.match_id}")
        print(f"   黑方: 小陈 (AI)")
        print(f"   白方: 诸葛虾 (AI)")
        print(f"   Broker: {self.broker_host}:{self.broker_port}")
        print()
        
        # 连接
        try:
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            
            # 等待连接
            timeout = 10
            while not self.connected and timeout > 0:
                time.sleep(1)
                timeout -= 1
                
            if not self.connected:
                print("❌ 连接超时")
                return
                
            print("✅ 对局已开始，等待落子...")
            
            # 保持运行
            while not self.game_over:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 收到退出信号")
            self._end_game()
        finally:
            self.client.loop_stop()
            self.client.disconnect()
            
if __name__ == "__main__":
    match = Simple19x19Match()
    match.start()
