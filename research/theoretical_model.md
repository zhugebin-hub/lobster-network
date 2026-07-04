# 理论模型：算力时间调度的形式化框架

**创建时间**：2026-03-28  
**版本**：v1.0

---

## 一、符号约定

### 1.1 基本符号

| 符号 | 含义 | 单位 |
|------|------|------|
| $t$ | 时间 | 秒 |
| $\mathcal{T}$ | 时间范围 $[0, T]$ | 秒 |
| $\mathcal{R}$ | 资源集合 | - |
| $\mathcal{J}$ | 任务集合 | - |
| $r_i$ | 第 $i$ 个资源 | - |
| $j_k$ | 第 $k$ 个任务 | - |

### 1.2 资源类型

$$\mathcal{R} = \mathcal{R}_{\text{CPU}} \cup \mathcal{R}_{\text{GPU}} \cup \mathcal{R}_{\text{NPU}} \cup \mathcal{R}_{\text{MEM}}$$

---

## 二、资源模型

### 2.1 资源定义

每个资源 $r_i \in \mathcal{R}$ 由以下属性描述：

$$r_i = (\text{type}_i, C_i, p_i(t), w_i, \eta_i)$$

其中：
- $\text{type}_i \in \{\text{CPU}, \text{GPU}, \text{NPU}, \text{MEM}\}$：资源类型
- $C_i$：总容量（cores/GPU 卡/GB）
- $p_i(t)$：时间变化的单位成本（元/秒）
- $w_i$：预热时间（秒）
- $\eta_i$：能源效率系数（用于绿色调度扩展）

### 2.2 资源状态

资源在时刻 $t$ 的状态：

$$s_i(t) = (u_i(t), h_i(t), q_i(t))$$

其中：
- $u_i(t) \in [0, 1]$：利用率
- $h_i(t) \in \{\text{cold}, \text{warm}, \text{hot}\}$：热状态
- $q_i(t)$：排队任务数

### 2.3 异构转换效率矩阵

不同资源类型间的任务迁移存在效率损耗：

$$E = \begin{bmatrix}
1 & \eta_{\text{CPU}\to\text{GPU}} & \eta_{\text{CPU}\to\text{NPU}} \\
\eta_{\text{GPU}\to\text{CPU}} & 1 & \eta_{\text{GPU}\to\text{NPU}} \\
\eta_{\text{NPU}\to\text{CPU}} & \eta_{\text{NPU}\to\text{GPU}} & 1
\end{bmatrix}$$

其中 $\eta_{a\to b} \in (0, 1]$ 表示从资源类型 $a$ 迁移到 $b$ 的效率。

**典型值**（基于经验测量）：
- $\eta_{\text{CPU}\to\text{GPU}} \approx 0.7$（GPU 加速比）
- $\eta_{\text{GPU}\to\text{NPU}} \approx 0.85$（NPU 专用优化）
- $\eta_{\text{CPU}\to\text{NPU}} \approx 0.6$

---

## 三、任务模型

### 3.1 任务定义

每个任务 $j_k \in \mathcal{J}$ 由以下属性描述：

$$j_k = (a_k, \mathbf{d}_k, \tau_k, dl_k, \delta_k, \pi_k)$$

其中：
- $a_k$：到达时间
- $\mathbf{d}_k = (d_{k,i})_{i \in \mathcal{R}}$：资源需求向量
- $\tau_k$：估计执行时长
- $dl_k$：截止时间（可选，$\infty$ 表示无截止）
- $\delta_k \in [0, 1]$：可延迟度（1=完全可延迟，0=不可延迟）
- $\pi_k \in \{\text{LOW}, \text{MEDIUM}, \text{HIGH}, \text{CRITICAL}\}$：优先级

### 3.2 任务类型分类

$$\mathcal{J} = \mathcal{J}_{\text{realtime}} \cup \mathcal{J}_{\text{inference}} \cup \mathcal{J}_{\text{training}} \cup \mathcal{J}_{\text{batch}}$$

| 类型 | $\delta_k$ | $dl_k$ | 典型 $\pi_k$ |
|------|-----------|--------|-------------|
| Realtime | 0 | 5s | CRITICAL |
| Inference | 0.3 | 30s | HIGH |
| Training | 0.7 | 1h | MEDIUM |
| Batch | 1.0 | 2h | LOW |

### 3.3 任务生命周期

$$\text{Lifecycle}_k = (a_k, s_k, e_k)$$

其中：
- $a_k$：到达时间
- $s_k$：开始执行时间（$s_k \geq a_k$）
- $e_k$：完成时间（$e_k = s_k + \text{actual\_duration}_k$）

**等待时间**：$W_k = s_k - a_k$

**响应时间**：$R_k = e_k - a_k = W_k + \text{actual\_duration}_k$

---

## 四、调度决策模型

### 4.1 调度策略

调度策略 $\sigma$ 是一个映射：

$$\sigma: (\mathcal{J}, \mathcal{R}, t) \to \mathcal{A}$$

