# 🐚 小薇 · V2 围棋进阶训练计划 — 25k→20k

> **版本**: V2.0 | **启动日期**: 2026-06-27
> **学员**: 小薇 (xiaowei)
> **教练**: 诸葛马（zhugema）
> **先修**: V1 7天速成（30k→25k，准确率 81.7%）
> **目标**: 25k → 20k（预计7-10天）

---

## 一、V1 复盘点

| 模块 | 得分 | 评价 |
|------|------|------|
| 综合/基本概念 | 7.0 | 🌟 最强项 |
| 吃子 | 6.5 | ✅ 良好 |
| 定式 | 6.0 | ✅ 良好 |
| 连接 | 4.0 | ⚠️ 需加强 |
| 实战 | 3.0 | ⚠️ 需加强 |
| **死活** | **3.5** | 🔴 **最弱项 — V2重点** |
| 分断 | 1.5 | 🔴 严重短板 |

## 二、V2 训练大纲

```
Phase 1 (1-3天): 🔴 死活专项突破
  Day 8: 死活进阶 — 刀五、梅花五、葡萄六、扳六
  Day 9: 死活实战 — 角上死活、边上死活、中央死活
  Day 10: 死活综合 — 对杀、双活、劫活

Phase 2 (4-5天): 🟡 连接分断强化
  Day 11: 连接进阶 — 尖、飞、双、虎口连接
  Day 12: 分断实战 — 断、扳、挖、靠断

Phase 3 (6-7天): 🟢 实战能力提升
  Day 13: 13x13 棋盘实战 — 布局+中盘+收官
  Day 14: 综合测评 — 进阶死活+实战模拟

每日流程:
  - 8题专项训练
  - 1局9x9或13x13实战
  - 错题复盘
```

## 三、评估标准

### 每日通过标准
- 准确率 ≥ 70%（进阶标准，比V1提高10%）
- 错题当日复盘完毕

### 升级标准（25k→20k）
- [ ] 死活专项准确率 ≥ 65%
- [ ] 能识别刀五/梅花五/葡萄六/扳六的死活
- [ ] 能解决边上和角上的基本死活题
- [ ] 连接/分断准确率 ≥ 70%
- [ ] 能在13x13棋盘完成完整对局
- [ ] 累计做题 ≥ 100题
- [ ] V2总体准确率 ≥ 72%

## 四、技术配置

```
训练器: domains/go/trainers/xiaowei_go_trainer_v2.py
题库:
  - domains/go/problem_bank/day8_problems.json  (死活进阶)
  - domains/go/problem_bank/day9_problems.json  (死活实战)
  - domains/go/problem_bank/day10_problems.json (死活综合)
  - domains/go/problem_bank/day11_problems.json (连接进阶)
  - domains/go/problem_bank/day12_problems.json (分断实战)
  - domains/go/problem_bank/day13_problems.json (13x13实战)
  - domains/go/problem_bank/day14_problems.json (综合测评)
```
