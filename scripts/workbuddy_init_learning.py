#!/usr/bin/env python3
"""WorkBuddy 学习模块初始化脚本
初始化 workbuddy 节点的学习状态，启动首个训练会话
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
STATE_DIR = PROJECT_ROOT / "domains" / "learning" / "trainers" / "state"
STATE_DIR.mkdir(parents=True, exist_ok=True)

def init_stock_predict():
    """初始化炒股预测学习状态"""
    state_file = STATE_DIR / "workbuddy_stock_state.json"
    
    if state_file.exists():
        print(f"⏭️ 炒股预测状态已存在: {state_file}")
        return False
    
    state = {
        "student": "workbuddy",
        "student_name": "WorkBuddy 助理龙虾",
        "module": "炒股预测",
        "style": "research_oriented",
        "current_phase": "phase1",
        "completed_count": 0,
        "total_completed": 0,
        "accuracy": 0.0,
        "streak_days": 0,
        "last_training_date": None,
        "phases": {
            "phase1": {"total": 20, "completed": 0, "correct": 0},
            "phase2": {"total": 20, "completed": 0, "correct": 0},
            "phase3": {"total": 20, "completed": 0, "correct": 0},
        },
        "initialized_at": datetime.now().isoformat()
    }
    
    state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2))
    print(f"✅ 炒股预测学习状态已初始化: {state_file}")
    return True

def init_network_protocol():
    """初始化网络协议学习状态"""
    state_file = STATE_DIR / "workbuddy_network_state.json"
    
    if state_file.exists():
        print(f"⏭️ 网络协议状态已存在: {state_file}")
        return False
    
    state = {
        "student": "workbuddy",
        "student_name": "WorkBuddy 助理龙虾",
        "module": "网络协议",
        "style": "research_oriented",
        "current_phase": "ch1",
        "completed_count": 0,
        "total_completed": 0,
        "accuracy": 0.0,
        "streak_days": 0,
        "last_training_date": None,
        "phases": {
            "ch1": {"total": 10, "completed": 0, "correct": 0},
            "ch2": {"total": 10, "completed": 0, "correct": 0},
            "ch3": {"total": 10, "completed": 0, "correct": 0},
            "ch4": {"total": 10, "completed": 0, "correct": 0},
            "ch5": {"total": 10, "completed": 0, "correct": 0},
        },
        "initialized_at": datetime.now().isoformat()
    }
    
    state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2))
    print(f"✅ 网络协议学习状态已初始化: {state_file}")
    return True

def init_drug_discovery():
    """初始化药物发现参与状态"""
    state_file = STATE_DIR / "workbuddy_drug_state.json"
    
    if state_file.exists():
        print(f"⏭️ 药物发现状态已存在: {state_file}")
        return False
    
    state = {
        "student": "workbuddy",
        "student_name": "WorkBuddy 助理龙虾",
        "module": "药物发现",
        "role": "计算化学 + 知识图谱",
        "tasks_completed": 0,
        "knowledge_graph_contributions": 0,
        "screening_contributions": 0,
        "last_active": datetime.now().isoformat(),
        "initialized_at": datetime.now().isoformat()
    }
    
    state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2))
    print(f"✅ 药物发现学习状态已初始化: {state_file}")
    return True


if __name__ == "__main__":
    print("=" * 50)
    print("🦞 WorkBuddy 学习模块初始化")
    print("=" * 50)
    
    summary = {
        "炒股预测": init_stock_predict(),
        "网络协议": init_network_protocol(),
        "药物发现": init_drug_discovery(),
    }
    
    print("\n" + "=" * 50)
    print("📊 模块初始化结果")
    print("=" * 50)
    for module, result in summary.items():
        status = "✅ 已初始化" if result else "⏭️ 已存在"
        print(f"  {module}: {status}")
    
    new_count = sum(1 for v in summary.values() if v)
    skip_count = sum(1 for v in summary.values() if not v)
    print(f"\n总计: {new_count} 新建 / {skip_count} 跳过")
    print(f"状态文件目录: {STATE_DIR}")