其中动作空间 $\mathcal{A}$ 包括：
- $\text{ALLOCATE}(j_k, r_i)$：分配任务 $j_k$ 到资源 $r_i$
- $\text{DELAY}(j_k, \Delta t)$：延迟任务 $j_k$ 执行 $\Delta t$ 时间
- $\text{MIGRATE}(j_k, r_i, r_{i'})$：迁移任务 $j_k$ 从 $r_i$ 到 $r_{i'}$
- $\text{PREEMPT}(j_k)$：抢占任务 $j_k$
- $\text{WARMUP}(r_i)$：预热资源 $r_i$

### 4.2 时间分层决策

$$\sigma = (\sigma_0, \sigma_1, \sigma_2, \sigma_3, \sigma_4)$$

| 层级 | 时间尺度 | 决策类型 | 频率 |
|------|---------|---------|------|
| $\sigma_0$ | 毫秒 | 请求路由 | 每请求 |
| $\sigma_1$ | 秒 | 热备管理 | 1-10 Hz |
| $\sigma_2$ | 分钟 | 批处理队列 | 0.1-1 Hz |
| $\sigma_3$ | 小时 | 跨域迁移 | 1/小时 |
| $\sigma_4$ | 天 | 容量规划 | 1/天 |

---

## 五、成本模型

### 5.1 总成本分解

$$C_{\text{total}} = C_{\text{resource}} + C_{\text{migration}} + C_{\text{delay}} + C_{\text{violation}}$$

### 5.2 资源成本

$$C_{\text{resource}} = \sum_{k \in \mathcal{J}} \sum_{i \in \mathcal{R}} \int_{s_k}^{e_k} p_i(t) \cdot d_{k,i} \, dt$$

**离散化近似**：

$$C_{\text{resource}} \approx \sum_{k \in \mathcal{J}} \sum_{i \in \mathcal{R}} p_i(t_k^*) \cdot d_{k,i} \cdot (e_k - s_k)$$

其中 $t_k^*$ 是任务执行期间的代表性时间点。

### 5.3 迁移成本

$$C_{\text{migration}} = \sum_{(k, i, i') \in \mathcal{M}} \left( \alpha \cdot \text{data}_{k,i\to i'} + \beta \cdot \text{context}_{k} \right)$$

其中：
- $\mathcal{M}$：迁移事件集合
- $\text{data}_{k,i\to i'}$：需要迁移的数据量
- $\text{context}_{k}$：上下文切换开销
- $\alpha, \beta$：成本系数

**典型值**：
- $\alpha \approx 0.01$ 元/GB（网络传输成本）
- $\beta \approx 0.1$ 元/次（GPU 上下文切换）

### 5.4 延迟成本

$$C_{\text{delay}} = \sum_{k \in \mathcal{J}} \gamma_k \cdot \max(0, s_k - a_k)$$

其中 $\gamma_k$ 是任务 $k$ 的单位时间延迟成本。

**与优先级的关系**：
$$\gamma_k = \gamma_0 \cdot 2^{\pi_k - 1}$$

其中 $\pi_k \in \{1, 2, 3, 4\}$ 对应 LOW/MEDIUM/HIGH/CRITICAL。

### 5.5 SLA 违约成本

$$C_{\text{violation}} = \sum_{k \in \mathcal{J}} \mathbb{I}(e_k > dl_k) \cdot \rho_k$$

其中 $\rho_k$ 是任务 $k$ 的违约惩罚。

**典型值**：
- Realtime 任务：$\rho_k = 100$ 元/次
- Inference 任务：$\rho_k = 10$ 元/次
- Training/Batch 任务：$\rho_k = 1$ 元/次

---

## 六、优化问题

### 6.1 目标函数

$$\min_{\sigma} \mathbb{E}[C_{\text{total}}]$$

即最小化期望总成本。

### 6.2 约束条件

**资源容量约束**：
$$\sum_{k: s_k \leq t < e_k} d_{k,i} \leq C_i, \quad \forall i \in \mathcal{R}, \forall t \in \mathcal{T}$$

**截止时间约束**（硬约束）：
$$e_k \leq dl_k, \quad \forall k \in \mathcal{J}_{\text{realtime}}$$

**截止时间约束**（软约束，纳入成本）：
$$\mathbb{I}(e_k > dl_k) \text{ 计入 } C_{\text{violation}}, \quad \forall k \in \mathcal{J} \setminus \mathcal{J}_{\text{realtime}}$$

**可延迟度约束**：
$$s_k - a_k \leq (1 - \delta_k) \cdot \Delta_{\max}, \quad \forall k \in \mathcal{J}$$

其中 $\Delta_{\max}$ 是最大允许延迟。

### 6.3 问题复杂度

**定理 1**：上述优化问题是 NP-hard。

**证明思路**：可归约到经典的 Job Shop Scheduling Problem (JSSP)，后者是强 NP-hard。

**推论**：需要启发式或近似算法求解。

---

## 七、时间套利理论

### 7.1 套利机会定义

**定义 1**（时间套利机会）：存在时刻 $t_1, t_2$ 和任务 $j_k$，满足：

$$p_i(t_1) > p_i(t_2) \cdot (1 + \epsilon)$$

且任务 $j_k$ 可延迟：$\delta_k > 0$，$dl_k - a_k > t_2 - t_1$。

### 7.2 套利收益

**命题 1**：延迟任务 $j_k$ 从 $t_1$ 到 $t_2$ 执行的净收益为：

$$\text{Gain}_k = \underbrace{(p_i(t_1) - p_i(t_2)) \cdot d_{k,i} \cdot \tau_k}_{\text{资源成本节省}} - \underbrace{\gamma_k \cdot (t_2 - t_1)}_{\text{延迟成本}}$$

**套利条件**：$\text{Gain}_k > 0$

### 7.3 最优延迟时间

**命题 2**：对于可延迟任务 $j_k$，最优延迟时间 $\Delta t^*$ 满足：

$$\Delta t^* = \arg\max_{\Delta t \in [0, dl_k - a_k]} \left[ (p_i(t) - p_i(t + \Delta t)) \cdot d_{k,i} \cdot \tau_k - \gamma_k \cdot \Delta t \right]$$

### 7.4 价格预测误差的影响

**命题 3**：若价格预测存在误差 $\hat{p}(t) = p(t) + \epsilon(t)$，则期望收益损失为：

$$\mathbb{E}[\text{Loss}] \approx \frac{1}{2} \cdot \text{Var}(\epsilon) \cdot \frac{\partial^2 \text{Gain}}{\partial p^2}$$

**启示**：价格预测的方差直接影响套利效果，需要高精度预测。

---

## 八、强化学习公式化

### 8.1 MDP 定义

将调度问题建模为马尔可夫决策过程 $(\mathcal{S}, \mathcal{A}, P, R, \gamma)$：

**状态空间** $\mathcal{S}$：
$$s_t = (\mathbf{u}_t, \mathbf{q}_t, \mathbf{p}_t, \mathbf{l}_t, \text{time}_t)$$

其中：
- $\mathbf{u}_t$：资源利用率向量
- $\mathbf{q}_t$：各队列长度
- $\mathbf{p}_t$：当前价格向量
- $\mathbf{l}_t$：负载预测特征
- $\text{time}_t$：时间特征（小时、星期）

**动作空间** $\mathcal{A}$：离散动作集合（见 4.1 节）

**转移概率** $P$：由负载到达和服务时间分布决定

**奖励函数** $R$：
$$r(s, a, s') = -\Delta C_{\text{total}} - \lambda_1 \cdot \text{SLA\_violation} - \lambda_2 \cdot \text{migration}$$

**折扣因子** $\gamma = 0.99$

### 8.2 策略梯度

使用 PPO 算法，策略梯度为：

$$\nabla_\theta J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta} \left[ \sum_{t=0}^T \nabla_\theta \log \pi_\theta(a_t | s_t) \cdot A^\pi(s_t, a_t) \right]$$

其中优势函数 $A^\pi(s, a) = Q^\pi(s, a) - V^\pi(s)$。

---

## 九、理论边界

### 9.1 竞争分析

**定理 2**（竞争比下界）：对于在线调度问题，任何确定性算法的竞争比至少为 $\Omega(\log n)$，其中 $n$ 是任务数。

### 9.2 近似保证

**定理 3**：若负载预测误差有界 $|\hat{l}_t - l_t| \leq \epsilon$，则时间套利算法的近似比为：

$$\frac{C_{\text{ours}}}{C_{\text{optimal}}} \leq 1 + O(\epsilon)$$

---

## 十、模型扩展

### 10.1 多租户公平性

引入公平性约束：

$$\text{Jain's Index} = \frac{(\sum_k u_k)^2}{n \cdot \sum_k u_k^2} \geq \theta$$

其中 $\theta \in (0, 1)$ 是公平性阈值。

### 10.2 碳感知调度

将能源效率纳入目标：

$$C_{\text{total}}' = C_{\text{total}} + \lambda_{\text{carbon}} \cdot \sum_{k, i} \text{carbon}_i(t) \cdot d_{k,i} \cdot \tau_k$$

其中 $\text{carbon}_i(t)$ 是时刻 $t$ 资源 $i$ 的碳强度。

### 10.3 边缘 - 云协同

扩展模型支持边缘资源：

$$\mathcal{R} = \mathcal{R}_{\text{edge}} \cup \mathcal{R}_{\text{cloud}}$$

考虑网络延迟约束：

$$\text{latency}_{k, \text{edge}} \leq L_{\max}, \quad \forall k \in \mathcal{J}_{\text{latency-sensitive}}$$

---

## 十一、待验证假设

| 假设编号 | 假设内容 | 验证方法 |
|---------|---------|---------|
| H1 | 负载存在显著的日周期模式 | 时间序列分析 |
| H2 | 价格波动幅度 > 2× | 历史价格统计 |
| H3 | 30%+ 任务可延迟 | 任务类型分布分析 |
| H4 | 预测误差 < 20% | 预测模型评估 |
| H5 | 迁移开销 < 节省的 50% | 迁移实验测量 |

---

*理论模型版本：v1.0*  
*下一步：通过实验验证假设 H1-H5*
