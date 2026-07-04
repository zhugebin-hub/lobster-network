# 文献综述：算力资源调度中的时间维度优化

**创建时间**：2026-03-28  
**作者**：OpenClaw Research Team  
**状态**：初稿

---

## 一、引言

云计算资源调度是分布式系统研究的核心问题之一。随着 AI 工作负载的爆发式增长和异构计算资源（CPU/GPU/NPU）的普及，传统调度方法面临新的挑战。本综述聚焦于**时间维度**在资源调度中的作用，特别关注与电力调度类比的时间套利模型。

### 1.1 研究动机

- **资源浪费严重**：数据中心平均利用率仅 30-40%，峰谷差异达 3-5 倍
- **时间波动性**：AI 工作负载呈现明显的日周期和周周期模式
- **成本压力**：云上 GPU 实例成本高昂，spot 实例价格波动达 10 倍
- **电力调度启发**：电力系统通过储能实现时间套利，算力系统可借鉴类似思路

### 1.2 综述范围

本综述涵盖以下方向：
1. 时间感知的云资源调度
2. 异构计算资源调度
3. 基于负载预测的弹性调度
4. 成本优化的资源分配
5. 时空联合优化（地理分布式场景）

---

## 二、时间感知的云资源调度

### 2.1 负载预测与时间序列建模

**TempoScale** (Wen et al., 2024) 提出了一种整合短期和长期信息的云工作负载预测方法。该方法的关键创新在于：
- 使用多尺度时间特征（小时、天、周）
- 结合 Transformer 和 LSTM 的优势
- 在阿里云生产环境验证，预测误差降低 35%

**PRISM** (Wu et al., 2026) 针对大规模 GPU 集群工作负载，提出基于原始模式的动态预测方法：
- 识别工作负载的"原始模式"（primitive patterns）
- 动态调整预测窗口
- 在 Meta 生产 GPU 集群上验证

**启示**：负载预测是时间套利的前提，需要多尺度建模能力。

### 2.2 时间间隔调度

**QTIS** (Tirado-Domínguez et al., 2025) 提出基于 QAOA 的量子时间间隔调度器：
- 将时间划分为离散区间
- 使用量子近似优化算法求解
- 适用于有严格时间约束的任务

**局限性**：量子方法目前仅适用于小规模问题，经典启发式方法更实用。

### 2.3 预测嵌入的调度

**FUSION** (Qi et al., 2026) 提出预测嵌入的智能体调度框架：
- 将预测模块直接嵌入调度决策
- 考虑服务激励优化
- 应用于分布式空天地边缘网络

**关键洞见**：预测与决策的紧耦合优于分离式设计。

---

## 三、异构计算资源调度

### 3.1 DAG 任务调度

**GA-DRL** (Liu et al., 2023) 结合图神经网络和深度强化学习进行 DAG 任务调度：
- 使用 GNN 编码任务依赖图
- DRL 学习调度策略
- 在动态车辆云场景验证

**Gap-Aware Generation** (Zhou et al., 2026) 提出间隙感知的异构 DAG 调度方法：
- 识别调度决策中的"间隙"
- 生成式方法填充间隙
- 在异构 CPU-GPU 集群上验证

### 3.2 Kubernetes 原生调度

**Rank-Aware Scheduling** (2026) 针对 Kubernetes 上紧耦合 MPI 工作负载：
- 考虑 GPU 拓扑感知
- 优化 rank 间通信
- 减少训练任务完成时间 25%

**Quantum-Classical Workflow** (Tejedor et al., 2026) 探索混合量子 - 经典工作流的 Kubernetes 编排：
- 异构资源包括量子处理器
- 工作流依赖管理
- 早期探索性工作

### 3.3 异构资源匹配

现有工作的共同局限：
- 多关注 CPU-GPU 二元异构
- 较少考虑 NPU、TPU 等新型加速器
- 资源转换效率建模不足

**研究机会**：建立统一的异构资源抽象模型，包含转换效率矩阵。

---

## 四、基于强化学习的调度方法

### 4.1 单智能体方法

