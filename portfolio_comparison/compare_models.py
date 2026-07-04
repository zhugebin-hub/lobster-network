"""
马科维茨模型 vs Treynor-Black 模型组合对比分析
统一无风险利率：1.7%
数据源：yfinance (A股 + 沪深300)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

import yfinance as yf

# ============================================================
# 1. 配置参数
# ============================================================
RISK_FREE_RATE = 0.017  # 统一使用 1.7%（10年期国债收益率）

# 股票池（根据原报告中的股票）
STOCKS = {
    "宁德时代": "300750.SZ",
    "赣锋锂业": "002460.SZ",
    "隆基绿能": "601012.SS",
    "工商银行": "601398.SS",
    "长江电力": "600900.SS",
    "平安银行": "000001.SZ",
    "招商银行": "600036.SS",
    "比亚迪": "002594.SZ",
    "贵州茅台": "600519.SS",
    "伊利股份": "600887.SS",
    "片仔癀": "600436.SS",
    "恒瑞医药": "600276.SS",
}

# 样本期间
START_DATE = "2021-01-01"
END_DATE = "2025-12-31"

print("=" * 60)
print("马科维茨 vs Treynor-Black 模型对比分析")
print(f"无风险利率: {RISK_FREE_RATE*100:.1f}%")
print(f"样本期间: {START_DATE} ~ {END_DATE}")
print("=" * 60)

# ============================================================
# 2. 获取数据
# ============================================================
print("\n[1] 获取股票数据...")

tickers = list(STOCKS.values())
names = list(STOCKS.keys())
ticker_to_name = {v: k for k, v in STOCKS.items()}

data = yf.download(tickers, start=START_DATE, end=END_DATE, progress=False, group_by='ticker')

# 提取收盘价
all_returns = {}
for ticker in tickers:
    name = ticker_to_name[ticker]
    try:
        if isinstance(data.columns, pd.MultiIndex):
            close = data[ticker]['Close'].dropna()
        else:
            close = data[ticker].dropna()
        returns = close.pct_change().dropna()
        all_returns[name] = returns
        print(f"  ✓ {name}: {len(returns)} 个交易日")
    except Exception as e:
        print(f"  ✗ {name}: {e}")

returns_df = pd.DataFrame(all_returns).dropna()
print(f"\n合并后有效交易日: {len(returns_df)}")
print(f"股票数量: {len(returns_df.columns)}")

# ============================================================
# 3. 马科维茨模型
# ============================================================
print("\n[2] 马科维茨均值-方差优化...")

mean_returns = returns_df.mean() * 252  # 年化
cov_matrix = returns_df.cov() * 252     # 年化协方差矩阵
n_assets = len(returns_df.columns)

# 蒙特卡洛模拟
np.random.seed(42)
n_portfolios = 50000

weights = np.random.dirichlet(np.ones(n_assets), n_portfolios)
port_returns = np.dot(weights, mean_returns.values)
port_risks = np.array([np.sqrt(np.dot(w, np.dot(cov_matrix.values, w))) for w in weights])
sharpe_ratios = (port_returns - RISK_FREE_RATE) / port_risks

# 最优夏普比率组合
best_idx = np.argmax(sharpe_ratios)
mw_weights = weights[best_idx]
mw_return = port_returns[best_idx]
mw_risk = port_risks[best_idx]
mw_sharpe = sharpe_ratios[best_idx]

print(f"\n马科维茨最优组合（最大夏普比率）:")
print(f"  年化收益率: {mw_return*100:.2f}%")
print(f"  年化波动率: {mw_risk*100:.2f}%")
print(f"  夏普比率: {mw_sharpe:.4f}")
print(f"\n权重分布 (>{1:.0f}%):")
for i, name in enumerate(returns_df.columns):
    if mw_weights[i] > 0.01:
        print(f"  {name}: {mw_weights[i]*100:.2f}%")

# ============================================================
# 4. Treynor-Black 模型
# ============================================================
print("\n[3] Treynor-Black 主动组合模型...")

# 获取市场基准（沪深300）
print("  获取沪深300基准数据...")
market_data = yf.download("000300.SS", start=START_DATE, end=END_DATE, progress=False)
if isinstance(market_data.columns, pd.MultiIndex):
    market_close = market_data['Close'].dropna()
else:
    market_close = market_data.dropna()
market_returns = market_close.pct_change().dropna()

# 对齐数据
common_idx = returns_df.index.intersection(market_returns.index)
returns_aligned = returns_df.loc[common_idx]
market_returns = market_returns.loc[common_idx]
print(f"  ✓ 基准数据: {len(market_returns)} 个交易日")

# 单指数模型回归
print("\n  进行单指数模型回归...")
excess_returns = returns_aligned - RISK_FREE_RATE / 252
market_excess = market_returns - RISK_FREE_RATE / 252

alphas = {}
betas = {}
residual_vars = {}

for stock in returns_aligned.columns:
    y = excess_returns[stock].values
    x = market_excess.values
    
    X = np.column_stack([np.ones(len(x)), x])
    beta_hat = np.linalg.lstsq(X, y, rcond=None)[0]
    
    alpha = beta_hat[0] * 252  # 年化 Alpha
    beta = beta_hat[1]
    
    y_pred = X @ beta_hat
    residuals = y - y_pred
    residual_var = np.var(residuals) * 252
    
    alphas[stock] = alpha
    betas[stock] = beta
    residual_vars[stock] = residual_var

# 主动组合权重（按 Alpha/残差方差 比例）
alpha_series = pd.Series(alphas)
w_active_raw = alpha_series / pd.Series(residual_vars)
w_active_raw = w_active_raw.clip(lower=0)  # 只做多正Alpha
w_active = w_active_raw / w_active_raw.sum()

# 主动组合指标
active_alpha = (w_active * alpha_series).sum()
active_beta = (w_active * pd.Series(betas)).sum()
active_residual_var = (w_active ** 2 * pd.Series(residual_vars)).sum()

# 最优配置
active_sharpe_sq = active_alpha ** 2 / active_residual_var
market_annual_return = market_excess.mean() * 252
market_annual_risk = market_returns.std() * np.sqrt(252)
market_sharpe = market_annual_return / market_annual_risk
market_sharpe_sq = market_sharpe ** 2

w0_active = active_sharpe_sq / market_sharpe_sq
w_active_final = w0_active / (1 + (1 - active_beta) * w0_active)
w_market_final = 1 - w_active_final

# T-B 组合整体指标
tb_alpha = w_active_final * active_alpha
tb_beta = w_active_final * active_beta + w_market_final * 1.0
tb_return = tb_alpha + tb_beta * market_annual_return + RISK_FREE_RATE
tb_risk = np.sqrt((tb_beta ** 2 * market_returns.var() * 252) + 
                   (w_active_final ** 2 * active_residual_var))
tb_sharpe = (tb_return - RISK_FREE_RATE) / tb_risk

print(f"\nTreynor-Black 模型结果 (Rf={RISK_FREE_RATE*100:.1f}%):")
print(f"  主动组合权重: {w_active_final*100:.2f}%")
print(f"  市场组合权重: {w_market_final*100:.2f}%")
print(f"  组合 Alpha: {tb_alpha*100:.2f}%")
print(f"  组合 Beta: {tb_beta:.4f}")
print(f"  年化收益率: {tb_return*100:.2f}%")
print(f"  年化波动率: {tb_risk*100:.2f}%")
print(f"  夏普比率: {tb_sharpe:.4f}")

print(f"\n个股 Alpha（年化）:")
for stock, alpha in sorted(alphas.items(), key=lambda x: x[1], reverse=True):
    flag = "★" if alpha > 0.05 else " "
    print(f"  {flag} {stock}: {alpha*100:.2f}%")

print(f"\n主动组合内部分布:")
for stock in w_active.index:
    if w_active[stock] > 0.01:
        print(f"  {stock}: {w_active[stock]*100:.2f}%")

# ============================================================
# 5. 对比总结
# ============================================================
print("\n" + "=" * 60)
print("📊 统一无风险利率 (1.7%) 下的模型对比")
print("=" * 60)

print(f"\n| 指标           | 马科维茨      | Treynor-Black   |")
print(f"|----------------|---------------|-----------------|")
print(f"| 年化收益率     | {mw_return*100:>10.2f}% | {tb_return*100:>10.2f}% |")
print(f"| 年化波动率     | {mw_risk*100:>10.2f}% | {tb_risk*100:>10.2f}% |")
print(f"| 夏普比率       | {mw_sharpe:>10.4f} | {tb_sharpe:>10.4f} |")

# 行业分类
industry_map = {
    "平安银行": "银行", "招商银行": "银行", "工商银行": "银行",
    "宁德时代": "电力设备", "赣锋锂业": "电力设备", "隆基绿能": "电力设备", "比亚迪": "电力设备",
    "长江电力": "公用事业",
    "贵州茅台": "食品饮料", "伊利股份": "食品饮料",
    "片仔癀": "医药生物", "恒瑞医药": "医药生物",
}

print(f"\n马科维茨权重分布:")
mw_by_industry = {}
for i, name in enumerate(returns_df.columns):
    if mw_weights[i] > 0.01:
        ind = industry_map.get(name, "其他")
        mw_by_industry[ind] = mw_by_industry.get(ind, 0) + mw_weights[i]
        print(f"  {name} ({ind}): {mw_weights[i]*100:.2f}%")
print(f"\n马科维茨行业集中度:")
for ind, w in sorted(mw_by_industry.items(), key=lambda x: -x[1]):
    print(f"  {ind}: {w*100:.2f}%")

print(f"\nT-B 主动组合权重分布:")
for stock in w_active.index:
    if w_active[stock] > 0.01:
        ind = industry_map.get(stock, "其他")
        print(f"  {stock} ({ind}): {w_active[stock]*100:.2f}%")

# ============================================================
# 6. 等权组合基准
# ============================================================
print("\n[对比] 等权组合基准:")
ew_return = mean_returns.mean()
ew_risk = np.sqrt(np.dot(np.ones(n_assets)/n_assets, np.dot(cov_matrix.values, np.ones(n_assets)/n_assets)))
ew_sharpe = (ew_return - RISK_FREE_RATE) / ew_risk
print(f"  年化收益率: {ew_return*100:.2f}%")
print(f"  年化波动率: {ew_risk*100:.2f}%")
print(f"  夏普比率: {ew_sharpe:.4f}")

# ============================================================
# 7. 保存结果
# ============================================================
import json

results = {
    'risk_free_rate': RISK_FREE_RATE,
    'period': f'{START_DATE} ~ {END_DATE}',
    'n_trading_days': len(returns_df),
    'n_stocks': len(returns_df.columns),
    'markowitz': {
        'return': float(mw_return),
        'risk': float(mw_risk),
        'sharpe': float(mw_sharpe),
        'weights': {name: float(mw_weights[i]) for i, name in enumerate(returns_df.columns) if mw_weights[i] > 0.005},
    },
    'treynor_black': {
        'return': float(tb_return),
        'risk': float(tb_risk),
        'sharpe': float(tb_sharpe),
        'alpha': float(tb_alpha),
        'beta': float(tb_beta),
        'active_weight': float(w_active_final),
        'market_weight': float(w_market_final),
        'stock_alphas': {k: float(v) for k, v in alphas.items()},
        'stock_betas': {k: float(v) for k, v in betas.items()},
        'active_weights': {k: float(v) for k, v in w_active.items() if v > 0.005},
    },
    'equal_weight': {
        'return': float(ew_return),
        'risk': float(ew_risk),
        'sharpe': float(ew_sharpe),
    },
}

with open('/home/admin/.openclaw/workspace/portfolio_comparison/results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)

print("\n📁 结果已保存至: portfolio_comparison/results.json")
print("\n✅ 对比分析完成！")
