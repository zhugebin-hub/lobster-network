#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 v1.1 围棋7天速成训练方案
目标：通过高强度训练在7天内提升段位

设计原则：
1. SSH共享替代NFS：使用SCP/SSH进行文件传输
2. 7天紧凑训练：每天高强度训练
3. 实时评估：每天生成评估报告
4. 迭代优化：根据评估结果调整训练

SSH共享架构：
- 本地：/home/admin/go-training/shared/
- 小陈：admin@121.43.80.231:/home/admin/go-training/shared/
- 诸葛虾：admin@172.24.56.3:/home/admin/go-training/shared/

作者：诸葛马 (Hermes)
日期：2026-06-27
"""

import json
import os
import subprocess
from datetime import datetime
from typing import Dict, List, Any

# ═══════════════════════════════════════════════════════════
# SSH共享配置
# ═══════════════════════════════════════════════════════════

SSH_CONFIG = {
    "xiaochen": {
        "host": "121.43.80.231",
        "user": "admin",
        "key": "~/.ssh/id_rsa_hermes",
        "shared_dir": "/home/admin/go-training/shared",
        "to_dir": "to-xiaochen",
        "from_dir": "from-xiaochen",
    },

    "xiaowei": {
        "name": "小薇",
        "type": "基础型",
        "current_level": "30k (零基础)",
        "target_dan": "25k",
        "accuracy_baseline": {"入门": 0.50, "初级": 0.30, "中级": 0.20, "高级": 0.10},
        "problem_count": 0,
        "win_rate": 0.0,
        "strengths": ["零基础学习动力强", "无先入为主错误习惯"],
        "weaknesses": ["完全零基础", "需要从头学习基本规则"],
        "path": ["入门", "15级", "10级", "5级", "1级", "初段", "二段", "三段", "四段", "五段", "六段", "七段", "八段", "九段"],
    },

    "zhuguxia": {
        "host": "172.24.56.3",
        "user": "admin",
        "key": "~/.ssh/id_rsa_hermes",
        "shared_dir": "/home/admin/go-training/shared",
        "to_dir": "to-zhuguxia",
        "from_dir": "from-zhuguxia",
    },

    "xiaowei": {
        "host": "unknown",
        "user": "admin",
        "key": "~/.ssh/id_rsa_hermes",
        "shared_dir": "/home/admin/go-training/shared",
        "to_dir": "to-xiaowei",
        "from_dir": "from-xiaowei",
    },

    "qoder": {
        "host": "172.24.56.3",  # qoder在诸葛虾服务器上
        "user": "admin",
        "key": "~/.ssh/id_rsa_hermes",
        "shared_dir": "/home/admin/go-training/shared",
        "to_dir": "to-qoder",
        "from_dir": "from-qoder",
    },
}

# ═══════════════════════════════════════════════════════════
# 7天速成训练方案
# ═══════════════════════════════════════════════════════════

SEVEN_DAY_PLAN = {
    "day1": {
        "date": "2026-06-27",
        "focus": "基础巩固",
        "skills": ["吃子技巧", "基本死活"],
        "problem_count": 50,
        "game_count": 5,
        "target_accuracy": 0.85,
        "custom_modules": {
            "xiaochen": "扑与倒扑专项辨析",
            "zhuguxia": "征子路线专项",
            "qoder": "速率套利训练",
        },
    },
    "day2": {
        "date": "2026-06-28",
        "focus": "手筋训练",
        "skills": ["双打吃", "倒扑", "接不归"],
        "problem_count": 60,
        "game_count": 6,
        "target_accuracy": 0.80,
        "custom_modules": {
            "xiaochen": "推理力强化",
            "zhuguxia": "反思日志训练",
            "qoder": "系统性知识构建",
        },
    },
    "day3": {
        "date": "2026-06-29",
        "focus": "死活进阶",
        "skills": ["直三", "曲三", "刀五"],
        "problem_count": 70,
        "game_count": 7,
        "target_accuracy": 0.75,
        "custom_modules": {
            "xiaochen": "高级死活题",
            "zhuguxia": "复杂手筋",
            "qoder": "实战对局",
        },
    },
    "day4": {
        "date": "2026-06-30",
        "focus": "定式学习",
        "skills": ["星位定式", "小目定式"],
        "problem_count": 80,
        "game_count": 8,
        "target_accuracy": 0.70,
        "custom_modules": {
            "xiaochen": "定式辨析",
            "zhuguxia": "定式应用",
            "qoder": "定式实战",
        },
    },
    "day5": {
        "date": "2026-07-01",
        "focus": "布局理论",
        "skills": ["三连星", "中国流"],
        "problem_count": 90,
        "game_count": 10,
        "target_accuracy": 0.65,
        "custom_modules": {
            "xiaochen": "布局实战",
            "zhuguxia": "布局创新",
            "qoder": "布局体系",
        },
    },
    "day6": {
        "date": "2026-07-02",
        "focus": "中盘战斗",
        "skills": ["中盘战术", "形势判断"],
        "problem_count": 100,
        "game_count": 12,
        "target_accuracy": 0.60,
        "custom_modules": {
            "xiaochen": "中盘强化",
            "zhuguxia": "中盘计算",
            "qoder": "中盘实战",
        },
    },
    "day7": {
        "date": "2026-07-03",
        "focus": "综合评估",
        "skills": ["全面测试"],
        "problem_count": 120,
        "game_count": 15,
        "target_accuracy": 0.55,
        "custom_modules": {
            "xiaochen": "综合测试",
            "zhuguxia": "综合测试",
            "qoder": "综合测试",
        },
    },
}

# ═══════════════════════════════════════════════════════════
# SSH共享工具函数
# ═══════════════════════════════════════════════════════════

def ssh_command(host: str, key: str, command: str) -> str:
    """执行SSH命令"""
    full_cmd = f"ssh -i {key} -o StrictHostKeyChecking=no {host} '{command}'"
    result = subprocess.run(full_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout

def scp_send(host: str, key: str, local_file: str, remote_path: str) -> bool:
    """通过SCP发送文件"""
    full_cmd = f"scp -i {key} -o StrictHostKeyChecking=no {local_file} {remote_path}"
    result = subprocess.run(full_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.returncode == 0

def scp_receive(host: str, key: str, remote_file: str, local_path: str) -> bool:
    """通过SCP接收文件"""
    full_cmd = f"scp -i {key} -o StrictHostKeyChecking=no {remote_file} {local_path}"
    result = subprocess.run(full_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.returncode == 0

# ═══════════════════════════════════════════════════════════
# 7天训练方案生成器
# ═══════════════════════════════════════════════════════════

def generate_seven_day_plan(student_id: str) -> Dict[str, Any]:
    """为每位学员生成7天训练方案"""
    plan = {
        "student_id": student_id,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_days": 7,
        "total_problems": 0,
        "total_games": 0,
        "days": [],
    }
    
    for day_key, day_info in SEVEN_DAY_PLAN.items():
        day_plan = {
            "day": day_key,
            "date": day_info["date"],
            "focus": day_info["focus"],
            "skills": day_info["skills"],
            "problem_count": day_info["problem_count"],
            "game_count": day_info["game_count"],
            "target_accuracy": day_info["target_accuracy"],
            "custom_module": day_info["custom_modules"].get(student_id, ""),
        }
        plan["days"].append(day_plan)
        plan["total_problems"] += day_info["problem_count"]
        plan["total_games"] += day_info["game_count"]
    
    return plan


# ═══════════════════════════════════════════════════════════
# 生成Markdown报告
# ═══════════════════════════════════════════════════════════

def format_plan_to_markdown(plan: Dict[str, Any]) -> str:
    """将学习方案格式化为Markdown"""
    md = []
    md.append(f"# 🚀 {plan['student_id']} 7天速成训练方案")
    md.append("")
    md.append(f"> 生成时间：{plan['generated_at']}")
    md.append(f"> 总天数：{plan['total_days']}天")
    md.append(f"> 总题量：{plan['total_problems']}题")
    md.append(f"> 总局数：{plan['total_games']}局")
    md.append("")
    
    # 训练计划表
    md.append("## 📅 每日训练计划")
    md.append("")
    md.append("| 日期 | 重点 | 题量 | 对局数 | 目标准确率 | 定制模块 |")
    md.append("|------|------|------|--------|------------|----------|")
    for day in plan["days"]:
        md.append(f"| {day['date']} | {day['focus']} | {day['problem_count']} | {day['game_count']} | {day['target_accuracy']:.0%} | {day['custom_module']} |")
    md.append("")
    
    # SSH共享说明
    md.append("## 📡 SSH共享配置")
    md.append("")
    md.append("```bash")
    md.append("# 发送训练任务")
    md.append(f"scp -i ~/.ssh/id_rsa_hermes task.json admin@{SSH_CONFIG[plan['student_id']]['host']}:/home/admin/go-training/shared/{SSH_CONFIG[plan['student_id']]['to_dir']}/")
    md.append("")
    md.append("# 接收训练结果")
    md.append(f"scp -i ~/.ssh/id_rsa_hermes admin@{SSH_CONFIG[plan['student_id']]['host']}:/home/admin/go-training/shared/{SSH_CONFIG[plan['student_id']]['from_dir']}/result.json ./")
    md.append("```")
    md.append("")
    
    md.append("---")
    md.append(f"*方案由诸葛马 (Hermes) v1.1 自动生成*")
    
    return "\n".join(md)


# ═══════════════════════════════════════════════════════════
# 主执行流程
# ═══════════════════════════════════════════════════════════

def main():
    """生成三位学员的7天速成训练方案"""
    print("=" * 70)
    print("🚀 小龙虾网络 v1.1 — 围棋7天速成训练方案生成系统")
    print("=" * 70)
    print()
    
    plans = {}
    markdowns = {}
    
    for student_id in SSH_CONFIG:
        print(f"📝 生成 {student_id} 的7天速成训练方案...")
        
        plan = generate_seven_day_plan(student_id)
        markdown = format_plan_to_markdown(plan)
        
        plans[student_id] = plan
        markdowns[student_id] = markdown
        
        print(f"  ✓ 总题量：{plan['total_problems']}题")
        print(f"  ✓ 总局数：{plan['total_games']}局")
        print()
    
    # 保存文件
    output_dir = "/home/admin/lobster-network/docs/seven_day_plan"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for student_id, plan in plans.items():
        # 保存JSON
        json_path = os.path.join(output_dir, f"plan_{student_id}_{timestamp}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(plan, f, ensure_ascii=False, indent=2)
        print(f"  ✓ JSON: {json_path}")
        
        # 保存Markdown
        md_path = os.path.join(output_dir, f"plan_{student_id}_{timestamp}.md")
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(markdowns[student_id])
        print(f"  ✓ Markdown: {md_path}")
    
    print("\n" + "=" * 70)
    print("✅ 7天速成训练方案生成完成！")
    print("=" * 70)
    
    return plans, markdowns


if __name__ == "__main__":
    plans, markdowns = main()
