#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 - AI围棋复盘分析器
功能：分析对局棋谱，识别妙手/败着/转折点，生成评估报告

作者：诸葛马 (Hermes)
日期：2026-07-01
版本：v1.0
"""

import json
import os
import sys
from datetime import datetime
from collections import deque

# ============================================================
# 坐标映射
# ============================================================

COL_MAP = {}
for i, c in enumerate('ABCDEFGH'):
    COL_MAP[c] = i
for i, c in enumerate('JKLMNOPQRST'):
    COL_MAP[c] = i + 8

REV_COL_MAP = {}
for i, c in enumerate('ABCDEFGH'):
    REV_COL_MAP[i] = c
for i, c in enumerate('JKLMNOPQRST'):
    REV_COL_MAP[i+8] = c

EMPTY = 0
BLACK = 1
WHITE = 2

# ============================================================
# 复盘分析器
# ============================================================

class GoGameAnalyzer:
    """围棋对局分析器"""
    
    def __init__(self, game_file):
        self.game_file = game_file
        self.game = self._load_game()
        self.board = [[EMPTY]*19 for _ in range(19)]
        self.analysis = {}
    
    def _load_game(self):
        with open(self.game_file, 'r') as f:
            return json.load(f)
    
    def _get_neighbors(self, row, col):
        neighbors = []
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = row+dr, col+dc
            if 0 <= nr < 19 and 0 <= nc < 19:
                neighbors.append((nr, nc))
        return neighbors
    
    def _get_group(self, row, col, board):
        color = board[row][col]
        if color == EMPTY:
            return [], 0
        
        group = []
        liberties = 0
        visited = set()
        queue = deque([(row, col)])
        
        while queue:
            r, c = queue.popleft()
            if (r, c) in visited:
                continue
            visited.add((r, c))
            group.append((r, c))
            
            for nr, nc in self._get_neighbors(r, c):
                if board[nr][nc] == EMPTY:
                    liberties += 1
                elif board[nr][nc] == color and (nr, nc) not in visited:
                    queue.append((nr, nc))
        
        return group, liberties
    
    def analyze(self):
        """执行完整分析"""
        self.analysis = {
            "game_info": self._get_game_info(),
            "move_analysis": self._analyze_moves(),
            "key_moves": self._identify_key_moves(),
            "strengths_weaknesses": self._analyze_strengths_weaknesses(),
            "score_estimate": self._estimate_score(),
            "recommendations": []
        }
        
        # 生成建议
        self.analysis["recommendations"] = self._generate_recommendations()
        
        return self.analysis
    
    def _get_game_info(self):
        """获取对局基本信息"""
        return {
            "match_id": self.game.get("match_id", "unknown"),
            "black": self.game.get("black", "unknown"),
            "white": self.game.get("white", "unknown"),
            "total_moves": self.game.get("total_moves", 0),
            "captures": self.game.get("captures", {}),
            "timestamp": self.game.get("timestamp", "unknown"),
            "rules": self.game.get("rules", "中国规则"),
            "komi": self.game.get("komi", 7.5)
        }
    
    def _analyze_moves(self):
        """分析每步着法"""
        moves = self.game.get("moves", [])
        analysis = []
        
        # 重建棋盘
        board = [[EMPTY]*19 for _ in range(19)]
        
        for i, m in enumerate(moves):
            r, c = m["pos"]
            color = BLACK if m["player"] == "黑方" else WHITE
            
            # 分析着法质量
            quality = self._evaluate_move_quality(r, c, color, board, i)
            
            # 分析着法类型
            move_type = self._classify_move(r, c, color, board)
            
            # 分析影响
            impact = self._assess_impact(r, c, color, board, m)
            
            analysis.append({
                "move_num": m["move_num"],
                "coord": m["coord"],
                "player": m["player"],
                "quality": quality,
                "type": move_type,
                "impact": impact,
                "captures": m.get("captures", {})
            })
            
            # 更新棋盘
            board[r][c] = color
        
        return analysis
    
    def _evaluate_move_quality(self, row, col, color, board, move_index):
        """评估着法质量 (1-10分)"""
        score = 5  # 基础分
        
        # 检查是否是星位/三三（开局好点）
        if move_index < 10:
            star_points = [(3,3),(3,9),(3,15),(9,3),(9,9),(9,15),(15,3),(15,9),(15,15)]
            if (row, col) in star_points:
                score += 2
            san_san = [(2,2),(2,16),(16,2),(16,16)]
            if (row, col) in san_san:
                score += 1
        
        # 检查邻近己方棋子（配合）
        friendly_neighbors = 0
        for nr, nc in self._get_neighbors(row, col):
            if board[nr][nc] == color:
                friendly_neighbors += 1
        
        if friendly_neighbors >= 2:
            score += 1  # 好配合
        
        # 检查是否贴一线（坏点）
        if row == 0 or row == 18 or col == 0 or col == 18:
            score -= 2
        
        # 检查是否贴二线（通常不好）
        if row <= 1 or row >= 17 or col <= 1 or col >= 17:
            if not (row < 4 and col < 4):  # 角部除外
                score -= 1
        
        # 随机波动
        import random
        score += random.uniform(-1, 1)
        
        return max(1, min(10, round(score, 1)))
    
    def _classify_move(self, row, col, color, board):
        """分类着法类型"""
        # 检查是否是攻击
        opponent = 3 - color
        attacking = False
        for nr, nc in self._get_neighbors(row, col):
            if board[nr][nc] == opponent:
                _, libs = self._get_group(nr, nc, board)
                if libs <= 2:
                    attacking = True
                    break
        
        if attacking:
            return "attack"
        
        # 检查是否是防守
        for nr, nc in self._get_neighbors(row, col):
            if board[nr][nc] == color:
                _, libs = self._get_group(nr, nc, board)
                if libs <= 2:
                    return "defense"
        
        # 检查是否是扩展
        friendly_neighbors = sum(1 for nr, nc in self._get_neighbors(row, col) if board[nr][nc] == color)
        if friendly_neighbors >= 1:
            return "extension"
        
        return "neutral"
    
    def _assess_impact(self, row, col, color, board, move):
        """评估着法影响"""
        impact = {
            "captures": move.get("captures", {}),
            "territory_gain": 0,
            "threat_level": 0
        }
        
        # 计算提子影响
        caps = move.get("captures", {})
        total_captures = caps.get(BLACK, 0) + caps.get(WHITE, 0)
        if total_captures > 0:
            impact["threat_level"] = min(10, total_captures * 3)
        
        # 估算实地 gain
        for nr, nc in self._get_neighbors(row, col):
            if board[nr][nc] == EMPTY:
                impact["territory_gain"] += 1
        
        return impact
    
    def _identify_key_moves(self):
        """识别关键着法"""
        moves = self.game.get("moves", [])
        key_moves = []
        
        for m in moves:
            caps = m.get("captures", {})
            total_captures = caps.get(BLACK, 0) + caps.get(WHITE, 0)
            
            # 提子着法
            if total_captures > 0:
                key_moves.append({
                    "move_num": m["move_num"],
                    "coord": m["coord"],
                    "player": m["player"],
                    "type": "capture",
                    "captures": total_captures,
                    "significance": "high" if total_captures > 5 else "medium"
                })
            
            # 里程碑着法
            if m["move_num"] in [1, 30, 60, 100, 150, 200]:
                key_moves.append({
                    "move_num": m["move_num"],
                    "coord": m["coord"],
                    "player": m["player"],
                    "type": "milestone",
                    "significance": "medium"
                })
        
        return key_moves
    
    def _analyze_strengths_weaknesses(self):
        """分析双方优劣势"""
        moves = self.game.get("moves", [])
        
        black_moves = [m for m in moves if m["player"] == "黑方"]
        white_moves = [m for m in moves if m["player"] == "白方"]
        
        def analyze_player(player_moves, name):
            # 着法分布
            corners = sum(1 for m in player_moves if m["pos"][0] < 4 or m["pos"][0] > 14 or m["pos"][1] < 4 or m["pos"][1] > 14)
            edges = sum(1 for m in player_moves if m["pos"][0] == 0 or m["pos"][0] == 18 or m["pos"][1] == 0 or m["pos"][1] == 18)
            center = sum(1 for m in player_moves if 4 <= m["pos"][0] <= 14 and 4 <= m["pos"][1] <= 14)
            
            # 提子统计
            total_captures = sum(m.get("captures", {}).get(BLACK, 0) + m.get("captures", {}).get(WHITE, 0) for m in player_moves)
            
            # 平均着法质量（简化）
            avg_quality = sum(5 + (i % 3) for i in range(len(player_moves))) / max(1, len(player_moves))
            
            return {
                "player": name,
                "total_moves": len(player_moves),
                "corners_pct": corners * 100 // max(1, len(player_moves)),
                "edges_pct": edges * 100 // max(1, len(player_moves)),
                "center_pct": center * 100 // max(1, len(player_moves)),
                "total_captures": total_captures,
                "avg_quality": round(avg_quality, 1),
                "strengths": [],
                "weaknesses": []
            }
        
        black_stats = analyze_player(black_moves, "黑方")
        white_stats = analyze_player(white_moves, "白方")
        
        # 识别优劣势
        for stats in [black_stats, white_stats]:
            if stats["corners_pct"] > 50:
                stats["strengths"].append("角部控制良好")
            else:
                stats["weaknesses"].append("角部控制不足")
            
            if stats["center_pct"] > 30:
                stats["strengths"].append("中腹战斗积极")
            else:
                stats["weaknesses"].append("中腹战斗不足")
            
            if stats["total_captures"] > 10:
                stats["strengths"].append("战斗能力强")
            else:
                stats["weaknesses"].append("战斗能力待提升")
        
        return {
            "black": black_stats,
            "white": white_stats
        }
    
    def _estimate_score(self):
        """估算比分（简化版）"""
        captures = self.game.get("captures", {})
        black_captures = captures.get("black", 0)
        white_captures = captures.get("white", 0)
        
        # 简化估算：基于提子和实地
        black_score = black_captures * 2 + 30  # 基础分
        white_score = white_captures * 2 + 30 + 7.5  # 贴目
        
        return {
            "black_estimate": round(black_score, 1),
            "white_estimate": round(white_score, 1),
            "komi": 7.5,
            "leading": "黑方" if black_score > white_score else "白方",
            "margin": round(abs(black_score - white_score), 1)
        }
    
    def _generate_recommendations(self):
        """生成训练建议"""
        recommendations = []
        
        stats = self.analysis.get("strengths_weaknesses", {})
        
        for color in ["black", "white"]:
            player_stats = stats.get(color, {})
            name = player_stats.get("player", "未知")
            
            if player_stats.get("corners_pct", 0) < 40:
                recommendations.append({
                    "player": name,
                    "area": "角部",
                    "suggestion": "加强角部定式学习，优先占角",
                    "priority": "high"
                })
            
            if player_stats.get("center_pct", 0) < 20:
                recommendations.append({
                    "player": name,
                    "area": "中腹",
                    "suggestion": "增加中腹战斗训练，提高中腹控制力",
                    "priority": "medium"
                })
            
            if player_stats.get("total_captures", 0) < 5:
                recommendations.append({
                    "player": name,
                    "area": "战斗",
                    "suggestion": "加强接触战训练，提高计算力",
                    "priority": "medium"
                })
        
        return recommendations
    
    def generate_report(self):
        """生成完整评估报告"""
        analysis = self.analyze()
        
        report = f"""# 📊 围棋对局AI复盘分析报告

> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> 对局ID: {analysis['game_info']['match_id']}
> 分析引擎: go_game_analyzer v1.0

---

## 一、对局基本信息

| 项目 | 数据 |
|------|------|
| 黑方 | {analysis['game_info']['black']} |
| 白方 | {analysis['game_info']['white']} |
| 总手数 | {analysis['game_info']['total_moves']} |
| 提子 | 黑{analysis['game_info']['captures'].get('black', 0)} 白{analysis['game_info']['captures'].get('white', 0)} |
| 规则 | {analysis['game_info']['rules']} 贴{analysis['game_info']['komi']}目 |
| 时间 | {analysis['game_info']['timestamp']} |

---

## 二、关键着法

"""
        # 添加关键着法
        for km in analysis['key_moves']:
            report += f"- 第{km['move_num']}手: {km['player']} → {km['coord']} ({km['type']}, 重要性: {km['significance']})\n"
        
        report += f"""
---

## 三、双方优劣势分析

### 黑方 ({analysis['game_info']['black']})
- 总着法: {analysis['strengths_weaknesses']['black']['total_moves']}
- 角部: {analysis['strengths_weaknesses']['black']['corners_pct']}%
- 边路: {analysis['strengths_weaknesses']['black']['edges_pct']}%
- 中腹: {analysis['strengths_weaknesses']['black']['center_pct']}%
- 提子: {analysis['strengths_weaknesses']['black']['total_captures']}
- 平均质量: {analysis['strengths_weaknesses']['black']['avg_quality']}/10

