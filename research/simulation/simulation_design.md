# 算力调度仿真实验设计

## 一、仿真环境架构

### 1.1 整体架构
```
┌─────────────────────────────────────────────────────────┐
│                    仿真控制器                            │
│  - 负载生成器  - 调度器  - 评估器  - 可视化              │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│  负载跟踪器    │ │  资源池       │ │  成本计算器   │
│  (Load Trace) │ │  (Resources)  │ │  (Cost)       │
└───────────────┘ └───────────────┘ └───────────────┘
```

### 1.2 核心组件

#### 负载跟踪器 (Load Tracer)
- **输入**：历史 token 消耗日志、API 调用记录
- **功能**：
  - 重放历史负载模式
  - 生成合成负载（基于统计分布）
  - 支持突发负载注入
- **输出**：时间序列负载数据 (timestamp, task_type, resource_demand, priority)

#### 资源池 (Resource Pool)
- **资源类型**：
  ```python
  RESOURCES = {
      "cpu": {"capacity": 100, "unit": "cores", "cost_per_hour": 0.05},
      "gpu": {"capacity": 16, "unit": "A100", "cost_per_hour": 3.50},
      "npu": {"capacity": 32, "unit": "Ascend", "cost_per_hour": 2.00},
      "memory": {"capacity": 512, "unit": "GB", "cost_per_hour": 0.01},
  }
  ```
- **状态**：
  - 已用/可用容量
  - 预热状态（冷/温/热）
  - 队列深度

#### 调度器 (Scheduler)
- **接口**：
  ```python
  class Scheduler:
      def allocate(self, task: Task) -> Allocation:
          """分配资源给任务"""
          pass
      
      def migrate(self, task_id: str, new_resource: str) -> bool:
          """迁移任务到新资源"""
          pass
      
      def preempt(self, task_id: str) -> bool:
          """抢占任务"""
          pass
  ```

#### 成本计算器 (Cost Calculator)
- **成本模型**：
  ```
  总成本 = 资源租赁成本 + 迁移成本 + 延迟惩罚 + SLA 违约成本
  
  资源租赁成本 = Σ(资源类型 × 使用时长 × 单价)
  迁移成本 = 数据搬运时间 × 单位时间成本 + 上下文切换开销
  延迟惩罚 = max(0, 实际延迟 - SLA 延迟) × 惩罚系数
  SLA 违约成本 = 违约次数 × 单次违约成本
  ```

---

## 二、调度算法实现

### 2.1 Baseline 算法

#### Round-Robin (轮询)
```python
class RoundRobinScheduler(Scheduler):
    def allocate(self, task):
        # 简单轮询分配
        resource = self.resources[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.resources)
        return resource
```

#### Priority-Based (优先级)
```python
class PriorityScheduler(Scheduler):
    def allocate(self, task):
        # 按优先级分配最优资源
        if task.priority == "high":
            return self.get_best_resource()
        else:
            return self.get_cheapest_resource()
```

### 2.2 时间套利算法 (Time-Arbitrage)

```python
class TimeArbitrageScheduler(Scheduler):
    """
    核心思想：低谷时段预加载任务，高峰时段释放资源
    """
    
    def __init__(self, price_predictor, load_predictor):
        self.price_predictor = price_predictor  # 价格预测
        self.load_predictor = load_predictor    # 负载预测
        self.task_queue = PriorityQueue()
        self.warm_pool = []  # 预热资源池
    
    def allocate(self, task):
        current_price = self.price_predictor.get_current_price()
        predicted_price = self.price_predictor.predict_next_hour()
        
        # 决策逻辑
        if current_price > predicted_price * 1.5:
            # 当前价格高，预测会下降 → 延迟非紧急任务
            if task.can_delay():
                self.task_queue.push(task, delay_minutes=30)
                return self.allocate_from_warm_pool(task)
        
        if current_price < self.price_threshold_low:
            # 当前价格低 → 预加载可延迟任务
            self.preload_deferrable_tasks()
        
        return self.allocate_immediate(task)
    
    def preload_deferrable_tasks(self):
        """在低价时段预加载可延迟任务"""
        for task in self.task_queue.get_deferrable():
            if self.has_capacity():
                self.warm_pool.append(self.allocate_resource(task))
```

### 2.3 强化学习调度 (RL Scheduler)

