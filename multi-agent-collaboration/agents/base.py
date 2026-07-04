"""
智能体基类
定义智能体的基本行为和属性
"""

import random
from typing import List, Dict, Optional, Tuple
from engine.room import EscapeRoom, Room, Puzzle, Clue


class BaseAgent:
    """智能体基类"""
    
    def __init__(self, agent_id: str, name: str, role: str):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.location: Tuple[int, int] = (0, 0)
        self.inventory: List[str] = []
        self.knowledge: Dict[str, str] = {}  # 知识库
        self.skills: List[str] = []
        self.is_alive: bool = True
    
    def can_solve(self, puzzle: Puzzle) -> bool:
        """检查是否能解决谜题"""
        return self.role in puzzle.required_skills
    
    def can_collect(self, clue: Clue) -> bool:
        """检查是否能收集线索"""
        if clue.required_skill:
            return self.role == clue.required_skill
        return True
    
    def choose_move(self, room: EscapeRoom) -> Optional[Tuple[int, int]]:
        """选择移动位置（子类可重写）"""
        row, col = self.location
        nearby = room.get_nearby_rooms(row, col)
        
        # 优先选择未访问的房间
        unvisited = []
        for r, c in nearby:
            r_obj = room.get_room(r, c)
            if r_obj and not r_obj.is_visited:
                unvisited.append((r, c))
        
        if unvisited:
            return random.choice(unvisited)
        
        # 否则随机选择
        if nearby:
            return random.choice(nearby)
        
        return None
    
    def choose_puzzle(self, room: Room) -> Optional[str]:
        """选择要解决的谜题（子类可重写）"""
        for puzzle in room.puzzles:
            if not puzzle.is_solved and self.can_solve(puzzle):
                return puzzle.puzzle_id
        return None
    
    def choose_clue(self, room: Room) -> Optional[str]:
        """选择要收集的线索（子类可重写）"""
        for clue in room.clues:
            if not clue.is_collected and self.can_collect(clue):
                return clue.clue_id
        return None
    
    def get_state(self) -> Dict:
        """获取智能体状态"""
        return {
            'agent_id': self.agent_id,
            'name': self.name,
            'role': self.role,
            'location': self.location,
            'inventory': self.inventory,
            'knowledge_keys': list(self.knowledge.keys()),
            'skills': self.skills,
            'is_alive': self.is_alive
        }


class DetectiveAgent(BaseAgent):
    """侦探智能体 - 擅长逻辑推理"""
    
    def __init__(self, agent_id: str = "lobster-001", name: str = "虾尔"):
        super().__init__(agent_id, name, "detective")
        self.skills = ["logic_reasoning", "clue_analysis"]
    
    def choose_puzzle(self, room: Room) -> Optional[str]:
        """侦探优先选择逻辑推理谜题"""
        for puzzle in room.puzzles:
            if not puzzle.is_solved and "detective" in puzzle.required_skills:
                return puzzle.puzzle_id
        return super().choose_puzzle(room)


class EngineerAgent(BaseAgent):
    """工程师智能体 - 擅长机械操作"""
    
    def __init__(self, agent_id: str = "hermes", name: str = "诸葛马"):
        super().__init__(agent_id, name, "engineer")
        self.skills = ["mechanism破解", "密码破解"]
    
    def choose_puzzle(self, room: Room) -> Optional[str]:
        """工程师优先选择机关谜题"""
        for puzzle in room.puzzles:
            if not puzzle.is_solved and "engineer" in puzzle.required_skills:
                return puzzle.puzzle_id
        return super().choose_puzzle(room)


class ScholarAgent(BaseAgent):
    """学者智能体 - 擅长知识解读"""
    
    def __init__(self, agent_id: str = "scholar-001", name: str = "学者"):
        super().__init__(agent_id, name, "scholar")
        self.skills = ["古文解读", "知识检索"]
    
    def choose_puzzle(self, room: Room) -> Optional[str]:
        """学者优先选择密码锁谜题"""
        for puzzle in room.puzzles:
            if not puzzle.is_solved and "scholar" in puzzle.required_skills:
                return puzzle.puzzle_id
        return super().choose_puzzle(room)


class GuideAgent(BaseAgent):
    """向导智能体 - 擅长路径规划"""
    
    def __init__(self, agent_id: str = "guide-001", name: str = "向导"):
        super().__init__(agent_id, name, "guide")
        self.skills = ["路径规划", "空间感知"]
    
    def choose_move(self, room: EscapeRoom) -> Optional[Tuple[int, int]]:
        """向导优先选择通往出口的路径"""
        row, col = self.location
        nearby = room.get_nearby_rooms(row, col)
        
        # 计算到出口的距离
        exit_row, exit_col = room.exit_location
        best_move = None
        best_dist = float('inf')
        
        for r, c in nearby:
            r_obj = room.get_room(r, c)
            if r_obj and not r_obj.is_visited:
                dist = abs(r - exit_row) + abs(c - exit_col)
                if dist < best_dist:
                    best_dist = dist
                    best_move = (r, c)
        
        if best_move:
            return best_move
        
        return super().choose_move(room)


def create_agents() -> List[BaseAgent]:
    """创建所有智能体"""
    return [
        DetectiveAgent(),
        EngineerAgent(),
        ScholarAgent(),
        GuideAgent()
    ]


if __name__ == '__main__':
    agents = create_agents()
    
    print("=== 智能体列表 ===")
    for agent in agents:
        print(f"{agent.name} ({agent.role}) - 技能: {', '.join(agent.skills)}")
    
    print("\n=== 智能体状态 ===")
    for agent in agents:
        print(f"{agent.name}: {agent.get_state()}")
