# AI人文思考报告 - 项目说明

## 项目信息
- **作者：** 黄宝怡
- **学校：** 浙江工商大学 人工智能学院
- **主题：** 与AI助手对话的人文思考
- **日期：** 2026-05-14

## 项目结构
```
ai-humanities-report/
├── 报告.md                    # 完整报告（主文档）
├── src/                       # 源代码
│   ├── bias_detector.py       # 词嵌入偏见检测
│   ├── simple_rag.py          # 简化版RAG系统
│   └── timeline.py            # AI发展时间线
├── data/                      # 数据文件
│   ├── ai_timeline.json       # AI发展时间线数据
│   └── system_prompt_template.md # 系统提示词模板
├── output/                    # 运行输出
│   ├── bias_detection_results.json # 偏见检测结果
│   └── rag_test_results.json     # RAG测试结果
└── README.md                  # 本文件
```

## 快速开始
```bash
# 运行AI发展时间线
python src/timeline.py

# 运行词嵌入偏见检测
python src/bias_detector.py

# 运行RAG系统测试
python src/simple_rag.py
```

## 报告内容
1. 与小龙虾AI的5段深度对话记录
2. 课程知识结合（公平性、可解释性、偏见检测）
3. RAG技术深入探讨与实践
4. 系统运行截图与数据
5. 个人心得体会
