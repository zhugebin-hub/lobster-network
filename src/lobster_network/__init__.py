"""
小龙虾网络核心模块 V2.1
"""

from .node import Node
from .dialogue import DialogueEngine, DialogueResult
from .emergence import EmergenceDetector, EmergenceEvent
from .world_state import WorldState, WorldStateManager
from .node_registry import NodeRegistry, NodeRegistration
from .lobster_network import LobsterNetwork
from .trading import TradingSystem, Task, Product, Order, UserProfile
from .token_economy import TokenEconomy, Transaction, Block, Wallet
from .smart_contract import SmartContractSystem, SmartContract, ContractCondition
from .cross_chain import CrossChainSystem, LiquidityPool, CrossChainTransaction, BridgeNode
from .multi_currency import MultiCurrencySystem, MultiCurrencyWallet, ExchangeRecord

# TODO (P2/v0.5.0): assessment 模块 — 8维度评估引擎 + Clawvard 桥接
# 当前 assessment/ 子包的源码文件尚未落地，需在新版本中创建并导出以下模块：
#   from .assessment import AssessmentEngine, ClawvardBridge
# 相关设计文档见: clawvard-experiment-guide.md, clawvard-token.md

__version__ = "0.4.1"
__all__ = [
    "Node",
    "DialogueEngine",
    "DialogueResult",
    "EmergenceDetector",
    "EmergenceEvent",
    "WorldState",
    "WorldStateManager",
    "NodeRegistry",
    "NodeRegistration",
    "LobsterNetwork",
    "TradingSystem",
    "Task",
    "Product",
    "Order",
    "UserProfile",
    "TokenEconomy",
    "Transaction",
    "Block",
    "Wallet",
    "SmartContractSystem",
    "SmartContract",
    "ContractCondition",
    "CrossChainSystem",
    "LiquidityPool",
    "CrossChainTransaction",
    "BridgeNode",
    "MultiCurrencySystem",
    "MultiCurrencyWallet",
    "ExchangeRecord",
]
