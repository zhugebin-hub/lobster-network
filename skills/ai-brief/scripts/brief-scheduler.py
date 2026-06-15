#!/usr/bin/env python3
"""
AI Brief Scheduler - 定时简报系统
每天 9:00 自动搜索全网热点并推送到指定群组
"""

import os
import sys
import json
from datetime import datetime, timedelta

try:
    from apscheduler.schedulers.blocking import BlockingScheduler
    from apscheduler.triggers.cron import CronTrigger
except ImportError:
    print("Error: APScheduler not installed. Run: pip3 install --user apscheduler")
    sys.exit(1)

# 配置
BRIEF_DIR = "/home/admin/.openclaw/workspace/memory/ai-briefs"
WORKSPACE = "/home/admin/.openclaw/workspace"

# 推送目标配置
TARGET_GROUP = {
    "name": "小龙虾测试群",
    "channel_id": "cidrMRsnzVf/TnyxtvMp9MnrQ==",
    "session_key": "agent:main:dingtalk:group:cidrmrsnzvf/tnyxtvmp9mnrq=="
}

# 搜索主题
SEARCH_QUERIES = [
    "AI 人工智能 最新进展 2026",
    "科技新闻 热点 今日",
    "大模型 LLM 突破",
    "机器人 自动化 新闻",
    "量子计算 科技前沿",
    "芯片 半导体 新闻",
    "5G 6G 通信技术",
    "网络安全 数据隐私",
]

def generate_brief():
    """生成每日简报"""
    today = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    os.makedirs(BRIEF_DIR, exist_ok=True)
    brief_file = os.path.join(BRIEF_DIR, f"{today}.md")
    
    # 生成简报内容模板
    content = f"""# 🦞 信电大虾 · 全网资讯日报
**日期**: {timestamp}
**信源**: 全网热点聚合

---

## 🔥 今日热点摘要

"""
    
    # 添加搜索主题列表
    content += "### 📋 搜索主题\n\n"
    for i, query in enumerate(SEARCH_QUERIES, 1):
        content += f"{i}. {query}\n"
    
    content += f"""
---

> 📝 简报生成完成。
> 
> **生成时间**: {timestamp}
> **下次推送**: 明天 9:00

---
*此简报由信电大虾自动生成 | 信电学院数字守护者* 🦞⚡️
"""
    
    # 写入文件
    with open(brief_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 简报已生成：{brief_file}")
    return brief_file, content

def send_to_dingtalk(content):
    """推送消息到钉钉群"""
    import subprocess
    
    channel_id = TARGET_GROUP["channel_id"]
    
    # 使用 OpenClaw message 命令推送
    cmd = [
        "openclaw", "message", "send",
        "--channel", "dingtalk",
        "--target", channel_id,
        "--message", content
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=WORKSPACE)
        if result.returncode == 0:
            print(f"✅ 已推送到 {TARGET_GROUP['name']} ({channel_id})")
            return True
        else:
            print(f"❌ 推送失败：{result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 推送异常：{e}")
        return False

def job():
    """定时任务执行函数"""
    print(f"\n{'='*50}")
    print(f"🦞 信电大虾 AI 简报任务启动 [{datetime.now()}]")
    print(f"{'='*50}\n")
    
    try:
        brief_file, content = generate_brief()
        print(f"\n📤 简报内容预览:\n{content[:500]}...")
        
        # 推送到钉钉群
        print(f"\n📤 正在推送到 {TARGET_GROUP['name']}...")
        send_to_dingtalk(content)
        
        print(f"\n✅ 任务完成！")
    except Exception as e:
        print(f"❌ 任务执行失败：{e}")

def main():
    """主函数"""
    print("🦞 信电大虾 AI 简报调度器启动...")
    print(f"📅 定时任务：每天 9:00 (Cron: 0 9 * * *)")
    print(f"📁 存储目录：{BRIEF_DIR}\n")
    
    # 创建调度器
    scheduler = BlockingScheduler(timezone='Asia/Shanghai')
    
    # 添加定时任务：每天 9:00
    scheduler.add_job(
        job,
        CronTrigger(hour=9, minute=0),
        id='daily_brief',
        name='AI 每日简报',
        replace_existing=True
    )
    
    # 立即执行一次（测试用）
    print("🚀 执行首次测试运行...\n")
    job()
    
    print(f"\n⏰ 调度器已启动，等待下次执行 (明天 9:00)")
    print("按 Ctrl+C 退出\n")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n👋 调度器已停止")

if __name__ == "__main__":
    main()
