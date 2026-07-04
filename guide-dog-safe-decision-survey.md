# 智能导盲犬：资源受限条件下的个性化可信安全决策与边缘部署 —— 文献调研

> 调研时间：2026-06-12
> 聚焦方向：边缘端实时安全决策 + 面向个体差异的安全策略校准

---

## 一、安全决策框架（可信安全导航）

### 1.1 控制障碍函数 CBF —— 形式化安全保障

**[1] "Force-Compliance MPC and Robot-User CBFs for Interactive Navigation and User-Robot Safety in Hexapod Guide Robots"** ⭐ 最直接相关
- 作者：Zehua Fan, Feng Gao, Zhijun Chen, Yunpeng Yin, Limin Yang
- 年份：2025
- 期刊：**IEEE Transactions on Automation Science and Engineering (TASE)**
- DOI：[10.1109/tase.2025.3596630](https://doi.org/10.1109/tase.2025.3596630)
- **核心贡献**：在六足导盲机器人上，结合**力顺应MPC**（Force-Compliance Model Predictive Control）与**机器人-用户CBF**（Control Barrier Functions），实现交互式导航与人-机安全保障。
- **可借鉴点**：CBF 提供形式化安全保证（Safety Invariant），MPC 处理力交互的顺应性，直接对应"资源受限条件下的安全干预"和"个体差异安全策略校准"——不同用户对牵引力的接受度不同，可通过CBF约束参数个性化调整。

**[2] "Lyapunov-based Control Barrier Functions for Real-Time Safe Navigation in Three-dimension Complex Environments"**
- 作者：Zhiwei Hou
- 年份：2025
- 期刊：**IEEE Robotics and Automation Letters (RA-L)**
- DOI：[10.1109/lra.2025.3634911](https://doi.org/10.1109/lra.2025.3634911)
- **核心贡献**：Lyapunov-CBF结合，在3D复杂环境中实现实时安全导航。
- **可借鉴点**：CBF的实时计算效率适合边缘部署，Lyapunov提供稳定性保证。

**[3] "Corridor-based Adaptive Control Barrier & Lyapunov Functions for Safe Mobile Robot Navigation"**
- 作者：Nicholas Mohammad, Nicola Bezzo
- 年份：2026
- 会议：**IEEE CDC 2025**（控制领域顶级会议）
- DOI：[10.1109/cdc57313.2025.11312266](https://doi.org/10.1109/cdc57313.2025.11312266)
- **核心贡献**：自适应CBF，走廊约束下的安全导航。
- **可借鉴点**：自适应CBF可根据环境复杂度动态调整安全边界——对应"个体差异安全策略校准"。

### 1.2 安全约束强化学习

**[4] "Trust-SAC: Trust Guided Reinforcement Learning for Safe Robot Navigation with Dynamic Window Approach"** ⭐ 核心参考
- 作者：Yuhan Wang, Haonan Li, Hu Luo, Gebel Elena Sergeevna
- 年份：2026
- DOI：[10.21203/rs.3.rs-9283070/v1](https://doi.org/10.21203/rs.3.rs-9283070/v1)
- **核心贡献**：提出 Trust-SAC 框架，让RL智能体动态评估自身动作的可靠性，与经典DWA（Dynamic Window Approach）专家策略比较，输出控制动作(v, ω)的同时输出信任权重 τ。
- **关键机制**：
  - 策略学习输出 **trust weight τ**，调制基于critic的信任奖励
  - 自适应平衡**探索、效率与安全**，基于实时环境风险
  - 在4种Gazebo环境中，成功率高于SAC、PPO和DWA
- **可借鉴点**：**"可信"决策的核心机制**——不盲目信任端到端RL，而是让智能体自己评估何时信赖经典安全策略（DWA）。这完美对应"资源受限条件下的个性化可信安全决策"：τ 可按用户个性化校准（保守型用户τ偏DWA，激进型用户τ偏RL）。

**[5] "SafeNav: A Safety-Constrained Reinforcement Learning Framework for Autonomous Mobile Robot Navigation"** ⭐ 核心参考
- 作者：Thomas Müller
- 年份：2026
- DOI：[10.21203/rs.3.rs-9441537/v1](https://doi.org/10.21203/rs.3.rs-9441537/v1)
- **核心贡献**：分层框架，碰撞感知A*规划器 + PPO速度控制器 + **CBF-inspired在线安全滤波器**。
- **关键指标**：
  - 1800次仿真试验，20%障碍密度下成功率 **95.8%**
  - 安全违规率仅 **0.48%**
  - 路径长度比最优基线减少 **31.4%**
- **安全机制**：
  - 实时障碍物膨胀更新（处理动态障碍）
  - 安全引导的熵调度（训练阶段）
  - Lagrangian约束（训练阶段可证明限制安全违规率）
- **可借鉴点**：分层架构适合边缘部署（规划器和控制器可分离计算），在线安全滤波器是轻量级的实时安全干预模块。

**[6] "Safe Robot Navigation Using Constrained Hierarchical Reinforcement Learning"**
- 作者：Felippe Schmoeller Roza, Hassan Rasheed, Karsten Roscher
- 年份：2023
- 会议：IEEE ICMLA 2022
- DOI：[10.1109/icmla55696.2022.00123](https://doi.org/10.1109/icmla55696.2022.00123)
- **核心贡献**：约束分层强化学习用于安全机器人导航。

### 1.3 混合安全策略

**[7] "SARAD: LLM-Based Safety-Aware Hybrid Reinforcement Learning with Collision Prediction for Autonomous Driving"**
- 作者：Kangyu Wu, Guoxi Chen, Ya Zhang
- 年份：2025
- DOI：[10.2139/ssrn.5599504](https://doi.org/10.2139/ssrn.5599504)
- **核心贡献**：LLM辅助的安全感知混合RL + 碰撞预测，用于自动驾驶。
- **可借鉴点**：碰撞预测模块可迁移到导盲犬场景，LLM可作为离线策略生成器（不部署在边缘端）。

---

## 二、个性化用户适配与安全策略校准

### 2.1 用户自适应导航

**[8] "USER-ADAPTIVE NAVIGATION FOR ELDERLY PEDESTRIANS BASED ON PREFERENCE INFORMATION"**
- 年份：2023
- 会议：E-Society / Mobile Learning 2023
- DOI：[10.33965/es_ml2023_202302l004](https://doi.org/10.33965/es_ml2023_202302l004)
- **核心贡献**：基于老年人偏好信息的用户自适应导航，使用路线评价和步行历史。
- **可借鉴点**：通过用户反馈（路线评价）和历史数据（步行习惯）自适应调整导航策略——直接对应"面向个体差异的安全导盲策略校准"。

**[9] "A STUDY ON USER-ADAPTIVE NAVIGATION INCORPORATING PREFERENCE OF ELDERLY PEDESTRIANS"**
- 年份：2023
- 期刊：IADIS International Journal on CSIS
- DOI：[10.33965/ijcsis_2023180106](https://doi.org/10.33965/ijcsis_2023180106)
- **核心贡献**：使用路线评价和步行历史数据的老年人偏好自适应导航。

**[10] "Towards a User Adaptive Assistive Robot: Learning from Demonstration Using Navigation Functions"**
- 作者：Xanthi S. Papageorgiou, Athanasios C. Dometios, Costas S. Tzafestas
- 年份：2021
- 会议：**IEEE/RSJ IROS 2021**（机器人顶级会议）
- DOI：[10.1109/iros51168.2021.9636200](https://doi.org/10.1109/iros51168.2021.9636200)
- **核心贡献**：通过示教学习（Learning from Demonstration）实现用户自适应辅助机器人导航。
- **可借鉴点**：用户演示 → 学习个性化导航策略，对应"安全策略校准方法"。

**[11] "Learning Personalized Human-Aware Robot Navigation Using Virtual Reality Demonstrations from a User Study"**
- 作者：Jorge de Heuvel, Nathan Corral, Lilli Bruckschen, Maren Bennewitz
- 年份：2022
- 会议：**IEEE RO-MAN 2022**（人机交互顶级会议）
- DOI：[10.1109/ro-man53752.2022.9900554](https://doi.org/10.1109/ro-man53752.2022.9900554)
- **核心贡献**：通过VR示教从用户研究学习个性化人机感知导航。
- **可借鉴点**：用户研究+示教学习，可迁移到导盲犬的个性化安全策略校准。

### 2.2 个性化偏好学习

**[12] "Meta Preference Learning for Fast User Adaptation in Human-Supervisory Multi-Robot Deployments"**
- 作者：Chao Huang, Wenhao Luo, Rui Liu
- 年份：2021
- 会议：**IEEE/RSJ IROS 2021**
- DOI：[10.1109/iros51168.2021.9636515](https://doi.org/10.1109/iros51168.2021.9636515)
- **核心贡献**：元偏好学习（Meta Preference Learning），快速适配新用户。
- **可借鉴点**：元学习框架可在少量交互后快速适配新用户的偏好/安全阈值——对应"冷启动"个性化安全策略校准。

**[13] "UHTP: A User-Aware Hierarchical Task Planning Framework for Communication-Free, Mutually-Adaptive Human-Robot Collaboration"**
- 作者：Kartik Ramachandruni, Cassandra Kent, Sonia Chernova
- 年份：2023
- 期刊：**ACM Transactions on Human-Robot Interaction**
- DOI：[10.1145/3623387](https://doi.org/10.1145/3623387)
- **核心贡献**：用户感知的分层任务规划框架，无需通信的双向自适应人机协作。
- **可借鉴点**：无需显式通信即可自适应——对导盲犬场景（视障用户无法视觉交互）特别重要。

---

## 三、边缘端实时部署

### 3.1 边缘量化与模型压缩

**[14] "Edge-Optimized Real-Time Object Detection in AIoT Systems Using Quantized YOLOv8 and Deep SORT"**
- 作者：Chaoran Li
- 年份：2026
- 期刊：Informatica
- DOI：[10.31449/inf.v50i7.10210](https://doi.org/10.31449/inf.v50i7.10210)
- **可借鉴点**：INT8量化+Deep SORT，边缘设备低延迟多目标识别。

**[15] "A Lightweight Neural Network Compression Pipeline for Resource-Constrained Edge AI Systems"**
- 作者：Som Subhro Nath
- 年份：2026
- DOI：[10.21203/rs.3.rs-9295528/v1](https://doi.org/10.21203/rs.3.rs-9295528/v1)
- **可借鉴点**：完整的轻量级压缩pipeline（剪枝+量化+知识蒸馏），边缘部署一站式方案。

### 3.2 边缘端强化学习部署

**[16] "Optimizing Reinforcement Learning-Based Visual Navigation for Resource-Constrained Devices"**
- 作者：U. Vijetha, V. Geetha
- 年份：2023
- 期刊：**IEEE Access**
- DOI：[10.1109/access.2023.3323801](https://doi.org/10.1109/access.2023.3323801)
- **核心贡献**：针对资源受限设备优化基于RL的视觉导航。
- **可借鉴点**：直接解决"资源受限条件下RL导航部署"问题。

**[17] "Energy-Efficient On-Device Reinforcement Learning for Adaptive Multi-Sensor Scheduling in Resource-Constrained Edge Systems"**
- 作者：Oussama EL ALLAM, Mohamed Hamlich
- 年份：2025
- DOI：[10.2139/ssrn.5648910](https://doi.org/10.2139/ssrn.5648910)
- **核心贡献**：资源受限边缘系统上的设备端RL，用于自适应多传感器调度。
- **可借鉴点**：在资源受限条件下用RL做传感器调度决策——导盲犬的多传感器（相机+雷达+IMU）可按用户需求和场景动态调度。

### 3.3 边缘硬件平台部署实践

**[18] "Edge Computing-based Real-Time Surveillance System with YOLOv8 using NVIDIA Jetson Nano"**
- 作者：Vedant Ghodmare 等
- 年份：2025
- 会议：ICPCSN 2025
- DOI：[10.1109/icpcsn65854.2025.11034845](https://doi.org/10.1109/icpcsn65854.2025.11034845)

**[19] "An Optimized GhostNet-YOLOv8 Architecture for Real-Time Object Detection in Edge AIoT Surveillance Applications"**
- 作者：Monish Sai Krishna Namana, Budidi Udaya Kumar
- 年份：2026
- 会议：ICIIP 2025
- DOI：[10.1109/iciip68302.2025.11346418](https://doi.org/10.1109/iciip68302.2025.11346418)

---

## 四、导盲犬机器人安全策略与交互

### 4.1 导盲犬系统级安全

**[20] "System Configuration and Navigation of a Guide Dog Robot: Toward Animal Guide Dog-Level Guiding Work"**
- 作者：Hochul Hwang, Tim Xia, Ibrahima Keita, Ken Suzuki, Joydeep Biswas
- 年份：2023
- 会议：**IEEE ICRA 2023** ⭐ 顶会
- DOI：[10.1109/icra48891.2023.10160573](https://doi.org/10.1109/icra48891.2023.10160573)
- **核心贡献**：系统性导盲机器人配置与导航，以真实导盲犬水平为目标。
- **可借鉴点**：系统级安全策略设计，包括避障、路径规划、用户交互安全。

**[21] "Low-cost guide dog robot navigation using Dueling DQN"**
- 作者：Feiran Fang
- 年份：2024
- 期刊：Applied and Computational Engineering
- DOI：[10.54254/2755-2721/95/20241751](https://doi.org/10.54254/2755-2721/95/20241751)
- **核心贡献**：低成本导盲机器人导航，Dueling DQN强化学习。
- **关键洞察**：现有导航方法只关注机器人轨迹，忽视了人的运动，导致用户-机器人路径冲突。提出同时考虑两者的导航方法。
- **可借鉴点**：**低成本=资源受限场景的直接对标**。Dueling DQN分离value和advantage，更适合边缘部署。

### 4.2 人机交互与牵引安全

**[22] "Towards Robotic Companions: Understanding Handler-Guide Dog Interactions for Informed Guide Dog Robot Design"**
- 作者：Hochul Hwang, Hee-Tae Jung, Nicholas A. Giudice
- 年份：2024
- 会议：**ACM CHI 2024** ⭐ 顶会
- DOI：[10.1145/3613904.3642181](https://doi.org/10.1145/3613904.3642181)
- **核心贡献**：从真实导盲犬- handler交互中提取设计原则。
- **可借鉴点**：真实导盲犬如何根据handler个体差异调整引导策略（速度、距离、牵引力）——这是"个体差异安全策略校准"的实证基础。

**[23] "Tethering a Human with a Quadruped Robot: A Guide Dog to Help Visually Impaired People"**
- 作者：Viviana Morlando, Vincenzo Lippiello, Fabio Ruggiero
- 年份：2023
- 会议：MED 2023
- DOI：[10.1109/med59994.2023.10185715](https://doi.org/10.1109/med59994.2023.10185715)
- **核心贡献**：四足机器人与视障人士牵引交互机制。
- **可借鉴点**：牵引力的安全阈值设定，不同用户对牵引力的感知差异。

**[24] "A remote guidance system for blind and visually impaired people via vibrotactile haptic feedback"**
- 作者：S. Scheggi, A. Talarico, D. Prattichizzo
- 年份：2014
- 会议：MED 2014
- DOI：[10.1109/med.2014.6961320](https://doi.org/10.1109/med.2014.6961320)
- **可借鉴点**：触觉反馈作为安全交互通道——不同用户对触觉刺激的敏感度不同，需个性化校准。

---

## 五、技术路线总结与可借鉴方案

### 5.1 "可信安全决策"技术路线

```
┌─────────────────────────────────────────────────────┐
│                 可信安全决策架构                        │
├─────────────────────────────────────────────────────┤
│  感知层 (轻量化)                                       │
│  GhostNet-YOLOv8 / INT8量化 / Deep SORT跟踪            │
│  [14][15][19]                                        │
├─────────────────────────────────────────────────────┤
│  决策层 (分层安全)                                     │
│  上层：A*/PPO路径规划 (SafeNav架构 [5])                 │
│  下层：Trust-SAC动作选择+信任权重τ [4]                   │
│  安全层：CBF在线安全滤波器 [1][2][3][5]                  │
├─────────────────────────────────────────────────────┤
│  个性化层 (用户适配)                                    │
│  CBF约束参数个性化 / τ偏好校准 / 示教学习 [1][4][8][10] │
│  元学习快速适配新用户 [12]                              │
├─────────────────────────────────────────────────────┤
│  部署层 (边缘实时)                                     │
│  Jetson Nano / 模型压缩 / 传感器自适应调度               │
│  [16][17][18]                                        │
└─────────────────────────────────────────────────────┘
```

### 5.2 关键技术映射

| 你的需求 | 最相关论文 | 关键技术 |
|---------|-----------|---------|
| 可信安全决策 | [4] Trust-SAC (2026) | RL+DWA信任权重动态调制 |
| 形式化安全保障 | [1] CBF+MPC (2025 TASE) | CBF安全不变量+力顺应MPC |
| 分层安全架构 | [5] SafeNav (2026) | CBF在线滤波器+Lagrangian约束PPO |
| 个体差异安全校准 | [8][9] 用户自适应导航(2023) | 偏好学习+历史数据适配 |
| 快速用户适配 | [12] 元偏好学习(2021 IROS) | Meta-Learning冷启动适配 |
| 示教个性化 | [10] IROS 2021 | Learning from Demonstration |
| 边缘RL部署 | [16] IEEE Access 2023 | 资源受限RL视觉导航优化 |
| 传感器调度 | [17] SSRN 2025 | 设备端RL多传感器自适应调度 |
| 低成本导盲 | [21] Fang 2024 | Dueling DQN低成本导航 |
| 真实导盲参考 | [22] CHI 2024 | 人-导盲犬交互实证设计原则 |

### 5.3 建议重点阅读（按优先级）

1. **[1] Fan & Gao (2025) TASE** — 六足导盲机器人CBF+MPC，最直接对标
2. **[4] Wang et al. (2026) Trust-SAC** — "可信"决策的核心机制，τ可调=个性化
3. **[5] Müller (2026) SafeNav** — 分层安全架构+CBF滤波器，工程可实现
4. **[12] Huang et al. (2021) IROS** — 元偏好学习，解决新用户快速适配
5. **[22] Hwang et al. (2024) CHI** — 真实导盲犬个体差异实证，论文motivation支撑
6. **[1] Hou (2025) RA-L** — Lyapunov-CBF实时安全导航，边缘部署参考
7. **[17] El Allam (2025)** — 设备端RL传感器调度，资源受限决策参考
