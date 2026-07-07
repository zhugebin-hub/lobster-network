# LobsterNetwork 优化完善方案 v0.4.1 → v0.6.0+

> 基于框架运行机制全面分析，结合前期审计发现的 7 个问题点  
> 生成日期：2026-07-07

---

## 一、前期审计问题清单回顾

| # | 问题 | 状态 | 优先级 |
|---|------|------|--------|
| 1 | `config.py` 中 `network_version` 不一致 | ✅ 已修复（0.2.0 → 0.4.1） | — |
| 2 | `clawvard_bridge.py` 中 User-Agent 版本号不一致 | ✅ 已修复（0.5.0 → 0.4.1） | — |
| 3 | HTTP 传输通道缺失 | ❌ 未修复 | P1 |
| 4 | SSH 传输未接入 Messenger | ❌ 未修复 | P1 |
| 5 | Assessment 模块未从 `__init__.py` 导出 | ❌ 待确认 | P0 |
| 6 | 占位文件存在但为空壳 | ❌ 未修复 | P0 |
| 7 | `network/__init__.py` 为空文件 | ❌ 未修复 | P0 |

---

## 二、P0 — 立即修复（本次执行）

### 2.1 Assessment 模块导出

**现状**：`src/lobster_network/assessment/` 目录在全面源码扫描中**未发现**。先前的审计报告所提及的 "401 行评估引擎 + 255 行 Clawvard 桥接代码" 在当前源码树中不存在对应 Python 文件。只有文档级别的 `clawvard-experiment-guide.md`。

**处理方案**：
- **若后续确认**代码以其他路径或分支存在，应立即恢复并导出
- **若代码已丢失**：将 Assessment 列入 P2 重新开发计划，暂不导出
- **本轮操作**：不强行创建空壳，避免虚假导出。在 `__init__.py` 中添加注释说明 Assessment 模块为规划中的 P2 功能

### 2.2 占位文件处理

**发现的占位/空壳文件**（在嵌套路径 `lobster-network/lobster-network/src/lobster_network/` 下）：

| 文件 | 实际大小 | 处理方案 |
|------|---------|---------|
| `global_scheduler.py` | 空（0 字节） | 添加 TODO 注释说明规划用途 |
| `message_queue.py` | 空（0 字节） | 添加 TODO 注释说明规划用途 |
| `rate_limiter.py` | 空（0 字节） | 添加 TODO 注释说明规划用途 |
| `network/__init__.py` | 空（0 字节） | 添加包文档字符串 |

**说明**：`manus_integration.py` 在全面扫描中不存在，可能已在之前被移除。

### 2.3 空文件处理

`network/__init__.py`（主包路径下）为空文件（0 字节），需添加最小包文档字符串。

---

## 三、P1 — 本周修复

### 3.1 HTTPTransport 实现

**目标**：补全 README 架构图中声明的 HTTP 传输通道。

**设计方案**：

```python
# src/lobster_network/network/http_transport.py
class HTTPTransport:
    """
    HTTP 传输通道
    
    功能：
    - RESTful API 消息收发（POST /messages/send, GET /messages/receive）
    - 长轮询（Long Polling）支持近实时通信
    - Bearer Token 认证
    - 消息批处理（batch send/receive）
    - 请求限流（token bucket）
    """
    
    def __init__(self, base_url, auth_token, timeout=30):
        ...
    
    def send_message(self, message: Dict) -> bool: ...
    def receive_messages(self, since: Optional[str] = None) -> List[Dict]: ...
    def health_check(self) -> bool: ...
```

**依赖**：`requests` 或 `httpx` 库。

**关键参数**：
- 超时：30s（对齐 SSH 通道）
- 重试：3 次 + 指数退避
- 批大小：最多 50 条/次

### 3.2 SSHTransport 接入 Messenger

**目标**：将已实现的 SSH 双通道（SSHChannel + SSHChannelV2）统一接入消息路由。

**设计方案**：
1. **统一接口**：定义 `TransportInterface` 抽象基类（`send` / `receive` / `health_check`）
2. **通道注册**：在 Messenger 中注册 `SSHTransport` 为可用通道
3. **通道选择策略**：
   - 优先级：WebSocket > SSH > HTTP > File
   - 故障切换：主通道连续 3 次失败后切换到备通道
4. **SSH 版本选择**：保留 SSHChannelV2（index 退避 + 去重），废弃 SSHChannel

### 3.3 统一日志格式

**现状**：各模块使用 `logging` 但格式不一致（有 `[SSHChannel]`、`📊`、`✅` 等 Emoji + 前缀混用）。

**方案**：
```python
# 统一格式
FORMAT = "%(asctime)s | %(levelname)-7s | %(name)-20s | %(message)s"

# 模块级别 logger 命名规范
logger = logging.getLogger("lobster_network.{module_name}")
```

### 3.4 错误码标准化

**设计方案**：定义全局错误码枚举

