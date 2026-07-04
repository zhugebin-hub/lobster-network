# 算力时间调度论文 - 资料共享索引

**项目**：Time-Arbitrage Scheduling for Heterogeneous Cloud Computing  
**创建时间**：2026-03-28  
**共享对象**：小龙虾研究群  
**状态**：🟢 开放讨论

---

## 📁 核心资料位置

### 工作目录
```
/home/admin/.openclaw/workspace/research/
```

### 文件结构
```
research/
├── 📄 SHARED_INDEX.md              # 本文件 - 资料索引
├── 📄 README.md                     # 项目总览
├── 📄 progress_tracker.md           # 进度追踪
├── 📄 briefing_20260328.md          # 研究简报
├── 📄 optimization_summary_20260328.md  # 优化总结
│
├── 📊 paper/                        # 论文相关
│   ├── 📄 paper_draft_v1.md         # 论文初稿 (Markdown 版) ⭐
│   ├── 📄 paper_v1.tex              # 论文 LaTeX 版 ⭐
│   ├── 📄 references.bib            # 参考文献
│   ├── 📄 writing_progress_20260328.md  # 写作进度
│   ├── 📄 generate_figures.py       # 图表生成脚本
│   └── 📊 figures/                  # 论文图表 (8 个 PDF)
│       ├── fig1_cost_comparison.pdf
│       ├── fig2_completion_rate.pdf
│       ├── fig3_sla_violations.pdf
│       ├── fig4_latency_comparison.pdf
│       ├── fig5_price_sensitivity.pdf
│       ├── fig6_deferrable_fraction.pdf
│       ├── fig7_hourly_load_pattern.pdf
│       └── fig8_architecture.pdf
│
├── 📚 experiments/                  # 实验报告
│   ├── experiment_results_20260328.md          # 实验 #1
│   ├── experiment_results_20260328_v2.md       # 实验 #2
│   ├── experiment_results_20260328_final.md    # 实验 #3 ⭐
│   └── hypothesis_validation.md     # 假设验证
│
├── 💻 simulation/                   # 仿真代码
│   ├── simulator.py                 # 仿真器核心 ⭐
│   ├── experiment_runner.py         # 实验运行器
│   └── results/                     # 实验数据
│       └── experiment_results_*.json
│
├── 📖 literature_review.md          # 文献综述 (15 篇论文)
├── 📐 theoretical_model.md          # 理论模型
└── 📊 data_collection/              # 数据采集
    └── token_usage.db               # SQLite 数据库
```

---

## 🎯 关键文件说明

### 必读文件（快速了解）

| 文件 | 说明 | 阅读时间 |
|------|------|---------|
| `README.md` | 项目总览，核心成果 | 5 分钟 |
| `briefing_20260328.md` | 研究简报，进展汇报 | 10 分钟 |
| `paper_draft_v1.md` | 论文初稿 (Markdown) | 30 分钟 |
| `experiment_results_20260328_final.md` | 最终实验结果 | 15 分钟 |

### 讨论文件（欢迎批注）

| 文件 | 讨论点 |
|------|--------|
| `paper_draft_v1.md` | 论文结构、论述逻辑、实验设计 |
| `theoretical_model.md` | 形式化模型、公式推导 |
| `optimization_summary_20260328.md` | 优化过程、经验教训 |

### 代码文件（可运行复现）

| 文件 | 功能 | 运行方式 |
|------|------|---------|
| `simulation/simulator.py` | 仿真器核心 | `python3 simulator.py` |
| `simulation/experiment_runner.py` | 实验运行器 | `python3 experiment_runner.py` |
| `paper/generate_figures.py` | 图表生成 | `python3 generate_figures.py` |

---

## 📊 核心成果速览

### 关键数据

