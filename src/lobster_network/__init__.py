"""
小龙虾网络核心模块 V2.2
"""

from .node import Node
from .dialogue import DialogueEngine, DialogueResult
from .emergence import EmergenceDetector, EmergenceEvent
from .world_state import WorldState, WorldStateManager
from .node_registry import NodeRegistry, NodeRegistration
from .lobster_network import LobsterNetwork
from .trading import TradingSystem, Task, Product, Order, UserProfile
from .token_economy import TokenEconomy, Transaction, Block, Wallet

__version__ = "0.4.2"
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
]
