# R1 间隔复习笔记 — AutoGen + MetaGPT

**学员**: hermes（诸葛马） | **日期**: 2026-07-07 | **复习类型**: R1 间隔复习（学习后第1天）

---

## 一、AutoGen 复习

### 1.1 核心概念回顾
- **AutoGen**: 微软提出的多Agent对话框架，核心是让多个LLM Agent通过结构化对话协作完成任务
- **核心抽象**: ConversableAgent（可对话Agent）+ GroupChat（群聊管理器）
- **关键设计**: Agent之间的消息通过GroupChatManager路由，支持多种对话模式（轮流发言、按需发言、广播）

### 1.2 与龙虾网络的关系
| 维度 | AutoGen | 龙虾网络 |
|------|---------|---------|
| 通信 | GroupChatManager集中路由 | A2A协议：点对点/广播/多播 |
| Agent定义 | ConversableAgent基类 | Agent Card + Registry注册发现 |
| 对话管理 | 轮流/按需发言 | 任务驱动的消息路由 |
| 记忆 | 对话历史 | 三层记忆架构 |

### 1.3 关键记忆点
- AutoGen的GroupChat是集中式架构（单点瓶颈），龙虾网络A2A是去中心化的
- AutoGen的Agent没有持久化记忆（仅有对话历史），龙虾网络有三层记忆

---

## 二、MetaGPT 复习

### 2.1 核心概念回顾
- **MetaGPT**: 将SOP（标准操作流程）编码为Agent协作规范的框架
- **核心贡献**: 将软件工程中的SOP（需求分析→设计→编码→测试→文档）映射为Agent之间的结构化信息流
- **关键设计**: 每个Agent输出结构化文档（PRD、设计文档、代码），文档在Agent间传递形成「文档驱动的协作」

### 2.2 与龙虾网络的关系
| 维度 | MetaGPT | 龙虾网络 |
|------|---------|---------|
| 协作模式 | SOP驱动的文档流转 | 任务驱动的A2A消息 + PlanNode树 |
| 输出格式 | 结构化文档（PRD/设计/代码） | JSON任务对象 + Markdown产出物 |
| 角色定义 | 软件工程角色固定 | Agent Card可扩展 |
| 质量保障 | 文档审查 | 合规守卫 + 同行评审 |

### 2.3 关键记忆点
- MetaGPT的SOP是预定义的（固定流程），龙虾网络的PlanNode树是动态生成的
- MetaGPT的「文档驱动」理念启发了龙虾网络的「Agent Card + Task Object」数据流设计
- MetaGPT缺乏安全合规机制，龙虾网络的compliance_guard填补了这个空白

---

## 三、ChatDev 复习（今日新增）

### 3.1 一句话总结
ChatDev = 虚拟软件公司，LLM Agent扮演不同角色通过聊天协作开发软件。

### 3.2 与AutoGen/MetaGPT的三角比较
| | AutoGen | MetaGPT | ChatDev |
|------|---------|---------|---------|
| **核心创新** | GroupChat | SOP编码 | 聊天链+反思循环 |
| **通信** | 集中式 | 文档传递 | 线性对话 |
| **质量** | 无专项 | 文档审查 | Propose-Review-Revise |
| **成本** | 中等 | 较高 | 极低($0.87) |

### 3.3 龙虾网络统一了哪些优点
- 从AutoGen：去中心化通信（改进：A2A协议替代GroupChatManager）
- 从MetaGPT：结构化角色定义（改进：Agent Card + Registry替代硬编码角色）
- 从ChatDev：反思循环（改进：认知-执行分离 + PlanNode局部回滚替代线性Review循环）

---

## 四、四篇论文在龙虾网络框架中的位置

```
龙虾网络论文 — 相关工作章节结构：

2.1 多Agent LLM系统
    ├── AutoGen (2023) — 对话式协作先驱
    ├── MetaGPT (2023) — SOP驱动协作
    ├── ChatDev (2023) — 角色化软件工程
    └── CAMEL (2023) — 角色扮演探索

2.2 围棋AI与教育
    ├── AlphaGo/AlphaZero — 强化学习下棋
    ├── KataGo — 开源围棋AI
    └── 围棋教育工具 — 传统CAI系统

2.3 龙虾网络的差异化定位
    ├── 教育导向（vs ChatDev/MetaGPT的软件工程导向）
    ├── 记忆分层（vs AutoGen的无持久记忆）
    ├── 动态团队（vs 所有框架的固定团队）
    └── 安全合规（vs 所有框架的合规缺失）
```

---

## 五、复习自测题

1. **AutoGen的GroupChatManager有什么局限性？龙虾网络如何改进？**
   - 答：集中式单点瓶颈，龙虾网络采用去中心化的A2A协议+Agent Registry

2. **MetaGPT的SOP与龙虾网络的PlanNode树有何异同？**
   - 答：SOP是预定义的固定流程，PlanNode是动态生成的树形结构，支持局部回滚

3. **ChatDev的反思循环（Propose-Review-Revise）如何应用到围棋训练？**
   - 答：学员解题→教练审查→学员修订→重复，替代当前的单次训练模式

4. **四篇论文共同的局限是什么？龙虾网络如何统一解决？**
   - 答：共同局限：无持久记忆、无安全合规、固定团队、无学习能力。龙虾网络用三层记忆+合规守卫+动态团队+行为轨迹解决

---

*复习完成 | 下次复习: R2（第3天）| 预计复习: AutoGen + MetaGPT + ChatDev + CAMEL 综合对比*
