#!/usr/bin/env python3
"""
旅行打包清单生成器
Usage: python packing_list.py --destination 拉萨 --days 5 --season 冬季
"""

import argparse
import json

# 基础清单（所有旅行通用）
BASE_LIST = {
    "🪪 证件类": ["身份证", "银行卡/信用卡", "少量现金", "学生证（如有）"],
    "📱 电子类": ["手机 + 充电器", "充电宝", "耳机", "相机（可选）"],
    "🧴 个人用品": ["牙刷牙膏", "毛巾", "洗发水沐浴露", "护肤品", "防晒霜"],
}

# 目的地特殊清单
DESTINATION_SPECIFIC = {
    "拉萨": {
        "药品": ["红景天（提前一周）", "布洛芬", "感冒药", "葡萄糖", "创可贴"],
        "衣物": ["厚外套", "保暖内衣", "帽子", "手套", "围巾"],
        "其他": ["墨镜（防紫外线）", "保温杯", "润唇膏", "高倍防晒霜"],
    },
    "云南": {
        "药品": ["感冒药", "肠胃药", "创可贴", "驱蚊水"],
        "衣物": ["外套（早晚温差大）", "舒适鞋子", "雨衣"],
        "其他": ["墨镜", "防晒霜", "雨伞"],
    },
    "三亚": {
        "药品": ["防晒霜", "芦荟胶", "肠胃药", "创可贴"],
        "衣物": ["泳衣", "拖鞋", "沙滩裤", "太阳帽", "薄外套"],
        "其他": ["防水手机袋", "浮潜装备（可选）", "沙滩巾"],
    },
    "日本": {
        "药品": ["常用药（带处方）", "感冒药", "肠胃药", "创可贴"],
        "衣物": ["舒适鞋子", "外套", "正装（如有高级餐厅计划）"],
        "其他": ["转换插头", "WiFi 蛋/流量卡", "护照", "签证"],
    },
    "泰国": {
        "药品": ["防晒霜", "驱蚊水", "肠胃药", "创可贴"],
        "衣物": ["短袖", "短裤", "泳衣", "拖鞋", "薄外套（商场空调）"],
        "其他": ["转换插头", "防水袋", "护照", "签证（落地签）"],
    },
    "欧洲": {
        "药品": ["常用药（带处方）", "感冒药", "肠胃药", "创可贴"],
        "衣物": ["舒适鞋子", "外套", "正装", "围巾"],
        "其他": ["转换插头（欧标）", "防盗包", "护照", "签证", "旅行保险"],
    },
}

# 季节调整
SEASON_ADJUSTMENTS = {
    "春季": ["外套", "雨伞", "薄毛衣"],
    "夏季": ["防晒霜", "墨镜", "帽子", "短袖", "驱蚊水"],
    "秋季": ["外套", "毛衣", "围巾"],
    "冬季": ["厚外套", "保暖内衣", "手套", "帽子", "围巾", "暖宝宝"],
}

def generate_packing_list(destination, days, season="秋季"):
    """生成打包清单"""
    
    packing_list = {}
    
    # 添加基础清单
    for category, items in BASE_LIST.items():
        packing_list[category] = items.copy()
    
    # 添加目的地特殊清单
    dest_key = destination
    if destination not in DESTINATION_SPECIFIC:
        for key in DESTINATION_SPECIFIC:
            if key in destination or destination in key:
                dest_key = key
                break
    
    if dest_key in DESTINATION_SPECIFIC:
        for category, items in DESTINATION_SPECIFIC[dest_key].items():
            packing_list[f"🎯 {dest_key} 专用"] = items
    
    # 添加季节调整
    if season in SEASON_ADJUSTMENTS:
        packing_list[f"🌤️ {season} 建议"] = SEASON_ADJUSTMENTS[season]
    
    # 根据天数调整
    if days >= 7:
        packing_list["📝 长旅行额外"] = ["更多换洗衣物", "洗衣液/洗衣片", "折叠衣架"]
    
    return packing_list

def main():
    parser = argparse.ArgumentParser(description='旅行打包清单生成器')
    parser.add_argument('--destination', type=str, required=True, help='目的地')
    parser.add_argument('--days', type=int, default=5, help='旅行天数')
    parser.add_argument('--season', type=str, default='秋季', choices=['春季', '夏季', '秋季', '冬季'], help='季节')
    parser.add_argument('--json', action='store_true', help='输出 JSON 格式')
    
    args = parser.parse_args()
    
    result = generate_packing_list(args.destination, args.days, args.season)
    
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"\n🎒 {args.destination} {args.days}天打包清单（{args.season}）\n")
        print("=" * 50)
        for category, items in result.items():
            print(f"\n{category}")
            for item in items:
                print(f"  ☐ {item}")
        print("\n" + "=" * 50)
        print("\n💡 提示：出发前检查所有证件有效期！\n")

if __name__ == '__main__':
    main()
