# LLM-Enhanced MIL 谣言检测模型

基于论文《LLM-Enhanced Multiple Instance Learning for Joint Rumor and Stance Detection with Social Context Information》的 PyTorch 实现。

---

## DeepSeek 在模型中的作用（重要）

**DeepSeek 负责的是"语义增强"，而不是立场标注。**

Weibo 数据集中每条帖子已经有人工/大模型标注好的立场标签（support / deny / question / comment）。  
DeepSeek 做的是：给定一条帖子、其对应的 claim、以及已有的立场标签，**生成一段自然语言解释**，说明这条帖子 *为什么* 持有该立场（例如语言特征、与 claim 的逻辑关系、上下文线索等）。

这段解释文本随后由 BERT 编码成 `explanation_embeddings`，输入到 GlobalAttention 中，用于推断 claim 的谣言概率。这是论文架构的核心组件，不可缺失。

```
帖子 + claim + 立场标签
        ↓  DeepSeek API
   解释文本（WHY 该帖持此立场）
        ↓  BERT 编码
  explanation_embeddings
        ↓
  GlobalAttention → 谣言概率
```

生成的解释会自动缓存到 `data/llm_cache/`，同一条帖子只调用一次 API。

---

## 项目结构

```
.
├── train.py                        # 训练入口脚本
├── test_pipeline.py                # 离线完整性测试（无需网络）
├── requirements.txt                # Python 依赖
├── config/
│   └── default.yaml                # 模型/训练超参数配置
├── data/
│   ├── processed/
│   │   ├── weibo_train.json        # 训练集（3728 条事件）
│   │   ├── weibo_val.json          # 验证集（466 条）
│   │   └── weibo_test.json         # 测试集（467 条）
│   └── llm_cache/                  # LLM 解释缓存（训练时自动生成）
├── scripts/
│   └── convert_weibo_data.py       # Weibo 原始数据 → JSON 转换脚本
└── src/
    ├── models/
    │   ├── llm_enhanced_mil.py     # 主模型（两阶段训练）
    │   ├── post_encoder.py         # Post 编码器（BERT + Sentence-BERT）
    │   ├── attention_mechanisms.py # 局部/全局/聚合注意力
    │   ├── binary_classifiers.py   # K=8 二元 stance 分类器
    │   └── aggregation.py          # 二元模型聚合模块
    ├── data/
    │   ├── dataset.py              # RumorStanceDataset
    │   ├── data_loader.py          # DataLoader 工厂
    │   └── llm_explanation_generator.py  # LLM 解释生成（真实/Mock）
    ├── training/
    │   └── trainer.py              # Trainer（两阶段训练循环）
    └── utils/
        ├── config_loader.py        # YAML 配置加载
        └── metrics.py              # 评估指标
```

---

## 第一步：配置 Python 环境

### 推荐 Python 版本
Python 3.9 ~ 3.11（已在 3.9/3.10 验证）

### 创建虚拟环境
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate
```

### 安装依赖
```bash
pip install -r requirements.txt
```

如果网速慢，可以加国内镜像：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 第二步：下载预训练模型

模型需要联网下载两个预训练模型（总共约 500 MB）：

### 方案 A：设置国内镜像后自动下载（推荐）

```bash
# Windows PowerShell
$env:HF_ENDPOINT="https://hf-mirror.com"

# 下载到本地缓存（之后训练可离线使用）
python -c "
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModel

print('下载 Sentence-BERT（多语言，支持中文）...')
SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

print('下载 Chinese BERT（用于解释文本编码）...')
AutoTokenizer.from_pretrained('bert-base-chinese')
AutoModel.from_pretrained('bert-base-chinese')

print('下载完成！')
"
```

### 方案 B：手动下载后配置本地路径

1. 从 [https://hf-mirror.com](https://hf-mirror.com) 下载：
   - `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
   - `bert-base-chinese`

2. 解压到本地目录（例如 `D:/models/`），修改 `config/default.yaml`：
   ```yaml
   model:
     post_encoder:
       model_name: "D:/models/paraphrase-multilingual-MiniLM-L12-v2"
       bert_model:  "D:/models/bert-base-chinese"
   ```

> **离线 fallback**：若 Sentence-BERT 无法加载，系统自动用 BERT mean-pooling 替代，功能不受影响，效果略降。

---

## 第三步：验证代码完整性（无需下载模型）

正式训练前，用 mock 编码器跑完整流水线测试：

```bash
python test_pipeline.py
```

全部显示 `[PASS]` 说明所有模块逻辑正确。

---

## 第四步：配置 DeepSeek API Key

DeepSeek 用于对每条帖子生成语义增强解释（见文档开头说明），是训练的必要步骤。

