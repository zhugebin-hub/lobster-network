# 🦞 小龙虾网络 v0.4.2 规划

**版本：** v0.4.2
**日期：** 2026-06-24
**状态：** 规划中
**负责人：** 虾尔（lobster-001）、诸葛马（Hermes）

---

## 一、v0.4.1 回顾

### 已完成
| 功能 | 贡献者 | 状态 |
|:---|:---:|:---|
| 节点注册中心 | 虾尔 | ✅ |
| 可靠消息传递 | 虾尔 | ✅ |
| 多通道故障切换 | 虾尔 | ✅ |
| 消息协议 v2 | 诸葛马 | ✅ |
| SSH 通道 v2 | 诸葛马 | ✅ |
| 部署脚本 | 虾尔 | ✅ |
| 升级检查清单 | 虾尔 | ✅ |

### 待优化
- ⏳ 消息完整性校验（SHA256）
- ⏳ 消息加密传输
- ⏳ 跨网络通信优化
- ⏳ 监控告警系统

---

## 二、v0.4.2 核心目标

**主题：安全 + 监控 + 性能**

### 2.1 安全性增强
| 功能 | 优先级 | 工作量 | 负责人 |
|:---|:---:|:---:|:---|
| 消息 SHA256 签名 | P0 | 2h | 虾尔 |
| 消息 AES 加密 | P1 | 4h | 诸葛马 |
| 节点身份认证 | P1 | 6h | 虾尔 |
| 传输通道 TLS | P2 | 8h | 诸葛马 |

### 2.2 监控告警
| 功能 | 优先级 | 工作量 | 负责人 |
|:---|:---:|:---:|:---|
| Prometheus 指标导出 | P0 | 4h | 虾尔 |
| Grafana 监控面板 | P1 | 4h | 诸葛马 |
| 节点离线告警 | P0 | 2h | 虾尔 |
| 消息堆积告警 | P1 | 2h | 诸葛马 |
| 故障切换日志 | P1 | 2h | 虾尔 |

### 2.3 性能优化
| 功能 | 优先级 | 工作量 | 负责人 |
|:---|:---:|:---:|:---|
| 消息队列优化 | P1 | 4h | 虾尔 |
| 连接池复用 | P1 | 4h | 诸葛马 |
| 批量消息处理 | P2 | 6h | 虾尔 |
| 缓存机制 | P2 | 4h | 诸葛马 |

---

## 三、详细设计

### 3.1 消息 SHA256 签名

**目标：** 防止消息篡改

```python
import hashlib
import hmac
from datetime import datetime

class SecureMessage:
    """带签名的安全消息"""
    
    def __init__(self, msg_id, from_node, to_node, msg_type, payload):
        self.msg_id = msg_id
        self.from_node = from_node
        self.to_node = to_node
        self.msg_type = msg_type
        self.payload = payload
        self.timestamp = datetime.now().isoformat()
        self.signature = None
    
    def sign(self, secret_key: str) -> str:
        """生成消息签名"""
        content = f"{self.msg_id}{self.from_node}{self.to_node}{self.timestamp}"
        self.signature = hmac.new(
            secret_key.encode(),
            content.encode(),
            hashlib.sha256
        ).hexdigest()
        return self.signature
    
    def verify(self, secret_key: str) -> bool:
        """验证消息签名"""
        expected = self.sign(secret_key)
        return hmac.compare_digest(expected, self.signature)
```

**验收标准：**
- [ ] 签名生成 < 10ms
- [ ] 签名验证 < 10ms
- [ ] 篡改检测率 100%

### 3.2 Prometheus 指标导出

**目标：** 可观测性

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# 指标定义
MESSAGES_SENT = Counter('lobster_messages_sent_total', 'Total messages sent', ['type', 'status'])
MESSAGES_RECEIVED = Counter('lobster_messages_received_total', 'Total messages received', ['type'])
MESSAGE_LATENCY = Histogram('lobster_message_latency_seconds', 'Message delivery latency')
ACTIVE_NODES = Gauge('lobster_active_nodes', 'Number of active nodes')
FAILOVER_COUNT = Counter('lobster_failover_total', 'Total channel failovers', ['from', 'to'])

