"""
密室引擎
实现密室地图、谜题、线索系统
"""

import json
import random
from enum import Enum
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field


class RoomType(Enum):
    """房间类型"""
    ENTRANCE = "入口"
    STUDY = "书房"
    CORRIDOR = "走廊"
    LABORATORY = "实验室"
    EXIT = "出口"
    STORAGE = "储藏室"
    LIVING_ROOM = "客厅"
    KITCHEN = "厨房"
    BEDROOM = "卧室"
    GARDEN = "花园"
    BASEMENT = "地下室"
    WORKSHOP = "工坊"
    LIBRARY = "图书馆"
    OBSERVATORY = "观察室"
    TOWER = "塔楼"
    DUNGEON = "地牢"
    ALTAR = "祭坛"
    SECRET_ROOM = "密室"
    TREASURE = "宝库"


class PuzzleType(Enum):
    """谜题类型"""
    PASSWORD_LOCK = "密码锁"
    MECHANISM = "机关陷阱"
    LOGIC_PUZZLE = "逻辑推理"
    PATH_FINDING = "路径规划"
    RESOURCE_MANAGEMENT = "资源管理"


class ClueType(Enum):
    """线索类型"""
    DOCUMENT = "文献"
    CODE = "密码"
    MECHANISM = "机关"
    MAP = "地图"
    ITEM = "物品"


@dataclass
class Clue:
    """线索"""
    clue_id: str
    clue_type: ClueType
    content: str
    location: Tuple[int, int]  # (row, col)
    required_skill: Optional[str] = None  # 需要的技能
    is_collected: bool = False
    collector: Optional[str] = None


@dataclass
class Puzzle:
    """谜题"""
    puzzle_id: str
    puzzle_type: PuzzleType
    location: Tuple[int, int]  # (row, col)
    difficulty: int  # 1-5
    solution: str
    required_skills: List[str] = field(default_factory=list)
    is_solved: bool = False
    solver: Optional[str] = None
    hint: str = ""


@dataclass
class Room:
    """房间"""
    row: int
    col: int
    room_type: RoomType
    name: str
    description: str
    is_locked: bool = False
    requires_key: bool = False
    key_location: Optional[Tuple[int, int]] = None
    puzzles: List[Puzzle] = field(default_factory=list)
    clues: List[Clue] = field(default_factory=list)
    is_visited: bool = False


