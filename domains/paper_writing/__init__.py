"""
论文撰写训练域 (Paper Writing Domain)
小龙虾网络第三训练域，与围棋域和海报域并列。
"""

DOMAIN_NAME = "paper_writing"
DOMAIN_VERSION = "1.0.0"
DOMAIN_DESCRIPTION = "学术论文撰写协同训练系统"
SKILL_FILE = "PAPER_WRITING_SKILL.md"
TRAINING_PLAN = "PAPER_TRAINING_PLAN.md"
EVALUATION_DIMENSIONS = [
    "structure",
    "abstract",
    "literature_review",
    "methodology",
    "data_analysis",
    "argumentation",
    "formatting",
    "citations",
]
PLAYERS = ["qoder", "xiaochen", "zhuguxia", "zhugebin"]
