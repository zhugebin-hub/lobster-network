# 三级记忆 AI 助手 - 实验项目

## 项目信息
- **主题：** 人工智能基础与机器学习
- **作者：** 黄宝怡（浙江工商大学 人工智能学院）
- **日期：** 2026-05-14

## 项目结构
```
three-level-memory-ai/
├── knowledge_base/          # 知识库素材（15份文档）
│   ├── articles/            # 文章类
│   ├── courseware/          # 课件类
│   └── web_pages/           # 网页类
├── src/                     # 源代码
│   ├── memory_system.py     # 三级记忆系统核心
│   ├── knowledge_processor.py # 知识库预处理
│   └── rag_engine.py        # RAG 检索引擎
├── tests/                   # 测试用例
│   └── test_cases.md        # 3组测试问题
├── reports/                 # 实验报告
│   └── experiment_report.md # 1页实验报告
├── output/                  # 运行输出
└── README.md                # 本文件
```

## 快速开始
```bash
pip install -r requirements.txt
python src/memory_system.py
```

## 三级记忆架构
1. **感知记忆** - 对话上下文窗口（单轮即时信息）
2. **短期记忆** - 跨会话历史缓存（数天对话记录）
3. **长期记忆** - 向量化知识库 + RAG 语义检索（永久存储）
