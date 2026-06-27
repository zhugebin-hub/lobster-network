#!/usr/bin/env python3
"""
将JSON格式的K线数据转换为CSV格式
"""

import json
import csv
import os
from pathlib import Path


def convert_kline_json_to_csv(json_file: str, csv_file: str):
    """将K线JSON数据转换为CSV格式"""
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    kline_list = data.get('result', {}).get('list', [])
    
    if not kline_list:
        print(f"警告: {json_file} 中没有K线数据")
        return
    
    # CSV字段定义
    fieldnames = [
        'date', 'open', 'high', 'low', 'close', 'volume',
        'ma5', 'ma10', 'ma20', 'ma30'
    ]
    
    with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for item in kline_list:
            row = {
                'date': item.get('day', ''),
                'open': item.get('open', ''),
                'high': item.get('high', ''),
                'low': item.get('low', ''),
                'close': item.get('close', ''),
                'volume': item.get('volume', ''),
                'ma5': item.get('maPrice5', '') or '',
                'ma10': item.get('maPrice10', '') or '',
                'ma20': item.get('maPrice20', '') or '',
                'ma30': item.get('maPrice30', '') or '',
            }
            writer.writerow(row)
    
    print(f"✅ 已转换 {len(kline_list)} 条记录到 {csv_file}")


if __name__ == '__main__':
    # 转换三只股票的数据
    stocks = [
        ('/tmp/maotai_kline.json', 'lobster-network/domains/stock_prediction/data/600519_贵州茅台.csv'),
        ('/tmp/wuliangye_kline.json', 'lobster-network/domains/stock_prediction/data/000858_五粮液.csv'),
        ('/tmp/zhaoshang_kline.json', 'lobster-network/domains/stock_prediction/data/600036_招商银行.csv'),
    ]
    
    for json_path, csv_path in stocks:
        if os.path.exists(json_path):
            # 确保目标目录存在
            os.makedirs(os.path.dirname(csv_path), exist_ok=True)
            convert_kline_json_to_csv(json_path, csv_path)
        else:
            print(f"⚠️  文件不存在: {json_path}")
