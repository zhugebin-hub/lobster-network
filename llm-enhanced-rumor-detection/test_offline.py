"""
离线测试脚本 - 完全不依赖网络，使用 Mock 模型
用于验证训练流程是否正常，不会因为网络问题而失败
"""
import os
import sys
import torch
import torch.nn as nn

print("=" * 80)
print("离线测试 - 使用 Mock 模型验证训练流程")
print("=" * 80)

try:
    print("\n[1/5] 导入必要模块...")
    from src.utils.config_loader import load_config
    
    print("\n[2/5] 加载配置...")
    config = load_config("config/default.yaml")
    print(f"  ✓ 配置加载成功")
    
    print("\n[3/5] 创建 Mock PostEncoder（不加载真实预训练模型）...")
    
    class MockPostEncoder(nn.Module):
        """Mock PostEncoder，不依赖预训练模型"""
        def __init__(self, config):
            super().__init__()
            self.hidden_dim = config.model.post_encoder.hidden_dim
            self.post_projection = nn.Linear(self.hidden_dim, self.hidden_dim)
            self.claim_projection = nn.Linear(self.hidden_dim, self.hidden_dim)
            self.explanation_projection = nn.Linear(self.hidden_dim, self.hidden_dim)
            
        def forward(self, claim, posts, explanations, structure_info, tree_structure):
            num_posts = len(posts)
            device = next(self.parameters()).device
            
            # 返回随机嵌入
            post_emb = torch.randn(num_posts, self.hidden_dim * 2, device=device)
            claim_emb = torch.randn(self.hidden_dim, device=device)
            expl_emb = torch.randn(num_posts, self.hidden_dim, device=device)
            
            return post_emb, claim_emb, expl_emb
    
    encoder = MockPostEncoder(config)
    print(f"  ✓ Mock PostEncoder 创建成功")
    
    print("\n[4/5] 创建完整模型...")
    from src.models.llm_enhanced_mil import LLMEnhancedMIL
    
    # 临时替换 PostEncoder
    import src.models.llm_enhanced_mil as mil_module
    original_PostEncoder = mil_module.PostEncoder
    mil_module.PostEncoder = MockPostEncoder
    
    model = LLMEnhancedMIL(config)
    print(f"  ✓ 模型创建成功")
    print(f"  - 参数数量: {sum(p.numel() for p in model.parameters()):,}")
    
    # 恢复原始 PostEncoder
    mil_module.PostEncoder = original_PostEncoder
    
    print("\n[5/5] 测试前向传播和损失计算...")
    model.eval()
    
    # 创建测试数据
    batch_data = {
        'claim': "测试声明",
        'posts': ["测试帖子1", "测试帖子2"],
        'explanations': ["测试解释1", "测试解释2"],
        'structure_info': ["root", "child"],
        'tree_structure': {0: [], 1: [0]},
        'rumor_label': 0
    }
    
    # 前向传播
    with torch.no_grad():
        outputs = model(batch_data)
        print(f"  ✓ 前向传播成功")
        print(f"  - Rumor probs shape: {outputs['rumor_probs'].shape}")
        print(f"  - Stance predictions shape: {outputs['stance_predictions'].shape}")
        
        # 测试损失计算
        losses_p1 = model.compute_loss(outputs, batch_data, phase=1)
        losses_p2 = model.compute_loss(outputs, batch_data, phase=2)
        print(f"  ✓ 损失计算成功")
        print(f"  - Phase 1 loss: {losses_p1['total_loss'].item():.4f}")
        print(f"  - Phase 2 loss: {losses_p2['total_loss'].item():.4f}")
        
        # 测试预测
        pred_p1 = model.predict(batch_data, use_phase1_logic=True)
        pred_p2 = model.predict(batch_data, use_phase1_logic=False)
        print(f"  ✓ 预测成功")
        print(f"  - Phase 1 rumor class: {pred_p1['rumor_class'].item()}")
        print(f"  - Phase 2 rumor class: {pred_p2['rumor_class'].item()}")
    
    print("\n" + "=" * 80)
    print("✅ 离线测试通过！训练流程正常，可以开始训练。")
    print("=" * 80)
    print("\n提示:")
    print("1. 如果要使用真实预训练模型，需要先下载模型到本地")
    print("2. 或者设置 HuggingFace 镜像: export HF_ENDPOINT=https://hf-mirror.com")
    print("3. 当前配置使用 Mock LLM，训练速度会很快")
    
except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
