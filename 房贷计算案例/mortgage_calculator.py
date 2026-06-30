#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
个人房贷计算和分析微型案例 - Excel 生成器
作者：陈怡
日期：2026 年 4 月 16 日
"""

import pandas as pd
from datetime import datetime, timedelta

# 房贷参数配置
HOUSE_PRICE = 2000000      # 200 万
DOWN_PAYMENT_RATIO = 0.3   # 30% 首付
LOAN_YEARS = 30            # 30 年
ANNUAL_RATE = 0.042        # 4.2% 年利率
START_DATE = '2026-05-01'

def calculate_loan():
    """计算房贷详细信息"""
    
    # 基础计算
    down_payment = HOUSE_PRICE * DOWN_PAYMENT_RATIO
    loan_amount = HOUSE_PRICE - down_payment
    loan_months = LOAN_YEARS * 12
    monthly_rate = ANNUAL_RATE / 12
    
    # 等额本息计算
    monthly_payment = loan_amount * monthly_rate * (1 + monthly_rate)**loan_months / ((1 + monthly_rate)**loan_months - 1)
    total_payment = monthly_payment * loan_months
    total_interest = total_payment - loan_amount
    
    # 等额本金计算
    monthly_principal = loan_amount / loan_months
    first_month_payment = monthly_principal + loan_amount * monthly_rate
    last_month_payment = monthly_principal + monthly_principal * monthly_rate
    total_payment_2 = sum([monthly_principal + (loan_amount - monthly_principal * i) * monthly_rate for i in range(loan_months)])
    total_interest_2 = total_payment_2 - loan_amount
    
    # 生成还款计划表（前 60 期）
    schedule_1 = []
    schedule_2 = []
    remaining_1 = loan_amount
    remaining_2 = loan_amount
    start = datetime.strptime(START_DATE, '%Y-%m-%d')
    
    for i in range(1, min(61, loan_months + 1)):
        date = start + timedelta(days=30*i)
        
        # 等额本息
        interest_1 = remaining_1 * monthly_rate
        principal_1 = monthly_payment - interest_1
        remaining_1 -= principal_1
        remaining_1 = max(0, remaining_1)
        
        schedule_1.append({
            '期数': i,
            '还款日期': date.strftime('%Y-%m-%d'),
            '月供': round(monthly_payment, 2),
            '本金': round(principal_1, 2),
            '利息': round(interest_1, 2),
            '剩余本金': round(remaining_1, 2),
        })
        
        # 等额本金
        interest_2 = remaining_2 * monthly_rate
        payment_2 = monthly_principal + interest_2
        remaining_2 -= monthly_principal
        remaining_2 = max(0, remaining_2)
        
        schedule_2.append({
            '期数': i,
            '还款日期': date.strftime('%Y-%m-%d'),
            '月供': round(payment_2, 2),
            '本金': round(monthly_principal, 2),
            '利息': round(interest_2, 2),
            '剩余本金': round(remaining_2, 2),
        })
    
    return {
        'base': {
            '房屋总价': HOUSE_PRICE,
            '首付款': down_payment,
            '首付比例': f'{DOWN_PAYMENT_RATIO*100:.1f}%',
            '贷款总额': loan_amount,
            '贷款年限': LOAN_YEARS,
            '年利率': f'{ANNUAL_RATE*100:.2f}%',
        },
        '等额本息': {
            '月供': round(monthly_payment, 2),
            '还款总额': round(total_payment, 2),
            '利息总额': round(total_interest, 2),
            '利息占比': f'{total_interest/total_payment*100:.2f}%',
            'schedule': schedule_1,
        },
        '等额本金': {
            '首月月供': round(first_month_payment, 2),
            '末月月供': round(last_month_payment, 2),
            '每月递减': round(monthly_principal * monthly_rate, 2),
            '还款总额': round(total_payment_2, 2),
            '利息总额': round(total_interest_2, 2),
            '利息占比': f'{total_interest_2/total_payment_2*100:.2f}%',
            'schedule': schedule_2,
        },
    }

def generate_excel():
    """生成 Excel 文件"""
    
    print("=" * 60)
    print("个人房贷计算和分析微型案例")
    print("=" * 60)
    
    print("\n[1/4] 计算房贷数据...")
    data = calculate_loan()
    
    print("\n[2/4] 生成 Excel 文件...")
    
    with pd.ExcelWriter('陈怡_房贷计算分析表.xlsx', engine='openpyxl') as writer:
        
        # Sheet1: 基础信息
        base_df = pd.DataFrame({
            '项目': list(data['base'].keys()),
            '数值': list(data['base'].values()),
        })
        base_df.to_excel(writer, sheet_name='基础信息', index=False)
        
        # Sheet2: 还款方式对比
        comparison_df = pd.DataFrame({
            '指标': ['月供/首月月供', '还款总额', '利息总额', '利息占比'],
            '等额本息': [
                f"¥{data['等额本息']['月供']:,.2f}",
                f"¥{data['等额本息']['还款总额']:,.2f}",
                f"¥{data['等额本息']['利息总额']:,.2f}",
                data['等额本息']['利息占比'],
            ],
            '等额本金': [
                f"¥{data['等额本金']['首月月供']:,.2f}",
                f"¥{data['等额本金']['还款总额']:,.2f}",
                f"¥{data['等额本金']['利息总额']:,.2f}",
                data['等额本金']['利息占比'],
            ],
        })
        comparison_df.to_excel(writer, sheet_name='还款方式对比', index=False)
        
        # Sheet3: 等额本息计划
        schedule1_df = pd.DataFrame(data['等额本息']['schedule'])
        schedule1_df.to_excel(writer, sheet_name='等额本息计划', index=False)
        
        # Sheet4: 等额本金计划
        schedule2_df = pd.DataFrame(data['等额本金']['schedule'])
        schedule2_df.to_excel(writer, sheet_name='等额本金计划', index=False)
        
        # Sheet5: 分析建议
        interest_diff = data['等额本息']['利息总额'] - data['等额本金']['利息总额']
        analysis_df = pd.DataFrame({
            '分析维度': ['月供压力', '总利息支出', '适合人群', '提前还款建议', '推荐方案'],
            '分析内容': [
                f"等额本息月供固定 ¥{data['等额本息']['月供']:,.2f}；等额本金首月 ¥{data['等额本金']['首月月供']:,.2f}，逐月递减",
                f"等额本息总利息 ¥{data['等额本息']['利息总额']:,.2f}；等额本金总利息 ¥{data['等额本金']['利息总额']:,.2f}；差额 ¥{interest_diff:,.2f}",
                "等额本息：收入稳定、希望月供固定的家庭；等额本金：前期还款能力强、希望节省利息",
                "建议第 5-10 年提前还款，此时本金偿还比例较低，可节省更多利息",
                f"推荐等额本金，可节省利息 ¥{interest_diff:,.2f}",
            ],
        })
        analysis_df.to_excel(writer, sheet_name='分析建议', index=False)
    
    print("\n[3/4] 保存完成！")
    
    # 打印摘要
    print("\n" + "=" * 60)
    print("房贷计算摘要")
    print("=" * 60)
    print(f"\n房屋总价：¥{HOUSE_PRICE:,.2f}")
    print(f"首付款：¥{data['base']['首付款']:,.2f} ({data['base']['首付比例']})")
    print(f"贷款总额：¥{data['base']['贷款总额']:,.2f}")
    print(f"贷款年限：{LOAN_YEARS} 年")
    print(f"年利率：{data['base']['年利率']}")
    print("\n--- 等额本息 ---")
    print(f"月供：¥{data['等额本息']['月供']:,.2f}")
    print(f"还款总额：¥{data['等额本息']['还款总额']:,.2f}")
    print(f"利息总额：¥{data['等额本息']['利息总额']:,.2f}")
    print("\n--- 等额本金 ---")
    print(f"首月月供：¥{data['等额本金']['首月月供']:,.2f}")
    print(f"还款总额：¥{data['等额本金']['还款总额']:,.2f}")
    print(f"利息总额：¥{data['等额本金']['利息总额']:,.2f}")
    print(f"节省利息：¥{interest_diff:,.2f}")
    print("\n" + "=" * 60)
    print("Excel 文件已生成：陈怡_房贷计算分析表.xlsx")
    print("=" * 60)

if __name__ == '__main__':
    generate_excel()
