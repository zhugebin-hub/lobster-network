#!/usr/bin/env python3
"""
教育回报率分析 - Stata实操复现 (Python版)
使用statsmodels复现Stata回归分析流程
数据来源：模拟WAGE1数据集（Wooldridge教材）
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import json

np.random.seed(42)
OUTPUT_DIR = "/home/admin/.openclaw/workspace/stata_experiment/output"

# ============================================================
# 第一部分：生成模拟WAGE1数据
# ============================================================
print("=" * 60)
print("第一部分：数据生成与准备")
print("=" * 60)

N = 526  # WAGE1样本量

# 生成变量
educ = np.random.choice(range(5, 22), size=N, 
                         p=[0.01, 0.02, 0.03, 0.05, 0.08, 0.12, 0.15, 0.14, 0.12, 0.10, 0.07, 0.05, 0.03, 0.02, 0.005, 0.003, 0.002])
exper = np.maximum(0, np.random.normal(17, 8, N)).astype(int)
exper = np.clip(exper, 0, 51)
female = np.random.binomial(1, 0.476, N)
married = np.random.binomial(1, 0.60, N)

# 生成工资（基于明瑟方程）
true_beta_educ = 0.092
true_beta_exper = 0.040
true_beta_exper_sq = -0.0007
true_beta_female = -0.30
true_beta_married = 0.15
true_intercept = 0.55

error = np.random.normal(0, 0.426, N)
ln_wage = (true_intercept + true_beta_educ * educ + 
           true_beta_exper * exper + true_beta_exper_sq * exper**2 +
           true_beta_female * female + true_beta_married * married + error)
wage = np.exp(ln_wage)

# 创建DataFrame
df = pd.DataFrame({
    'wage': wage,
    'educ': educ,
    'exper': exper,
    'exper_sq': exper**2,
    'female': female,
    'married': married,
    'ln_wage': ln_wage
})

# 保存数据
df.to_csv(os.path.join(OUTPUT_DIR, "wage1_simulated.csv"), index=False)
print(f"✓ 数据已生成: {N} 个观测值")
print(f"✓ 数据已保存: wage1_simulated.csv")

# ============================================================
# 第二部分：描述性统计
# ============================================================
print("\n" + "=" * 60)
print("第二部分：描述性统计")
print("=" * 60)

desc_stats = df[['ln_wage', 'educ', 'exper', 'female']].describe()
print("\n描述性统计表:")
print(desc_stats)

# 保存描述性统计
desc_dict = {}
for var in ['ln_wage', 'educ', 'exper', 'female']:
    desc_dict[var] = {
        '均值': float(df[var].mean()),
        '标准差': float(df[var].std()),
        '最小值': float(df[var].min()),
        '最大值': float(df[var].max()),
        '观测值': int(df[var].count())
    }

with open(os.path.join(OUTPUT_DIR, "descriptive_stats.json"), 'w', encoding='utf-8') as f:
    json.dump(desc_dict, f, ensure_ascii=False, indent=2)
print(f"✓ 描述性统计已保存: descriptive_stats.json")

# ============================================================
# 第三部分：可视化 - 散点图
# ============================================================
print("\n" + "=" * 60)
print("第三部分：可视化分析")
print("=" * 60)

fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(df['educ'], df['ln_wage'], alpha=0.4, s=20, label='Observations')

# 拟合线
z = np.polyfit(df['educ'], df['ln_wage'], 1)
p = np.poly1d(z)
x_line = np.linspace(df['educ'].min(), df['educ'].max(), 100)
ax.plot(x_line, p(x_line), "r-", linewidth=2, label='Fitted Line')

ax.set_title('Education & Log Wage Relationship', fontsize=14)
ax.set_xlabel('Years of Education', fontsize=12)
ax.set_ylabel('Log Wage (ln(wage))', fontsize=12)
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "scatter_plot.png"), dpi=150)
plt.close()
print(f"✓ 散点图已保存: scatter_plot.png")

# ============================================================
# 第四部分：回归分析
# ============================================================
print("\n" + "=" * 60)
print("第四部分：回归分析")
print("=" * 60)

# 模型1：简单回归
print("\n--- 模型1：ln_wage ~ educ ---")
X1 = sm.add_constant(df['educ'])
model1 = sm.OLS(df['ln_wage'], X1).fit()
print(model1.summary())

# 模型2：明瑟方程（加入经验及平方项）
print("\n--- 模型2：ln_wage ~ educ + exper + exper_sq ---")
X2 = sm.add_constant(df[['educ', 'exper', 'exper_sq']])
model2 = sm.OLS(df['ln_wage'], X2).fit()
print(model2.summary())

# 模型3：完整模型（加入性别）
print("\n--- 模型3：ln_wage ~ educ + exper + exper_sq + female ---")
X3 = sm.add_constant(df[['educ', 'exper', 'exper_sq', 'female']])
model3 = sm.OLS(df['ln_wage'], X3).fit()
print(model3.summary())

# ============================================================
# 第五部分：提取回归结果
# ============================================================
print("\n" + "=" * 60)
print("第五部分：回归结果汇总")
print("=" * 60)

def extract_results(model, name):
    """提取回归结果"""
    results = {
        'name': name,
        'nobs': int(model.nobs),
        'rsquared': float(model.rsquared),
        'rsquared_adj': float(model.rsquared_adj),
        'fvalue': float(model.fvalue),
        'fprob': float(model.f_pvalue),
        'root_mse': float(model.mse_resid**0.5),
        'coefficients': {}
    }
    ci = model.conf_int()
    for i, var in enumerate(model.params.index):
        results['coefficients'][var] = {
            'coef': float(model.params[var]),
            'std_err': float(model.bse[var]),
            't': float(model.tvalues[var]),
            'p_value': float(model.pvalues[var]),
            'ci_lower': float(ci.iloc[i, 0]),
            'ci_upper': float(ci.iloc[i, 1])
        }
    return results

results = {
    'model1': extract_results(model1, "模型1 (仅教育)"),
    'model2': extract_results(model2, "模型2 (明瑟方程)"),
    'model3': extract_results(model3, "模型3 (完整模型)")
}

with open(os.path.join(OUTPUT_DIR, "regression_results.json"), 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"✓ 回归结果已保存: regression_results.json")

# ============================================================
# 第六部分：生成回归结果表格（文本格式）
# ============================================================
print("\n" + "=" * 60)
print("第六部分：生成回归结果表格")
print("=" * 60)

# 构建专业回归表格
vars_list = ['educ', 'exper', 'exper_sq', 'female', 'const']
var_labels = {
    'educ': '受教育年限 (educ)',
    'exper': '工作经验 (exper)',
    'exper_sq': '经验平方 (exper_sq)',
    'female': '性别 (female=1)',
    'const': '常数项'
}

# 表格头部
table_lines = []
table_lines.append("=" * 70)
table_lines.append("表1：教育回报率回归结果")
table_lines.append("=" * 70)

# 变量行
header = f"{'变量':<25} {'模型1':>12} {'模型2':>12} {'模型3':>12}"
table_lines.append(header)
table_lines.append("-" * 70)

for var in vars_list:
    line = f"{var_labels.get(var, var):<25}"
    for model in [model1, model2, model3]:
        if var in model.params:
            coef = model.params[var]
            se = model.bse[var]
            p = model.pvalues[var]
            stars = "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.10 else ""
            line += f" {coef:10.4f}{stars:>3}"
        else:
            line += f" {'-':>12}"
    table_lines.append(line)

table_lines.append("-" * 70)

# 标准误行
table_lines.append(f"{'(标准误)':<25}",)
se_line = f"{'':<25}"
for var in vars_list:
    for model in [model1, model2, model3]:
        if var in model.bse:
            se_line += f" ({model.bse[var]:10.4f})"
        else:
            se_line += f" {'':>12}"
table_lines.append(se_line)

table_lines.append("-" * 70)

# 统计量
stats_items = [
    ('观测值', 'nobs', '12.0f'),
    ('R-squared', 'rsquared', '12.4f'),
    ('Adjusted R-squared', 'rsquared_adj', '12.4f'),
    ('F统计量', 'fvalue', '12.2f'),
    ('Prob > F', 'f_pvalue', '12.4f'),
    ('Root MSE', 'mse_resid', '12.4f'),
]

for label, key, fmt in stats_items:
    line = f"{label:<25}"
    for m in [model1, model2, model3]:
        val = getattr(m, key)
        if key == 'mse_resid':
            val = val ** 0.5  # Root MSE
        line += " " + format(val, fmt)
    table_lines.append(line)

table_lines.append("=" * 70)
table_lines.append("注：* p<0.10, ** p<0.05, *** p<0.01")
table_lines.append("括号内为标准误")

table_text = "\n".join(table_lines)
print(table_text)

with open(os.path.join(OUTPUT_DIR, "regression_table.txt"), 'w', encoding='utf-8') as f:
    f.write(table_text)
print(f"\n✓ 回归表格已保存: regression_table.txt")

# ============================================================
# 第七部分：打印关键发现
# ============================================================
print("\n" + "=" * 60)
print("关键发现")
print("=" * 60)

educ_coef = model3.params['educ']
educ_p = model3.pvalues['educ']
print(f"1. 教育回报率: {educ_coef*100:.2f}% (p={educ_p:.4f})")
print(f"   → 在控制了工作经验和性别后，受教育年限每增加1年，")
print(f"     工资平均上涨约 {educ_coef*100:.1f}%")

exper_coef = model3.params['exper']
exper_sq_coef = model3.params['exper_sq']
print(f"\n2. 经验回报: 系数={exper_coef:.4f}, 平方项={exper_sq_coef:.6f}")
print(f"   → 经验回报为正，平方项为负，符合边际回报递减")

female_coef = model3.params['female']
female_p = model3.pvalues['female']
print(f"\n3. 性别差距: 系数={female_coef:.4f} (p={female_p:.4f})")
print(f"   → 女性工资显著低于男性（在{female_p*100:.1f}%水平上）")

print(f"\n4. 模型解释力: R² = {model3.rsquared:.4f}")
print(f"   → 模型解释了工资变异的 {model3.rsquared*100:.1f}%")

print("\n" + "=" * 60)
print("所有分析完成！")
print("=" * 60)
