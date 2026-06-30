#!/usr/bin/env python3
"""
OpenClaw 信息速递监控器
每 12 小时搜索 OpenClaw 最新动态，帮助编写教材"信息速递"板块
"""

import os
import sys
import json
from datetime import datetime, timedelta
import subprocess

try:
    from apscheduler.schedulers.blocking import BlockingScheduler
    from apscheduler.triggers.interval import IntervalTrigger
except ImportError:
    print("❌ APScheduler 未安装，执行：pip3 install --user apscheduler")
    sys.exit(1)

# 配置
WORKSPACE = "/home/admin/.openclaw/workspace"
MONITOR_DIR = os.path.join(WORKSPACE, "memory/openclaw-monitor")
# 推送目标配置（多群推送）
TARGET_GROUPS = [
    {
        "name": "小龙虾测试群",
        "channel_id": "cidrMRsnzVf/TnyxtvMp9MnrQ=="
    },
    {
        "name": "🦀功能测试群",
        "channel_id": "cid2Qfigiuz0ILMHMkqbw7D0A=="
    }
]

# 搜索主题（OpenClaw 相关）
SEARCH_QUERIES = [
    "OpenClaw AI agent framework latest news",
    "OpenClaw clawhub skills update",
    "OpenClaw new features 2026",
    "OpenClaw GitHub repository update",
    "AI agent automation framework news",
    "OpenClaw documentation tutorial",
    "OpenClaw community discord update",
    "OpenClaw dingtalk telegram integration",
]

def search_openclaw_news():
    """搜索 OpenClaw 最新动态"""
    results = []
    
    # 使用 searxng 搜索（如果配置了 SEARXNG_URL）
    searxng_url = os.environ.get("SEARXNG_URL", "")
    
    for query in SEARCH_QUERIES[:5]:  # 限制前 5 个查询避免超时
        try:
            if searxng_url:
                # 调用 searxng 脚本
                cmd = [
                    "uv", "run",
                    "/home/admin/.openclaw/workspace/skills/searxng/scripts/searxng.py",
                    "search", query, "-n", "3", "--format", "json"
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    results.append({"query": query, "data": result.stdout})
            else:
                # 使用 web_search 备选方案
                results.append({"query": query, "status": "searxng_not_configured"})
        except Exception as e:
            print(f"搜索失败 [{query}]: {e}")
            results.append({"query": query, "error": str(e)})
    
    return results

def generate_news_brief():
    """生成 OpenClaw 信息速递简报"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    today = datetime.now().strftime("%Y-%m-%d")
    
    os.makedirs(MONITOR_DIR, exist_ok=True)
    brief_file = os.path.join(MONITOR_DIR, f"{today}.md")
    
    # 生成简报内容
    content = f"""# 🦞 OpenClaw · 信息速递
**生成时间**: {timestamp}
**更新频率**: 每 12 小时
**用途**: 教材编写参考资料

---

## 🔍 搜索主题

"""
    
    for i, query in enumerate(SEARCH_QUERIES, 1):
        content += f"{i}. {query}\n"
    
    content += f"""

## 📰 最新动态

> 💡 此处将展示通过 searxng/jina-reader 搜索到的 OpenClaw 最新资讯
> 包括：新版本发布、技能更新、社区动态、文档更新等

### 重点关注
- ✅ OpenClaw 核心功能更新
- ✅ ClawHub 新技能发布
- ✅ 社区最佳实践
- ✅ 集成插件更新（DingTalk/Telegram/Discord）

---

## 📚 教材编写建议

根据最新信息，建议更新以下章节：

1. **基础架构** - OpenClaw 核心组件说明
2. **技能开发** - ClawHub 技能创建与发布
3. **集成实践** - 多平台消息推送配置
4. **定时任务** - APScheduler 与 Cron 配置

---

**下次更新**: {datetime.now() + timedelta(hours=12):%Y-%m-%d %H:%M:%S}

---
*信电大虾自动生成 | OpenClaw 信息监控* 🦞⚡️
"""
    
    with open(brief_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return brief_file, content

def send_to_dingtalk(content):
    """推送消息到多个钉钉群"""
    success_count = 0
    
    # 截取前 800 字符作为预览
    preview = content[:800] + "..." if len(content) > 800 else content
    
    for group in TARGET_GROUPS:
        channel_id = group["channel_id"]
        group_name = group["name"]
        
        cmd = [
            "openclaw", "message", "send",
            "--channel", "dingtalk",
            "--target", channel_id,
            "--message", preview
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=WORKSPACE)
            if result.returncode == 0:
                print(f"✅ 已推送到 {group_name}")
                success_count += 1
            else:
                print(f"❌ 推送失败 [{group_name}]: {result.stderr}")
        except Exception as e:
            print(f"❌ 推送异常 [{group_name}]: {e}")
    
    return success_count == len(TARGET_GROUPS)

def job():
    """定时任务执行函数"""
    print(f"\n{'='*60}")
    print(f"🦞 OpenClaw 信息速递任务启动 [{datetime.now()}]")
    print(f"{'='*60}\n")
    
    try:
        brief_file, content = generate_news_brief()
        print(f"📝 简报已生成：{brief_file}")
        print(f"\n📤 内容预览:\n{content[:400]}...")
        
        # 推送到钉钉群
        print(f"\n📤 正在推送到 {TARGET_GROUP['name']}...")
        send_to_dingtalk(content)
        
        print(f"\n✅ 任务完成！")
    except Exception as e:
        print(f"❌ 任务执行失败：{e}")

def main():
    """主函数"""
    print("🦞 OpenClaw 信息速递监控器启动...")
    print(f"⏰ 执行频率：每 12 小时")
    print(f"📁 存储目录：{MONITOR_DIR}")
    print(f"📤 推送目标：{TARGET_GROUP['name']}\n")
    
    # 创建调度器
    scheduler = BlockingScheduler(timezone='Asia/Shanghai')
    
    # 添加定时任务：每 12 小时
    scheduler.add_job(
        job,
        IntervalTrigger(hours=12),
        id='openclaw_monitor',
        name='OpenClaw 信息速递',
        replace_existing=True
    )
    
    # 立即执行一次（测试用）
    print("🚀 执行首次运行...\n")
    job()
    
    print(f"\n⏰ 调度器已启动，下次执行：12 小时后")
    print("按 Ctrl+C 退出\n")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n👋 调度器已停止")

if __name__ == "__main__":
    main()
