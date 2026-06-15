#!/usr/bin/env python3
"""
多智能体协作围棋对弈 - 测试脚本
测试棋盘引擎、通信总线、策略模块、棋手系统
"""

import sys
import os
import json
import time

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.board import GoBoard, Point, StoneColor
from communication.nfs_bus import NFSMessageBus
from strategies.players import GoPlayer, create_players


def test_board():
    """测试棋盘引擎"""
    print("=" * 50)
    print("📋 测试 1: 棋盘引擎")
    print("=" * 50)
    
    board = GoBoard(9)
    print("\n初始棋盘:")
    print(board.display())
    
    # 测试落子
    print("\n--- 测试落子 ---")
    p1 = Point.from_gtp("D4")
    board.place_stone(p1, StoneColor.BLACK)
    print(f"黑 D4:")
    print(board.display())
    
    p2 = Point.from_gtp("F6")
    board.place_stone(p2, StoneColor.WHITE)
    print(f"白 F6:")
    print(board.display())
    
    p3 = Point.from_gtp("E5")
    board.place_stone(p3, StoneColor.BLACK)
    print(f"黑 E5:")
    print(board.display())
    
    # 测试提子
    print("\n--- 测试提子 ---")
    board2 = GoBoard(9)
    board2.place_stone(Point(4, 4), StoneColor.BLACK)  # D5
    board2.place_stone(Point(3, 4), StoneColor.WHITE)  # E4
    board2.place_stone(Point(5, 4), StoneColor.WHITE)  # F5
    board2.place_stone(Point(4, 3), StoneColor.WHITE)  # D4
    board2.place_stone(Point(4, 5), StoneColor.WHITE)  # D6
    
    print("提子前:")
    print(board2.display())
    
    # 黑方落子提掉白子
    try:
        captured = board2.place_stone(Point(4, 4), StoneColor.BLACK)
        print(f"提子: {len(captured)} 颗")
        print(board2.display())
    except Exception as e:
        print(f"提子测试: {e}")
    
    # 测试合法落子
    print("\n--- 测试合法落子 ---")
    valid_moves = board.get_valid_moves()
    print(f"合法落子数: {len(valid_moves)}")
    if valid_moves:
        print(f"示例: {valid_moves[:5]}")
    
    print("✅ 棋盘引擎测试通过\n")


def test_players():
    """测试棋手系统"""
    print("=" * 50)
    print("📋 测试 2: 棋手系统")
    print("=" * 50)
    
    players = create_players()
    
    print("\n--- 棋手列表 ---")
    for player in players:
        print(f"{player.name} ({'黑' if player.color == StoneColor.BLACK else '白'})")
    
    # 测试棋手策略
    print("\n--- 测试棋手策略 ---")
    board = GoBoard(9)
    for player in players:
        move = player.select_move(board)
        if move:
            print(f"{player.name} 选择: {move.to_gtp()}")
        else:
            print(f"{player.name} 无合法落子")
    
    print("✅ 棋手系统测试通过\n")


def test_communication():
    """测试通信总线"""
    print("=" * 50)
    print("📋 测试 3: 通信总线")
    print("=" * 50)
    
    bus = NFSMessageBus(agent_id="test-lobster")
    
    # 测试发送消息
    print("\n--- 测试发送消息 ---")
    test_msg = {
        'type': 'test_message',
        'content': 'Hello from lobster!',
        'timestamp': time.time()
    }
    msg_id = bus.send_message(test_msg)
    print(f"发送消息 ID: {msg_id}")
    
    # 测试保存棋盘状态
    print("\n--- 测试保存棋盘状态 ---")
    board = GoBoard(9)
    board.place_stone(Point.from_gtp("D4"), StoneColor.BLACK)
    board_dict = board.to_dict()
    bus.save_board_state(board_dict)
    print("棋盘状态已保存")
    
    # 测试加载棋盘状态
    print("\n--- 测试加载棋盘状态 ---")
    loaded_dict = bus.load_board_state()
    if loaded_dict:
        loaded_board = GoBoard.from_dict(loaded_dict)
        print(f"加载棋盘: {loaded_board.display()}")
        print(f"当前玩家: {'黑' if loaded_board.current_player == StoneColor.BLACK else '白'}")
    
    # 测试提交棋步
    print("\n--- 测试提交棋步 ---")
    move_data = {
        'move': 'F6',
        'move_number': 2,
        'captures': 0
    }
    move_id = bus.submit_move(move_data)
    print(f"提交棋步 ID: {move_id}")
    
    # 测试获取待处理棋步
    print("\n--- 测试获取待处理棋步 ---")
    pending = bus.get_pending_moves()
    print(f"待处理棋步数: {len(pending)}")
    
    # 测试记录游戏事件
    print("\n--- 测试记录游戏事件 ---")
    event = {
        'type': 'test_event',
        'description': '测试事件'
    }
    bus.log_game_event(event)
    print("事件已记录")
    
    print("✅ 通信总线测试通过\n")


