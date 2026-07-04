# OpenClaw-SimBench 实验包

本实验包用于支撑论文《面向AI原生任务执行的“小龙虾模式”》中的“本地受控工具基准（OpenClaw-SimBench）”部分。

## 1. 目标

该基准不依赖 ToolBench API key，也不要求外部在线接口。其核心目标是：

- 在统一工具集合下评估工具选择可靠性
- 在 JSON Schema 约束下评估参数合法性
- 在可控异常条件下评估失败恢复能力
- 为 OpenClaw Full、w/o Validator、w/o Retry、Zero-shot、ReAct 等方法提供一致的比较环境

## 2. 目录结构

- `data/tools.json`：本地模拟工具定义
- `data/tasks.jsonl`：评测任务样本
- `templates/prompt_baseline.txt`：基础提示词模板
- `templates/prompt_react.txt`：ReAct 风格提示词模板
- `scripts/run_simbench.py`：主评测脚本
- `scripts/evaluate_metrics.py`：计算 TSR / THR / PFER / AIT / RRR
- `scripts/generate_tasks.py`：扩展任务样本生成器
- `results/`：实验输出目录

## 3. 任务类型

当前样本按复杂度分为三类：

1. 单工具任务：只需一次合法工具调用
2. 双工具任务：需要两步工具链
3. 多工具链任务：需要跨步骤状态传递与异常恢复

## 4. 指标说明

- **TSR**：任务成功率
- **THR**：工具幻觉率
- **PFER**：参数格式错误率
- **AIT**：平均交互轮数
- **RRR**：重试恢复率
- **TCR**：工具选择正确率（可选补充指标）
- **MCSR**：多工具链任务成功率（可选补充指标）

## 5. 运行方式

```bash
cd OpenClaw_SimBench_实验包
python scripts/run_simbench.py \
  --tasks data/tasks.jsonl \
  --tools data/tools.json \
  --method openclaw_full \
  --output results/openclaw_full_runs.jsonl

python scripts/evaluate_metrics.py \
  --input results/openclaw_full_runs.jsonl \
  --output results/openclaw_full_metrics.json
```

## 6. 方法映射建议

- `zero_shot`：不做工具约束与参数校验
- `react`：多轮推理，但不做 Schema 级验证
- `openclaw_wo_validator`：保留 Tool Registry，关闭参数校验
- `openclaw_wo_retry`：保留 Tool Registry + Validator，关闭 Retry
- `openclaw_full`：完整执行链

## 7. 如何补论文表3

建议按以下顺序补结果：

1. 先填总体指标（N 全部样本）
2. 再按单工具 / 双工具 / 多工具链分层统计
3. 最后在 5.6 节补消融与误差分析

## 8. 注意事项

- 当前脚本默认使用“模拟代理”输出，便于无模型依赖跑通流程。
- 若你后续接入真实模型，只需要替换 `call_agent()` 函数即可。
- 评测规则已经和论文中的 THR / PFER / AIT / RRR 定义对齐。


## 9. 200样本默认配置

本包已内置 200 条任务样本，默认配比为：

- 单工具任务：70
- 双工具任务：60
- 多工具链任务：70

默认评测文件为 `data/tasks.jsonl`（已指向 200 样本版本），同时保留 `data/tasks_200.jsonl` 作为显式命名文件。

若你想重新生成 200 条样本，可运行：

```bash
python scripts/generate_tasks.py --num_single 70 --num_double 60 --num_multi 70 --output data/tasks_200.jsonl
```