```python
class RLScheduler(Scheduler):
    """
    使用 PPO 算法学习最优调度策略
    """
    
    # 状态空间
    state_space = {
        "current_load": Float,      # 当前负载率 [0, 1]
        "resource_utilization": Dict[str, Float],  # 各资源利用率
        "queue_length": Integer,    # 队列长度
        "time_of_day": Float,       # 一天中的时间 [0, 24]
        "day_of_week": Integer,     # 星期几 [0, 6]
        "pending_tasks": Integer,   # 等待任务数
        "sla_risk": Float,          # SLA 违约风险 [0, 1]
    }
    
    # 动作空间
    action_space = {
        "allocate_cpu": Binary,
        "allocate_gpu": Binary,
        "allocate_npu": Binary,
        "delay_task": Binary,
        "migrate_task": Binary,
        "preempt_task": Binary,
    }
    
    # 奖励函数
    def calculate_reward(self, state, action, next_state):
        cost_saving = self.cost_before - self.cost_after
        sla_penalty = -10 if self.sla_violated else 0
        migration_penalty = -1 if action.migrate else 0
        
        return cost_saving + sla_penalty + migration_penalty
```

---

## 三、实验设计

### 3.1 实验场景

#### 场景 1：日常负载模式
- **输入**：7 天历史负载数据
- **目标**：验证时间套利在日常场景的效果
- **对比**：RR vs Priority vs TimeArbitrage

#### 场景 2：突发负载
- **输入**：基础负载 + 突发峰值（模拟热点事件）
- **目标**：验证弹性调度能力
- **指标**：峰值响应时间、成本超支比例

#### 场景 3：异构任务混合
- **输入**：CPU 密集型 + GPU 密集型 + 内存密集型任务混合
- **目标**：验证异构资源匹配效果
- **指标**：资源利用率、任务完成时间

### 3.2 评估指标

| 指标类别 | 具体指标 | 计算方式 |
|---------|---------|---------|
| **效率** | 资源利用率 | 已用资源 / 总资源 |
| | 任务吞吐量 | 完成任务数 / 时间 |
| | 平均响应时间 | Σ响应时间 / 任务数 |
| **成本** | 总成本 | 资源成本 + 迁移成本 + 惩罚 |
| | 成本节省率 | (Baseline 成本 - 实验成本) / Baseline 成本 |
| | 单位任务成本 | 总成本 / 任务数 |
| **质量** | SLA 满足率 | 满足 SLA 任务数 / 总任务数 |
| | 违约次数 | SLA 违约累计次数 |
| | 99 分位延迟 | P99 响应时间 |

### 3.3 实验配置

```yaml
experiments:
  - name: "baseline_comparison"
    duration: "7 days (simulated)"
    load_trace: "openclaw_7days_trace.json"
    algorithms: ["round_robin", "priority", "time_arbitrage"]
    metrics: ["cost", "utilization", "sla_compliance"]
    
  - name: "burst_handling"
    duration: "24 hours (simulated)"
    load_trace: "base_load + burst_injection"
    burst_config:
      magnitude: "3x normal"
      duration: "2 hours"
      time: "14:00-16:00"
    algorithms: ["priority", "time_arbitrage", "rl_scheduler"]
    
  - name: "heterogeneous_workload"
    duration: "3 days (simulated)"
    workload_mix:
      cpu_bound: 40%
      gpu_bound: 30%
      memory_bound: 20%
      io_bound: 10%
    algorithms: ["time_arbitrage", "rl_scheduler"]
```

---

## 四、数据收集与可视化

### 4.1 日志格式
```json
{
  "timestamp": "2026-03-28T14:30:00Z",
  "experiment_id": "exp_001",
  "algorithm": "time_arbitrage",
  "event_type": "allocation",
  "task_id": "task_12345",
  "resource_type": "gpu",
  "resource_id": "gpu_03",
  "cost": 0.035,
  "latency_ms": 2300,
  "sla_status": "met"
}
```

### 4.2 可视化图表
1. **负载时间序列图**：展示 24 小时负载波动
2. **资源利用率热力图**：小时 × 资源类型
3. **成本对比柱状图**：各算法成本对比
4. **SLA 合规率折线图**：随时间变化的合规率
5. **累积分布函数 (CDF)**：响应时间分布

---

## 五、实现计划

| 周次 | 任务 | 交付物 |
|------|------|--------|
| W1 | 仿真框架搭建 | simulator.py 核心框架 |
| W2 | Baseline 算法实现 | rr_scheduler.py, priority_scheduler.py |
| W3 | 时间套利算法实现 | time_arbitrage_scheduler.py |
| W4 | RL 调度器实现 | rl_scheduler.py (PPO) |
| W5 | 实验运行 + 数据收集 | 实验日志 + 原始数据 |
| W6 | 数据分析 + 可视化 | 图表 + 分析报告 |

---

*创建时间：2026-03-28*
