#!/usr/bin/env python3
"""
test_pipeline.py  --  离线完整流水线测试
Mock 掉所有需要下载的预训练模型，验证模型逻辑是否正确。
用法：  python test_pipeline.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import torch
import torch.nn as nn
from unittest.mock import patch, MagicMock

# ─────────────────────────────────────────────────────────────────────────────
# Mock HuggingFace / SentenceTransformer before any import
# ─────────────────────────────────────────────────────────────────────────────
HIDDEN = 768

class FakeSentenceTransformer:
    def encode(self, texts, convert_to_tensor=False):
        t = torch.randn(len(texts), HIDDEN)
        return t if convert_to_tensor else t.numpy()
    def get_sentence_embedding_dimension(self):
        return HIDDEN

class FakeTokenizerOutput(dict):
    pass

class FakeBertTokenizer:
    def __call__(self, texts, **kw):
        if isinstance(texts, str):
            texts = [texts]
        n = len(texts)
        L = 16
        out = FakeTokenizerOutput({
            'input_ids':      torch.zeros(n, L, dtype=torch.long),
            'attention_mask': torch.ones(n, L, dtype=torch.long),
            'token_type_ids': torch.zeros(n, L, dtype=torch.long),
        })
        return out

class FakeBertOutput:
    def __init__(self, n, L):
        self.last_hidden_state = torch.randn(n, L, HIDDEN)

class FakeConfig:
    hidden_size = HIDDEN

class FakeBertModel(nn.Module):
    config = FakeConfig()
    def __init__(self): super().__init__()
    def forward(self, input_ids, attention_mask=None, token_type_ids=None, **kw):
        n = input_ids.shape[0]
        return FakeBertOutput(n, input_ids.shape[1])

# Patch at module level before importing project code
with patch('transformers.AutoTokenizer.from_pretrained', return_value=FakeBertTokenizer()), \
     patch('transformers.AutoModel.from_pretrained',    return_value=FakeBertModel()), \
     patch('sentence_transformers.SentenceTransformer', return_value=FakeSentenceTransformer()):

    from src.utils.config_loader import load_config
    from src.models.llm_enhanced_mil import create_model
    from src.data.dataset import RumorStanceDataset, CollateFunction

# ─────────────────────────────────────────────────────────────────────────────
# Also patch inside PostEncoder so the already-imported classes use mock
# ─────────────────────────────────────────────────────────────────────────────
import src.models.post_encoder as pe_module
pe_module.AutoTokenizer = MagicMock(
    from_pretrained=MagicMock(return_value=FakeBertTokenizer()))
pe_module.AutoModel = MagicMock(
    from_pretrained=MagicMock(return_value=FakeBertModel()))
pe_module.SentenceTransformer = MagicMock(return_value=FakeSentenceTransformer())


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
PASS  = "[PASS]"
FAIL  = "[FAIL]"

def check(name, cond, detail=""):
    if cond:
        print(f"  {PASS}  {name}")
    else:
        print(f"  {FAIL}  {name}  {detail}")
    return cond


def make_fake_sample(n_posts=5):
    """Build a minimal sample dict without loading any data file."""
    return {
        'claim':         "这是一个测试谣言声明",
        'posts':         [f"帖子内容 {i}" for i in range(n_posts)],
        'explanations':  [f"解释文本 {i}" for i in range(n_posts)],
        'structure_info':[f"t{i+1} replied to c" for i in range(n_posts)],
        'tree_structure': {0: [1, 2], 1: [0, 3], 2: [0], 3: [1, 4], 4: [3]},
        'rumor_label':   1,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 1. Config
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== 1. 配置加载 ===")
cfg = load_config('config/default.yaml')
all_ok = True
all_ok &= check("学习率 = 0.001",          cfg.training.learning_rate == 0.001)
all_ok &= check("Phase1 epochs = 200",    cfg.training.num_epochs_phase1 == 200)
all_ok &= check("Phase2 epochs = 100",    cfg.training.num_epochs_phase2 == 100)
all_ok &= check("ρ = 0.3",               cfg.model.post_encoder.retention_ratio == 0.3)
all_ok &= check("λ = 0.5",               cfg.model.attention.local_retention_ratio == 0.5)
all_ok &= check("num_rumor_classes = 2",  cfg.model.mil.num_rumor_classes == 2)
all_ok &= check("num_binary_classifiers = 8", cfg.model.mil.num_binary_classifiers == 8)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Dataset
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== 2. 数据集 ===")
ds = RumorStanceDataset('data/processed/weibo_train.json', cfg,
                        mode='train', use_mock_llm=True)
all_ok &= check(f"训练集大小 > 0  (实际: {len(ds)})",  len(ds) > 0)
sample = ds[0]
all_ok &= check("样本含 'claim'",             'claim'       in sample)
all_ok &= check("样本含 'posts'",             'posts'       in sample)
all_ok &= check("样本含 'explanations'",      'explanations' in sample)
all_ok &= check("样本含 'rumor_label'",       'rumor_label'  in sample)
all_ok &= check("rumor_label 是整数 0/1",
                isinstance(sample['rumor_label'], int) and sample['rumor_label'] in (0, 1))
all_ok &= check("帖子数 <= 100",              len(sample['posts']) <= 100)

val_ds = RumorStanceDataset('data/processed/weibo_val.json', cfg,
                             mode='val', use_mock_llm=True)
all_ok &= check(f"验证集大小 > 0  (实际: {len(val_ds)})",  len(val_ds) > 0)


# ─────────────────────────────────────────────────────────────────────────────
# 3. 模型构建（使用 mock 数据）
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== 3. 模型构建 ===")
# Patch PostEncoder __init__ to use our fake models
from src.models.post_encoder import PostEncoder

_orig_init = PostEncoder.__init__
def _mock_init(self, config):
    nn.Module.__init__(self)
    self.config = config
    self.hidden_dim = config.model.post_encoder.hidden_dim
    self.retention_ratio = config.model.post_encoder.retention_ratio
    self.bert_tokenizer = FakeBertTokenizer()
    self.bert_model = FakeBertModel()
    self.sentence_bert = FakeSentenceTransformer()
    self._use_sbert = True
    self.post_projection         = nn.Linear(HIDDEN, HIDDEN)
    self.explanation_projection  = nn.Linear(HIDDEN, HIDDEN)
    self.claim_projection        = nn.Linear(HIDDEN, HIDDEN)
    self.dropout = nn.Dropout(0.1)

PostEncoder.__init__ = _mock_init

model = create_model(cfg)
n_params = sum(p.numel() for p in model.parameters())
all_ok &= check(f"模型参数量 > 0  (实际: {n_params:,})", n_params > 0)
all_ok &= check("包含 post_encoder",          hasattr(model, 'post_encoder'))
all_ok &= check("包含 binary_classifiers",    hasattr(model, 'binary_classifiers'))
all_ok &= check("包含 hierarchical_attention",hasattr(model, 'hierarchical_attention'))
all_ok &= check("包含 aggregation",           hasattr(model, 'aggregation'))
all_ok &= check("K=8 二元分类器",
                len(model.binary_classifiers.stance_classifiers) == 8)


# ─────────────────────────────────────────────────────────────────────────────
# 4. 前向传播
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== 4. 前向传播 ===")
sample_data = make_fake_sample(n_posts=6)
model.train()
outputs = model(sample_data)

all_ok &= check("输出含 'rumor_probs'",       'rumor_probs'         in outputs)
all_ok &= check("输出含 'stance_predictions'", 'stance_predictions'  in outputs)
all_ok &= check("输出含 'binary_rumor_probs'", 'binary_rumor_probs'  in outputs)
all_ok &= check("rumor_probs shape = (2,)",
                outputs['rumor_probs'].shape == (2,))
all_ok &= check("stance_predictions shape = (6, 4)",
                outputs['stance_predictions'].shape == (6, 4))
all_ok &= check(f"binary_rumor_probs 长度 = 8",
                len(outputs['binary_rumor_probs']) == 8)
# 每个 binary_rumor_prob 应该是标量 tensor
for bk in outputs['binary_rumor_probs']:
    if not (isinstance(bk, torch.Tensor) and bk.ndim == 0):
        all_ok &= check("binary_rumor_probs[k] 是标量", False,
                        f"得到 shape={bk.shape}")
        break
else:
    all_ok &= check("binary_rumor_probs[k] 都是标量", True)


# ─────────────────────────────────────────────────────────────────────────────
# 5. 损失函数
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== 5. 损失函数 ===")
for label in (0, 1):
    sample_data['rumor_label'] = label
    out = model(sample_data)

    l1 = model.compute_loss(out, sample_data, phase=1)
    all_ok &= check(f"Phase1 loss 可计算 (label={label})", 'total_loss' in l1)
    all_ok &= check(f"Phase1 loss 有梯度 (label={label})",
                    l1['total_loss'].requires_grad)
    all_ok &= check(f"Phase1 loss 值有限 (label={label})",
                    l1['total_loss'].isfinite().item())

    l2 = model.compute_loss(out, sample_data, phase=2)
    all_ok &= check(f"Phase2 loss 可计算 (label={label})", 'total_loss' in l2)
    all_ok &= check(f"Phase2 loss 有梯度 (label={label})",
                    l2['total_loss'].requires_grad)
    all_ok &= check(f"Phase2 loss 值有限 (label={label})",
                    l2['total_loss'].isfinite().item())


# ─────────────────────────────────────────────────────────────────────────────
# 6. 反向传播
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== 6. 反向传播 ===")
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
sample_data['rumor_label'] = 1

# Phase 1
model.train()
out = model(sample_data)
l1 = model.compute_loss(out, sample_data, phase=1)
optimizer.zero_grad()
l1['total_loss'].backward()
grad_norms = [p.grad.norm().item() for p in model.parameters()
              if p.grad is not None and p.requires_grad]
all_ok &= check("Phase1 反向传播成功，梯度数 > 0", len(grad_norms) > 0)
all_ok &= check("Phase1 梯度值有限",
                all(g == g and g < 1e10 for g in grad_norms))
optimizer.step()

# Phase 2 (freeze all but aggregation)
for p in model.parameters():     p.requires_grad = False
for p in model.aggregation.parameters(): p.requires_grad = True
out = model(sample_data)
l2 = model.compute_loss(out, sample_data, phase=2)
optimizer.zero_grad()
l2['total_loss'].backward()
grad_norms2 = [p.grad.norm().item() for p in model.aggregation.parameters()
               if p.grad is not None]
all_ok &= check("Phase2 反向传播成功", len(grad_norms2) > 0)
# restore
for p in model.parameters(): p.requires_grad = True


# ─────────────────────────────────────────────────────────────────────────────
# 7. predict 方法
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== 7. Predict ===")
preds = model.predict(sample_data)
all_ok &= check("predict 含 'rumor_class'",   'rumor_class'   in preds)
all_ok &= check("predict 含 'stance_classes'", 'stance_classes' in preds)
all_ok &= check("rumor_class 是标量",
                preds['rumor_class'].ndim == 0)
all_ok &= check("rumor_class ∈ {0,1}",
                preds['rumor_class'].item() in (0, 1))
all_ok &= check("stance_classes shape = (6,)",
                preds['stance_classes'].shape == (6,))


# ─────────────────────────────────────────────────────────────────────────────
# 8. Trainer 两阶段训练（1 step 验证）
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== 8. Trainer 两阶段训练（1 step）===")
from src.training.trainer import Trainer
from torch.utils.data import DataLoader

class SingleSampleDataset(torch.utils.data.Dataset):
    def __init__(self, s): self.s = s
    def __len__(self): return 4
    def __getitem__(self, i): return dict(self.s)

fake_loader = DataLoader(
    SingleSampleDataset(make_fake_sample()),
    batch_size=1, collate_fn=lambda b: b[0]
)

# Minimal config mock
cfg.training.num_epochs_phase1 = 1
cfg.training.num_epochs_phase2 = 1
cfg.training.patience          = 999
cfg.logging.save_every_n_epochs = 999

# Patch create_data_loaders to return our fake loaders
import src.training.trainer as trainer_mod
_orig_create = trainer_mod.create_data_loaders
trainer_mod.create_data_loaders = lambda *a, **kw: (fake_loader, fake_loader, fake_loader)

trainer = Trainer(cfg)
trainer.model = model   # reuse the already-built model
# Rebuild phase2 optimizer for the reused model
trainer.optimizer_p2 = torch.optim.Adam(
    model.aggregation.parameters(), lr=1e-3)

try:
    trainer.train()
    all_ok &= check("Trainer.train() 两阶段无异常", True)
except Exception as e:
    all_ok &= check("Trainer.train() 两阶段无异常", False, str(e))

trainer_mod.create_data_loaders = _orig_create  # restore


# ─────────────────────────────────────────────────────────────────────────────
# 总结
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 50)
if all_ok:
    print("全部测试通过！代码逻辑完整正确。")
else:
    print("存在失败的测试项，请检查上方 [FAIL] 输出。")
print("=" * 50)
sys.exit(0 if all_ok else 1)