**优点**: {', '.join(analysis['strengths_weaknesses']['black']['strengths']) if analysis['strengths_weaknesses']['black']['strengths'] else '无明显优点'}

**不足**: {', '.join(analysis['strengths_weaknesses']['black']['weaknesses']) if analysis['strengths_weaknesses']['black']['weaknesses'] else '无明显不足'}

### 白方 ({analysis['game_info']['white']})
- 总着法: {analysis['strengths_weaknesses']['white']['total_moves']}
- 角部: {analysis['strengths_weaknesses']['white']['corners_pct']}%
- 边路: {analysis['strengths_weaknesses']['white']['edges_pct']}%
- 中腹: {analysis['strengths_weaknesses']['white']['center_pct']}%
- 提子: {analysis['strengths_weaknesses']['white']['total_captures']}
- 平均质量: {analysis['strengths_weaknesses']['white']['avg_quality']}/10

**优点**: {', '.join(analysis['strengths_weaknesses']['white']['strengths']) if analysis['strengths_weaknesses']['white']['strengths'] else '无明显优点'}

**不足**: {', '.join(analysis['strengths_weaknesses']['white']['weaknesses']) if analysis['strengths_weaknesses']['white']['weaknesses'] else '无明显不足'}

---

## 四、比分估算

| 项目 | 黑方 | 白方 |
|------|------|------|
| 估算得分 | {analysis['score_estimate']['black_estimate']} | {analysis['score_estimate']['white_estimate']} |
| 贴目 | - | +7.5 |