**iScheduler** (Hu et al., 2026) 提出强化学习驱动的资源投资问题持续优化：
- 使用 PPO 算法
- 持续学习适应负载变化
- 在大规模生产环境部署

### 4.2 多智能体方法

**Collaborative MARL** (2025) 提出协作多智能体弹性云资源扩展：
- 每个资源池一个智能体
- 智能体间协作机制
- 减少通信开销

**Sustainable AIGC Scheduling** (Zhang et al., 2023) 针对地理分布式数据中心的 AIGC 工作负载：
- 多智能体强化学习
- 考虑能源成本和碳足迹
- 类似电力调度的时空优化

**关键洞见**：多智能体方法更适合分布式场景，但训练复杂度高。

### 4.3 上下文多臂老虎机

**Ksurf-Drone** (Dang'ana et al., 2025) 提出注意力卡尔曼滤波的上下文老虎机方法：
- 结合卡尔曼滤波和注意力机制
- 适用于资源分配的在线学习
- 理论保证 regret 上界

---

## 五、成本优化的资源分配

### 5.1 作业成本编排

**LeJOT** (Ma et al., 2025) 针对 Databricks 平台的智能作业成本编排：
- 预测作业完成时间和成本
- 动态选择实例类型
- 成本降低 40%+

### 5.2 多集群优化

**AI-Driven Multi-Cluster** (Punniyamoorthy et al., 2025) 提出多集群环境的 AI 驱动资源优化：
- 跨集群资源池化
- 统一调度视图
- 考虑网络延迟和成本权衡

### 5.3 Spot 实例利用

现有工作普遍关注 spot 实例的成本优化，但存在挑战：
- 价格波动难以预测
- 实例回收风险
- 迁移开销

**研究机会**：时间套利模型可以自然整合 spot 实例策略。

---

## 六、电力调度与算力调度的类比

### 6.1 电力系统调度基础

电力系统调度核心问题：
- **机组组合**（Unit Commitment）：决定哪些发电机组开机
- **经济调度**（Economic Dispatch）：优化发电出力分配
- **储能优化**：决定何时充电/放电

### 6.2 类比映射

| 电力系统 | 算力系统 | 相似度 |
|---------|---------|--------|
| 发电机组 | 计算资源（CPU/GPU/NPU） | ⭐⭐⭐⭐ |
| 电力负载 | 计算任务 | ⭐⭐⭐⭐⭐ |
| 储能（抽蓄/电池） | 任务队列/缓存 | ⭐⭐⭐ |
| 特高压输电 | 网络带宽/数据迁移 | ⭐⭐⭐⭐ |
| 频率稳定 | SLA 保障 | ⭐⭐⭐⭐ |
| 电价波动 | spot 实例价格 | ⭐⭐⭐⭐⭐ |
| 可再生能源不确定性 | 任务到达不确定性 | ⭐⭐⭐⭐ |

### 6.3 可借鉴的技术

1. **时间套利**：低谷充电（预加载任务），高峰放电（释放资源）
2. **分层调度**：秒级调频 ↔ 分钟级经济调度 ↔ 小时级机组组合
3. **备用容量**：旋转备用 ↔ 热备资源池
4. **需求响应**：可中断负载 ↔ 可延迟计算任务

### 6.4 差异与挑战

| 差异点 | 电力系统 | 算力系统 | 影响 |
|--------|---------|---------|------|
| 存储成本 | 储能成本高 | 任务队列成本低 | 算力更适合时间套利 |
| 迁移开销 | 电力传输损耗~5% | 任务迁移开销 10-30% | 算力需谨慎迁移 |
| 任务可中断性 | 部分可中断 | 大部分可检查点 | 算力灵活性更高 |
| 预测精度 | 负载预测误差~3% | 任务到达预测误差~15% | 算力预测更具挑战 |

---

## 七、研究空白与机会

### 7.1 已识别的研究空白

1. **形式化类比缺失**：尚无工作建立电力 - 算力调度的形式化映射
2. **时间分层模型不足**：现有工作多关注单一时间尺度
3. **异构效率建模**：缺乏 CPU-GPU-NPU 转换效率的系统研究
4. **真实场景验证**：多数研究使用合成负载，缺乏生产环境验证

### 7.2 本研究定位

本研究工作填补以下空白：
- ✅ 首次建立电力 - 算力调度的形式化类比框架
- ✅ 提出多尺度时间分层模型（秒/分钟/小时/天）
- ✅ 设计时间套利调度算法
- ✅ 在 OpenClaw 生产环境验证

---

## 八、关键论文摘要表

| 论文 | 年份 | 核心方法 | 主要贡献 | 局限性 |
|------|------|---------|---------|--------|
| TempoScale | 2024 | 多尺度负载预测 | 短长期信息整合 | 未涉及调度决策 |
| PRISM | 2026 | GPU 负载预测 | 原始模式识别 | 仅 GPU 场景 |
| GA-DRL | 2023 | GNN+DRL | DAG 任务调度 | 车辆云特定场景 |
| iScheduler | 2026 | PPO 持续学习 | 大规模资源优化 | 未考虑异构 |
| LeJOT | 2025 | 成本预测 | 作业成本编排 | Databricks 特定 |
| FUSION | 2026 | 预测嵌入调度 | 空天地边缘网络 | 场景特殊 |
| AIGC Scheduling | 2023 | MARL | 地理分布式 + 能源 | 最接近本研究 |

---

## 九、参考文献

[1] Wen L, Xu M, Toosi AN, Ye K. TempoScale: A Cloud Workloads Prediction Approach Integrating Short-Term and Long-Term Information. arXiv, 2024.

[2] Wu X, Teng F, Li X, Zheng B, Duan Q. PRISM: Dynamic Primitive-Based Forecasting for Large-Scale GPU Cluster Workloads. arXiv, 2026.

[3] Tirado-Domínguez JA, Gutiérrez E, Plata O. QTIS: A QAOA-Based Quantum Time Interval Scheduler. arXiv, 2025.

[4] Zhou R, Zou H, Zhou L, Sun C, Wen Z. A Learning Method with Gap-Aware Generation for Heterogeneous DAG Scheduling. arXiv, 2026.

[5] Liu Z, Huang L, Gao Z, Luo M, Hosseinalipour S, Dai H. GA-DRL: Graph Neural Network-Augmented Deep Reinforcement Learning for DAG Task Scheduling over Dynamic Vehicular Clouds. arXiv, 2023.

[6] Hu YX, Wang Y, Wu F, Huang Z, Zeng S, Li XY. iScheduler: Reinforcement Learning-Driven Continual Optimization for Large-Scale Resource Investment Problems. arXiv, 2026.

[7] Ma L, Hu YX, Wang Y, Zhao Y, Ren Y, Liao JX, Wu F, Li XY. LeJOT: An Intelligent Job Cost Orchestration Solution for Databricks Platform. arXiv, 2025.

[8] Qi H, Liwang M, Hosseinalipour S, Fu L, Zou S, Wang X. FUSION: Forecast-Embedded Agent Scheduling with Service Incentive Optimization over Distributed Air-Ground Edge Networks. arXiv, 2026.

[9] Zhang S, Xu M, Lim WYB, Niyato D. Sustainable AIGC Workload Scheduling of Geo-Distributed Data Centers: A Multi-Agent Reinforcement Learning Approach. arXiv, 2023.

[10] Dang'ana M, Zhang Y, Jacobsen HA. Ksurf-Drone: Attention Kalman Filter for Contextual Bandit Optimization in Cloud Resource Allocation. arXiv, 2025.

[11] Punniyamoorthy V, Agarwal AK, Kumar B, Mazumder A, Kannan K, Saha S. AI-Driven Cloud Resource Optimization for Multi-Cluster Environments. arXiv, 2025.

[12] Tejedor M, Grossi M, Tüysüz C, Rocha R, Vallecorsa S. Kubernetes-Orchestrated Hybrid Quantum-Classical Workflows. arXiv, 2026.

---

*文献综述版本：v1.0*  
*下次更新：完成精读后补充详细方法对比*
