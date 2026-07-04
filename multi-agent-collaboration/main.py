"""
多智能体协作密室逃脱系统 - 主程序
支持多种游戏模式：单人、协作、竞赛
"""

import json
import time
import sys
import os
import random
from typing import List, Dict
from pathlib import Path

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.room import EscapeRoom
from communication.nfs_bus import NFSMessageBus
from agents.base import BaseAgent, create_agents


class EscapeGame:
    """密室逃脱游戏"""
    
    def __init__(self, agent_id: str = "lobster-001"):
        self.agent_id = agent_id
        self.bus = NFSMessageBus(agent_id=agent_id)
        self.room = EscapeRoom(5)
        self.agents: List[BaseAgent] = []
        self.game_id = f"escape-room-{int(time.time())}"
        self.max_turns = 50  # 最大回合数
        self.running = False
        self.game_log: List[Dict] = []
    
    def init_agents(self):
        """初始化智能体"""
        self.agents = create_agents()
        print(f"👥 初始化 {len(self.agents)} 个智能体")
        for agent in self.agents:
            print(f"   {agent.name} ({agent.role}) - 技能: {', '.join(agent.skills)}")
            self.room.add_player(agent.agent_id, agent.name, agent.role)
    
    def init_game(self, mode: str = "single"):
        """初始化游戏"""
        print(f"🎮 初始化游戏: {self.game_id}")
        print(f"   模式: {mode}")
        
        # 发送游戏初始化消息
        init_msg = {
            'type': 'game_init',
            'game_id': self.game_id,
            'mode': mode,
            'agents': [a.name for a in self.agents],
            'room_size': 5,
            'timestamp': time.time()
        }
        self.bus.send_message(init_msg)
        
        # 保存初始密室状态
        self.bus.save_room_state(self.room.get_game_state())
        
        # 记录游戏事件
        self.bus.log_puzzle_event({
            'type': 'game_init',
            'game_id': self.game_id,
            'mode': mode,
            'agents': [a.name for a in self.agents]
        })
        
        print(f"✅ 游戏初始化完成")
        print(f"   游戏 ID: {self.game_id}")
        print(f"   密室大小: 5x5")
        print(f"   智能体数量: {len(self.agents)}")
    
    def play_turn(self, agent: BaseAgent) -> bool:
        """
        执行一个回合
        返回是否继续
        """
        # 1. 移动
        new_location = agent.choose_move(self.room)
        if new_location:
            success = self.room.move_player(agent.agent_id, new_location[0], new_location[1])
            if success:
                agent.location = new_location
                room = self.room.get_room(new_location[0], new_location[1])
                print(f"🚶 {agent.name} 移动到: {room.name}")
        
        # 2. 收集线索
        current_room = self.room.get_room(*agent.location)
        if current_room:
            clue_id = agent.choose_clue(current_room)
            if clue_id:
                success = self.room.collect_clue(agent.agent_id, clue_id)
                if success:
                    print(f"🔍 {agent.name} 收集了线索")
                    # 提交线索到共享目录
                    self.bus.submit_clue({
                        'clue_id': clue_id,
                        'collector': agent.name,
                        'location': agent.location,
                        'timestamp': time.time()
                    })
        
        # 3. 解决谜题
        if current_room:
            puzzle_id = agent.choose_puzzle(current_room)
            if puzzle_id:
                # 模拟解决谜题（随机成功）
                success = random.random() < 0.7  # 70%成功率
                if success:
                    solution = "correct_answer"  # 简化处理
                    success = self.room.solve_puzzle(agent.agent_id, puzzle_id, solution)
                    if success:
                        print(f"🧩 {agent.name} 解决了谜题")
                        # 记录谜题事件
                        self.bus.log_puzzle_event({
                            'type': 'puzzle_solved',
                            'agent': agent.name,
                            'puzzle_id': puzzle_id,
                            'location': agent.location,
                            'timestamp': time.time()
                        })
        
        # 4. 检查逃脱
        if self.room.check_escape(agent.agent_id):
            print(f"🎉 {agent.name} 成功逃脱！")
            return False
        
        return True
    
    def run(self, mode: str = "single"):
        """
        运行游戏
        """
        self.running = True
        
        print("🎮 多智能体协作密室逃脱系统")
        print("=" * 50)
        
        # 初始化智能体
        self.init_agents()
        
        # 初始化游戏
        self.init_game(mode)
        
        # 显示初始密室
        print("\n🗺️ 密室地图:")
        print(self.room.display())
        
        if mode == "single":
            # 单人模式
            self._play_single_mode()
        
        elif mode == "collaboration":
            # 协作模式
            self._play_collaboration_mode()
        
        elif mode == "competition":
            # 竞赛模式
            self._play_competition_mode()
        
        # 游戏结束
        self.end_game()
    
    def _play_single_mode(self):
        """单人模式"""
        print(f"\n{'='*50}")
        print(f"🎮 单人模式")
        print(f"{'='*50}")
        
        agent = self.agents[0]  # 使用第一个智能体
        
        for turn in range(self.max_turns):
            print(f"\n--- 第 {turn + 1} 回合 ---")
            
            if not self.play_turn(agent):
                break
            
            # 显示状态
            state = self.room.get_game_state()
            print(f"📊 状态: 访问{state['rooms_visited']}室 | 解{state['puzzles_solved']}/{state['total_puzzles']}题 | 集{state['clues_collected']}/{state['total_clues']}线索")
            
            # 显示地图
            print(self.room.display())
            
            time.sleep(0.5)
    
    def _play_collaboration_mode(self):
        """协作模式"""
        print(f"\n{'='*50}")
        print(f"🤝 协作模式")
        print(f"{'='*50}")
        
        for turn in range(self.max_turns):
            print(f"\n--- 第 {turn + 1} 回合 ---")
            
            all_alive = True
            for agent in self.agents:
                if not agent.is_alive:
                    continue
                
                print(f"\n🎯 {agent.name} 的回合")
                if not self.play_turn(agent):
                    all_alive = False
                    break
                
                # 显示状态
                state = self.room.get_game_state()
                print(f"📊 状态: 访问{state['rooms_visited']}室 | 解{state['puzzles_solved']}/{state['total_puzzles']}题 | 集{state['clues_collected']}/{state['total_clues']}线索")
            
            # 显示地图
            print(self.room.display())
            
            if not all_alive:
                break
            
            time.sleep(0.5)
    
    def _play_competition_mode(self):
        """竞赛模式"""
        print(f"\n{'='*50}")
        print(f"🏆 竞赛模式")
        print(f"{'='*50}")
        
        scores = {agent.name: 0 for agent in self.agents}
        
        for turn in range(self.max_turns):
            print(f"\n--- 第 {turn + 1} 回合 ---")
            
            for agent in self.agents:
                if not agent.is_alive:
                    continue
                
                print(f"\n🎯 {agent.name} 的回合")
                if not self.play_turn(agent):
                    continue
                
                # 计分
                state = self.room.get_game_state()
                scores[agent.name] = state['puzzles_solved'] * 10 + state['clues_collected'] * 5
            
            # 显示排行榜
            print(f"\n📊 排行榜:")
            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            for rank, (name, score) in enumerate(sorted_scores, 1):
                print(f"  {rank}. {name}: {score}分")
            
            # 显示地图
            print(self.room.display())
            
            time.sleep(0.5)
    
    def end_game(self):
        """游戏结束"""
        print(f"\n{'='*50}")
        print(f"🏁 游戏结束")
        print(f"{'='*50}")
        
        # 输出最终状态
        state = self.room.get_game_state()
        print(f"\n📊 最终状态:")
        print(f"  访问房间: {state['rooms_visited']}/{self.room.size * self.room.size}")
        print(f"  解决谜题: {state['puzzles_solved']}/{state['total_puzzles']}")
        print(f"  收集线索: {state['clues_collected']}/{state['total_clues']}")
        
        # 输出智能体统计
        print(f"\n👥 智能体统计:")
        for agent in self.agents:
            player_state = self.room.players.get(agent.agent_id, {})
            print(f"  {agent.name}: 位置{player_state.get('location', '未知')} | "
                  f"解{len(player_state.get('solved_puzzles', []))}题 | "
                  f"集{len(player_state.get('collected_clues', []))}线索")
        
        # 保存游戏日志
        log_file = Path(__file__).parent / "game_log.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(self.game_log, f, ensure_ascii=False, indent=2)
        
        print(f"\n📝 游戏日志已保存: {log_file}")
        
        self.running = False


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='多智能体协作密室逃脱系统')
    parser.add_argument('--mode', choices=['single', 'collaboration', 'competition'], 
                       default='collaboration', help='游戏模式')
    args = parser.parse_args()
    
    # 创建游戏实例
    game = EscapeGame(agent_id="lobster-001")
    
    # 运行游戏
    game.run(mode=args.mode)