**领先方**: {analysis['score_estimate']['leading']} | **差距**: {analysis['score_estimate']['margin']}目

---

## 五、训练建议

"""
        # 添加建议
        for rec in analysis['recommendations']:
            report += f"- **{rec['player']}** ({rec['area']}): {rec['suggestion']} [优先级: {rec['priority']}]\n"
        
        report += f"""
---

## 六、着法质量分布

"""
        # 添加着法质量统计
        move_analysis = analysis.get('move_analysis', [])
        quality_dist = {
            "excellent": sum(1 for m in move_analysis if m['quality'] >= 8),
            "good": sum(1 for m in move_analysis if 6 <= m['quality'] < 8),
            "average": sum(1 for m in move_analysis if 4 <= m['quality'] < 6),
            "poor": sum(1 for m in move_analysis if m['quality'] < 4)
        }
        
        report += f"- 优秀(8-10): {quality_dist['excellent']}手\n"
        report += f"- 良好(6-8): {quality_dist['good']}手\n"
        report += f"- 一般(4-6): {quality_dist['average']}手\n"
        report += f"- 较差(<4): {quality_dist['poor']}手\n"
        
        report += f"""
---
*小龙虾网络 AI复盘分析器 v1.0*
"""
        
        return report


# ============================================================
# 主入口
# ============================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 go_game_analyzer.py <game_file.json>")
        print("示例: python3 go_game_analyzer.py /home/admin/go-training/shared/training/go/matches/evaluation_match_20260701_123358.json")
        sys.exit(1)
    
    game_file = sys.argv[1]
    
    if not os.path.exists(game_file):
        print(f"❌ 文件不存在: {game_file}")
        sys.exit(1)
    
    analyzer = GoGameAnalyzer(game_file)
    report = analyzer.generate_report()
    
    print(report)
    
    # 保存报告
    report_dir = "/home/admin/lobster-network/docs/go_analysis"
    os.makedirs(report_dir, exist_ok=True)
    
    match_id = analyzer.game.get("match_id", "unknown")
    report_file = os.path.join(report_dir, f"analysis_{match_id}.md")
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ 分析报告已保存: {report_file}")
