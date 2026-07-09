# 协作协议 — 食物过敏药物研制项目

## 1. 通信协议
本项目使用 OADP-Science v1.0 协议进行智能体间通信。

### 消息类型
- SCIENCE_HELLO: 节点注册，携带能力列表和领域标签
- SCIENCE_TASK: 任务分发，包含任务类型、输入数据、质量要求
- SCIENCE_RESULT: 结果上报，包含输出数据、置信度、验证状态
- SCIENCE_REVIEW: 同行评审，包含评审意见、修改建议、质量评分
- SCIENCE_HEARTBEAT: 心跳消息，包含负载状态和任务进度

### 消息格式
所有消息使用JSON格式，通过.shared/messages/queue/{node_id}/inbox/传递。

## 2. 节点分工

| 节点 | 角色 | 负责方向 | 智能体 |
|------|------|----------|--------|
| qoder | 主攻研究员 | 化合物设计+虚拟筛选 | compound-design-agent, virtual-screening-agent |
| xiaochen | 研究员 | 靶点发现+文献挖掘 | allergen-target-agent, literature-mining-agent |
| zhuguxia | 研究员 | ADMET预测+毒性评估 | admet-prediction-agent, toxicity-assessment-agent |
| hermes | 协调者 | 全局协调+质量把控 | - |
| zhugema | 路由 | 任务路由+进度监控 | - |

## 3. 数据共享规范

### 输入数据
- 知识库: domains/drug_discovery/knowledge_base/
- 文献: .shared/training/drug_discovery/literature/

### 输出数据
- 各节点结果: .shared/training/drug_discovery/from-{node_id}/
- 阶段报告: .shared/training/drug_discovery/reports/
- 最终成果: .shared/training/drug_discovery/final/

### 命名规范
- 文件: {stage}_{node}_{date}.{ext}
- 示例: target_discovery_xiaochen_20260709.json

## 4. 质量标准

### 任务完成标准
- 靶点发现: 每个靶点需提供druggability_score > 0.5
- 化合物设计: 需符合Lipinski五规则 (MW<500, LogP<5, HBD≤5, HBA≤10)
- 虚拟筛选: 需提供docking_score和enrichment_factor
- ADMET预测: 需提供完整5维预测结果
- 毒性评估: safety_grade需达到B以上

### 评审标准
- 准确性: 结果与已知数据的一致性
- 创新性: 方法或发现的新颖程度
- 完整性: 数据和文档的完整度
- 可重复性: 其他节点能否复现结果

## 5. 安全约束

### 三层安全护栏
- L1 输入护栏: 危险指令过滤 + 敏感信息脱敏
- L2 执行护栏: 操作白名单 + 资源配额
- L3 输出护栏: 内容审核 + 格式校验

### 差分隐私
- 处理敏感数据时启用，ε=1.0, δ=10⁻⁵

## 6. 进度管理

### 每日站会 (20:00)
格式:
1. 今日完成的任务
2. 遇到的问题
3. 明日计划

### 阶段评审
- Phase 1结束: 知识图谱评审 (hermes主持)
- Phase 2结束: 候选化合物评审 (全节点投票)
- Phase 3结束: 论文评审 (hermes + 外部评审)

## 7. 奖励机制
- 完成任务: 10-50 LBC (根据复杂度)
- 发现重要靶点: 100 LBC
- 论文贡献: 200 LBC
- 里程碑达成: 50 LBC/Phase
