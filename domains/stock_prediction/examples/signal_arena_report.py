#!/usr/bin/env python3
"""
Signal Arena 定时汇报任务

按照建议的4个时间点自动汇报：
- 9:00（开盘前）
- 15:00（收盘后）
- 20:00（晚间）
- 24:00（深夜）
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from signal_arena_client import LobsterNetworkSignalTrader


def create_scheduled_report(trader: LobsterNetworkSignalTrader, 
                           report_type: str = "regular"):
    """
    创建定时汇报
    
    Args:
        trader: 交易器实例
        report_type: 汇报类型 (pre_market/post_market/evening/midnight)
    """
    print(f"\n{'='*60}")
    print(f"🦞 Signal Arena {report_type} 汇报")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # 生成报告
    report = trader.generate_report()
    
    # 根据汇报类型调整内容
    if report_type == "pre_market":
        print("📊 开盘前准备")
        print("- 检查账户状态")
        print("- 查看昨日持仓")
        print("- 准备今日交易计划")
        
    elif report_type == "post_market":
        print("📈 收盘总结")
        print("- 今日交易回顾")
        print("- 盈亏分析")
        print("- 明日策略展望")
        
    elif report_type == "evening":
        print("🌙 晚间复盘")
        print("- 全天表现总结")
        print("- 市场动态分析")
        
    elif report_type == "midnight":
        print("🌃 深夜简报")
        print("- 最终账户状态")
        print("- 排行榜位置")
    
    # 发送钉钉汇报
    trader.send_dingtalk_report(report)
    
    print(f"\n✅ {report_type} 汇报完成")


def setup_cron_jobs(api_key: str, dingtalk_config: Dict = None):
    """
    设置定时汇报任务
    
    Args:
        api_key: Signal Arena API密钥
        dingtalk_config: 钉钉配置
    """
    trader = LobsterNetworkSignalTrader(api_key, dingtalk_config)
    
    print("="*60)
    print("🦞 小龙虾网络 - Signal Arena 定时汇报配置")
    print("="*60)
    print("\n建议的定时汇报时间:")
    print("  1. 09:00 - 开盘前准备")
    print("  2. 15:00 - 收盘后总结")
    print("  3. 20:00 - 晚间复盘")
    print("  4. 24:00 - 深夜简报")
    print("\n⚠️  注意: 需要使用 cron_use 技能设置真实的定时任务")
    print("="*60)
    
    return trader


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="Signal Arena 定时汇报")
    parser.add_argument('--api-key', required=True, help='Signal Arena API Key')
    parser.add_argument('--type', choices=['pre_market', 'post_market', 'evening', 'midnight'],
                       default='regular', help='汇报类型')
    parser.add_argument('--setup', action='store_true', help='仅显示配置信息')
    
    args = parser.parse_args()
    
    if args.setup:
        setup_cron_jobs(args.api_key)
    else:
        trader = LobsterNetworkSignalTrader(args.api_key)
        create_scheduled_report(trader, args.type)
