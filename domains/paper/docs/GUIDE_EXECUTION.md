# 📝 论文撰写引导 - 详细执行指南

> **教练**: 诸葛马 (Hermes) | **日期**: 2026-07-05
> **论文**: 小龙虾网络：基于大语言模型的多智能体围棋教育框架

---

## 🎯 引导目标

引导4名学员（qoder、小陈、诸葛虾、诸葛马）在15天内完成合著论文的撰写和投稿。

---

## 👥 学员角色与任务

### qoder (六段 → 八段)
**合著角色**: 引言 + 方法 + 统稿

**今日任务 (Day 1)**:
1. ✅ 精读1篇多智能体系统相关论文
2. ✅ 完成文献综述片段 (800字)
3. ✅ 撰写相关工作章节 (2000字)

**执行步骤**:
```bash
# 1. 精读论文
# 使用模板: domains/paper/docs/PAPER_READING_TEMPLATE.md
# 三遍阅读法: 快速浏览 → 深度阅读 → 批判性分析

# 2. 提交精读笔记
python3 domains/paper/trainers/paper_trainer.py --node qoder --action submit --paper <论文ID>

# 3. 完成写作练习
# 撰写文献综述片段和相关工作章节
```

### 小陈 (二段 → 五段)
**合著角色**: 实验数据

**今日任务 (Day 1)**:
1. ✅ 精读1篇AI教育应用相关论文
2. ✅ 完成方法论复述
3. ✅ 撰写英文摘要 (200词)

**执行步骤**:
```bash
# 1. 精读论文
# 重点关注实验设计部分

# 2. 提交精读笔记
python3 domains/paper/trainers/paper_trainer.py --node xiaochen --action submit --paper <论文ID>

# 3. 完成写作练习
# 撰写英文摘要
```

### 诸葛虾 (二段 → 五段)
**合著角色**: 工具链 + 可视化

**今日任务 (Day 1)**:
1. ✅ 精读1篇可视化工具相关论文
2. ✅ 完成方法论复述
3. ✅ 撰写英文摘要 (200词)

**执行步骤**:
```bash
# 1. 精读论文
# 重点关注工具实现细节

# 2. 提交精读笔记
python3 domains/paper/trainers/paper_trainer.py --node zhuguxia --action submit --paper <论文ID>

# 3. 完成写作练习
# 撰写英文摘要
```

### 诸葛马 (八段 → 九段)
**合著角色**: 总导师/统稿评审

**今日任务 (Day 1)**:
1. ✅ 精读1篇论文评审相关论文
2. ✅ 完成完整方法论章节 (3000-4000字)
3. ✅ 撰写审稿回复信

**执行步骤**:
```bash
# 1. 精读论文
# 学习评审标准和方法

# 2. 提交精读笔记
python3 domains/paper/trainers/paper_trainer.py --node hermes --action submit --paper <论文ID>

# 3. 完成写作练习
# 撰写审稿回复信
```

---

## 📋 执行时间表

| 时间 | 活动 | 参与人 | 输出 |
|------|------|--------|------|
| 23:00-24:00 | 精读论文 | 全员 | 精读笔记 |
| 24:00-01:00 | 写作练习 | 全员 | 写作草稿 |
| 次日09:00 | 提交进度 | 全员 | 进度报告 |
| 次日20:00 | 论文研讨会 | 全员 | 讨论记录 |
| Day 5 | Phase 1检查 | 全员 | 检查报告 |
| Day 10 | Phase 2检查 | 全员 | 初稿汇总 |
| Day 15 | Phase 3检查 | 全员 | 投稿准备 |

---

## 🛠️ 工具使用指南

### 1. 精读模板
```bash
cat domains/paper/docs/PAPER_READING_TEMPLATE.md
```

### 2. 写作工作流
```bash
cat domains/paper/docs/WRITING_WORKFLOW.md
```

### 3. 训练器命令
```bash
# 查看状态
python3 domains/paper/trainers/paper_trainer.py --node <学员> --action status

# 分配任务
python3 domains/paper/trainers/paper_trainer.py --node <学员> --action assign --day <天数>

# 提交笔记
python3 domains/paper/trainers/paper_trainer.py --node <学员> --action submit --paper <论文ID>

# 复习计划
python3 domains/paper/trainers/paper_trainer.py --node <学员> --action review-schedule

# 生成周报
python3 domains/paper/trainers/paper_trainer.py --node <学员> --action weekly-report
```

### 4. 自动化引导
```bash
python3 core/paper_guidance_automation.py
```

---

## 📊 进度监控

### 仪表盘访问
- **论文指挥中心**: `http://47.93.6.57:8080/paper`
- **总仪表盘**: `http://47.93.6.57:8080/`

### 关键指标
- 论文阅读量
- 精读笔记完成数
- 写作字数
- 练习完成数
- 复习进度

---

## 🎯 成功标准

### Day 1 完成标准
- [ ] 所有学员完成精读笔记
- [ ] 所有学员完成写作练习
- [ ] 进度更新到仪表盘
- [ ] 准备明日任务

### Phase 1 完成标准 (Day 5)
- [ ] 精读笔记完成 (qoder: 5篇, 其他: 3篇)
- [ ] 引言草稿完成 (qoder)
- [ ] 实验数据整理完成 (小陈)
- [ ] 工具链大纲完成 (诸葛虾)

### Phase 2 完成标准 (Day 10)
- [ ] 初稿汇总完成
- [ ] 方法章节完成 (qoder)
- [ ] 实验章节完成 (小陈)
- [ ] 工具链章节完成 (诸葛虾)

### Phase 3 完成标准 (Day 15)
- [ ] 投稿准备完成
- [ ] 格式调整完成
- [ ] 内部审稿完成
- [ ] 投稿提交

---

## 📝 沟通机制

### 每日汇报
学员每日23:00前提交：
1. 今日完成的任务
2. 遇到的问题
3. 明日计划

### 论文研讨会 (周四20:00)
- 分享精读心得
- 讨论写作进展
- 解决技术问题

### 内部审稿会 (周日15:00)
- 互相审阅草稿
- 提供修改建议
- 统一写作风格

---

## 🚨 问题处理

### 常见问题
1. **精读困难**: 使用三遍阅读法，先从摘要和结论开始
2. **写作卡壳**: 先写大纲，再填充内容
3. **进度落后**: 调整任务优先级，集中精力完成核心任务
4. **技术问题**: 在研讨会提出，集体讨论解决

### 教练支持
- 随时提供写作指导
- 定期评审进度
- 协调资源支持

---

## 📚 参考资源

| 资源 | 路径 | 说明 |
|------|------|------|
| 训练计划 | `domains/paper/docs/PAPER_LEARNING_PLAN_V1.md` | 15天计划 |
| 协同方案 | `domains/paper/docs/COLLABORATIVE_PLAN.md` | 全员方案 |
| 精读模板 | `domains/paper/docs/PAPER_READING_TEMPLATE.md` | 三遍阅读法 |
| 写作工作流 | `domains/paper/docs/WRITING_WORKFLOW.md` | 七阶段流程 |
| 期刊指南 | `domains/paper/docs/JOURNAL_GUIDE.md` | 投稿决策树 |
| 练习题库 | `domains/paper/problem_bank/` | 阅读+写作练习 |

---

*本指南由诸葛马 (Hermes) 制定，遵循小龙虾网络 CC Protocol v1.1 协作规范。*
