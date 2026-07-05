#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L3 社区学习环 - 总调度器
- 根据当前日期自动选择要运行的模块
- 周六: 周对抗赛
- 周日: 讨论局
- 周五: qoder技术助教
- 月末: 跨域知识迁移
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from community.weekly_tournament import run_tournament
from community.discussion_game import run_discussion
from community.technical_instructor import run_instructor
from community.cross_domain import run_cross_domain


def log(message):
    """写入日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def get_week_number():
    """获取当前周数"""
    return datetime.now().isocalendar()[1]


def is_last_friday():
    """判断是否是本月最后一个周五"""
    now = datetime.now()
    # 检查是否是周五
    if now.weekday() != 4:  # 4 = Friday
        return False
    # 检查下周是否还是同一个月
    from datetime import timedelta
    next_week = now + timedelta(days=7)
    return next_week.month != now.month


def run_l3_community():
    """运行L3社区学习环"""
    now = datetime.now()
    weekday = now.weekday()  # 0=Monday, 6=Sunday
    week_number = get_week_number()

    log(f"\n{'='*60}")
    log(f"🦞 L3 社区学习环 - 总调度器")
    log(f"{'='*60}")
    log(f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')} (周{weekday+1})")
    log(f"当前周数: 第{week_number}周")

    results = {}

    # 周五: qoder技术助教
    if weekday == 4:
        log(f"\n👨‍🏫 触发: qoder技术助教")
        try:
            doc_file = run_instructor(week_number)
            results["technical_instructor"] = doc_file
        except Exception as e:
            log(f"❌ 技术助教运行失败: {e}")

    # 周六: 周对抗赛
    elif weekday == 5:
        log(f"\n🏆 触发: 周对抗赛")
        try:
            output_file = run_tournament(week_number)
            results["weekly_tournament"] = output_file
        except Exception as e:
            log(f"❌ 对抗赛运行失败: {e}")

    # 周日: 讨论局
    elif weekday == 6:
        log(f"\n💬 触发: 讨论局")
        try:
            report_file = run_discussion(week_number)
            results["discussion_game"] = report_file
        except Exception as e:
            log(f"❌ 讨论局运行失败: {e}")

    # 月末: 跨域知识迁移
    if is_last_friday():
        log(f"\n🌐 触发: 跨域知识迁移 (月末)")
        try:
            report_file = run_cross_domain(now.month, now.year)
            results["cross_domain"] = report_file
        except Exception as e:
            log(f"❌ 跨域迁移运行失败: {e}")

    # 保存运行结果
    if results:
        results_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "last_run.json"
        )
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": now.isoformat(),
                "weekday": weekday,
                "week_number": week_number,
                "results": results,
            }, f, indent=2, ensure_ascii=False)
        log(f"\n📝 运行结果已保存: {results_file}")

    log(f"\n🏁 L3 社区学习环调度完成")
    return results


if __name__ == "__main__":
    run_l3_community()
