# 更新日志

## [1.0.0-rc1] - 2026-06-26

### 重大新增：P0-P2 任务完成

#### 世界地图引擎完善
- 版本历史回溯功能（get_version_history、get_version_info）
- 版本历史保留最近 100 个版本
- 修复版本号递增 bug
- 23 个单元测试全部通过

#### 多节点联调环境
- MockNode 模拟节点（虾尔、诸葛马、小陈）
- 消息传递测试（单轮/多轮对话）
- 故障切换测试（心跳超时/恢复）
- 世界地图同步测试（chunk 共享、宝藏解锁）
- 并发节点操作测试
- 8 个联调测试全部通过

#### NFS 通道测试
- NFS 通道模拟类
- 消息发送/接收/持久化测试
- 多节点通信测试（虾尔↔诸葛马↔小陈）
- 并发发送测试（10 线程）
- 7 个 NFS 通道测试全部通过

#### 协议合规性测试
- 世界地图/chunk/treasure 结构验证
- 消息格式验证（dialogue_request、world_update、portal_record）
- 涌现计算公式验证
- 错误处理验证（重复 chunk、无效版本、权限控制）
- 14 个协议合规测试全部通过

#### 故障切换测试
- NFS → file 通道自动切换
- 所有通道失败处理（pending 队列）
- 待处理消息重试机制
- 多节点故障切换场景
- 7 个故障切换测试全部通过

#### 涌现计算详细说明
- 涌现计算公式详细说明（spec/emergence_calculation.md）
- 各变量计算方法（perspective_diff、knowledge_overlap、dialogue_depth、novelty_factor）
- 涌现等级定义（none/low/medium/high/very_high）
- 动态权重调整
- 涌现值平滑
- 12 个涌现计算测试全部通过

#### 版本升级
- OADP 协议升级到 v1.0.0-rc1
- 协议状态从草案升级为候选发布

### 测试统计
- 新增测试：55 个
- 全部通过：55/55 ✅
- 代码提交：3 次

---

## [0.4.1] - 2026-06-24

### 重大新增：注册中心 + 可靠消息 + 部署脚本

#### 节点注册中心（NodeRegistry）
- 节点注册/注销（含能力声明和传输通道配置）
- 心跳检测（定期心跳，自动检测节点存活）
- 健康检查（全量健康检查，自动标记 offline/suspected）
- 节点发现（按类型/状态/能力查找节点）
- 持久化（JSON 文件持久化，重启后自动恢复）
- 回调机制（心跳回调、状态变化回调）

#### 可靠消息传递（Messenger）
- 消息确认（ACK/NACK 机制）
- 自动重试（指数退避）
- 多通道故障切换（NFS → SSH → HTTP → File）
- 消息持久化（按状态分类存储）
- 消息过期（TTL 机制）
- 优先级队列

#### 集成层（integration.py）
- 统一API，整合注册中心和消息传递
- `LobsterNetworkWithRegistry` 类
- 简化节点注册和消息发送流程

#### 自动化部署
- 一键部署：`deploy_v0.4.1.sh deploy`
- 一键回滚：`deploy_v0.4.1.sh rollback`
- 健康检查：`deploy_v0.4.1.sh health`
- 测试验证：`deploy_v0.4.1.sh test`

#### 升级检查清单
- 60+ 检查项
- 覆盖所有模块和配置

### 测试
- **62个单元测试全部通过**
- 注册中心测试：37个
- 协议增强测试：25个

---

## [0.4.0] - 2026-06-24

### 重大更新：SSH通信 + 消息协议增强

#### 消息协议v2（message_protocol_v2.py）
- 消息重试（指数退避，默认3次）
- 消息确认（接收方确认机制）
- 消息去重（基于内容哈希）
- 消息持久化（JSON 文件存储）
- 消息过期（TTL 机制）
- 优先级（normal/high/critical）

#### SSH通道v2（ssh_channel_v2.py）
- 重试机制（指数退避）
- 超时控制
- 错误恢复
- 连接池
- 健康检查
- 原子写入（.tmp + rename）

#### 节点注册中心v2
- 持久化存储
- 心跳检测
- 健康检查
- 事件回调

#### 版本整合
- 诸葛马版 + 虾尔版整合
- 以诸葛马版为基础，合并虾尔版增强功能

---

## [0.6.0] - 2026-06-25

