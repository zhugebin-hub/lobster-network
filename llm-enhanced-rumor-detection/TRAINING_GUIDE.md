# 训练指南 - 已优化版本

## 🚨 重要说明

这份代码已经过优化，解决了以下关键问题：

### 修复的问题
1. ✅ **关闭真实 LLM 调用**：改用 `use_mock_llm: true`，避免每个样本都调 DeepSeek API
2. ✅ **缩小训练规模**：从 200+100 epoch 改为 10+5 epoch，适合快速验证
3. ✅ **减少数据规模**：max_posts 从 100 降到 50，序列长度减半
4. ✅ **去掉冗余日志**：删除每个 epoch 打印完整预测列表的 DEBUG 代码

### 原代码的主要问题
- ❌ `use_mock_llm: false` 导致训练时每个样本、每条帖子都调用 DeepSeek API
- ❌ API 调用有 1 秒强制延迟，导致训练极慢（两天才 8 个 epoch）
- ❌ 配置过重（200+100 epoch，100 posts，256 explanation length）
- ❌ 冗余日志拖慢训练

---

## 📊 当前配置说明

### 任务类型
这是一个**联合任务**，不是单纯的二分类或四分类：

- **主任务：谣言检测（二分类）**
  - `non-rumor` vs `rumor`
  - 训练日志里的 `rumor_acc` 就是这个指标
  
- **辅助任务：立场检测（四分类）**
  - `support` / `deny` / `question` / `comment`
  - 训练日志里的 `stance_acc` 是这个指标

### 当前 epoch 配置
```yaml
num_epochs_phase1: 10  # 第一阶段（原 200）
num_epochs_phase2: 5   # 第二阶段（原 100）
```

**总计 15 个 epoch**，适合快速验证模型逻辑和训练流程。

### 数据规模配置
```yaml
max_posts_per_claim: 50   # 每个 claim 最多 50 条帖子（原 100）
max_post_length: 64       # 帖子最大长度 64（原 128）
max_explanation_length: 128  # 解释最大长度 128（原 256）
```

---

## 🚀 训练步骤

### 1. 确认环境
```bash
# 检查 CUDA 是否可用
python -c "import torch; print('CUDA:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"

# 查看 GPU 状态
nvidia-smi
```

### 2. 启动训练
```bash
python train.py
```

### 3. 监控训练（另开终端）
```bash
# 实时查看 GPU 使用
nvidia-smi -l 2

# 查看训练进程
ps aux | grep train.py
```

---

## 📈 预期训练时间

### 使用 Mock LLM（当前配置）
- **Phase 1（10 epoch）**：约 1-3 小时（取决于 GPU 和数据集大小）
- **Phase 2（5 epoch）**：约 0.5-1.5 小时
- **总计**：约 2-5 小时

### 如果改回真实 LLM（不推荐）
- **极慢**，可能需要数天甚至数周
- 每个样本都会调用 DeepSeek API，有 1 秒延迟
- 不适合直接训练，建议先离线生成 explanation

---

## 📊 准确率说明

### 训练日志里的 `rumor_acc` 是什么
这是**谣言二分类准确率**，不是四分类立场准确率。

### 正常水平参考
- **二分类 rumor_acc**：
  - `< 0.5`：明显有问题，需要检查配置和数据
  - `0.5 - 0.7`：一般水平
  - `> 0.7`：较好水平
  - `> 0.8`：很好水平

- **四分类 stance_acc**：
  - `< 0.3`：接近随机
  - `0.3 - 0.5`：一般水平
  - `> 0.5`：较好水平

### 如果准确率只有 0.33
这是**二分类准确率**，说明：
- 模型效果不理想
- 可能是训练轮数太少（当前只有 10+5）
- 可能是数据质量问题
- 可能是配置需要调整

---

## ⚙️ 如果要改回正式训练配置

**不建议直接改回 200+100 epoch + 真实 LLM。**

### 推荐方案
1. **先用当前配置验证训练流程正常**
2. **逐步增加 epoch**：
   ```yaml
   num_epochs_phase1: 50
   num_epochs_phase2: 25
   ```
3. **确认效果后再考虑是否增加到 100+50**
4. **始终保持 `use_mock_llm: true`**

### 如果一定要用真实 LLM
**强烈建议先离线生成 explanation**：

1. 写一个脚本，对所有训练/验证/测试数据预生成 explanation
2. 把 explanation 写回 JSON 的每个 post 里
3. 这样训练时就不会重复调用 API

否则训练时间会非常长（数天到数周）。

---

## 🔍 常见问题

### Q1: 为什么训练这么慢？
**A:** 如果你用的是 `use_mock_llm: false`，那就是因为每个样本都在调 DeepSeek API。改成 `true` 即可。

### Q2: 准确率只有 0.33 正常吗？
**A:** 不正常。这是二分类准确率，说明模型效果不好。可能原因：
- 训练轮数太少（当前只有 15 个 epoch）
- 数据质量问题
- 配置需要调整

### Q3: 两天才跑到 8 个 epoch 正常吗？
**A:** 完全不正常。这说明你用的是 `use_mock_llm: false`，每个样本都在调 API。改成 `true` 后，15 个 epoch 应该在几小时内完成。

### Q4: 这个模型到底是二分类还是四分类？
**A:** 都有。这是联合任务：
- **主任务：谣言二分类**（训练日志里的 `rumor_acc`）
- **辅助任务：立场四分类**（训练日志里的 `stance_acc`）

### Q5: 如何停止训练？
```bash
# 只停训练，不要杀系统进程
pkill -f "python train.py"

# 或者先查进程 ID
ps aux | grep train.py
kill -9 <PID>
```

**不要用 `pkill -9 python` 或 `kill -9 <jupyter_pid>`**，会把整个环境杀掉。

---

## 📝 训练日志示例

正常的训练日志应该类似：

```
Device: cuda
Model params: 12,345,678
Phase 1 epochs: 10 | Phase 2 epochs: 5

=== Phase 1: Training binary classifiers + encoder ===
Phase1/Ep0: 100%|████████| 100/100 [00:30<00:00, 3.33it/s, loss=0.6543, lr=0.001000]
Validation: 100%|████████| 20/20 [00:05<00:00, 4.00it/s]

[P1] Epoch 0: train_loss=0.6543  val_loss=0.6234
  rumor_acc=0.5500  rumor_f1=0.5234

...
```

如果你看到：
- 每个 batch 都卡很久
- 日志里出现大量 API 错误
- 或者根本没有进度条

那说明配置有问题。

---

## 🎯 下一步建议

1. **先用当前配置跑完 15 个 epoch**
2. **确认训练流程正常、GPU 正常使用**
3. **查看最终的 rumor_acc 和 rumor_f1**
4. **如果效果不理想，再考虑调整配置**

不要一上来就用 200+100 epoch + 真实 LLM，那样会浪费大量时间。

---

## 📞 如果遇到问题

检查以下几点：

1. **配置文件是否正确**
   ```bash
   cat config/default.yaml | grep -E "use_mock_llm|num_epochs"
   ```

2. **CUDA 是否可用**
   ```bash
   python -c "import torch; print(torch.cuda.is_available())"
   ```

3. **GPU 是否在工作**
   ```bash
   nvidia-smi
   ```

4. **训练进程是否存在**
   ```bash
   ps aux | grep train.py
   ```

---

**最后提醒：当前配置已经是优化后的快速验证版，适合先确认训练流程正常。不要直接改回 200+100 epoch + 真实 LLM。**
