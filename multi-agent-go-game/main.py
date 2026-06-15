"""
多智能体协作围棋对弈系统 - 主程序
支持多种比赛模式：单局、锦标赛、让子棋
"""

import json
import time
import sys
import os
from typing import List, Dict
from pathlib import Path

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.board import GoBoard, Point, StoneColor
from communication.nfs_bus import NFSMessageBus
from strategies.players import GoPlayer, create_players


class GoGame:
    """围棋对弈游戏"""
    
    def __init__(self, agent_id: str = "lobster-001"):
        self.agent_id = agent_id
        self.bus = NFSMessageBus(agent_id=agent_id)
        self.board = GoBoard(9)
        self.game_id = f"go-game-{int(time.time())}"
        self.max_moves = 81  # 9x9 棋盘最多 81 手
        self.running = False
        self.players: List[GoPlayer] = []
        self.game_log: List[Dict] = []
    
    def init_players(self):
        """初始化棋手"""
        self.players = create_players()
        print(f"👥 初始化 {len(self.players)} 个棋手")
        for player in self.players:
            print(f"   {player.name} ({'黑' if player.color == StoneColor.BLACK else '白'})")
    
    def init_game(self, mode: str = "single"):
        """初始化游戏"""
        print(f"🎮 初始化游戏: {self.game_id}")
        print(f"   模式: {mode}")
        
        # 发送游戏初始化消息
        init_msg = {
            'type': 'game_init',
            'game_id': self.game_id,
            'mode': mode,
            'players': [p.name for p in self.players],
            'board_size': 9,
            'timestamp': time.time()
        }
        self.bus.send_message(init_msg)
        
        # 保存初始棋盘状态
        self.bus.save_board_state(self.board.to_dict())
        
        # 记录游戏事件
        self.bus.log_game_event({
            'type': 'game_init',
            'game_id': self.game_id,
            'mode': mode,
            'players': [p.name for p in self.players]
        })
        
        print(f"✅ 游戏初始化完成")
        print(f"   游戏 ID: {self.game_id}")
        print(f"   棋盘大小: 9x9")
        print(f"   棋手数量: {len(self.players)}")
    
    def play_single_game(self, player1: GoPlayer, player2: GoPlayer) -> str:
        """
        单局对弈
        返回胜者
        """
        print(f"\n{'='*50}")
        print(f"🎮 单局对弈: {player1.name} vs {player2.name}")
        print(f"{'='*50}")
        
        # 重置棋盘
        self.board = GoBoard(9)
        
        # 显示初始棋盘
        print("\n初始棋盘:")
        print(self.board.display())
        
        move_count = 0
        last_move = None
        
        while move_count < self.max_moves:
            # 选择当前玩家
            if self.board.current_player == StoneColor.BLACK:
                current_player = player1
            else:
                current_player = player2
            
            # 选择落子
            move = current_player.select_move(self.board)
            
            if move is None:
                # 没有合法落子，pass
                self.board.pass_move()
                print(f"⏭️ {current_player.name} Pass（虚手）")
                
                # 检查是否连续 pass
                if len(self.board.move_history) > 1:
                    last_move = self.board.move_history[-1]
                    prev_move = self.board.move_history[-2]
                    if last_move[0] is None and prev_move[0] is None:
                        print("🏁 双方连续 pass，游戏结束")
                        break
            else:
                # 执行落子
                captured = self.board.place_stone(move, self.board.current_player)
                gtp = move.to_gtp()
                color_name = "黑" if self.board.current_player == StoneColor.WHITE else "白"
                
                print(f"\n第 {move_count + 1} 手: {current_player.name} ({color_name}) {gtp} (提子: {len(captured)})")
                print(self.board.display_with_last_move(move))
                
                # 记录棋谱
                self.game_log.append({
                    'move_number': move_count + 1,
                    'player': current_player.name,
                    'color': color_name,
                    'move': gtp,
                    'captures': len(captured)
                })
                
                last_move = move
            
            move_count += 1
            
            # 检查是否连续 pass
            if len(self.board.move_history) > 1:
                last_move = self.board.move_history[-1]
                prev_move = self.board.move_history[-2]
                if last_move[0] is None and prev_move[0] is None:
                    print("🏁 双方连续 pass，游戏结束")
                    break
        
        # 游戏结束
        print(f"\n{'='*50}")
        print(f"🏁 游戏结束")
        print(f"总手数: {move_count}")
        print(f"提子: 黑{self.board.captures[StoneColor.BLACK]} 白{self.board.captures[StoneColor.WHITE]}")
        
        # 胜负判定
        black_captures = self.board.captures[StoneColor.BLACK]
        white_captures = self.board.captures[StoneColor.WHITE]
        
        if black_captures > white_captures:
            winner = player1
            loser = player2
            result = f"{player1.name} 胜"
        elif white_captures > black_captures:
            winner = player2
            loser = player1
            result = f"{player2.name} 胜"
        else:
            winner = None
            loser = None
            result = "平局"
        
        if winner:
            winner.record_win()
            loser.record_loss()
            print(f"🏆 胜者: {winner.name}")
        else:
            player1.record_draw()
            player2.record_draw()
            print(f"🏆 结果: 平局")
        
        # 记录游戏事件
        self.bus.log_game_event({
            'type': 'game_end',
            'game_id': self.game_id,
            'winner': winner.name if winner else "平局",
            'total_moves': move_count,
            'black_captures': black_captures,
            'white_captures': white_captures
        })
        
        return result
    
    def play_tournament(self) -> Dict:
        """
        锦标赛模式
        所有棋手两两对弈
        """
        print(f"\n{'='*50}")
        print(f"🏆 锦标赛模式")
        print(f"{'='*50}")
        
        results = {}
        for player in self.players:
            results[player.name] = {'wins': 0, 'losses': 0, 'draws': 0}
        
        # 两两对弈
        for i in range(len(self.players)):
            for j in range(i + 1, len(self.players)):
                player1 = self.players[i]
                player2 = self.players[j]
                
                print(f"\n--- {player1.name} vs {player2.name} ---")
                
                # 重置棋盘
                self.board = GoBoard(9)
                
                move_count = 0
                while move_count < self.max_moves:
                    # 选择当前玩家
                    if self.board.current_player == StoneColor.BLACK:
                        current_player = player1
                    else:
                        current_player = player2
                    
                    # 选择落子
                    move = current_player.select_move(self.board)
                    
                    if move is None:
                        self.board.pass_move()
                        print(f"⏭️ {current_player.name} Pass")
                        
                        if len(self.board.move_history) > 1:
                            last_move = self.board.move_history[-1]
                            prev_move = self.board.move_history[-2]
                            if last_move[0] is None and prev_move[0] is None:
                                break
                    else:
                        captured = self.board.place_stone(move, self.board.current_player)
                        gtp = move.to_gtp()
                        color_name = "黑" if self.board.current_player == StoneColor.WHITE else "白"
                        print(f"♟️ {current_player.name} ({color_name}) {gtp} (提子: {len(captured)})")
                    
                    move_count += 1
                    
                    if len(self.board.move_history) > 1:
                        last_move = self.board.move_history[-1]
                        prev_move = self.board.move_history[-2]
                        if last_move[0] is None and prev_move[0] is None:
                            break
                
                # 胜负判定
                black_captures = self.board.captures[StoneColor.BLACK]
                white_captures = self.board.captures[StoneColor.WHITE]
                
                if black_captures > white_captures:
                    winner = player1
                    loser = player2
                elif white_captures > black_captures:
                    winner = player2
                    loser = player1
                else:
                    winner = None
                    loser = None
                
                if winner:
                    winner.record_win()
                    loser.record_loss()
                    results[winner.name]['wins'] += 1
                    results[loser.name]['losses'] += 1
                    print(f"🏆 {winner.name} 胜")
                else:
                    player1.record_draw()
                    player2.record_draw()
                    results[player1.name]['draws'] += 1
                    results[player2.name]['draws'] += 1
                    print(f"🏆 平局")
        
        # 输出排行榜
        print(f"\n{'='*50}")
        print(f"🏆 锦标赛排行榜")
        print(f"{'='*50}")
        
        # 按胜率排序
        sorted_players = sorted(self.players, key=lambda p: p.get_stats()['win_rate'], reverse=True)
        
        for rank, player in enumerate(sorted_players, 1):
            stats = player.get_stats()
            print(f"{rank}. {player.name}: {stats['wins']}胜 {stats['losses']}负 {stats['draws']}平 (胜率: {stats['win_rate']:.1f}%)")
        
        return results
    
    def run(self, mode: str = "single"):
        """
        运行游戏
        """
        self.running = True
        
        print("🎮 多智能体协作围棋对弈系统")
        print("=" * 50)
        
        # 初始化棋手
        self.init_players()
        
        # 初始化游戏
        self.init_game(mode)
        
        if mode == "single":
            # 单局对弈
            if len(self.players) >= 2:
                result = self.play_single_game(self.players[0], self.players[1])
                print(f"\n最终结果: {result}")
        
        elif mode == "tournament":
            # 锦标赛模式
            results = self.play_tournament()
        
        elif mode == "round_robin":
            # 循环赛模式
            print(f"\n{'='*50}")
            print(f"🔄 循环赛模式")
            print(f"{'='*50}")
            
            # 每个棋手与其他所有棋手对弈
            for i in range(len(self.players)):
                for j in range(i + 1, len(self.players)):
                    player1 = self.players[i]
                    player2 = self.players[j]
                    
                    print(f"\n--- {player1.name} vs {player2.name} ---")
                    result = self.play_single_game(player1, player2)
                    print(f"结果: {result}")
        
        # 游戏结束
        self.end_game()
    
    def end_game(self):
        """游戏结束"""
        print(f"\n{'='*50}")
        print(f"🏁 所有比赛结束")
        print(f"{'='*50}")
        
        # 输出所有棋手统计
        print(f"\n📊 棋手统计:")
        for player in self.players:
            stats = player.get_stats()
            print(f"  {player.name}: {stats['wins']}胜 {stats['losses']}负 {stats['draws']}平 (胜率: {stats['win_rate']:.1f}%)")
        
        # 保存游戏日志
        log_file = Path(__file__).parent / "game_log.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(self.game_log, f, ensure_ascii=False, indent=2)
        
        print(f"\n📝 棋谱已保存: {log_file}")
        
        self.running = False


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='多智能体协作围棋对弈系统')
    parser.add_argument('--mode', choices=['single', 'tournament', 'round_robin'], 
                       default='single', help='比赛模式')
    args = parser.parse_args()
    
    # 创建游戏实例
    game = GoGame(agent_id="lobster-001")
    
    # 运行游戏
    game.run(mode=args.mode)