### 新增
- feat: Enhanced dialogue engine with semantic emergence computation (Jaccard similarity, n-gram analysis)
- feat: Learning coordinator closing assessment-training feedback loop
- feat: HTTP transport for real inter-node network communication
- feat: Adaptive training plans based on 8-dimension assessment results
- feat: Collaboration suggestions between complementary nodes

### 修复
- fix: Version alignment across setup.py, __init__.py, README

### 重构
- refactor: Cleaned up domains/assessment duplicate code

---

## [0.5.0] - 2026-06-24

### 新增
- feat: 8-dimension capability assessment engine (EightDimEngine)
- feat: Clawvard School API bridge (practice + exam modes)
- feat: Dimension profiles with per-domain weight mapping
- feat: Improvement advisor with targeted suggestions

### 修复
- fix: Python 3.9 staticmethod callable bug in scorer map

---

## [0.4.0] - 2026-06-23

### 新增
- feat: Production-grade node registry with TTL heartbeats and health checks
- feat: Reliable message delivery with multi-transport failover (NFS/SSH/HTTP/File)
- feat: Enhanced message protocol v2 (dedup, TTL, retry, persistence)
- feat: SSH channel v2 with retry/timeout/statistics
- feat: Integration layer combining registry + messenger + network
>>>>>>> da05930 (feat: v0.6.0 — 语义涌现引擎 + 学习协调器 + HTTP传输层)

---

## [0.3.0] - 2026-06-22

### 重大新增：时间套利模式 (Time Arbitrage Mode)

引入**五维时间套利引擎**，系统性利用网络中节点的时间差异：

1. **速率套利 (Speed Arbitrage)** —— 利用不同Agent的学习速度差，快速节点生成原始洞见，慢速节点深化验证
2. **错峰套利 (Off-Peak Arbitrage)** —— 利用非高峰时段（深夜00:00-06:00）的低成本算力执行高强度训练
3. **反思套利 (Reflection Arbitrage)** —— 基于艾宾浩斯遗忘曲线，在记忆保留率降至最佳点时触发复习（V4错题本每3天机制的理论升级）
4. **复利套利 (Compound Arbitrage)** —— 多轮对话的涌现呈指数增长：E_total = E_1 × (1+r)^(N-1)
5. **时距套利 (Temporal Distance Arbitrage)** —— 知识价值随时间呈倒U型曲线，48-72小时后达到峰值

### 新增文件
- `src/lobster_network/time_arbitrage.py` — 时间套利引擎核心模块
- `examples/time_arbitrage_demo.py` — 五维套利完整演示

### 架构改进
- 网络层和工具层移入 `src/lobster_network/` 包内，统一Python包结构
- `__init__.py` 统一导出套利层所有类
- 版本升级到 v0.3.0

---

## [0.2.0] - 2026-06-22

### 重大更新：项目融合
- **框架层**与**运营层**统一整合为单一项目
- 重新设计四层架构：框架层 → 运营层 → 应用层 → 基础设施层
- 统一 `__init__.py` 入口，导出所有核心类
- 更新 `setup.py` 支持分层安装（core/full/dev）

### 新增
- `src/lobster_network/` — 核心框架（节点、对话、涌现、世界状态）
- `src/network/` — 因陀罗网拓扑、SSH通道
- `src/utils/` — 配置、日志、消息协议
- `core/` — 运营系统（调度器、Agent、教练、工具）
- `domains/go/` — 围棋训练领域（3个学生训练器、题库）
- `domains/poster/` — 海报设计领域（PPT生成框架）
- `examples/indra_net_demo.py` — 因陀罗网演示
- 统一 README（中英双语，含架构图）

### 改进
- 版本升级到 v0.2.0
- 项目结构更清晰，按功能分层组织

---

## [0.1.0] - 2026-06-21

### 新增
- 核心引擎：节点模型、对话引擎、涌现检测、世界状态管理
- 主网络类：LobsterNetwork（因陀罗网拓扑）
- 示例代码：多Agent对话示例
- 测试代码：15个单元测试用例
- 理论文档：对话即创造文章、架构设计、合作方案
- 项目配置：README、LICENSE、CONTRIBUTING、setup.py

### 测试
- 所有15个测试用例通过
- 示例代码运行成功，涌现值0.90

### 已知问题
- 涌现值计算算法需要优化（当前固定为0.90）
- SSH通信通道尚未实现
- 因陀罗网拓扑实现尚未完成

---

**你不停对话，世界就不停扩展** 🦞⚡️