```python
class LobsterErrorCode(Enum):
    # 1xxx: 网络层
    NETWORK_UNREACHABLE = 1001
    CHANNEL_TIMEOUT = 1002
    HEARTBEAT_LOST = 1003
    
    # 2xxx: 框架层
    NODE_NOT_FOUND = 2001
    DIALOGUE_FAILED = 2002
    EMERGENCE_THRESHOLD_NOT_MET = 2003
    
    # 3xxx: 经济层
    INSUFFICIENT_BALANCE = 3001
    CONTRACT_EXECUTION_FAILED = 3002
```

---

## 四、P2 — v0.5.0 版本目标

### 4.1 8 维度评估引擎集成

**设计**：基于 README 中的 8 维度概念，实现可插拔的评估引擎。

| 维度 | 评估指标 | 数据源 |
|------|---------|--------|
| 对话质量 | 涌现值均值/标准差 | DialogueEngine |
| 学习速度 | 单位时间解题数/正确率趋势 | Hermes Coach |
| 知识覆盖 | loaded_chunks 多样性 | WorldState |
| 宝藏产出 | unlocked_treasures 数量/质量 | WorldState |
| 协作效率 | 节点间对话次数/有效率 | EmergenceDetector |
| 资源利用 | 时间套利收益率 | TimeArbitrage |
| 稳定性 | 节点在线率/心跳丢失率 | NodeRegistry |
| 创新能力 | new_insight 去重后的新颖度 | DialogueEngine |

### 4.2 Clawvard 桥接上线

**前置条件**：
- Assessment 代码恢复或重写（见 P0-2.1）
- 与 Clawvard 实验平台的 API 集成

**API 设计**：
```python
class ClawvardBridge:
    def submit_experiment(self, config: Dict) -> str: ...
    def get_results(self, experiment_id: str) -> Dict: ...
    def compare_baseline(self, experiment_id: str, baseline_id: str) -> Dict: ...
```

### 4.3 SSH 通道版本合并

- 废弃 `ssh_channel_v2.py`（命名混乱，与 `ssh_channel.py` 功能重叠）
- 将 `SSHChannelV2` 重命名为 `SSHChannel`
- 删除旧版 `SSHChannel`

---

## 五、P3 — v0.6.0+ 版本目标

### 5.1 语义涌现引擎

**目标**：将当前基于硬编码二值判断的涌现值计算升级为基于 LLM 嵌入的语义级计算。

**升级方案**：
- `perspective_distance`：当前仅判断字符串相等 → 改为基于 embedding 的余弦距离
- `knowledge_complementarity`：当前仅判断字符串相等 → 改为基于知识图谱的重叠度
- `dialogue_depth`：当前恒为 1.0 → 改为基于对话轮次的实际深度
- `novelty_of_output`：当前恒为 0.5 → 改为基于 LLM 评估的真实新颖度

### 5.2 学习协调器

**目标**：基于 TimeArbitrage 的五维套利分析结果，自动为每个节点制定最优学习节奏。

**功能**：
- 动态调整 `learning_rate`
- 自适应难度阶梯
- 跨学员知识迁移

### 5.3 K8s 部署方案

**目标**：提供生产级 Kubernetes 部署方案。

**交付物**：
- `deploy/kubernetes/`：Deployment / Service / ConfigMap / Secret
- `deploy/helm/`：Helm Chart
- `deploy/docker/`：Dockerfile + docker-compose
- 资源配额：512MB-2GB/节点（对齐 WebSocket 内存限制设计）

---

## 六、架构债务清单

| 债务项 | 严重程度 | 影响范围 | 建议处理版本 |
|--------|---------|---------|------------|
| Messenger 抽象层缺失 | 高 | 多通道调度不可用 | P1 |
| SSH 双版本共存 | 中 | 维护成本 + 命名混乱 | P2 |
| 涌现值硬编码 | 中 | 涌现检测精度不足 | P3 |
| `network/__init__.py` 为空 | 低 | 包结构不完整 | P0 |
| 占位文件目录嵌套 | 低 | 模块路径混乱 | P0 |
| HTTP 传输声明但未实现 | 中 | README 与代码不一致 | P1 |
| 日志格式不统一 | 低 | 调试体验 | P1 |

---

## 七、执行顺序与时间线

```
P0（今天 2026-07-07）
├── 占位文件 TODO 标记
├── network/__init__.py 补充文档字符串
└── __init__.py 补充 Assessment 规划注释

P1（本周 2026-07-07 ~ 07-13）
├── HTTPTransport 实现
├── SSHTransport 接入 Messenger
├── 统一日志格式
└── 错误码标准化

P2（v0.5.0，2-3 周）
├── 8 维度评估引擎
├── Clawvard 桥接
├── SSH 版本合并
└── Assessment 模块重写/恢复

P3（v0.6.0，4-6 周）
├── 语义涌现引擎
├── 学习协调器
└── K8s 部署方案
```

---

## 八、风险评估

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| Assessment 代码永久丢失 | 中 | P2 工作量翻倍 | 排查历史 commit、备份分支 |
| HTTPTransport 与现有 WebSocket 冲突 | 低 | 重复劳动 | 设计统一 TransportInterface |
| 语义涌现引擎需要 LLM API 依赖 | 中 | 成本增加、离线不可用 | 保留硬编码降级路径 |
| SSH 双版本合并引入 regression | 低 | SSH 传输中断 | 全量测试 + 灰度切换 |