1. 获取 API Key：[https://platform.deepseek.com](https://platform.deepseek.com)

2. 设置环境变量（每次训练前设置，或写入系统环境变量）：
   ```bash
   # Windows PowerShell
   $env:DEEPSEEK_API_KEY="sk-xxxxxx"

   # Linux / macOS
   export DEEPSEEK_API_KEY="sk-xxxxxx"
   ```

3. 确认 `config/default.yaml` 中：
   ```yaml
   use_mock_llm: false   # 已默认设置为 false，使用真实 API
   ```

> **费用说明**：每条帖子生成一次解释（约 100 词），生成后自动缓存到 `data/llm_cache/`。训练集共 ~200K 条帖子，首次运行会调用大量 API，后续 epoch 直接读缓存，不再重复计费。
>
> **如需快速验证代码流程（不计费）**：可临时将 `use_mock_llm: true`，使用 Mock 解释跑通训练循环，确认无误后再切回 `false` 正式训练。

---

## 第五步：配置其他训练参数

`config/default.yaml` 核心参数说明：

```yaml
model:
  post_encoder:
    retention_ratio: 0.3        # ρ：post 树交互保留比例（论文最优值）
  attention:
    local_retention_ratio: 0.5  # λ：局部注意力保留比例（论文最优值）

training:
  learning_rate: 0.001          # Adam 学习率（论文值）
  num_epochs_phase1: 200        # Phase 1：训练编码器 + 8 个二元分类器
  num_epochs_phase2: 100        # Phase 2：仅训练聚合模块
  patience: 30                  # Early stopping 耐心轮数

device: "cuda"   # 有 GPU 改为 "cuda"，否则 "cpu"
```

---

## 第六步：启动训练

```bash
# 使用默认配置训练
python train.py

# 指定配置文件
python train.py --config config/default.yaml

# 从断点继续（Phase 1 或 Phase 2 均可）
python train.py --resume checkpoints/best_model_p1.pt

# 固定随机种子（复现实验）
python train.py --seed 42
```

训练过程自动保存：
- `checkpoints/best_model_p1.pt` — Phase 1 最优模型
- `checkpoints/best_model_p2.pt` — Phase 2 最优模型（最终结果）
- `logs/` — TensorBoard 日志

查看训练曲线：
```bash
tensorboard --logdir logs
```

---

## 第七步：数据说明（无需操作）

`data/processed/` 中已包含从原始 Weibo 数据集转换好的完整数据：

| 文件 | 样本数 |
|------|--------|
| `weibo_train.json` | 3728 |
| `weibo_val.json`   | 466  |
| `weibo_test.json`  | 467  |
| **合计** | **4661** |

**无需重新转换**。如果将来需要重新生成（例如换原始数据），可运行：

```bash
python scripts/convert_weibo_data.py \
  --weibo_root "C:/path/to/Weibo_stance" \
  --output_dir "data/processed"
```

---

## 模型架构简介

```
输入：微博帖子序列（已含立场标签）+ claim 文本
      ↓
PostEncoder（Sentence-BERT + BERT）
  ├── post-level 编码（含传播树交互，ρ=0.3）
  └── explanation-level 编码（DeepSeek 生成的语义解释 → BERT 编码）
      ↓
K=8 个二元 stance 分类器（Nr×Ns = 2×4）
      ↓
HierarchicalStanceTreeAttention（每个分类器独立运行）
  ├── LocalAttention（λ=0.5，树邻居 dot-product 注意力）
  └── GlobalAttention（explanation-guided，输出 ỹ_c^k 谣言概率）
      ↓
BinaryModelsAggregation（claim-explanation 点积注意力）
  ├── 输出：最终 stance 预测（4 类）
  └── 输出：最终 rumor 预测（2 类：rumor / non-rumor）
```

### 两阶段训练

| 阶段 | 损失函数 | 训练参数 |
|------|---------|---------|
| Phase 1（200 epoch） | BCE(ỹ_c^k, y^k) × 8（论文 Eq.12） | PostEncoder + 8 分类器 + HierarchicalAttention |
| Phase 2（100 epoch） | BCE(ŷ_{c,r}, y_r) × 2（论文 Eq.13） | 仅 BinaryModelsAggregation（其余冻结） |

---

## 预期性能

根据论文，Weibo 数据集（二分类：rumor / non-rumor）目标：

| 指标 | 目标 |
|------|------|
| Micro-F1 | > 80% |
| Accuracy | > 82% |

---

## 常见问题

**Q: `DEEPSEEK_API_KEY not set` 错误**  
A: 见第四步，训练前需设置 `DEEPSEEK_API_KEY` 环境变量。

**Q: `OSError: We couldn't connect to 'https://huggingface.co'`**  
A: 需先下载预训练模型（见第二步），设置镜像：
```bash
$env:HF_ENDPOINT="https://hf-mirror.com"
```

**Q: `CUDA out of memory`**  
A: 减小 `config/default.yaml` 中的 `max_posts_per_claim`，或改用 `device: "cpu"`。

**Q: 训练很慢**  
A: 使用 GPU（`device: "cuda"`）。CPU 下每 epoch 约需数小时。
