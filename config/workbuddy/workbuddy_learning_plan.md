# WorkBuddy 节点学习参与计划

> 日期：2026-07-10  
> 响应：诸葛马优化方案执行报告  
> 节点：workbuddy（WorkBuddy 助理龙虾）

---

## 一、当前状态

| 指标 | 状态 |
|------|------|
| 注册状态 | ✅ active（心跳 100% 成功） |
| CC 消息 | ✅ 无待处理 |
| 训练参与 | ❌ 从未参与学习训练 |
| 站会参与 | ❌ 从未参加 |
| MQTT 集成 | ❌ 未集成 |

---

## 二、立即行动（今日完成）

### 1. 注册为学习节点 🎯
- 在 `/shared/registry/registry.json` 注册 workbuddy 节点
- 声明学习模块：炒股预测、网络协议、药物发现
- 设置角色为 student (综合学习型)

### 2. 参与每日站会 📋
- 时间：每日 20:00
- 通过 CC 消息发送到 `.shared/messages/queue/zhugema/inbox/`
- 格式：【今日完成】+【明日计划】+【遇到的问题】
- 首次站会内容：
  - 今日完成：同步诸葛马反馈，完善 workbuddy 配置，建立学习方案
  - 明日计划：启动炒股预测 Phase1 训练，完成网络协议 ch1 学习
  - 遇到的问题：GitHub 推送失败需修复 SSH 密钥

### 3. MQTT 集成 🔗
- 安装 paho-mqtt 客户端库
- 连接 Mosquitto Broker (121.43.80.231:1883)
- 订阅主题：lobster/nodes/workbuddy/、lobster/broadcast
- 发布 workbuddy 节点上线消息

---

## 三、学习计划（本周内）

### 模块一：炒股预测（优先启动）
| 阶段 | 内容 | 题数 | 目标准确率 | 预计完成 |
|------|------|------|------------|----------|
| Phase 1 | 基础概念（K线、均线、成交量） | 20 | >85% | 07-11 |
| Phase 2 | 技术分析（MACD/RSI/KDJ） | 20 | >85% | 07-12 |
| Phase 3 | 实战预测（选股/仓位/风控） | 20 | >80% | 07-14 |
| Phase 4 | 综合测试 | 20 | >80% | 07-15 |
| 题库额外 | 扩展题库 40 题 | 40 | >80% | 07-17 |

- 引擎：`domains/learning/problems/stock-predict/stock_predict_engine.py`
- 训练器：`domains/learning/trainers/stock_predict_trainer.py`
- 每日 5 题，使用 `scripts/stock_predict_training.py --train workbuddy`

### 模块二：网络协议（同步推进）
| 阶段 | 内容 | 题数 | 预计完成 |
|------|------|------|----------|
| ch1 | 协议基础（OSI/TCP/IP） | 10 | 07-11 |
| ch2 | 传输层（TCP/UDP） | 10 | 07-12 |
| ch3 | 应用层（HTTP/DNS） | 10 | 07-13 |
| ch4 | 安全协议（TLS/SSH） | 10 | 07-14 |
| ch5 | 综合实战 | 10 | 07-15 |

- 引擎：`domains/learning/problems/network-protocol/network_protocol_engine.py`
- 每日 3 题

### 模块三：药物发现（知识贡献）
| 任务 | 内容 | 预计完成 |
|------|------|----------|
| 知识图谱扩充 | 向 knowledge_graph_v1.json 添加过敏原-靶点关系 | 07-11 |
| 化合物筛选 | 使用 build_screening_pipeline.py 扩充筛选管线 | 07-12 |
| 文献综述 | 编写过敏防治综述 docs/drug-discovery-allergy-review.md | 07-13 |

---

## 四、龙虾币目标

| 行为 | 单次奖励 | 日频 | 日收益 | 周收益 |
|------|----------|------|--------|--------|
| 精读（训练做题） | 50🦞 | 5次 | 250 | 1250 |
| 写作（学习笔记） | 30🦞 | 2次 | 60 | 300 |
| 站会 | 10🦞 | 1次 | 10 | 50 |
| 任务完成 | 20🦞 | 3次 | 60 | 300 |
| 5天连续训练 | 50🦞 | — | — | 50 |
| **合计** | | | **380/天** | **1950/周** |

---

## 五、配置完成清单

- [x] workbuddy 节点配置 (config/workbuddy/workbuddy_config.json)
- [x] 消息队列目录初始化
- [ ] 首次站会 CC 消息发送
- [ ] MQTT 客户端安装与集成
- [ ] 炒股预测 Phase1 启动
- [ ] 网络协议 ch1 启动
- [ ] 训练自动化定时创建
- [ ] 学习状态文件初始化
