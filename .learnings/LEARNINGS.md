# Learnings Log

> OpenClaw 自改进学习日志
> 创建时间：2026-04-19
> 参考：Hermes Agent 设计理念

---

## 使用说明

本文件记录从任务执行中提取的学习点、错误和改进建议。

### 快速记录

```bash
# 添加学习记录
./scripts/add-learning.sh "学习内容" "类别"

# 查看待处理学习
./scripts/manage-memory.sh status

# 搜索学习记录
./scripts/search-memory.sh "关键词"
```

---

## 学习记录

### [LRN-20260419-001] hermes-agent 调研完成

**Logged**: 2026-04-19T08:30:00+08:00
**Priority**: high
**Status**: promoted
**Area**: docs

### Summary
完成 Hermes Agent 框架调研，发现三层记忆架构值得借鉴

### Details
- Hermes 使用 ChromaDB 向量存储实现语义回忆
- OpenClaw 目前只有文件-based 记忆，缺乏语义检索
- 自改进能力是 Hermes 的核心差异化功能

### Suggested Action
1. 增强 self-improvement skill，支持自动提取 learnings
2. 评估添加 ChromaDB 向量存储的可行性
3. 开发全文搜索工具

### Metadata
- Source: task_completion
- Related Files: hermes-agent-research.md, hermes-design-analysis.md
- Tags: hermes, memory, self-improvement

### Resolution
- **Resolved**: 2026-04-19T08:45:00+08:00
- **Promoted**: memory-upgrade-plan.md
- **Notes**: 已创建实施计划文档，开始分阶段实施

---

### [LRN-20260419-002] 教学自动化需求明确

**Logged**: 2026-04-19T08:25:00+08:00
**Priority**: high
**Status**: pending
**Area**: docs

### Summary
图图老师的教学自动化需求已明确，5 大核心场景

### Details
1. 智能生成练习题（P0）
2. 自动批改作业（P0）
3. 学情分析报告（P1）
4. 教案自动生成（P1）
5. 错题本管理（P1）

### Suggested Action
1. 等待 Hermes 调研报告完成后匹配技术方案
2. 优先实现练习题生成功能
3. 考虑使用 Qwen/Math 专用模型

### Metadata
- Source: user_requirement
- Related Files: teaching-automation-requirements.md
- Tags: teaching, automation, requirements

---

## 错误记录

### [ERR-20260419-001] 无

当前无待处理错误。

---

## 功能请求

### [FEAT-20260419-001] 语义记忆检索

**Logged**: 2026-04-19T08:35:00+08:00
**Priority**: high
**Status**: pending
**Area**: infra

### Requested Capability
用户能够基于语义搜索历史记忆，而非仅靠关键词

### User Context
- 用户询问"上次我让你做什么来着？"时，需要语义检索
- 用户说"用上次那个方法处理这个"时，需要关联历史任务
- 当前文件-based 记忆无法满足这些场景

### Complexity Estimate
medium

### Suggested Implementation
1. 安装 ChromaDB 和中文嵌入模型
2. 开发索引服务，自动索引所有记忆文件
3. 开发检索 API，支持语义搜索
4. 集成到 OpenClaw，任务前自动检索相关上下文

### Metadata
- Frequency: recurring
- Related Features: search-memory, memory-management

---

### [FEAT-20260419-002] 自动技能创建

**Logged**: 2026-04-19T08:35:00+08:00
**Priority**: medium
**Status**: pending
**Area**: infra

### Requested Capability
从成功任务中自动创建技能文档

### User Context
- Hermes 能够自动从任务执行中创建和优化技能
- OpenClaw 目前需要手动创建技能
- 用户期望"越用越聪明"的体验

### Complexity Estimate
complex

### Suggested Implementation
1. 分析成功任务模式
2. 生成技能文档模板
3. 自动保存到 skills/ 目录
4. 支持人工审核和优化

### Metadata
- Frequency: recurring
- Related Features: self-improvement, skill-creator

---

## 统计信息

| 类别 | 数量 |
|------|------|
| 学习记录 | 2 |
| 错误记录 | 0 |
| 功能请求 | 2 |
| 已解决 | 1 |
| 待处理 | 3 |

---

**最后更新**: 2026-04-19
