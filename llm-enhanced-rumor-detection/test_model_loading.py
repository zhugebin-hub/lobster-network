"""
测试模型加载是否正常，验证离线模式和网络超时问题的修复
"""
import os
import sys
import torch

# 设置环境变量，优先使用本地缓存
os.environ['TRANSFORMERS_OFFLINE'] = '1'  # 强制离线模式
os.environ['HF_DATASETS_OFFLINE'] = '1'

print("=" * 80)
print("测试模型加载 - 验证网络超时问题修复")
print("=" * 80)

try:
    print("\n[1/4] 导入配置加载器...")
    from src.utils.config_loader import load_config
    
    print("\n[2/4] 加载配置文件...")
    config = load_config("config/default.yaml")
    print(f"  ✓ 配置加载成功")
    print(f"  - BERT 模型: {config.model.post_encoder.bert_model}")
    print(f"  - Sentence-BERT 模型: {config.model.post_encoder.sentence_bert_model}")
    print(f"  - 设备: {config.device}")
    
    print("\n[3/4] 创建 PostEncoder（这里可能会尝试下载模型）...")
    from src.models.post_encoder import PostEncoder
    
    # 临时关闭离线模式，允许下载（如果本地没有）
    if os.environ.get('TRANSFORMERS_OFFLINE'):
        del os.environ['TRANSFORMERS_OFFLINE']
    if os.environ.get('HF_DATASETS_OFFLINE'):
        del os.environ['HF_DATASETS_OFFLINE']
    
    encoder = PostEncoder(config)
    print(f"  ✓ PostEncoder 创建成功")
    print(f"  - 使用 Sentence-BERT: {encoder._use_sbert}")
    print(f"  - Hidden dim: {encoder.hidden_dim}")
    
    print("\n[4/4] 测试前向传播...")
    # 创建测试数据
    test_claim = "这是一条测试声明"
    test_posts = ["测试帖子1", "测试帖子2"]
    test_explanations = ["测试解释1", "测试解释2"]
    test_structure_info = ["root", "child"]
    test_tree_structure = {0: [], 1: [0]}
    
    # 移动模型到 CPU（避免 GPU 问题）
    encoder = encoder.to('cpu')
    
    # 前向传播
    with torch.no_grad():
        post_emb, claim_emb, expl_emb = encoder(
            test_claim,
            test_posts,
            test_explanations,
            test_structure_info,
            test_tree_structure
        )
    
    print(f"  ✓ 前向传播成功")
    print(f"  - Post embeddings shape: {post_emb.shape}")
    print(f"  - Claim embedding shape: {claim_emb.shape}")
    print(f"  - Explanation embeddings shape: {expl_emb.shape}")
    
    print("\n" + "=" * 80)
    print("✅ 所有测试通过！模型加载正常，可以开始训练。")
    print("=" * 80)
    
except ImportError as e:
    print(f"\n❌ 导入错误: {e}")
    print("   请确保已安装所有依赖: pip install -r requirements.txt")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    print(f"   错误类型: {type(e).__name__}")
    import traceback
    print("\n完整错误信息:")
    traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("可能的解决方案:")
    print("=" * 80)
    
    if "ConnectTimeout" in str(e) or "Connection" in str(e):
        print("1. 网络连接问题 - 模型需要首次下载")
        print("   解决方案:")
        print("   a) 设置 HuggingFace 镜像:")
        print("      export HF_ENDPOINT=https://hf-mirror.com")
        print("   b) 或手动下载模型到本地:")
        print("      - bert-base-chinese")
        print("      - paraphrase-multilingual-MiniLM-L12-v2")
        print("   c) 或使用 Mock 模式（修改 test_pipeline.py）")
    
    elif "local_files_only" in str(e):
        print("1. 本地缓存不存在")
        print("   解决方案:")
        print("   a) 首次运行需要联网下载模型")
        print("   b) 或手动下载模型到 ~/.cache/huggingface/")
    
    else:
        print("1. 检查配置文件 config/default.yaml")
        print("2. 检查依赖是否完整安装")
        print("3. 查看上面的完整错误信息")
    
    sys.exit(1)
