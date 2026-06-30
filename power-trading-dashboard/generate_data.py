#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电力调度与电价期货交易 - 模拟数据生成器
用于生成历史交易数据、负荷数据、价格数据等
"""

import json
import random
from datetime import datetime, timedelta

# 配置
CITIES = ['杭州', '宁波', '温州', '嘉兴', '湖州', '绍兴', '金华', '台州']
CONTRACTS = ['ELEC-2024Q2', 'ELEC-2024Q3', 'ELEC-2024Q4', 'ELEC-2025Q1', 'ELEC-2025Q2']
SIDES = ['发电侧', '电网侧', '用户侧']

def generate_load_data(days=30):
    """生成电力负荷历史数据"""
    data = []
    base_date = datetime.now()
    
    for day in range(days):
        date = base_date - timedelta(days=day)
        for hour in range(24):
            # 模拟日内负荷曲线（双峰型）
            if 6 <= hour <= 9:  # 早高峰
                load_factor = 0.9 + random.random() * 0.2
            elif 17 <= hour <= 21:  # 晚高峰
                load_factor = 0.95 + random.random() * 0.15
            elif 0 <= hour <= 5:  # 深夜低谷
                load_factor = 0.5 + random.random() * 0.2
            else:  # 平时段
                load_factor = 0.7 + random.random() * 0.2
            
            # 基础负荷 45000 MW
            load = int(45000 * load_factor + random.randint(-1000, 1000))
            
            # 电价与负荷正相关
            price = 450 + (load - 35000) / 100 + random.randint(-30, 30)
            
            data.append({
                'timestamp': date.replace(hour=hour, minute=0, second=0).isoformat(),
                'load_mw': load,
                'price_yuan_mwh': round(price, 2),
                'temperature': random.randint(15, 35)
            })
    
    return sorted(data, key=lambda x: x['timestamp'])

def generate_trade_records(count=100):
    """生成交易记录"""
    trades = []
    base_time = datetime.now()
    
    for i in range(count):
        trade_time = base_time - timedelta(minutes=random.randint(0, 1440))
        contract = random.choice(CONTRACTS)
        direction = random.choice(['买入', '卖出'])
        
        # 根据合约确定基准价格
        base_prices = {
            'ELEC-2024Q2': 568,
            'ELEC-2024Q3': 592,
            'ELEC-2024Q4': 615,
            'ELEC-2025Q1': 548,
            'ELEC-2025Q2': 575
        }
        price = base_prices[contract] + random.randint(-20, 20)
        volume = random.randint(100, 1000)
        amount = round(price * volume / 10, 2)  # 万元
        
        trades.append({
            'trade_id': f'T{trade_time.strftime("%Y%m%d%H%M%S")}{i:03d}',
            'timestamp': trade_time.isoformat(),
            'contract': contract,
            'direction': direction,
            'price': price + random.random(),
            'volume': volume,
            'amount': amount,
            'status': random.choice(['成交', '成交', '成交', '待成交'])
        })
    
    return sorted(trades, key=lambda x: x['timestamp'], reverse=True)

def generate_regional_data():
    """生成区域供需数据"""
    data = []
    
    for city_idx, city in enumerate(CITIES):
        for side_idx, side in enumerate(SIDES):
            # 基础供需指数 0-100
            base_index = random.randint(50, 95)
            
            # 负荷数据
            base_load = random.randint(5000, 15000)
            
            # 供需缺口（正数表示供大于求，负数表示供不应求）
            gap = random.randint(-2000, 2500)
            
            data.append({
                'city': city,
                'city_idx': city_idx,
                'side': side,
                'side_idx': side_idx,
                'supply_demand_index': base_index,
                'load_mw': base_load,
                'gap_mw': gap
            })
    
    return data

def generate_contract_stats():
    """生成合约统计数据"""
    stats = []
    
    base_prices = {
        'ELEC-2024Q2': 568,
        'ELEC-2024Q3': 592,
        'ELEC-2024Q4': 615,
        'ELEC-2025Q1': 548,
        'ELEC-2025Q2': 575
    }
    
    for contract in CONTRACTS:
        base_price = base_prices[contract]
        open_price = base_price + random.randint(-15, 15)
        close_price = base_price + random.randint(-10, 10)
        high_price = max(open_price, close_price) + random.randint(5, 20)
        low_price = min(open_price, close_price) - random.randint(5, 20)
        
        volume = random.randint(5000, 50000)
        position = random.randint(10000, 100000)
        turnover = round(volume * base_price / 10000, 2)  # 亿元
        
        stats.append({
            'contract': contract,
            'open': open_price + random.random(),
            'high': high_price + random.random(),
            'low': low_price + random.random(),
            'close': close_price + random.random(),
            'change_percent': round((close_price - open_price) / open_price * 100, 2),
            'volume': volume,
            'position': position,
            'turnover': turnover
        })
    
    return stats

def generate_volatility_data(days=7):
    """生成波动率数据"""
    data = []
    base_date = datetime.now()
    
    weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    
    for day in range(days):
        date = base_date - timedelta(days=days - day - 1)
        weekday = weekdays[date.weekday()]
        
        # 日内波动率
        intraday_vol = round(random.uniform(2.0, 6.0), 1)
        # 历史波动率（20 日）
        historical_vol = round(random.uniform(3.0, 4.5), 1)
        
        data.append({
            'date': date.strftime('%Y-%m-%d'),
            'weekday': weekday,
            'intraday_volatility': intraday_vol,
            'historical_volatility': historical_vol,
            'max_price': round(random.uniform(600, 700), 2),
            'min_price': round(random.uniform(450, 550), 2)
        })
    
    return data

def export_all_data():
    """导出所有数据到 JSON 文件"""
    output = {
        'generated_at': datetime.now().isoformat(),
        'load_data': generate_load_data(7),  # 7 天小时数据
        'trade_records': generate_trade_records(50),
        'regional_data': generate_regional_data(),
        'contract_stats': generate_contract_stats(),
        'volatility_data': generate_volatility_data()
    }
    
    with open('sample_data.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 数据已生成并保存到 sample_data.json")
    print(f"   - 负荷数据：{len(output['load_data'])} 条")
    print(f"   - 交易记录：{len(output['trade_records'])} 条")
    print(f"   - 区域数据：{len(output['regional_data'])} 条")
    print(f"   - 合约统计：{len(output['contract_stats'])} 条")
    print(f"   - 波动率数据：{len(output['volatility_data'])} 条")

if __name__ == '__main__':
    export_all_data()