class EscapeRoom:
    """密室逃脱系统"""
    
    def __init__(self, size: int = 5):
        self.size = size
        self.grid = [[None for _ in range(size)] for _ in range(size)]
        self.players: Dict[str, Dict] = {}
        self.game_log: List[Dict] = []
        self.items: Dict[str, Dict] = {}  # 物品系统
        self.keys: Dict[str, Tuple[int, int]] = {}  # 钥匙位置
        self.exit_location: Tuple[int, int] = (4, 4)  # 出口位置
        self.entrance_location: Tuple[int, int] = (0, 0)  # 入口位置
        
        self._initialize_room()
    
    def _initialize_room(self):
        """初始化密室"""
        # 定义房间布局
        room_layout = [
            [RoomType.ENTRANCE, RoomType.STUDY, RoomType.CORRIDOR, RoomType.LABORATORY, RoomType.EXIT],
            [RoomType.STORAGE, RoomType.LIVING_ROOM, RoomType.KITCHEN, RoomType.BEDROOM, RoomType.GARDEN],
            [RoomType.BASEMENT, RoomType.WORKSHOP, RoomType.LIBRARY, RoomType.OBSERVATORY, RoomType.TOWER],
            [RoomType.DUNGEON, RoomType.ALTAR, RoomType.SECRET_ROOM, RoomType.TREASURE, RoomType.EXIT],
            [RoomType.ENTRANCE, RoomType.STUDY, RoomType.CORRIDOR, RoomType.LABORATORY, RoomType.EXIT],
        ]
        
        # 创建房间
        for r in range(self.size):
            for c in range(self.size):
                room_type = room_layout[r][c]
                room = Room(
                    row=r,
                    col=c,
                    room_type=room_type,
                    name=room_type.value,
                    description=self._get_room_description(room_type)
                )
                
                # 添加谜题
                if random.random() < 0.4:  # 40%概率有谜题
                    puzzle = self._create_puzzle(r, c)
                    room.puzzles.append(puzzle)
                
                # 添加线索
                if random.random() < 0.5:  # 50%概率有线索
                    clue = self._create_clue(r, c)
                    room.clues.append(clue)
                
                # 某些房间需要钥匙
                if room_type in [RoomType.SECRET_ROOM, RoomType.TREASURE, RoomType.TOWER]:
                    room.is_locked = True
                    room.requires_key = True
                    # 钥匙放在随机位置
                    key_r, key_c = random.randint(0, self.size-1), random.randint(0, self.size-1)
                    room.key_location = (key_r, key_c)
                    self.keys[f"key_{r}_{c}"] = (key_r, key_c)
                
                self.grid[r][c] = room
    
    def _get_room_description(self, room_type: RoomType) -> str:
        """获取房间描述"""
        descriptions = {
            RoomType.ENTRANCE: "密室的入口，光线昏暗",
            RoomType.STUDY: "书房，书架上摆满了古籍",
            RoomType.CORRIDOR: "长长的走廊，墙壁上有奇怪的符号",
            RoomType.LABORATORY: "实验室，桌上有各种化学试剂",
            RoomType.EXIT: "出口！但需要密码才能打开",
            RoomType.STORAGE: "储藏室，堆放着各种杂物",
            RoomType.LIVING_ROOM: "客厅，壁炉里还有余温",
            RoomType.KITCHEN: "厨房，空气中弥漫着奇怪的味道",
            RoomType.BEDROOM: "卧室，床上有未整理过的痕迹",
            RoomType.GARDEN: "花园，植物茂盛但有些诡异",
            RoomType.BASEMENT: "地下室，阴冷潮湿",
            RoomType.WORKSHOP: "工坊，桌上有各种工具",
            RoomType.LIBRARY: "图书馆，书架上有很多珍贵的文献",
            RoomType.OBSERVATORY: "观察室，有望远镜和星图",
            RoomType.TOWER: "塔楼，可以俯瞰整个密室",
            RoomType.DUNGEON: "地牢，墙壁上有抓痕",
            RoomType.ALTAR: "祭坛，上面有奇怪的符号",
            RoomType.SECRET_ROOM: "密室，隐藏着重要的秘密",
            RoomType.TREASURE: "宝库，据说有逃脱的关键物品",
        }
        return descriptions.get(room_type, "一个神秘的房间")
    
    def _create_puzzle(self, row: int, col: int) -> Puzzle:
        """创建谜题"""
        puzzle_types = [PuzzleType.PASSWORD_LOCK, PuzzleType.MECHANISM, 
                       PuzzleType.LOGIC_PUZZLE, PuzzleType.PATH_FINDING]
        puzzle_type = random.choice(puzzle_types)
        
        solutions = {
            PuzzleType.PASSWORD_LOCK: "42",
            PuzzleType.MECHANISM: "顺时针旋转3圈",
            PuzzleType.LOGIC_PUZZLE: "答案是B",
            PuzzleType.PATH_FINDING: "向北走3步",
        }
        
        hints = {
            PuzzleType.PASSWORD_LOCK: "密码与生命、宇宙及一切有关",
            PuzzleType.MECHANISM: "注意齿轮的转动方向",
            PuzzleType.LOGIC_PUZZLE: "仔细阅读墙上的文字",
            PuzzleType.PATH_FINDING: "跟随地上的脚印",
        }
        
        skills_map = {
            PuzzleType.PASSWORD_LOCK: ["scholar"],
            PuzzleType.MECHANISM: ["engineer"],
            PuzzleType.LOGIC_PUZZLE: ["detective"],
            PuzzleType.PATH_FINDING: ["guide"],
        }
        
        return Puzzle(
            puzzle_id=f"puzzle_{row}_{col}",
            puzzle_type=puzzle_type,
            location=(row, col),
            difficulty=random.randint(1, 3),
            solution=solutions[puzzle_type],
            required_skills=skills_map[puzzle_type],
            hint=hints[puzzle_type]
        )
    
    def _create_clue(self, row: int, col: int) -> Clue:
        """创建线索"""
        clue_types = [ClueType.DOCUMENT, ClueType.CODE, ClueType.MECHANISM, 
                     ClueType.MAP, ClueType.ITEM]
        clue_type = random.choice(clue_types)
        
        contents = {
            ClueType.DOCUMENT: "一本古老的日记，记载着密室的秘密",
            ClueType.CODE: "墙上刻着一串数字：42",
            ClueType.MECHANISM: "一个复杂的齿轮装置",
            ClueType.MAP: "一张密室地图，标记着出口位置",
            ClueType.ITEM: "一把古老的钥匙",
        }
        
        skills_map = {
            ClueType.DOCUMENT: "scholar",
            ClueType.CODE: "detective",
            ClueType.MECHANISM: "engineer",
            ClueType.MAP: "guide",
            ClueType.ITEM: None,
        }
        
        return Clue(
            clue_id=f"clue_{row}_{col}",
            clue_type=clue_type,
            content=contents[clue_type],
            location=(row, col),
            required_skill=skills_map[clue_type]
        )
    
    def add_player(self, player_id: str, name: str, role: str):
        """添加玩家"""
        self.players[player_id] = {
            'name': name,
            'role': role,
            'location': self.entrance_location,
            'inventory': [],
            'solved_puzzles': [],
            'collected_clues': [],
            'is_alive': True
        }
        self.log_event('player_join', player_id, f"{name} 加入游戏")
    
    def move_player(self, player_id: str, row: int, col: int) -> bool:
        """移动玩家"""
        if player_id not in self.players:
            return False
        
        player = self.players[player_id]
        
        # 检查边界
        if not (0 <= row < self.size and 0 <= col < self.size):
            return False
        
        room = self.grid[row][col]
        
        # 检查房间是否锁定
        if room.is_locked and room.requires_key:
            key_id = f"key_{row}_{col}"
            if key_id not in player['inventory']:
                return False
        
        # 移动
        old_location = player['location']
        player['location'] = (row, col)
        room.is_visited = True
        
        self.log_event('player_move', player_id, 
                      f"{player['name']} 从 {old_location} 移动到 {room.name}")
        return True
    
    def collect_clue(self, player_id: str, clue_id: str) -> bool:
        """收集线索"""
        if player_id not in self.players:
            return False
        
        player = self.players[player_id]
        row, col = player['location']
        room = self.grid[row][col]
        
        # 查找线索
        for clue in room.clues:
            if clue.clue_id == clue_id and not clue.is_collected:
                # 检查技能要求
                if clue.required_skill:
                    if player['role'] != clue.required_skill:
                        # 需要协作
                        return False
                
                clue.is_collected = True
                clue.collector = player_id
                player['collected_clues'].append(clue_id)
                
                self.log_event('clue_collected', player_id, 
                             f"{player['name']} 收集了线索: {clue.content[:20]}...")
                return True
        
        return False
    
    def solve_puzzle(self, player_id: str, puzzle_id: str, solution: str) -> bool:
        """解决谜题"""
        if player_id not in self.players:
            return False
        
        player = self.players[player_id]
        row, col = player['location']
        room = self.grid[row][col]
        
        # 查找谜题
        for puzzle in room.puzzles:
            if puzzle.puzzle_id == puzzle_id and not puzzle.is_solved:
                # 检查技能要求
                if player['role'] not in puzzle.required_skills:
                    # 需要协作
                    return False
                
                # 检查答案
                if solution == puzzle.solution:
                    puzzle.is_solved = True
                    puzzle.solver = player_id
                    player['solved_puzzles'].append(puzzle_id)
                    
                    # 如果是密码锁谜题，可能获得钥匙
                    if puzzle.puzzle_type == PuzzleType.PASSWORD_LOCK:
                        key_id = f"key_{row}_{col}"
                        if key_id in self.keys:
                            player['inventory'].append(key_id)
                            self.log_event('item_obtained', player_id, 
                                         f"{player['name']} 获得了钥匙")
                    
                    self.log_event('puzzle_solved', player_id, 
                                 f"{player['name']} 解决了谜题: {puzzle.puzzle_type.value}")
                    return True
        
        return False
    
    def check_escape(self, player_id: str) -> bool:
        """检查是否逃脱成功"""
        if player_id not in self.players:
            return False
        
        player = self.players[player_id]
        if player['location'] == self.exit_location:
            # 需要解决所有谜题
            all_solved = all(
                puzzle.is_solved 
                for row in self.grid 
                for room in row 
                for puzzle in room.puzzles
            )
            
            if all_solved:
                self.log_event('escape_success', player_id, 
                             f"{player['name']} 成功逃脱！")
                return True
        
        return False
    
    def get_room(self, row: int, col: int) -> Optional[Room]:
        """获取房间"""
        if 0 <= row < self.size and 0 <= col < self.size:
            return self.grid[row][col]
        return None
    
    def get_nearby_rooms(self, row: int, col: int) -> List[Tuple[int, int]]:
        """获取相邻房间"""
        nearby = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if 0 <= nr < self.size and 0 <= nc < self.size:
                nearby.append((nr, nc))
        return nearby
    
    def log_event(self, event_type: str, player_id: str, description: str):
        """记录事件"""
        event = {
            'type': event_type,
            'player_id': player_id,
            'description': description,
            'timestamp': __import__('time').time()
        }
        self.game_log.append(event)
    
    def get_game_state(self) -> Dict:
        """获取游戏状态"""
        return {
            'size': self.size,
            'players': {pid: {
                'name': p['name'],
                'role': p['role'],
                'location': p['location'],
                'inventory': p['inventory'],
                'solved_puzzles': len(p['solved_puzzles']),
                'collected_clues': len(p['collected_clues'])
            } for pid, p in self.players.items()},
            'rooms_visited': sum(1 for row in self.grid for room in row if room.is_visited),
            'puzzles_solved': sum(1 for row in self.grid for room in row 
                                 for puzzle in room.puzzles if puzzle.is_solved),
            'clues_collected': sum(1 for row in self.grid for room in row 
                                  for clue in room.clues if clue.is_collected),
            'total_puzzles': sum(len(room.puzzles) for row in self.grid for room in row),
            'total_clues': sum(len(room.clues) for row in self.grid for room in row),
        }
    
    def display(self) -> str:
        """显示密室地图"""
        lines = []
        lines.append("┌" + "──┬" * (self.size - 1) + "──┐")
        
        for r in range(self.size):
            row_str = "│"
            for c in range(self.size):
                room = self.grid[r][c]
                if room.is_visited:
                    if room.is_locked:
                        row_str += " 🔒"
                    else:
                        row_str += f" {room.name[:2]}"
                else:
                    row_str += " ？ "
                row_str += "│"
            lines.append(row_str)
            
            if r < self.size - 1:
                lines.append("├" + "──┼" * (self.size - 1) + "──┤")
        
        lines.append("└" + "──┴" * (self.size - 1) + "──┘")
        
        return "\n".join(lines)


if __name__ == '__main__':
    room = EscapeRoom(5)
    print("=== 密室地图 ===")
    print(room.display())
    
    # 添加玩家
    room.add_player("lobster-001", "虾尔", "detective")
    room.add_player("hermes", "诸葛马", "engineer")
    
    # 移动玩家
    room.move_player("lobster-001", 0, 1)
    room.move_player("hermes", 1, 0)
    
    print("\n=== 游戏状态 ===")
    state = room.get_game_state()
    print(json.dumps(state, indent=2, ensure_ascii=False))
    
    print("\n=== 密室地图（已探索） ===")
    print(room.display())
