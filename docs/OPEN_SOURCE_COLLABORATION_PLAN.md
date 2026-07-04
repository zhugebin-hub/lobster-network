# 小龙虾网络开源项目 — GitHub协作方案

> **版本**: v1.0 | **日期**: 2026-06-21
> **项目名**: lobster-network（暂定）
> **同步人**: qoder小龙虾 → 诸葛马（教练/Hermes）
> **性质**: 开源项目的仓库组织与协作维护方案

---

## 一、项目概述

### 1.1 什么是"小龙虾网络"

小龙虾网络是一个 **AI多智能体协作学习框架**，让多个AI学员在教练的指导下，通过消息驱动、自动化调度、多层反馈闭环的机制，在真实任务中学习成长。

目前已在两个领域验证：围棋训练（3人协同，V6深夜自动调度）和视觉设计（HTML+Playwright海报/PPT管线）。

### 1.2 开源的价值

将这个项目开源，有几个核心价值：

1. **可复现**：任何人都可以搭建自己的"小龙虾网络"，训练自己的AI学员
2. **可验证**：开源代码和数据让社区可以验证四层反馈闭环是否真的有效
3. **可贡献**：社区可以为框架添加新的学习域（编程、写作、音乐等）
4. **可演化**：开源后项目不再依赖单一团队，社区驱动持续演进

### 1.3 当前资产盘点

服务器上已有的可开源代码和文档（共约4000行核心代码）：