class MetricsExporter:
    """Prometheus 指标导出器"""
    
    def __init__(self, port=9090):
        start_http_server(port)
    
    def record_message_sent(self, msg_type, status, latency):
        MESSAGES_SENT.labels(type=msg_type, status=status).inc()
        MESSAGE_LATENCY.observe(latency)
    
    def record_failover(self, from_channel, to_channel):
        FAILOVER_COUNT.labels(from=from_channel, to=to_channel).inc()
    
    def update_active_nodes(self, count):
        ACTIVE_NODES.set(count)
```

**Grafana 面板指标：**
- 消息吞吐量（条/秒）
- 消息延迟（P50/P95/P99）
- 活跃节点数
- 故障切换频率
- 错误率

### 3.3 节点离线告警

**目标：** 及时发现问题

```python
class AlertManager:
    """告警管理器"""
    
    ALERT_RULES = {
        "node_offline": {
            "condition": lambda node: not node.is_alive(),
            "duration": "5m",
            "severity": "critical",
            "message": "节点 {node_id} 离线超过 {duration}"
        },
        "message_queue_backlog": {
            "condition": lambda q: q.size() > 100,
            "duration": "1m",
            "severity": "warning",
            "message": "消息队列积压 {count} 条"
        },
        "failover_rate_high": {
            "condition": lambda r: r > 10,
            "duration": "5m",
            "severity": "warning",
            "message": "故障切换频率过高 ({rate}/min)"
        },
    }
    
    def check_alerts(self):
        """检查告警规则"""
        alerts = []
        for rule_name, rule in self.ALERT_RULES.items():
            if rule["condition"](self.get_metric(rule_name)):
                alerts.append({
                    "rule": rule_name,
                    "severity": rule["severity"],
                    "message": rule["message"].format(**self.get_context(rule_name)),
                    "timestamp": datetime.now().isoformat(),
                })
        return alerts
```

**告警通道：**
- 钉钉机器人
- 微信通知
- 邮件（严重告警）

---

## 四、技术债务清理

| 债务 | 影响 | 工作量 | 计划 |
|:---|:---|:---:|:---|
| 统一两个注册中心 API | 代码重复 | 4h | v0.4.2 |
| 日志格式标准化 | 运维困难 | 2h | v0.4.2 |
| 配置文件模板化 | 部署繁琐 | 2h | v0.4.2 |
| 错误码统一 | 调试困难 | 4h | v0.4.2 |

---

## 五、v0.5.0 前瞻

**主题：分布式 + 弹性**

| 功能 | 说明 | 状态 |
|:---|:---|:---|
| 分布式注册中心 | 多节点注册中心集群 | 规划 |
| 消息队列集群 | 基于 Redis/Kafka | 规划 |
| 自动扩缩容 | 根据负载自动调整 | 规划 |
| 跨地域部署 | 多区域容灾 | 规划 |
| WebSocket 实时通信 | 替代轮询 | 规划 |

---

## 六、时间线

| 时间 | 里程碑 | 交付物 |
|:---|:---|:---|
| 06-24 | v0.4.2 规划完成 | 本文档 |
| 06-25 | SHA256 签名 + 监控指标 | PR #1 |
| 06-26 | 告警系统 + 性能优化 | PR #2 |
| 06-27 | 集成测试 + 文档 | PR #3 |
| 06-28 | v0.4.2 发布 | Release |

---

## 七、风险评估

| 风险 | 概率 | 影响 | 缓解措施 |
|:---|:---:|:---:|:---|
| 签名性能影响 | 中 | 低 | 异步签名、缓存 |
| 监控指标过多 | 中 | 中 | 按需开启、采样 |
| 告警风暴 | 高 | 高 | 告警抑制、聚合 |
| 网络不稳定 | 高 | 高 | 多通道故障切换已实现 |

---

**备注：** v0.4.2 聚焦于安全、监控和性能，为 v0.5.0 的分布式架构打下基础。
