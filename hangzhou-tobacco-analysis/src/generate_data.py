"""
杭州烟草销售数据生成器
生成模拟的销售数据用于教学演示
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# 设置随机种子保证可复现
np.random.seed(42)
random.seed(42)

# ==================== 1. 店铺信息 ====================
shops = [
    {"店铺 ID": "S001", "店铺名称": "上城区卷烟专卖店", "区域": "上城区", "面积": 80, "店员数": 3},
    {"店铺 ID": "S002", "店铺名称": "下城区烟草直营店", "区域": "下城区", "面积": 120, "店员数": 5},
    {"店铺 ID": "S003", "店铺名称": "江宁区便民烟酒店", "区域": "江宁区", "面积": 50, "店员数": 2},
    {"店铺 ID": "S004", "店铺名称": "拱墅区旗舰体验店", "区域": "拱墅区", "面积": 200, "店员数": 8},
    {"店铺 ID": "S005", "店铺名称": "西湖区旅游特产店", "区域": "西湖区", "面积": 60, "店员数": 4},
    {"店铺 ID": "S006", "店铺名称": "滨江区高新园店", "区域": "滨江区", "面积": 90, "店员数": 4},
    {"店铺 ID": "S007", "店铺名称": "萧山区机场店", "区域": "萧山区", "面积": 150, "店员数": 6},
    {"店铺 ID": "S008", "店铺名称": "余杭区未来科技城店", "区域": "余杭区", "面积": 100, "店员数": 5},
    {"店铺 ID": "S009", "店铺名称": "临安区景区店", "区域": "临安区", "面积": 40, "店员数": 2},
    {"店铺 ID": "S010", "店铺名称": "富阳区商业中心店", "区域": "富阳区", "面积": 110, "店员数": 5},
]

shops_df = pd.DataFrame(shops)
shops_df.to_csv("data/shops.csv", index=False, encoding="utf-8-sig")
print(f"✓ 生成店铺信息：{len(shops_df)} 家店铺")

# ==================== 2. 香烟品类信息 ====================
products = [
    {"品类 ID": "P001", "品牌": "中华", "品规": "硬中华", "价格": 45, "档次": "高档"},
    {"品类 ID": "P002", "品牌": "中华", "品规": "软中华", "价格": 65, "档次": "高档"},
    {"品类 ID": "P003", "品牌": "利群", "品规": "硬利群", "价格": 14, "档次": "中档"},
    {"品类 ID": "P004", "品牌": "利群", "品规": "软利群", "价格": 22, "档次": "中档"},
    {"品类 ID": "P005", "品牌": "利群", "品规": "阳光利群", "价格": 36, "档次": "高档"},
    {"品类 ID": "P006", "品牌": "芙蓉王", "品规": "硬芙蓉王", "价格": 25, "档次": "中档"},
    {"品类 ID": "P007", "品牌": "芙蓉王", "品规": "软芙蓉王", "价格": 35, "档次": "高档"},
    {"品类 ID": "P008", "品牌": "黄鹤楼", "品规": "硬黄鹤楼", "价格": 20, "档次": "中档"},
    {"品类 ID": "P009", "品牌": "黄鹤楼", "品规": "软黄鹤楼", "价格": 50, "档次": "高档"},
    {"品类 ID": "P010", "品牌": "南京", "品规": "硬南京", "价格": 12, "档次": "低档"},
    {"品类 ID": "P011", "品牌": "南京", "品规": "雨花石", "价格": 55, "档次": "高档"},
    {"品类 ID": "P012", "品牌": "黄山", "品规": "硬黄山", "价格": 10, "档次": "低档"},
    {"品类 ID": "P013", "品牌": "黄山", "品规": "徽商新视界", "价格": 100, "档次": "高档"},
    {"品类 ID": "P014", "品牌": "玉溪", "品规": "硬玉溪", "价格": 23, "档次": "中档"},
    {"品类 ID": "P015", "品牌": "云烟", "品规": "硬云烟", "价格": 10, "档次": "低档"},
]

products_df = pd.DataFrame(products)
products_df.to_csv("data/products.csv", index=False, encoding="utf-8-sig")
print(f"✓ 生成商品信息：{len(products_df)} 个品规")

# ==================== 3. 销售记录 ====================
# 生成 2025 年 1 月 1 日 -2025 年 12 月 31 日 的销售数据
start_date = datetime(2025, 1, 1)
end_date = datetime(2025, 12, 31)

sales_records = []

# 不同区域的销售系数（景区和机场销量较高）
region_factor = {
    "上城区": 1.0, "下城区": 1.1, "江宁区": 0.9, "拱墅区": 1.2,
    "西湖区": 1.5, "滨江区": 1.1, "萧山区": 1.3, "余杭区": 1.2,
    "临安区": 0.8, "富阳区": 1.0
}

# 不同档次的销量系数
price_factor = {"低档": 1.5, "中档": 1.0, "高档": 0.6}

current_date = start_date
while current_date <= end_date:
    # 周末销量系数
    weekend_factor = 1.3 if current_date.weekday() >= 5 else 1.0
    
    # 节假日销量系数（简化处理：春节、国庆等）
    holiday_factor = 1.0
    if current_date.month == 2 and current_date.day <= 15:  # 春节
        holiday_factor = 2.0
    elif current_date.month == 10 and current_date.day <= 7:  # 国庆
        holiday_factor = 1.5
    elif current_date.month == 5 and current_date.day <= 5:  # 五一
        holiday_factor = 1.3
    
    # 月份系数（春节月份、国庆月份销量高）
    month_factor = 1.0
    if current_date.month in [1, 2, 9, 10]:
        month_factor = 1.3
    
    for shop in shops:
        for product in products:
            # 基础销量
            base_sales = random.randint(5, 30)
            
            # 综合系数
            total_factor = (
                region_factor[shop["区域"]] * 
                price_factor[product["档次"]] * 
                weekend_factor * 
                holiday_factor * 
                month_factor
            )
            
            # 实际销量（添加随机波动）
            sales_qty = int(base_sales * total_factor * random.uniform(0.8, 1.2))
            
            if sales_qty > 0:
                sales_records.append({
                    "日期": current_date.strftime("%Y-%m-%d"),
                    "店铺 ID": shop["店铺 ID"],
                    "店铺名称": shop["店铺名称"],
                    "区域": shop["区域"],
                    "品类 ID": product["品类 ID"],
                    "品牌": product["品牌"],
                    "品规": product["品规"],
                    "价格": product["价格"],
                    "档次": product["档次"],
                    "销售数量": sales_qty,
                    "销售金额": sales_qty * product["价格"]
                })
    
    current_date += timedelta(days=1)

sales_df = pd.DataFrame(sales_records)
sales_df.to_csv("data/sales_records.csv", index=False, encoding="utf-8-sig")
print(f"✓ 生成销售记录：{len(sales_df)} 条")

# ==================== 4. 生成汇总统计表 ====================
# 按店铺汇总
shop_summary = sales_df.groupby(["店铺 ID", "店铺名称", "区域"]).agg({
    "销售数量": "sum",
    "销售金额": "sum"
}).reset_index()
shop_summary.columns = ["店铺 ID", "店铺名称", "区域", "总销量", "总销售额"]
shop_summary.to_csv("data/shop_summary.csv", index=False, encoding="utf-8-sig")
print(f"✓ 生成店铺汇总：{len(shop_summary)} 条")

# 按品牌汇总
brand_summary = sales_df.groupby(["品牌", "档次"]).agg({
    "销售数量": "sum",
    "销售金额": "sum"
}).reset_index()
brand_summary.columns = ["品牌", "档次", "总销量", "总销售额"]
brand_summary.to_csv("data/brand_summary.csv", index=False, encoding="utf-8-sig")
print(f"✓ 生成品类汇总：{len(brand_summary)} 条")

# 按日期汇总
date_summary = sales_df.groupby("日期").agg({
    "销售数量": "sum",
    "销售金额": "sum"
}).reset_index()
date_summary.columns = ["日期", "总销量", "总销售额"]
date_summary.to_csv("data/date_summary.csv", index=False, encoding="utf-8-sig")
print(f"✓ 生成日期汇总：{len(date_summary)} 条")

print("\n✅ 数据生成完成！")
print(f"   数据文件保存至：data/ 目录")