| 类别 | 文件 | 行数 | 说明 |
|------|------|------|------|
| **调度系统** | go_coach_dispatcher_v6_nocturnal.py | 193 | V6深夜自动出题调度器 |
| **教练系统** | hermes_coach.py | 464 | 诸葛马教练（计划生成+评估） |
| **学员训练器** | xiaochen_go_trainer_v2.py | 632 | 小陈训练器（稳健型） |
| | zhuguxia_go_trainer_v3.py | 491 | 诸葛虾训练器（速度型） |
| | qoder_go_trainer_v1.py | 209 | qoder训练器（技术尖兵） |
| **视觉设计** | HTML_PLAYWRIGHT_VISUAL_SKILL.md | 607 | HTML+Playwright管线技能文档 |
| | ppt_generator.py | 359 | PPT生成框架（6种模板） |
| **技能体系** | GO_NINE_DAN_SKILL.md | 748 | 围棋九段技能体系 |
| **训练计划** | GO_TRAINING_PLAN_V5.md | 232 | 三龙虾协同作战方案 |
| **理念文档** | NETWORK_CONSTRUCTION_PHILOSOPHY.md | 321 | 网络建设理念 |
| **题库** | problem_bank/*.json | ~5000+ | 围棋死活/手筋/定式/官子/布局题库 |

---

## 二、GitHub仓库结构

### 2.1 建议的仓库组织

```
lobster-network/                  # 主仓库
├── README.md                     # 项目介绍（中英文）
├── LICENSE                       # MIT License
├── CONTRIBUTING.md               # 贡献指南
├── CHANGELOG.md                  # 变更日志
│
├── docs/                         # 文档目录
│   ├── architecture.md           # 系统架构说明
│   ├── philosophy.md             # 网络建设理念
│   ├── quickstart.md             # 快速上手指南
│   ├── domains/                  # 各学习域文档
│   │   ├── go/                   # 围棋域
│   │   │   ├── nine-dan-skill.md
│   │   │   ├── training-plan.md
│   │   │   └── rules.md
│   │   └── poster/               # 海报设计域
│   │       ├── visual-skill.md
│   │       └── ppt-guide.md
│   └── api/                      # API文档
│
├── core/                         # 核心框架
│   ├── dispatcher/               # 自动化调度引擎
│   │   ├── base_dispatcher.py    # 调度器基类
│   │   ├── go_dispatcher.py      # 围棋域调度实现
│   │   ├── nocturnal.py          # 深夜特训模式
│   │   └── README.md
│   │
│   ├── coach/                    # 教练系统
│   │   ├── hermes_coach.py       # 诸葛马教练
│   │   ├── evaluator.py          # 评估引擎
│   │   ├── planner.py            # 训练计划生成器
│   │   └── README.md
│   │
│   ├── agents/                   # AI学员框架
│   │   ├── base_agent.py         # 学员基类
│   │   ├── agent_profiles/       # 学员档案
│   │   │   ├── qoder.json
│   │   │   ├── xiaochen.json
│   │   │   └── zhuguxia.json
│   │   └── README.md
│   │
│   ├── messaging/                # 消息通信
│   │   ├── queue.py              # 文件队列实现
│   │   ├── ssh_bridge.py         # SSH桥接
│   │   └── README.md
│   │
│   └── feedback/                 # 四层反馈闭环
│       ├── realtime.py           # 秒级自动评估
│       ├── daily.py              # 日级教练分析
│       ├── weekly.py             # 周级协同学习
│       └── task_level.py         # 任务级用户验收
│
├── domains/                      # 学习域实现
│   ├── go/                       # 围棋域
│   │   ├── trainers/
│   │   │   ├── qoder_trainer.py
│   │   │   ├── xiaochen_trainer.py
│   │   │   └── zhuguxia_trainer.py
│   │   ├── problem_bank/         # 围棋题库
│   │   │   ├── life_death.json
│   │   │   ├── tesuji.json
│   │   │   ├── joseki.json
│   │   │   ├── endgame.json
│   │   │   └── fuseki.json
│   │   ├── evaluator.py          # 围棋评估器
│   │   └── README.md
│   │
│   └── poster/                   # 海报设计域
│       ├── tools/
│       │   ├── ppt_generator.py  # PPT生成框架
│       │   └── poster_renderer.py# 海报渲染器
│       ├── templates/            # HTML/CSS模板
│       └── README.md
│
├── tests/                        # 测试
│   ├── test_dispatcher.py        # 调度器测试
│   ├── test_coach.py             # 教练系统测试
│   ├── test_messaging.py         # 消息通信测试
│   ├── test_feedback.py          # 反馈闭环测试
│   ├── domains/
│   │   ├── test_go_trainer.py    # 围棋训练器测试
│   │   └── test_poster_tools.py  # 海报工具测试
│   └── integration/
│       ├── test_full_pipeline.py # 全流程集成测试
│       └── test_multi_agent.py   # 多智能体协作测试
│
├── scripts/                      # 运维脚本
│   ├── setup.sh                  # 一键部署
│   ├── deploy_cron.sh            # 部署定时任务
│   └── monitor.py                # 运行状态监控
│
├── data/                         # 示例数据
│   ├── sample_profiles/          # 示例学员档案
│   ├── sample_problems/          # 示例题库
│   └── sample_messages/          # 示例消息
│
└── examples/                     # 使用示例
    ├── quickstart_go.py          # 围棋训练快速上手
    ├── quickstart_poster.py      # 海报设计快速上手
    └── add_new_domain.py         # 添加新学习域
```

### 2.2 仓库命名建议

| 候选名称 | 说明 | 推荐度 |
|---------|------|--------|
| `lobster-network` | 直译"小龙虾网络"，简洁有力 | 首选 |
| `ai-lobster-academy` | 强调AI+教育属性 | 备选 |
| `multi-agent-learning` | 技术描述，SEO友好但缺少个性 | 备选 |

---

## 三、协作角色分工

### 3.1 各角色在开源项目中的定位

```
┌─────────────────────────────────────────────────┐
│                  诸葛斌教授                       │
│              项目发起人 · Maintainer              │
│     负责：方向把控、重大决策、社区治理             │
└───────────────────┬─────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────┐
│              qoder小龙虾                          │
│           技术负责人 · Core Contributor           │
│  负责：核心代码维护、PR审核、新域开发、CI/CD      │
└───────────────────┬─────────────────────────────┘
                    │
┌───────────────────┼─────────────────────────────┐
│                   │                             │
│  ┌────────────────▼────────────┐  ┌─────────────▼──────────┐
│  │       诸葛马（教练）         │  │   小陈 / 诸葛虾        │
│  │    Domain Expert · Reviewer │  │  Tester · Contributor  │
│  │ 负责：训练策略、评估模型、   │  │ 负责：集成测试、       │
│  │ 围棋域内容、文档审核         │  │ Bug报告、真实场景验证  │
│  └─────────────────────────────┘  └────────────────────────┘
```

### 3.2 具体职责清单

**诸葛斌教授（Maintainer）**
- 确定项目方向和开源策略
- 审核重大feature的合并
- 社区对外沟通（博客、演讲、论文）
- 审批新Contributor加入

**qoder小龙虾（Core Contributor）**
- 维护core/目录下的核心框架代码
- 审核Pull Request
- 开发新学习域的实现
- 维护CI/CD流水线
- 处理Issue中的技术Bug
- 编写技术文档和API文档

**诸葛马（Domain Expert / Reviewer）**
- 维护训练策略和评估模型
- 审核围棋域（domains/go/）的内容更新
- 编写和更新技能体系文档
- 验证新feature对训练效果的影响
- 为社区用户解答训练策略相关问题

**小陈 / 诸葛虾（Tester / Contributor）**
- 在真实训练场景中测试系统
- 提交Bug Report和Feature Request
- 测试新功能在不同环境下的兼容性
- 贡献训练数据和使用案例

---

## 四、协作工作流

### 4.1 Git分支策略

```
main ───────────────────────────────────── 稳定发布分支
  │
  ├── develop ──────────────────────────── 开发集成分支
  │     │
  │     ├── feature/go-dispatcher-v7 ──── 围棋V7调度器开发
  │     ├── feature/poster-animation ──── 海报动画功能
  │     ├── feature/new-domain-coding ── 新增编程学习域
  │     └── feature/feedback-dashboard ── 反馈闭环可视化面板
  │
  ├── hotfix/fix-message-loss ──────────── 紧急修复
  │
  └── release/v1.0 ────────────────────── 发布准备
```

### 4.2 PR审核流程

```
Contributor提交PR
      │
      ▼
qoder小龙虾 技术审核（代码质量、架构一致性）
      │
      ▼
诸葛马 领域审核（训练策略合理性、文档准确性）—— 如涉及训练相关内容
      │
      ▼
诸葛斌教授 最终审批 —— 仅重大feature需要
      │
      ▼
合并到develop → CI自动测试 → 合并到main
```

### 4.3 Issue管理

使用GitHub Issue Template：

| 模板 | 用途 | 分配 |
|------|------|------|
| Bug Report | 报告系统错误 | qoder小龙虾处理 |
| Feature Request | 新功能建议 | 教授审批 |
| Domain Proposal | 新学习域提案 | 全员讨论 |
| Training Question | 训练策略问题 | 诸葛马解答 |
| Documentation | 文档改进 | qoder小龙虾+诸葛马 |

---

## 五、维护与更新计划

### 5.1 版本发布节奏

| 版本类型 | 频率 | 内容 |
|---------|------|------|
| Patch（x.x.1） | 随时 | Bug修复、文档修正 |
| Minor（x.1.0） | 每2周 | 新功能、新域、性能优化 |
| Major（2.0.0） | 每季度 | 架构升级、重大重构 |

### 5.2 维护分工时间表

| 周期 | qoder小龙虾 | 诸葛马 | 小陈/诸葛虾 |
|------|-------------|--------|-------------|
| 每天 | 处理PR、修复Bug | 分析训练数据、更新策略 | 执行训练、提交反馈 |
| 每周 | 代码review、依赖更新 | 技能文档更新、评估模型调优 | 兼容性测试、用例贡献 |
| 每两周 | Minor版本发布 | 训练效果报告 | 集成测试验证 |
| 每月 | 架构审查、技术债清理 | 训练体系大版本更新 | 社区用例收集 |

### 5.3 文档维护规则

- 每个PR必须附带相关文档更新
- 技能文档使用统一模板（参考GO_NINE_DAN_SKILL.md格式）
- 所有README保持中英双语
- CHANGELOG.md记录每次发布的变更

---

## 六、测试方案

### 6.1 测试层次

```
┌──────────────────────────────────────────┐
│          集成测试 (Integration)           │
│  完整的多智能体协作流程端到端验证         │
│  负责人: 小陈 + 诸葛虾                   │
└──────────────────┬───────────────────────┘
                   │
┌──────────────────▼───────────────────────┐
│          组件测试 (Component)             │
│  调度器、教练、消息队列、反馈闭环         │
│  负责人: qoder小龙虾                     │
└──────────────────┬───────────────────────┘
                   │
┌──────────────────▼───────────────────────┐
│          单元测试 (Unit)                  │
│  每个模块的函数级测试                     │
│  负责人: qoder小龙虾 + CI自动运行         │
└──────────────────────────────────────────┘
```

### 6.2 关键测试场景

**调度器测试**
- 正常时段出题（验证题目难度匹配学员等级）
- 深夜特训模式（验证强度分级：热身→极限→定式库）
- 消息投递可靠性（验证inbox/outbox不丢消息）
- 错题间隔重复（验证1天→3天→7天→14天的调度逻辑）

**教练系统测试**
- 训练计划生成（验证计划覆盖学员短板）
- 评估准确性（验证升/降级判定合理）
- 动态难度调节（准确率<60%连续2天自动降级）
- 九段技能文档引用（验证训练内容与技能文档对齐）

**多智能体协作测试**
- 三人同时在线时的消息分发
- 对抗赛调度（循环制、计时、结果记录）
- 讨论局（同一盘棋的三人复盘流程）
- qoder技术助教模式（知识传递链路）

**跨域迁移测试**
- 新增一个学习域需要多少步骤
- 围棋域的调度器能否复用到其他域
- 反馈闭环框架是否域无关

### 6.3 CI/CD流水线

```yaml
# .github/workflows/ci.yml（建议配置）
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v --cov=core --cov-report=xml
      - run: playwright install chromium  # 海报域测试需要
      
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: ruff check core/ domains/
      - run: mypy core/
      
  docs:
    runs-on: ubuntu-latest
    steps:
      - run: python scripts/check_docs.py  # 检查文档链接、格式
```

### 6.4 诸葛马参与的测试验证

诸葛马作为"领域专家"，在每次发布前需要验证：

1. **训练策略回归测试**：新代码不能破坏现有的训练计划生成逻辑
2. **评估模型一致性**：同样的训练数据，评估结果应该一致
3. **技能文档同步**：代码变更是否与技能文档保持一致
4. **训练效果趋势**：新版本不能导致学员训练效果明显下降

---

## 七、诸葛马的具体协作任务

### 7.1 短期任务（本周）

1. **阅读并理解仓库结构**
   - 位置：/shared/opensource/lobster-network/（部署后）
   - 重点关注：core/框架代码、docs/文档
   - 时间：1天内完成

2. **审核围棋域内容**
   - 检查 domains/go/ 下的所有训练计划、技能文档
   - 确认内容准确、结构合理
   - 时间：2天内完成

3. **制定V7调度器需求**
   - 基于V6的运行经验，提出V7的改进需求
   - 写成Issue提交到GitHub
   - 时间：3天内完成

### 7.2 中期任务（2-4周）

4. **编写围棋域自动化测试用例**
   - 基于真实训练数据，编写测试用例
   - 覆盖：出题逻辑、评估逻辑、升/降级逻辑
   - 放入 tests/domains/test_go_trainer.py

5. **建立训练效果基准线（Baseline）**
   - 记录当前V6的训练效果数据
   - 作为后续版本对比的基准
   - 放入 data/baselines/

6. **审核社区PR中的训练策略变更**
   - 任何涉及训练计划、评估模型的PR都需要诸葛马审核
   - 确保新变更不会破坏训练效果

### 7.3 长期任务

7. **扩展围棋技能体系**
   - 持续更新 GO_NINE_DAN_SKILL.md
   - 增加新的定式、战术、AI理论
   - 目标：从v1.0升级到v2.0

8. **参与新学习域的策略设计**
   - 当社区贡献新的学习域时
   - 诸葛马提供教学策略方面的专业意见
   - 确保新域也遵循四层反馈闭环

9. **撰写训练方法论白皮书**
   - 总结多智能体协作学习的实践经验
   - 可作为学术论文或技术博客发布

---

## 八、下一步行动计划

### 8.1 立即可执行

| 步骤 | 负责人 | 内容 | 时间 |
|------|--------|------|------|
| 1 | 诸葛斌教授 | 创建GitHub仓库 `lobster-network` | 今天 |
| 2 | qoder小龙虾 | 将服务器代码迁移到仓库结构 | 1-2天 |
| 3 | qoder小龙虾 | 编写README.md（中英文） | 1天 |
| 4 | qoder小龙虾 | 配置CI/CD（GitHub Actions） | 1天 |
| 5 | 诸葛马 | 审核围棋域内容 | 2天 |
| 6 | 全员 | 第一次全流程测试 | 3天后 |

### 8.2 首次发布目标

**v0.1.0 — Alpha发布**
- 核心框架可用（dispatcher + coach + messaging）
- 围棋域完整可用（题库 + 训练器 + 评估器）
- 海报域基础可用（HTML+Playwright管线）
- 文档基本完整（README + quickstart + architecture）
- 测试覆盖率 > 60%

### 8.3 需要诸葛马确认的事项

1. 仓库名称 `lobster-network` 是否合适？
2. 开源许可证选择 MIT 还是 Apache 2.0？
3. 围棋域的训练数据（对局记录、做题历史）是否一并开源？
4. 诸葛马作为Reviewer，每周能投入多少时间审核PR？
5. 是否需要先内部运行稳定后再公开，还是现在就开放仓库？

---

## 九、沟通机制

### 9.1 GitHub作为主战场

- **代码讨论**：PR评论、Code Review
- **问题追踪**：Issue（带模板）
- **决策记录**：GitHub Discussions
- **发布公告**：GitHub Releases

### 9.2 服务器作为训练场

- 服务器（121.43.80.231）保持为实际的训练运行环境
- GitHub仓库的代码定期同步到服务器
- 服务器上的训练数据定期备份到GitHub（脱敏后）

### 9.3 消息队列作为日常通信

- 现有的 `/shared/messages/` 消息队列继续使用
- 新增 `/shared/opensource/` 目录用于开源项目相关文件
- 诸葛马的训练决策通过消息队列下发

---

> **本文档由诸葛斌教授提出方向，qoder小龙虾整理成协作方案**
> **同步目标**: 诸葛马（教练/Hermes）—— 请阅读后反馈
> **同步日期**: 2026-06-21
> **预期反馈时间**: 诸葛马确认后启动仓库搭建
