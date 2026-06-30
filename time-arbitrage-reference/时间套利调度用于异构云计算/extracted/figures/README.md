# 论文图表目录

**生成时间**：2026-03-28 11:30  
**图表数量**：8 个  
**格式**：PDF (300 DPI)

---

## 图表列表

### Figure 1: Cost Comparison
- **文件**：`fig1_cost_comparison.pdf`
- **内容**：Round-Robin vs Time-Arbitrage 成本对比
- **关键数据**：$3.59 → $0.26 (92.8% 节省)
- **用途**：论文 Figure 1，展示核心成果

### Figure 2: Task Completion Rate
- **文件**：`fig2_completion_rate.pdf`
- **内容**：任务完成率对比
- **关键数据**：100% vs 100%
- **用途**：论文 Figure 2，证明无任务丢失

### Figure 3: SLA Violation Comparison
- **文件**：`fig3_sla_violations.pdf`
- **内容**：SLA 违约次数对比
- **关键数据**：44 vs 44 (36% 违约率)
- **用途**：论文 Figure 3，展示 SLA 情况

### Figure 4: Latency Comparison
- **文件**：`fig4_latency_comparison.pdf`
- **内容**：平均延迟对比
- **关键数据**：155.67s vs 155.67s
- **用途**：论文 Figure 4，证明延迟未增加

### Figure 5: Price Ratio Sensitivity
- **文件**：`fig5_price_sensitivity.pdf`
- **内容**：价格比对成本节省的影响
- **关键数据**：2×→78%, 3×→93%, 5×→96%, 10×→98%
- **用途**：论文 Figure 5，敏感性分析

### Figure 6: Deferrable Fraction Analysis
- **文件**：`fig6_deferrable_fraction.pdf`
- **内容**：可延迟任务比例的影响（双子图）
- **关键数据**：20%/40%/60%/80% 对应的节省和完成率
- **用途**：论文 Figure 6，参数敏感性

### Figure 7: Hourly Load Pattern
- **文件**：`fig7_hourly_load_pattern.pdf`
- **内容**：合成小时负载模式（日周期）
- **关键数据**：高峰/平时/低谷时段标注
- **用途**：论文 Figure 7，负载特征展示

### Figure 8: System Architecture
- **文件**：`fig8_architecture.pdf`
- **内容**：时间套利调度器架构图
- **关键组件**：Task Arrival → Urgency Check → Price Check → Decision
- **用途**：论文 Figure 8，系统设计展示

---

## 使用指南

### LaTeX 引用

```latex
% 在论文中引用图表
\begin{figure}[t]
\centering
\includegraphics[width=0.95\columnwidth]{figures/fig1_cost_comparison.pdf}
\caption{Cost Comparison: Time-Arbitrage reduces cost by 92.8\%}
\label{fig:cost}
\end{figure}

% 文中引用
As shown in Figure~\ref{fig:cost}, ...
```

### 颜色方案

- **绿色** (#27AE60)：Time-Arbitrage / 优化后 / 节省
- **红色** (#E74C3C)：Round-Robin / Baseline / 问题
- **蓝色** (#3498DB)：数据 / 中性
- **橙色** (#F39C12)：警告 / 注意

---

## 生成脚本

```bash
cd research/paper
python3 generate_figures.py
```

输出目录：`figures/`

---

## 图片质量

- **分辨率**：300 DPI
- **格式**：PDF (矢量图，可无限缩放)
- **尺寸**：单栏 (8.5cm) / 双栏 (17.5cm)
- **字体**：DejaVu Sans (10-14pt)

---

## 修改建议

如需修改图表：
1. 编辑 `generate_figures.py`
2. 运行脚本重新生成
3. 更新 LaTeX 中的引用

---

*图表生成：OpenClaw Research Agent*  
*最后更新：2026-03-28*