| 指标 | Baseline | Time-Arbitrage | 改善 |
|------|----------|----------------|------|
| **成本** | $3.59/12h | $0.26/12h | **-92.8%** 🚀 |
| **完成率** | 100% | **100%** | ✅ 保持 |
| **SLA 违约** | 44 次 | 44 次 | ⚠️ 持平 |
| **延迟** | 156s | 156s | ✅ 持平 |

### 经济价值

- **中型部署**（$10k/月）：年节省 **$111,360**
- **大型部署**（100×GPU）：年节省 **$3.3M+**

---

## 💬 讨论话题建议

### 话题 1：论文结构
- 当前结构是否合理？
- 是否需要增加消融实验？
- Related Work 是否充分？

### 话题 2：实验设计
- 合成负载 vs 真实负载
- 12 小时仿真是否足够？
- 是否需要更多 Baseline 对比？

### 话题 3：理论深度
- 形式化模型是否充分？
- 是否需要更多理论证明？
- 竞争比分析是否必要？

### 话题 4：投稿策略
- ICDCS vs HPDC vs CCGrid？
- 是否需要补充实验？
- 预期录取概率？

### 话题 5：后续工作
- 真实数据验证计划
- RL 调度器集成
- 开源策略

---

## 🔗 快速访问链接

### 论文草稿
- [Markdown 版](file:///home/admin/.openclaw/workspace/research/paper/paper_draft_v1.md)
- [LaTeX 版](file:///home/admin/.openclaw/workspace/research/paper/paper_v1.tex)

### 实验报告
- [最终实验结果](file:///home/admin/.openclaw/workspace/research/experiments/experiment_results_20260328_final.md)

### 代码
- [仿真器](file:///home/admin/.openclaw/workspace/research/simulation/simulator.py)
- [实验运行器](file:///home/admin/.openclaw/workspace/research/simulation/experiment_runner.py)

### 图表
- [Figure 1: 成本对比](file:///home/admin/.openclaw/workspace/research/paper/figures/fig1_cost_comparison.pdf)
- [Figure 2: 完成率](file:///home/admin/.openclaw/workspace/research/paper/figures/fig2_completion_rate.pdf)
- [Figure 8: 架构图](file:///home/admin/.openclaw/workspace/research/paper/figures/fig8_architecture.pdf)

---

## 📅 时间线

```
✓ 2026-03-28 08:00  项目启动
✓ 2026-03-28 09:00  首轮实验完成
✓ 2026-03-28 11:10  三轮优化完成
✓ 2026-03-28 11:20  论文初稿完成
✓ 2026-03-28 11:30  图表 + LaTeX 完成
○ 2026-04-04        群内讨论
○ 2026-04-11        论文修改 v2.0
○ 2026-04-18        投稿提交
```

---

## 👥 团队成员

- **诸葛斌** - 项目发起/指导
- **OpenClaw Research Agent** - 研究执行/论文撰写
- **小龙虾群成员** - 讨论/建议/审阅

---

## 📞 联系方式

- **钉钉群**：小龙虾研究群
- **项目仓库**：`/home/admin/.openclaw/workspace/research/`
- **共享文档**：本文件

---

## 🎯 下一步行动

1. **群内讨论**（2026-03-28 ~ 2026-04-04）
   - 审阅论文初稿
   - 提出修改建议
   - 讨论投稿策略

2. **论文修改**（2026-04-05 ~ 2026-04-11）
   - 根据建议修改
   - 补充消融实验
   - 完善相关工作

3. **投稿准备**（2026-04-12 ~ 2026-04-18）
   - 最终格式检查
   - 作者确认
   - 提交论文

---

## 📝 讨论记录模板

### 2026-03-28 群讨论

**参与人员**：

**讨论要点**：
1. 
2. 
3. 

**决策**：
- [ ] 
- [ ] 

**行动项**：
- [ ] @某人 - 任务 - 截止日期

---

*索引创建时间：2026-03-28 11:35*  
*最后更新：2026-03-28 11:35*  
*维护者：OpenClaw Research Agent*
