"""
小龙虾网络 - 统一入口
Lobster Network - Unified Entry Point

对话即创造：一人一世界的世界观

v0.7.0 变更 (V3.1 优化层):
- 新增: 熔断器 (CircuitBreaker)，API 调用保护，CLOSED→OPEN→HALF_OPEN 状态机
- 新增: 健康检查 (HealthCheck)，CPU/内存/磁盘监控 + 服务连通性检测
- 新增: 缓存管理器 (CacheManager)，MD5 键值 + TTL 本地 JSON 缓存
- 新增: 向量记忆扩展器 (VectorMemoryExpander)，错题语义检索
- 新增: MCP 验证器 (MCPValidator)，训练时实时验证
- 新增: 模型路由器 (ModelRouter)，难度感知路由，成本降低 50%
- 新增: 龙虾币 (LobsterCoin)，训练经济闭环系统

v0.6.0 变更:
- 新增: 增强对话引擎，语义涌现计算 (Jaccard相似度, n-gram分析)
- 新增: 学习协调器 (LearningCoordinator)，闭合评估-训练反馈环
- 新增: HTTP传输通道 (HTTPTransport)，实现节点间真实网络通信
- 新增: 基于8维度评估结果的自适应训练计划
- 新增: 互补节点间的协作建议生成
- 修复: setup.py / __init__.py / README 版本号对齐
- 重构: 清理 domains/assessment 重复代码

v0.5.0 变更:
- 新增: 8维度能力评估引擎 (EightDimEngine)，参考 Clawvard School 评估体系
- 新增: 维度画像 (DimensionProfile)、Clawvard桥接 (ClawvardBridge)
- 新增: 评估维度定义、评分器、改进建议生成器
- 注意: network/node_registry.py 已弃用，请使用 registry.py

v0.4.0 变更:
- 新增: 节点注册中心 (NodeRegistry)、可靠消息 (Messenger)、集成层 (LobsterNetworkWithRegistry)
- 新增: SSH通道v2 (SSHChannelV2)、消息协议v2 (MessageProtocolV2)
- 新增: 交易系统 (TradingSystem)、代币经济 (TokenEconomy)、智能合约 (SmartContract)
- 新增: 跨链系统 (CrossChainSystem)、多币种系统 (MultiCurrencySystem)
"""

__version__ = "0.7.0"

# 框架层 (Framework Layer)
from .node import Node
from .dialogue import DialogueEngine, DialogueResult
from .emergence import EmergenceDetector, EmergenceEvent
from .world_state import WorldState, WorldStateManager
from .lobster_network import LobsterNetwork
from .node_registry import NodeRegistry, NodeRegistration

# 经济与交易层 (Economy & Trading Layer)
from .trading import TradingSystem, Task, Product, Order, UserProfile
from .token_economy import TokenEconomy, Transaction, Block, Wallet
from .smart_contract import SmartContractSystem, SmartContract, ContractCondition
from .cross_chain import CrossChainSystem, LiquidityPool, CrossChainTransaction, BridgeNode
from .multi_currency import MultiCurrencySystem, MultiCurrencyWallet, ExchangeRecord

# 网络层 (Network Layer)
from .network.indra_net import IndraNet, IndraNetNode
from .network.ssh_channel_v2 import SSHChannel
SSHChannelV2 = SSHChannel  # 向后兼容别名
from .network.ssh_transport import SSHTransport

# 可靠通信层 (Reliable Communication Layer) - v0.4.1 新增
from .registry import NodeRegistry, RegistrationInfo, TransportConfig, TransportType, NodeStatus
from .messenger import (
    Messenger, ReliableMessage, MessageStatus, MessageAttempt,
    NFSTransport, FileTransport,
)
from .integration import LobsterNetworkWithRegistry

# 工具层 (Utility Layer)
from .utils.config import NetworkConfig, ConfigManager
from .utils.logger import LobsterLogger, get_logger
from .utils.message_protocol_v2 import Message as MessageV2, MessageProtocol as MessageProtocolV2
from .utils.message_protocol import Message as LegacyMessage, MessageProtocol as LegacyMessageProtocol
from .utils.message_protocol import MessageProtocol  # master 新增

# 套利层 (Arbitrage Layer)
from .time_arbitrage import (
    TimeArbitrageEngine, ArbitrageType, NodeSpeedProfile,
    ArbitrageOpportunity, ArbitrageResult, ForgettingCurve,
)

# 别名（向后兼容）
Message = MessageV2  # v2 作为默认
MessageProtocol = MessageProtocolV2  # v2 作为默认

# v0.5.0 8维度评估层 (Assessment Layer) — 可选导入
try:
    from .assessment import (
        EightDimEngine, AssessmentResult,
        DimensionProfile, Dimension,
        ClawvardBridge, PracticeSession,
        DIMENSION_REGISTRY, DIMENSION_DESCRIPTIONS, DIMENSION_WEIGHTS,
    )
except ImportError:
    pass  # assessment 模块为可选增强

# v0.6.0 学习协调器与HTTP传输 (Learning Coordinator & HTTP Transport) — 可选导入
try:
    from .learning import LearningCoordinator
except ImportError:
    pass  # learning 模块为可选增强

try:
    from .network.http_transport import HTTPTransport
except ImportError:
    pass  # http_transport 模块为可选增强


__all__ = [
    # Version
    "__version__",
    # Core
    "Node", "DialogueEngine", "DialogueResult",
    "EmergenceDetector", "EmergenceEvent",
    "WorldState", "WorldStateManager",
    "LobsterNetwork",
    # Economy & Trading
    "TradingSystem", "Task", "Product", "Order", "UserProfile",
    "TokenEconomy", "Transaction", "Block", "Wallet",
    "SmartContractSystem", "SmartContract", "ContractCondition",
    "CrossChainSystem", "LiquidityPool", "CrossChainTransaction", "BridgeNode",
    "MultiCurrencySystem", "MultiCurrencyWallet", "ExchangeRecord",
    # Network
    "IndraNet", "IndraNetNode",
    "SSHChannel", "SSHChannelV2", "SSHTransport",
    # Reliable Communication (v0.4.1)
    "NodeRegistry", "RegistrationInfo", "TransportConfig", "TransportType", "NodeStatus",
    "Messenger", "ReliableMessage", "MessageStatus", "MessageAttempt",
    "NFSTransport", "FileTransport",
    "LobsterNetworkWithRegistry",
    # Message Protocol (v2 默认)
    "Message", "MessageProtocol",  # v2 (推荐)
    "MessageV2", "MessageProtocolV2",  # v2 显式
    "LegacyMessage", "LegacyMessageProtocol",  # v1 (兼容)
    # Arbitrage
    "TimeArbitrageEngine", "ArbitrageType", "NodeSpeedProfile",
    "ArbitrageOpportunity", "ArbitrageResult", "ForgettingCurve",
    # Utils
    "NetworkConfig", "ConfigManager",
    "LobsterLogger", "get_logger",
    # v0.5.0 Assessment Layer
    "EightDimEngine", "AssessmentResult",
    "DimensionProfile", "Dimension",
    "ClawvardBridge", "PracticeSession",
    "DIMENSION_REGISTRY", "DIMENSION_DESCRIPTIONS", "DIMENSION_WEIGHTS",
    # v0.6.0 Learning Coordinator & HTTP Transport
    "LearningCoordinator", "HTTPTransport",
]