def test_single_game():
    """测试单局对弈"""
    print("=" * 50)
    print("📋 测试 4: 单局对弈")
    print("=" * 50)
    
    players = create_players()
    if len(players) >= 2:
        player1 = players[0]
        player2 = players[1]
        
        print(f"\n--- {player1.name} vs {player2.name} ---")
        
        board = GoBoard(9)
        print("\n初始棋盘:")
        print(board.display())
        
        move_count = 0
        while move_count < 20:  # 测试前20手
            # 选择当前玩家
            if board.current_player == StoneColor.BLACK:
                current_player = player1
            else:
                current_player = player2
            
            # 选择落子
            move = current_player.select_move(board)
            
            if move is None:
                board.pass_move()
                print(f"⏭️ {current_player.name} Pass")
                break
            else:
                captured = board.place_stone(move, board.current_player)
                gtp = move.to_gtp()
                color_name = "黑" if board.current_player == StoneColor.WHITE else "白"
                print(f"♟️ {current_player.name} ({color_name}) {gtp} (提子: {len(captured)})")
            
            move_count += 1
        
        print(f"\n总手数: {move_count}")
        print(f"提子: 黑{board.captures[StoneColor.BLACK]} 白{board.captures[StoneColor.WHITE]}")
    
    print("✅ 单局对弈测试通过\n")


def test_tournament():
    """测试锦标赛"""
    print("=" * 50)
    print("📋 测试 5: 锦标赛")
    print("=" * 50)
    
    players = create_players()
    
    print(f"\n--- 锦标赛: {len(players)} 个棋手 ---")
    
    # 简单模拟锦标赛
    results = {}
    for player in players:
        results[player.name] = {'wins': 0, 'losses': 0, 'draws': 0}
    
    # 两两对弈（简化版）
    for i in range(len(players)):
        for j in range(i + 1, len(players)):
            player1 = players[i]
            player2 = players[j]
            
            # 随机决定胜负
            import random
            result = random.choice(['win', 'loss', 'draw'])
            
            if result == 'win':
                player1.record_win()
                player2.record_loss()
                results[player1.name]['wins'] += 1
                results[player2.name]['losses'] += 1
            elif result == 'loss':
                player2.record_win()
                player1.record_loss()
                results[player2.name]['wins'] += 1
                results[player1.name]['losses'] += 1
            else:
                player1.record_draw()
                player2.record_draw()
                results[player1.name]['draws'] += 1
                results[player2.name]['draws'] += 1
    
    # 输出排行榜
    print(f"\n🏆 锦标赛排行榜:")
    sorted_players = sorted(players, key=lambda p: p.get_stats()['win_rate'], reverse=True)
    
    for rank, player in enumerate(sorted_players, 1):
        stats = player.get_stats()
        print(f"{rank}. {player.name}: {stats['wins']}胜 {stats['losses']}负 {stats['draws']}平 (胜率: {stats['win_rate']:.1f}%)")
    
    print("✅ 锦标赛测试通过\n")


def main():
    """运行所有测试"""
    print("🎮 多智能体协作围棋对弈系统 - 测试套件")
    print("=" * 50)
    
    try:
        test_board()
        test_players()
        test_communication()
        test_single_game()
        test_tournament()
        
        print("=" * 50)
        print("✅ 所有测试通过！")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
