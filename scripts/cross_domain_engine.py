#!/usr/bin/env python3
"""
跨领域联动系统 (Cross-Domain Collaboration System)
实现围棋训练→金融预测→协议学习的知识迁移与协同

功能:
1. 围棋棋型识别 → 金融K线模式识别
2. 对局策略 → 交易策略
3. 协议学习 → 网络协议理解
4. 跨领域知识图谱

部署:
  python3 scripts/cross_domain_engine.py <domain_pair>
  示例: python3 scripts/cross_domain_engine.py go_stock
        python3 scripts/cross_domain_engine.py go_protocol
        python3 scripts/cross_domain_engine.py all

作者: 诸葛马 (Hermes)
日期: 2026-06-30
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional


class CrossDomainEngine:
    """跨领域联动引擎"""
    
    # 领域映射关系
    DOMAIN_MAPPINGS = {
        "go_stock": {
            "name": "围棋→金融",
            "source": "围棋",
            "target": "金融预测",
            "mappings": [
                {
                    "go_concept": "棋型识别",
                    "stock_concept": "K线模式识别",
                    "transfer_skill": "模式匹配能力",
                    "difficulty": "中",
                    "description": "围棋棋型识别训练的模式匹配能力可直接迁移到K线形态识别",
                },
                {
                    "go_concept": "布局战略",
                    "stock_concept": "仓位管理",
                    "transfer_skill": "全局规划能力",
                    "difficulty": "高",
                    "description": "布局的全局观帮助理解仓位的整体配置",
                },
                {
                    "go_concept": "中盘战斗",
                    "stock_concept": "短线交易",
                    "transfer_skill": "快速决策能力",
                    "difficulty": "中",
                    "description": "中盘战斗的即时判断能力适用于短线交易",
                },
                {
                    "go_concept": "官子计算",
                    "stock_concept": "止盈止损",
                    "transfer_skill": "精确计算能力",
                    "difficulty": "低",
                    "description": "官子的精确计算直接应用于止盈止损点位确定",
                },
                {
                    "go_concept": "厚薄判断",
                    "stock_concept": "风险评估",
                    "transfer_skill": "形势判断能力",
                    "difficulty": "高",
                    "description": "厚薄判断培养的形势感知能力适用于风险评估",
                },
            ],
        },
        "go_protocol": {
            "name": "围棋→协议",
            "source": "围棋",
            "target": "网络协议",
            "mappings": [
                {
                    "go_concept": "规则理解",
                    "protocol_concept": "协议规范",
                    "transfer_skill": "规则学习能力",
                    "difficulty": "低",
                    "description": "围棋规则学习培养的规则理解能力适用于协议规范学习",
                },
                {
                    "go_concept": "定式记忆",
                    "protocol_concept": "标准流程",
                    "transfer_skill": "流程记忆能力",
                    "difficulty": "中",
                    "description": "定式记忆训练的流程记忆能力适用于协议标准流程",
                },
                {
                    "go_concept": "变化图推演",
                    "protocol_concept": "异常处理",
                    "transfer_skill": "分支推理能力",
                    "difficulty": "高",
                    "description": "变化图推演培养的分支推理能力适用于协议异常处理",
                },
                {
                    "go_concept": "对局复盘",
                    "protocol_concept": "日志分析",
                    "transfer_skill": "复盘分析能力",
                    "difficulty": "中",
                    "description": "对局复盘培养的反思能力适用于协议日志分析",
                },
            ],
        },
        "stock_protocol": {
            "name": "金融→协议",
            "source": "金融预测",
            "target": "网络协议",
            "mappings": [
                {
                    "stock_concept": "数据清洗",
                    "protocol_concept": "报文解析",
                    "transfer_skill": "数据处理能力",
                    "difficulty": "中",
                    "description": "金融数据清洗培养的规范化处理能力适用于报文解析",
                },
                {
                    "stock_concept": "趋势预测",
                    "protocol_concept": "流量预测",
                    "transfer_skill": "时间序列分析",
                    "difficulty": "高",
                    "description": "金融趋势预测的时间序列分析方法可迁移到网络流量预测",
                },
            ],
        },
    }
    
    def __init__(self, domain_pair: str, base_dir: str = "/home/admin/lobster-network"):
        self.domain_pair = domain_pair
        self.base_dir = Path(base_dir)
        self.cross_domain_dir = self.base_dir / "knowledge" / "cross_domain"
        self.cross_domain_dir.mkdir(parents=True, exist_ok=True)
        
        self.mapping = self.DOMAIN_MAPPINGS.get(domain_pair, {})
    
    def analyze_transfer_potential(self) -> Dict:
        """分析知识迁移潜力"""
        if not self.mapping:
            return {"error": f"未知领域对: {self.domain_pair}"}
        
        mappings = self.mapping.get("mappings", [])
        
        # 计算迁移难度分布
        difficulty_dist = {"低": 0, "中": 0, "高": 0}
        for m in mappings:
            diff = m.get("difficulty", "中")
            difficulty_dist[diff] = difficulty_dist.get(diff, 0) + 1
        
        # 计算平均难度
        total_diff = sum(
            1 if m.get("difficulty") == "低" else 
            2 if m.get("difficulty") == "中" else 3 
            for m in mappings
        )
        avg_difficulty = total_diff / len(mappings) if mappings else 0
        
        # 评估迁移可行性
        feasibility = "高" if avg_difficulty <= 1.5 else "中" if avg_difficulty <= 2.5 else "低"
        
        return {
            "domain_pair": self.domain_pair,
            "name": self.mapping.get("name", ""),
            "source": self.mapping.get("source", ""),
            "target": self.mapping.get("target", ""),
            "total_mappings": len(mappings),
            "difficulty_distribution": difficulty_dist,
            "average_difficulty": round(avg_difficulty, 2),
            "feasibility": feasibility,
            "mappings": mappings,
            "analyzed_at": datetime.now().isoformat(),
        }
    
    def generate_learning_path(self, student_profile: Dict = None) -> List[Dict]:
        """生成跨领域学习路径"""
        if not self.mapping:
            return []
        
        mappings = self.mapping.get("mappings", [])
        
        # 按难度排序
        sorted_mappings = sorted(mappings, key=lambda x: {
            "低": 1, "中": 2, "高": 3
        }.get(x.get("difficulty", "中"), 2))
        
        # 生成学习路径
        path = []
        for i, mapping in enumerate(sorted_mappings, 1):
            step = {
                "step": i,
                "source_skill": mapping.get("go_concept") or mapping.get("stock_concept", ""),
                "target_skill": mapping.get("stock_concept") or mapping.get("protocol_concept", "") or "",
                "transfer_skill": mapping.get("transfer_skill", ""),
                "difficulty": mapping.get("difficulty", "中"),
                "estimated_hours": 2 if mapping.get("difficulty") == "低" else 4 if mapping.get("difficulty") == "中" else 8,
                "description": mapping.get("description", ""),
                "prerequisites": [p["step"] for p in path if p["difficulty"] in ["低"]] if i > 1 else [],
            }
            path.append(step)
        
        return path
    
    def create_knowledge_graph(self) -> Dict:
        """创建跨领域知识图谱"""
        if not self.mapping:
            return {"error": f"未知领域对: {self.domain_pair}"}
        
        mappings = self.mapping.get("mappings", [])
        
        # 构建图谱节点
        nodes = []
        edges = []
        
        # 源领域节点
        source_domain = self.mapping.get("source", "")
        target_domain = self.mapping.get("target", "")
        
        nodes.append({
            "id": f"{source_domain.lower()}_domain",
            "label": source_domain,
            "type": "domain",
            "color": "#4CAF50",
        })
        
        nodes.append({
            "id": f"{target_domain.lower()}_domain",
            "label": target_domain,
            "type": "domain",
            "color": "#2196F3",
        })
        
        # 映射节点和边
        for mapping in mappings:
            source_concept = mapping.get("go_concept") or mapping.get("stock_concept", "")
            target_concept = mapping.get("stock_concept") or mapping.get("protocol_concept", "") or ""
            transfer_skill = mapping.get("transfer_skill", "")
            
            # 概念节点
            nodes.append({
                "id": f"{source_domain.lower()}_{source_concept}",
                "label": source_concept,
                "type": "concept",
                "domain": source_domain,
            })
            
            nodes.append({
                "id": f"{target_domain.lower()}_{target_concept}",
                "label": target_concept,
                "type": "concept",
                "domain": target_domain,
            })
            
            # 技能节点
            nodes.append({
                "id": f"skill_{transfer_skill}",
                "label": transfer_skill,
                "type": "skill",
                "color": "#FF9800",
            })
            
            # 边
            edges.append({
                "source": f"{source_domain.lower()}_{source_concept}",
                "target": f"skill_{transfer_skill}",
                "label": "培养",
            })
            
            edges.append({
                "source": f"skill_{transfer_skill}",
                "target": f"{target_domain.lower()}_{target_concept}",
                "label": "迁移",
            })
            
            edges.append({
                "source": f"{source_domain.lower()}_domain",
                "target": f"{source_domain.lower()}_{source_concept}",
                "label": "包含",
            })
            
            edges.append({
                "source": f"{target_domain.lower()}_domain",
                "target": f"{target_domain.lower()}_{target_concept}",
                "label": "包含",
            })
        
        return {
            "domain_pair": self.domain_pair,
            "nodes": nodes,
            "edges": edges,
            "generated_at": datetime.now().isoformat(),
        }
    
    def run(self) -> Dict:
        """执行跨领域分析"""
        print(f"🔄 跨领域联动: {self.domain_pair}")
        
        # 分析迁移潜力
        analysis = self.analyze_transfer_potential()
        if "error" in analysis:
            print(f"  ❌ {analysis['error']}")
            return analysis
        
        print(f"  📊 {analysis['name']}")
        print(f"  📈 迁移映射: {analysis['total_mappings']} 个")
        print(f"  🎯 可行性: {analysis['feasibility']}")
        print(f"  📊 难度分布: {analysis['difficulty_distribution']}")
        
        # 生成学习路径
        learning_path = self.generate_learning_path()
        if learning_path:
            print(f"  🗺️ 学习路径: {len(learning_path)} 步")
            for step in learning_path:
                print(f"    {step['step']}. {step['source_skill']} → {step['target_skill']} ({step['difficulty']})")
        
        # 创建知识图谱
        graph = self.create_knowledge_graph()
        
        # 保存结果
        result_file = self.cross_domain_dir / f"{self.domain_pair}_analysis.json"
        result_file.write_text(json.dumps(analysis, indent=2, ensure_ascii=False))
        
        path_file = self.cross_domain_dir / f"{self.domain_pair}_learning_path.json"
        path_file.write_text(json.dumps(learning_path, indent=2, ensure_ascii=False))
        
        graph_file = self.cross_domain_dir / f"{self.domain_pair}_graph.json"
        graph_file.write_text(json.dumps(graph, indent=2, ensure_ascii=False))
        
        print(f"  ✅ 结果已保存: {result_file}")
        
        return {
            "analysis": analysis,
            "learning_path": learning_path,
            "graph_summary": {
                "nodes": len(graph.get("nodes", [])),
                "edges": len(graph.get("edges", [])),
            },
        }


def main():
    if len(sys.argv) < 2:
        print("用法: python3 cross_domain_engine.py <domain_pair|all>")
        print("示例: python3 cross_domain_engine.py go_stock")
        print("      python3 cross_domain_engine.py go_protocol")
        print("      python3 cross_domain_engine.py all")
        sys.exit(1)
    
    target = sys.argv[1]
    
    if target == "all":
        pairs = ["go_stock", "go_protocol", "stock_protocol"]
        print(f"🔄 批量跨领域分析 {len(pairs)} 个领域对...")
        
        all_results = []
        for pair in pairs:
            engine = CrossDomainEngine(pair)
            result = engine.run()
            all_results.append(result)
            print()
        
        # 生成汇总报告
        summary = {
            "generated_at": datetime.now().isoformat(),
            "total_pairs": len(pairs),
            "results": [r.get("analysis", {}) for r in all_results if "analysis" in r or "total_mappings" in r],
        }
        
        summary_file = Path("/home/admin/lobster-network/knowledge/cross_domain/summary.json")
        summary_file.parent.mkdir(parents=True, exist_ok=True)
        summary_file.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
        print(f"📊 汇总报告: {summary_file}")
        
    else:
        engine = CrossDomainEngine(target)
        engine.run()


if __name__ == "__main__":
    main()
