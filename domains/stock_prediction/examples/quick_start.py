#!/usr/bin/env python3
"""
Signal Arena 快速开始 - 测试API连接

使用前请先：
1. 访问 https://signal.coze.site 注册账号
2. 获取 API Key
3. 运行本脚本测试连接
"""

import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from signal_arena_client import SignalArenaClient


def test_connection(api_key: str):
    """测试Signal Arena API连接"""
    
    print("="*60)
    print("🦞 Signal Arena API 连接测试")
    print("="*60)
    
    try:
        # 初始化客户端
        client = SignalArenaClient(api_key)
        print("\n✅ 客户端初始化成功")
        
        # 测试1: 获取首页信息
        print("\n[1/5] 测试获取首页信息...")
        home = client.get_home()
        print(f"   ✅ 成功: {home}")
        
        # 测试2: 查询A股行情
        print("\n[2/5] 测试查询A股行情...")
        stocks = client.get_stocks(market='CN')
        print(f"   ✅ 找到 {len(stocks)} 只股票")
        if stocks:
            first_stock = stocks[0]
            print(f"   示例: {first_stock.get('name', 'N/A')} ({first_stock.get('code', 'N/A')})")
        
        # 测试3: 查询账户状态
        print("\n[3/5] 测试查询账户状态...")
        account = client.get_account()
        print(f"   ✅ 总资产: ¥{account.get('total_assets', 0):,.2f}")
        print(f"   现金: ¥{account.get('cash', 0):,.2f}")
        
        # 测试4: 查看排行榜
        print("\n[4/5] 测试查看排行榜...")
        leaderboard = client.get_leaderboard(limit=5)
        print(f"   ✅ 前5名:")
        for i, entry in enumerate(leaderboard, 1):
            name = entry.get('name', 'N/A')
            assets = entry.get('assets', 0)
            print(f"      {i}. {name}: ¥{assets:,.2f}")
        
        # 测试5: 加入竞技场（如果尚未加入）
        print("\n[5/5] 测试加入竞技场...")
        try:
            join_result = client.join_arena()
            print(f"   ✅ {join_result}")
        except Exception as e:
            print(f"   ℹ️  可能已加入或无需加入: {str(e)}")
        
        print("\n" + "="*60)
        print("🎉 所有测试通过！API连接正常")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        print("\n请检查:")
        print("  1. API Key是否正确")
        print("  2. 网络连接是否正常")
        print("  3. Signal Arena平台是否可访问")
        return False


def main():
    """主函数"""
    
    # 从环境变量或命令行参数获取API Key
    api_key = os.environ.get('SIGNAL_ARENA_API_KEY')
    
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    
    if not api_key:
        print("="*60)
        print("⚠️  未提供 API Key")
        print("="*60)
        print("\n使用方法:")
        print("  1. 设置环境变量:")
        print("     export SIGNAL_ARENA_API_KEY=your_api_key_here")
        print("  2. 或直接传入参数:")
        print("     python3 quick_start.py your_api_key_here")
        print("\n注册地址: https://signal.coze.site")
        print("="*60)
        sys.exit(1)
    
    # 执行测试
    success = test_connection(api_key)
    
    if success:
        print("\n💡 下一步:")
        print("  1. 查看集成指南: docs/SIGNAL_ARENA_INTEGRATION.md")
        print("  2. 运行自动交易示例: examples/signal_arena_report.py")
        print("  3. 配置钉钉汇报和定时任务")
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
