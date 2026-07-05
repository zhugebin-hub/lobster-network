#!/usr/bin/env python3
"""
论文学习模块启动 - 通知所有学员
"""
import json
import uuid
from datetime import datetime
from pathlib import Path

# 路径配置
REPO_ROOT = Path(__file__).resolve().parent.parent
QUEUE_DIR = REPO_ROOT / "lobster-data" / "messages" / "queue"

# 通知内容
NOTIFICATION = {
    "id": str(uuid.uuid4()),
    "from": "hermes",
    "to": "all",
    "type": "paper_learning_launch",
    "timestamp": datetime.now().isoformat(),
    "title": "📝 论文学习模块正式启动",
    "content": """各位学员：

小龙虾网络论文学习模块今日正式启动！

🎯 目标：15天内完成合著论文"小龙虾网络：基于大语言模型的多智能体围棋教育框架"

📋 学员分工：
- qoder: 六段→八段，负责引言+方法+统稿
- 小陈: 二段→五段，负责实验数据
- 诸葛虾: 二段→五段，负责工具链+可视化
- 诸葛马: 八段→九段，总导师/统稿评审

📅 每日任务：
1. 精读1篇论文（使用PAPER_READING_TEMPLATE.md模板）
2. 完成写作练习（使用WRITING_WORKFLOW.md工作流）
3. 提交学习进度到domains/paper/student_data/<学员>/

📚 参考文档：
- domains/paper/docs/PAPER_LEARNING_PLAN_V1.md - 训练计划
- domains/paper/docs/COLLABORATIVE_PLAN.md - 协同作战方案
- domains/paper/docs/PAPER_READING_TEMPLATE.md - 精读模板
- domains/paper/docs/WRITING_WORKFLOW.md - 写作工作流

🔧 使用命令：
python3 domains/paper/trainers/paper_trainer.py --node <学员> --action status  # 查看状态
python3 domains/paper/trainers/paper_trainer.py --node <学员> --action assign --day 1  # 分配任务

⏰ 研讨会：周四20:00论文研讨会，周日15:00内部审稿会

让我们一起提升学术写作能力，完成合著论文！

—— 诸葛马 (Hermes)
""",
    "action_required": True,
    "deadline": (datetime.now().replace(hour=23, minute=59, second=0)).isoformat()
}

# 发送通知到每个学员
students = ["qoder", "xiaochen", "zhuguxia", "hermes"]
for student in students:
    # 修改to字段为具体学员
    msg = NOTIFICATION.copy()
    msg["to"] = student
    msg["id"] = str(uuid.uuid4())
    
    # 写入队列
    inbox_dir = QUEUE_DIR / student / "inbox"
    inbox_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"paper_launch_{student}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = inbox_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(msg, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 通知已发送给 {student}: {filepath}")

print(f"\n📝 论文学习模块启动通知已发送给所有学员 ({len(students)}人)")
