#!/usr/bin/env python3
"""
多智能体协作密室逃脱 - 测试脚本
测试密室引擎、通信总线、智能体系统
"""

import sys
import os
import json
import time

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.room import EscapeRoom
from communication.nfs_bus import NFSMessageBus
from agents.base import create_agents


def test_room():
    """测试密室引擎"""
    print("=" * 50)
    print("📋 测试 1: 密室引擎")
    print("=" * 50)
    
    room = EscapeRoom(5)
    print("\n初始密室地图:")
    print(room.display())
    
    # 添加玩家
    print("\n--- 添加玩家 ---")
    room.add_player("lobster-001", "虾尔", "detective")
    room.add_player("hermes", "诸葛马", "engineer")
    print("✅ 玩家添加成功")
    
    # 移动玩家
    print("\n--- 移动玩家 ---")
    room.move_player("lobster-001", 0, 1)
    room.move_player("hermes", 1, 0)
    print("✅ 玩家移动成功")
    
    # 显示状态
    print("\n--- 游戏状态 ---")
    state = room.get_game_state()
    print(f"房间大小: {state['size']}x{state['size']}")
    print(f"访问房间: {state['rooms_visited']}")
    print(f"解决谜题: {state['puzzles_solved']}/{state['total_puzzles']}")
    print(f"收集线索: {state['clues_collected']}/{state['total_clues']}")
    
    # 显示地图
    print("\n--- 密室地图（已探索） ---")
    print(room.display())
    
    print("✅ 密室引擎测试通过\n")


def test_agents():
    """测试智能体系统"""
    print("=" * 50)
    print("📋 测试 2: 智能体系统")
    print("=" * 50)
    
    agents = create_agents()
    
    print("\n--- 智能体列表 ---")
    for agent in agents:
        print(f"{agent.name} ({agent.role}) - 技能: {', '.join(agent.skills)}")
    
    # 测试智能体行为
    print("\n--- 测试智能体行为 ---")
    room = EscapeRoom(5)
    room.add_player("lobster-001", "虾尔", "detective")
    
    agent = agents[0]  # 侦探
    agent.location = (0, 0)
    
    # 测试移动
    move = agent.choose_move(room)
    if move:
        print(f"{agent.name} 选择移动到: {move}")
    
    # 测试收集线索
    current_room = room.get_room(*agent.location)
    if current_room:
        clue_id = agent.choose_clue(current_room)
        if clue_id:
            print(f"{agent.name} 选择收集线索: {clue_id}")
    
    # 测试解决谜题
    if current_room:
        puzzle_id = agent.choose_puzzle(current_room)
        if puzzle_id:
            print(f"{agent.name} 选择解决谜题: {puzzle_id}")
    
    print("✅ 智能体系统测试通过\n")


def test_communication():
    """测试通信总线"""
    print("=" * 50)
    print("📋 测试 3: 通信总线")
    print("=" * 50)
    
    bus = NFSMessageBus(agent_id="test-lobster")
    
    # 测试发送消息
    print("\n--- 测试发送消息 ---")
    test_msg = {
        'type': 'room_init',
        'room_id': 'escape-room-20260603',
        'size': 5,
        'players': ['lobster-001', 'hermes']
    }
    msg_id = bus.send_message(test_msg)
    print(f"发送消息 ID: {msg_id}")
    
    # 测试保存密室状态
    print("\n--- 测试保存密室状态 ---")
    room_state = {
        'size': 5,
        'players_visited': 2,
        'puzzles_solved': 1,
        'clues_collected': 3
    }
    bus.save_room_state(room_state)
    print("密室状态已保存")
    
    # 测试加载密室状态
    print("\n--- 测试加载密室状态 ---")
    loaded_state = bus.load_room_state()
    if loaded_state:
        print(f"加载密室状态: {loaded_state}")
    
    # 测试提交线索
    print("\n--- 测试提交线索 ---")
    clue_data = {
        'clue_id': 'clue_0_1',
        'collector': '虾尔',
        'location': (0, 1),
        'content': '一本古老的日记',
        'timestamp': time.time()
    }
    clue_id = bus.submit_clue(clue_data)
    print(f"提交线索 ID: {clue_id}")
    
    # 测试获取待处理线索
    print("\n--- 测试获取待处理线索 ---")
    pending_clues = bus.get_pending_clues()
    print(f"待处理线索数: {len(pending_clues)}")
    
    # 测试记录谜题事件
    print("\n--- 测试记录谜题事件 ---")
    event = {
        'type': 'puzzle_solved',
        'agent': '虾尔',
        'puzzle_id': 'puzzle_0_1',
        'location': (0, 1),
        'timestamp': time.time()
    }
    bus.log_puzzle_event(event)
    print("事件已记录")
    
    print("✅ 通信总线测试通过\n")


def test_collaboration():
    """测试协作模式"""
    print("=" * 50)
    print("📋 测试 4: 协作模式")
    print("=" * 50)
    
    room = EscapeRoom(5)
    agents = create_agents()
    
    # 添加所有玩家
    for agent in agents:
        room.add_player(agent.agent_id, agent.name, agent.role)
    
    print(f"\n--- 协作模式: {len(agents)} 个智能体 ---")
    print("\n初始密室地图:")
    print(room.display())
    
    # 模拟协作过程
    for turn in range(10):
        print(f"\n--- 第 {turn + 1} 回合 ---")
        
        for agent in agents:
            # 移动
            move = agent.choose_move(room)
            if move:
                room.move_player(agent.agent_id, move[0], move[1])
                agent.location = move
                room_obj = room.get_room(move[0], move[1])
                print(f"🚶 {agent.name} 移动到: {room_obj.name}")
            
            # 收集线索
            current_room = room.get_room(*agent.location)
            if current_room:
                clue_id = agent.choose_clue(current_room)
                if clue_id:
                    room.collect_clue(agent.agent_id, clue_id)
                    print(f"🔍 {agent.name} 收集了线索")
            
            # 解决谜题
            if current_room:
                puzzle_id = agent.choose_puzzle(current_room)
                if puzzle_id:
                    import random
                    if random.random() < 0.7:
                        room.solve_puzzle(agent.agent_id, puzzle_id, "correct_answer")
                        print(f"🧩 {agent.name} 解决了谜题")
        
        # 显示状态
        state = room.get_game_state()
        print(f"📊 状态: 访问{state['rooms_visited']}室 | 解{state['puzzles_solved']}/{state['total_puzzles']}题 | 集{state['clues_collected']}/{state['total_clues']}线索")
        
        # 显示地图
        print(room.display())
    
    print("✅ 协作模式测试通过\n")


def main():
    """运行所有测试"""
    print("🎮 多智能体协作密室逃脱系统 - 测试套件")
    print("=" * 50)
    
    try:
        test_room()
        test_agents()
        test_communication()
        test_collaboration()
        
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
