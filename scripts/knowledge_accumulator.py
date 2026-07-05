#!/usr/bin/env python3
"""
知识沉淀系统 (Knowledge Accumulation System)
将训练经验、对局复盘、错误模式转化为可复用知识库

功能:
1. 错误模式提取与分类
2. 对局复盘知识化
3. 训练经验沉淀
4. 知识库检索与推荐

部署:
  python3 scripts/knowledge_accumulator.py <node_id>
  或定时: 0 2 * * * python3 scripts/knowledge_accumulator.py all

作者: 诸葛马 (Hermes)
日期: 2026-06-30
"""

import json
import os
import sys
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import Counter


class KnowledgeAccumulator:
    """知识沉淀引擎"""
    
    # 知识分类体系
    KNOWLEDGE_CATEGORIES = {
        "tactic": {
            "name": "战术知识",
            "subcategories": ["征子", "倒扑", "扑", "枷吃", "接不归", "金鸡独立"],
        },
        "strategy": {
            "name": "战略知识",
            "subcategories": ["布局", "中盘", "官子", "厚薄判断", "攻防转换"],
        },
        "pattern": {
            "name": "棋型知识",
            "subcategories": ["基本棋型", "常见定式", "变化图", "手筋"],
        },
        "meta": {
            "name": "元认知知识",
            "subcategories": ["错误模式", "解题思路", "时间管理", "心态调整"],
        },
    }
    
    def __init__(self, node_id: str, base_dir: str = "/home/admin/lobster-network"):
        self.node_id = node_id
        self.base_dir = Path(base_dir)
        self.knowledge_dir = self.base_dir / "knowledge" / node_id
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
        self.global_knowledge_dir = self.base_dir / "knowledge" / "global"
        self.global_knowledge_dir.mkdir(parents=True, exist_ok=True)
        
        self.results_dir = self.base_dir / "results" / node_id
        
        # 知识库索引
        self.index_file = self.knowledge_dir / "knowledge_index.json"
        self.index = self.load_index()
    
    def load_index(self) -> Dict:
        """加载知识索引"""
        if self.index_file.exists():
            try:
                return json.loads(self.index_file.read_text())
            except:
                pass
        return {
            "node_id": self.node_id,
            "created_at": datetime.now().isoformat(),
            "entries": [],
            "categories": {},
            "total_entries": 0,
        }
    
    def save_index(self):
        """保存知识索引"""
        self.index["total_entries"] = len(self.index["entries"])
        self.index["updated_at"] = datetime.now().isoformat()
        self.index_file.write_text(json.dumps(self.index, indent=2, ensure_ascii=False))
    
    def extract_error_patterns(self) -> List[Dict]:
        """从训练结果中提取错误模式"""
        patterns = []
        
        if not self.results_dir.exists():
            return patterns
        
        # 分析训练文件
        for filepath in sorted(self.results_dir.glob("*training*.json")):
            try:
                data = json.loads(filepath.read_text())
                
                # 提取错误题目
                if "wrong_answers" in data:
                    for wrong in data["wrong_answers"]:
                        pattern = {
                            "id": hashlib.md5(json.dumps(wrong, sort_keys=True).encode()).hexdigest()[:8],
                            "type": "error_pattern",
                            "category": wrong.get("category", "unknown"),
                            "subcategory": wrong.get("subcategory", "unknown"),
                            "problem_id": wrong.get("problem_id", ""),
                            "wrong_answer": wrong.get("wrong_answer", ""),
                            "correct_answer": wrong.get("correct_answer", ""),
                            "explanation": wrong.get("explanation", ""),
                            "source_file": filepath.name,
                            "extracted_at": datetime.now().isoformat(),
                            "node_id": self.node_id,
                            "frequency": 1,
                        }
                        patterns.append(pattern)
                
                # 提取错题统计
                if "statistics" in data:
                    stats = data["statistics"]
                    if stats.get("wrong_count", 0) > 0:
                        pattern = {
                            "id": hashlib.md5(f"{filepath.name}_stats".encode()).hexdigest()[:8],
                            "type": "error_summary",
                            "category": "meta",
                            "subcategory": "错误模式",
                            "total_wrong": stats.get("wrong_count", 0),
                            "accuracy": stats.get("accuracy", 0),
                            "source_file": filepath.name,
                            "extracted_at": datetime.now().isoformat(),
                            "node_id": self.node_id,
                        }
                        patterns.append(pattern)
                        
            except Exception as e:
                pass
        
        return patterns
    
    def extract_game_insights(self) -> List[Dict]:
        """从对局记录中提取知识"""
        insights = []
        
        if not self.results_dir.exists():
            return insights
        
        for filepath in sorted(self.results_dir.glob("*match*.json")):
            try:
                data = json.loads(filepath.read_text())
                
                insight = {
                    "id": hashlib.md5(filepath.read_text().encode()).hexdigest()[:8],
                    "type": "game_insight",
                    "category": "strategy",
                    "subcategory": data.get("phase", "unknown"),
                    "result": data.get("result", "unknown"),
                    "opponent": data.get("opponent", "unknown"),
                    "key_moves": data.get("key_moves", []),
                    "mistakes": data.get("mistakes", []),
                    "lessons": data.get("lessons", []),
                    "source_file": filepath.name,
                    "extracted_at": datetime.now().isoformat(),
                    "node_id": self.node_id,
                }
                insights.append(insight)
                
            except:
                pass
        
        return insights
    
    def extract_training_experience(self) -> List[Dict]:
        """从训练过程中提取经验"""
        experiences = []
        
        if not self.results_dir.exists():
            return experiences
        
        for filepath in sorted(self.results_dir.glob("*.json")):
            try:
                data = json.loads(filepath.read_text())
                
                # 提取训练元数据
                if "training_metadata" in data:
                    meta = data["training_metadata"]
                    experience = {
                        "id": hashlib.md5(f"{filepath.name}_meta".encode()).hexdigest()[:8],
                        "type": "training_experience",
                        "category": "meta",
                        "subcategory": "解题思路",
                        "strategy": meta.get("strategy", ""),
                        "time_spent": meta.get("time_spent", 0),
                        "hints_used": meta.get("hints_used", 0),
                        "success_rate": meta.get("success_rate", 0),
                        "source_file": filepath.name,
                        "extracted_at": datetime.now().isoformat(),
                        "node_id": self.node_id,
                    }
                    experiences.append(experience)
                    
            except:
                pass
        
        return experiences
    
    def categorize_knowledge(self, knowledge_item: Dict) -> str:
        """知识分类"""
        category = knowledge_item.get("category", "unknown")
        subcategory = knowledge_item.get("subcategory", "unknown")
        
        # 匹配分类体系
        for cat_key, cat_info in self.KNOWLEDGE_CATEGORIES.items():
            if category == cat_key or category in cat_info["subcategories"]:
                return cat_key
            
            if subcategory in cat_info["subcategories"]:
                return cat_key
        
        return "other"
    
    def deduplicate_knowledge(self, new_items: List[Dict]) -> List[Dict]:
        """知识去重"""
        existing_ids = {entry["id"] for entry in self.index.get("entries", [])}
        unique_items = []
        
        for item in new_items:
            if item["id"] not in existing_ids:
                unique_items.append(item)
                existing_ids.add(item["id"])
        
        return unique_items
    
    def accumulate(self) -> Dict:
        """执行知识沉淀"""
        print(f"📚 知识沉淀: {self.node_id}")
        
        # 提取各类知识
        error_patterns = self.extract_error_patterns()
        game_insights = self.extract_game_insights()
        training_exp = self.extract_training_experience()
        
        all_new = error_patterns + game_insights + training_exp
        unique_new = self.deduplicate_knowledge(all_new)
        
        if not unique_new:
            print(f"  ✅ 无新知识需要沉淀")
            return {"status": "no_new_knowledge", "node_id": self.node_id}
        
        # 分类并保存
        categorized = {}
        for item in unique_new:
            category = self.categorize_knowledge(item)
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(item)
            
            # 保存到分类文件
            cat_file = self.knowledge_dir / f"{category}_knowledge.json"
            existing = []
            if cat_file.exists():
                try:
                    existing = json.loads(cat_file.read_text())
                except:
                    pass
            
            existing.extend(categorized[category])
            cat_file.write_text(json.dumps(existing, indent=2, ensure_ascii=False))
            
            # 更新索引
            self.index["entries"].append({
                "id": item["id"],
                "type": item["type"],
                "category": category,
                "subcategory": item.get("subcategory", ""),
                "extracted_at": item.get("extracted_at", ""),
                "file": f"{category}_knowledge.json",
            })
        
        # 更新分类统计
        for cat, items in categorized.items():
            if cat not in self.index["categories"]:
                self.index["categories"][cat] = 0
            self.index["categories"][cat] += len(items)
        
        self.save_index()
        
        # 同步到全局知识库
        self.sync_to_global(unique_new)
        
        result = {
            "status": "completed",
            "node_id": self.node_id,
            "new_entries": len(unique_new),
            "categories": {cat: len(items) for cat, items in categorized.items()},
            "error_patterns": len(error_patterns),
            "game_insights": len(game_insights),
            "training_experiences": len(training_exp),
            "timestamp": datetime.now().isoformat(),
        }
        
        print(f"  📊 沉淀 {len(unique_new)} 条新知识")
        for cat, count in result["categories"].items():
            cat_name = self.KNOWLEDGE_CATEGORIES.get(cat, {}).get("name", cat)
            print(f"    - {cat_name}: {count}条")
        
        return result
    
    def sync_to_global(self, new_items: List[Dict]):
        """同步到全局知识库"""
        global_file = self.global_knowledge_dir / "global_knowledge.json"
        global_index = []
        
        if global_file.exists():
            try:
                global_index = json.loads(global_file.read_text())
            except:
                pass
        
        # 添加来源标记
        for item in new_items:
            item["source_node"] = self.node_id
            global_index.append(item)
        
        # 去重 (保留最近1000条)
        recent = global_index[-1000:]
        global_file.write_text(json.dumps(recent, indent=2, ensure_ascii=False))
    
    def search_knowledge(self, query: str, category: str = None) -> List[Dict]:
        """检索知识库"""
        results = []
        query_lower = query.lower()
        
        # 搜索分类文件
        search_dir = self.knowledge_dir if category is None else self.knowledge_dir / f"{category}_knowledge.json"
        
        files_to_search = [search_dir] if category else list(self.knowledge_dir.glob("*_knowledge.json"))
        
        for filepath in files_to_search:
            if not filepath.exists():
                continue
            try:
                data = json.loads(filepath.read_text())
                for item in data:
                    # 简单文本匹配
                    item_str = json.dumps(item).lower()
                    if query_lower in item_str:
                        results.append(item)
            except:
                pass
        
        return results[:20]  # 返回最多20条
    
    def generate_knowledge_report(self) -> Dict:
        """生成知识报告"""
        report = {
            "node_id": self.node_id,
            "generated_at": datetime.now().isoformat(),
            "total_entries": self.index.get("total_entries", 0),
            "categories": self.index.get("categories", {}),
            "recent_entries": self.index.get("entries", [])[-10:],
        }
        
        return report


def main():
    if len(sys.argv) < 2:
        print("用法: python3 knowledge_accumulator.py <node_id|all>")
        print("示例: python3 knowledge_accumulator.py xiaochen")
        print("      python3 knowledge_accumulator.py all")
        sys.exit(1)
    
    target = sys.argv[1]
    
    if target == "all":
        nodes = ["xiaochen", "zhuguxia", "qoder"]
        print(f"🔄 批量知识沉淀 {len(nodes)} 个节点...")
        
        for node in nodes:
            accumulator = KnowledgeAccumulator(node)
            result = accumulator.accumulate()
            print()
    else:
        accumulator = KnowledgeAccumulator(target)
        accumulator.accumulate()


if __name__ == "__main__":
    main()
