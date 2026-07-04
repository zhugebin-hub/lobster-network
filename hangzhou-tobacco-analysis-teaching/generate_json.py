"""
生成教学版数据 JSON 文件
将 CSV 数据转换为 JSON 格式供 HTML 页面使用
"""
import pandas as pd
import json

# 加载销售数据
sales = pd.read_csv("../hangzhou-tobacco-analysis/data/sales_records.csv")

# 转换为字典列表
data = []
for _, row in sales.iterrows():
    data.append({
        "日期": row["日期"],
        "店铺名称": row["店铺名称"],
        "区域": row["区域"],
        "品牌": row["品牌"],
        "档次": row["档次"],
        "销售数量": int(row["销售数量"]),
        "销售金额": int(row["销售金额"])
    })

# 保存为 JSON
with open("data/sales_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ 生成 JSON 数据：{len(data)} 条记录")
print(f"   文件位置：data/sales_data.json")
