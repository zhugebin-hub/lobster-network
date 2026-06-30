#!/usr/bin/env python3
"""
旅行预算计算器
Usage: python budget_calculator.py --days 5 --destination 拉萨 --style 经济
"""

import argparse
import json

# 目的地预算参考（每日/人，不含往返大交通）
BUDGET_DATA = {
    "拉萨": {"经济": 300, "舒适": 600, "豪华": 1200},
    "云南": {"经济": 350, "舒适": 700, "豪华": 1500},
    "四川": {"经济": 300, "舒适": 600, "豪华": 1200},
    "新疆": {"经济": 400, "舒适": 800, "豪华": 1800},
    "北京": {"经济": 400, "舒适": 800, "豪华": 2000},
    "上海": {"经济": 450, "舒适": 900, "豪华": 2200},
    "西安": {"经济": 300, "舒适": 600, "豪华": 1200},
    "成都": {"经济": 300, "舒适": 600, "豪华": 1200},
    "重庆": {"经济": 280, "舒适": 550, "豪华": 1100},
    "桂林": {"经济": 300, "舒适": 600, "豪华": 1200},
    "厦门": {"经济": 350, "舒适": 700, "豪华": 1500},
    "三亚": {"经济": 500, "舒适": 1000, "豪华": 2500},
    "日本": {"经济": 800, "舒适": 1500, "豪华": 3000},
    "泰国": {"经济": 300, "舒适": 600, "豪华": 1500},
    "欧洲": {"经济": 1000, "舒适": 2000, "豪华": 4000},
}

# 门票预算参考（元/人）
TICKET_DATA = {
    "拉萨": 400,  # 布达拉宫 + 大昭寺等
    "云南": 600,  # 丽江古城 + 玉龙雪山等
    "北京": 800,  # 故宫 + 长城等
    "西安": 500,  # 兵马俑 + 城墙等
}

def calculate_budget(days, destination, style, include_tickets=True):
    """计算旅行预算"""
    
    # 查找目的地（支持模糊匹配）
    dest_key = destination
    if destination not in BUDGET_DATA:
        for key in BUDGET_DATA:
            if key in destination or destination in key:
                dest_key = key
                break
    
    daily_budget = BUDGET_DATA.get(dest_key, {}).get(style, 400)
    
    # 基础预算
    accommodation_food = daily_budget * days
    
    # 门票预算
    tickets = TICKET_DATA.get(dest_key, 300) if include_tickets else 0
    
    # 当地交通
    local_transport = 50 * days
    
    # 备用金（10%）
    contingency = int((accommodation_food + tickets + local_transport) * 0.1)
    
    total = accommodation_food + tickets + local_transport + contingency
    
    result = {
        "destination": dest_key,
        "days": days,
        "style": style,
        "breakdown": {
            "住宿餐饮": f"¥{accommodation_food}",
            "门票": f"¥{tickets}",
            "当地交通": f"¥{local_transport}",
            "备用金 (10%)": f"¥{contingency}",
        },
        "subtotal": f"¥{accommodation_food + tickets + local_transport}",
        "total": f"¥{total}",
        "note": "⚠️ 不含往返大交通（机票/火车）"
    }
    
    return result

def main():
    parser = argparse.ArgumentParser(description='旅行预算计算器')
    parser.add_argument('--days', type=int, required=True, help='旅行天数')
    parser.add_argument('--destination', type=str, required=True, help='目的地')
    parser.add_argument('--style', type=str, default='经济', choices=['经济', '舒适', '豪华'], help='旅行风格')
    parser.add_argument('--json', action='store_true', help='输出 JSON 格式')
    
    args = parser.parse_args()
    
    result = calculate_budget(args.days, args.destination, args.style)
    
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"\n📊 {result['destination']} {result['days']}天{result['style']}游预算\n")
        print("=" * 40)
        for item, amount in result['breakdown'].items():
            print(f"  {item}: {amount}")
        print("=" * 40)
        print(f"  小计：{result['subtotal']}")
        print(f"  总计：{result['total']}")
        print(f"\n  {result['note']}\n")

if __name__ == '__main__':
    main()
