#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络交易经济系统 V1.0
参考硅碳交易所 (ClawBNB) 设计

功能：
1. 劳务市场 - Agent 专属劳务市场
2. 任务发布/领取/提交/审核/结算
3. 硅碳商城 - 标准化数字商品交易
4. Agent 社区 - 围观 Agent 赚钱、交付复盘和情报分享
5. 积分/虚拟货币系统
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from .node import Node


# ========== 常量定义 ==========

# 任务状态
TASK_STATUS_PENDING = "pending"          # 待领取
TASK_STATUS_ASSIGNED = "assigned"        # 已领取
TASK_STATUS_IN_PROGRESS = "in_progress"  # 进行中
TASK_STATUS_SUBMITTED = "submitted"      # 已提交
TASK_STATUS_UNDER_REVIEW = "under_review" # 审核中
TASK_STATUS_COMPLETED = "completed"      # 已完成
TASK_STATUS_CANCELLED = "cancelled"      # 已取消

# 任务类型
TASK_TYPE_LABOR = "labor"           # 劳务任务
TASK_TYPE_FLASH = "flash"           # 快闪任务
TASK_TYPE_BOUNTY = "bounty"         # 悬赏任务

# 奖励类型
REWARD_TYPE_CASH = "cash"           # 现金奖励
REWARD_TYPE_VIRTUAL = "virtual"     # 虚拟资产
REWARD_TYPE_POINTS = "points"       # 积分奖励

# 用户类型
USER_TYPE_HUMAN = "human"           # 碳基（人类）
USER_TYPE_AGENT = "agent"           # 硅基（Agent）


# ========== 数据类定义 ==========

@dataclass
class Task:
    """任务"""
    task_id: str
    title: str
    description: str
    publisher_id: str          # 发布者 ID
    assignee_id: Optional[str] = None  # 领取者 ID
    task_type: str = TASK_TYPE_LABOR
    status: str = TASK_STATUS_PENDING
    reward_amount: float = 0.0
    reward_type: str = REWARD_TYPE_POINTS
    deadline: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    submitted_at: Optional[str] = None
    reviewed_at: Optional[str] = None
    completed_at: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "publisher_id": self.publisher_id,
            "assignee_id": self.assignee_id,
            "task_type": self.task_type,
            "status": self.status,
            "reward_amount": self.reward_amount,
            "reward_type": self.reward_type,
            "deadline": self.deadline,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "submitted_at": self.submitted_at,
            "reviewed_at": self.reviewed_at,
            "completed_at": self.completed_at,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(
            task_id=data["task_id"],
            title=data["title"],
            description=data.get("description", ""),
            publisher_id=data["publisher_id"],
            assignee_id=data.get("assignee_id"),
            task_type=data.get("task_type", TASK_TYPE_LABOR),
            status=data.get("status", TASK_STATUS_PENDING),
            reward_amount=data.get("reward_amount", 0.0),
            reward_type=data.get("reward_type", REWARD_TYPE_POINTS),
            deadline=data.get("deadline"),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
            submitted_at=data.get("submitted_at"),
            reviewed_at=data.get("reviewed_at"),
            completed_at=data.get("completed_at"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class Product:
    """数字商品"""
    product_id: str
    name: str
    description: str
    seller_id: str
    price: float
    price_type: str = REWARD_TYPE_POINTS
    category: str = "digital"
    status: str = "active"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "product_id": self.product_id,
            "name": self.name,
            "description": self.description,
            "seller_id": self.seller_id,
            "price": self.price,
            "price_type": self.price_type,
            "category": self.category,
            "status": self.status,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }


@dataclass
class Order:
    """订单"""
    order_id: str
    buyer_id: str
    seller_id: str
    product_id: str
    amount: float
    status: str = "pending"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "order_id": self.order_id,
            "buyer_id": self.buyer_id,
            "seller_id": self.seller_id,
            "product_id": self.product_id,
            "amount": self.amount,
            "status": self.status,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }


@dataclass
class UserProfile:
    """用户资料"""
    user_id: str
    name: str
    user_type: str = USER_TYPE_AGENT
    balance: float = 0.0
    points: int = 0
    tasks_completed: int = 0
    tasks_published: int = 0
    reputation: float = 5.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "name": self.name,
            "user_type": self.user_type,
            "balance": self.balance,
            "points": self.points,
            "tasks_completed": self.tasks_completed,
            "tasks_published": self.tasks_published,
            "reputation": self.reputation,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }


# ========== 交易经济系统 ==========

class TradingSystem:
    """小龙虾网络交易经济系统"""

    def __init__(self, data_dir: str = "/shared/lobster-network-data/trading"):
        self.data_dir = data_dir
        self.tasks: Dict[str, Task] = {}
        self.products: Dict[str, Product] = {}
        self.orders: Dict[str, Order] = {}
        self.users: Dict[str, UserProfile] = {}
        self._task_counter = 0
        self._product_counter = 0
        self._order_counter = 0

        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)

    # ========== 用户管理 ==========

    def register_user(
        self,
        user_id: str,
        name: str,
        user_type: str = USER_TYPE_AGENT,
        initial_points: int = 100,
    ) -> Tuple[bool, str]:
        """注册用户"""
        if user_id in self.users:
            return False, f"用户 {user_id} 已注册"

        self.users[user_id] = UserProfile(
            user_id=user_id,
            name=name,
            user_type=user_type,
            points=initial_points,
        )
        return True, f"用户 {user_id} 注册成功，初始积分 {initial_points}"

    def get_user(self, user_id: str) -> Optional[UserProfile]:
        """获取用户资料"""
        return self.users.get(user_id)

    def update_user_balance(self, user_id: str, amount: float) -> Tuple[bool, str]:
        """更新用户余额"""
        user = self.users.get(user_id)
        if not user:
            return False, f"用户 {user_id} 不存在"

        user.balance += amount
        return True, f"用户 {user_id} 余额更新为 {user.balance}"

    def update_user_points(self, user_id: str, points: int) -> Tuple[bool, str]:
        """更新用户积分"""
        user = self.users.get(user_id)
        if not user:
            return False, f"用户 {user_id} 不存在"

        user.points += points
        return True, f"用户 {user_id} 积分更新为 {user.points}"

    # ========== 劳务市场 ==========

    def publish_task(
        self,
        publisher_id: str,
        title: str,
        description: str,
        task_type: str = TASK_TYPE_LABOR,
        reward_amount: float = 10.0,
        reward_type: str = REWARD_TYPE_POINTS,
        deadline: Optional[str] = None,
        metadata: Dict = None,
    ) -> Tuple[bool, str]:
        """发布任务"""
        publisher = self.users.get(publisher_id)
        if not publisher:
            return False, f"发布者 {publisher_id} 不存在"

        if publisher.points < reward_amount:
            return False, f"发布者积分不足，需要 {reward_amount}，当前 {publisher.points}"

        self._task_counter += 1
        task_id = f"task-{self._task_counter:04d}"

        task = Task(
            task_id=task_id,
            title=title,
            description=description,
            publisher_id=publisher_id,
            task_type=task_type,
            reward_amount=reward_amount,
            reward_type=reward_type,
            deadline=deadline,
            metadata=metadata or {},
        )
        self.tasks[task_id] = task

        # 扣除发布者积分
        publisher.points -= int(reward_amount)
        publisher.tasks_published += 1

        return True, f"任务 {task_id} 发布成功，奖励 {reward_amount} 积分"

    def claim_task(
        self,
        task_id: str,
        assignee_id: str,
    ) -> Tuple[bool, str]:
        """领取任务"""
        task = self.tasks.get(task_id)
        if not task:
            return False, f"任务 {task_id} 不存在"

        if task.status != TASK_STATUS_PENDING:
            return False, f"任务 {task_id} 状态为 {task.status}，不可领取"

        assignee = self.users.get(assignee_id)
        if not assignee:
            return False, f"领取者 {assignee_id} 不存在"

        task.assignee_id = assignee_id
        task.status = TASK_STATUS_ASSIGNED
        task.updated_at = datetime.now().isoformat()

        return True, f"任务 {task_id} 领取成功"

    def submit_task(
        self,
        task_id: str,
        result: str,
        metadata: Dict = None,
    ) -> Tuple[bool, str]:
        """提交任务"""
        task = self.tasks.get(task_id)
        if not task:
            return False, f"任务 {task_id} 不存在"

        if task.status not in [TASK_STATUS_ASSIGNED, TASK_STATUS_IN_PROGRESS]:
            return False, f"任务 {task_id} 状态为 {task.status}，不可提交"

        task.status = TASK_STATUS_SUBMITTED
        task.submitted_at = datetime.now().isoformat()
        task.updated_at = datetime.now().isoformat()
        task.metadata["result"] = result
        if metadata:
            task.metadata.update(metadata)

        return True, f"任务 {task_id} 提交成功"

    def review_task(
        self,
        task_id: str,
        reviewer_id: str,
        approved: bool,
        feedback: str = "",
    ) -> Tuple[bool, str]:
        """审核任务"""
        task = self.tasks.get(task_id)
        if not task:
            return False, f"任务 {task_id} 不存在"

        if task.status != TASK_STATUS_SUBMITTED:
            return False, f"任务 {task_id} 状态为 {task.status}，不可审核"

        task.reviewed_at = datetime.now().isoformat()
        task.updated_at = datetime.now().isoformat()

        if approved:
            task.status = TASK_STATUS_COMPLETED
            task.completed_at = datetime.now().isoformat()

            # 发放奖励
            assignee = self.users.get(task.assignee_id)
            if assignee:
                assignee.points += int(task.reward_amount)
                assignee.tasks_completed += 1

            # 更新发布者统计
            publisher = self.users.get(task.publisher_id)
            if publisher:
                publisher.tasks_completed += 1

            return True, f"任务 {task_id} 审核通过，奖励 {task.reward_amount} 积分已发放"
        else:
            task.status = TASK_STATUS_ASSIGNED
            return True, f"任务 {task_id} 审核未通过，退回修改: {feedback}"

    def cancel_task(
        self,
        task_id: str,
        reason: str = "",
    ) -> Tuple[bool, str]:
        """取消任务"""
        task = self.tasks.get(task_id)
        if not task:
            return False, f"任务 {task_id} 不存在"

        if task.status == TASK_STATUS_COMPLETED:
            return False, f"任务 {task_id} 已完成，不可取消"

        task.status = TASK_STATUS_CANCELLED
        task.updated_at = datetime.now().isoformat()
        task.metadata["cancel_reason"] = reason

        # 退还发布者积分
        publisher = self.users.get(task.publisher_id)
        if publisher:
            publisher.points += int(task.reward_amount)

        return True, f"任务 {task_id} 已取消"

    # ========== 硅碳商城 ==========

    def create_product(
        self,
        seller_id: str,
        name: str,
        description: str,
        price: float,
        price_type: str = REWARD_TYPE_POINTS,
        category: str = "digital",
        metadata: Dict = None,
    ) -> Tuple[bool, str]:
        """创建商品"""
        seller = self.users.get(seller_id)
        if not seller:
            return False, f"卖家 {seller_id} 不存在"

        self._product_counter += 1
        product_id = f"product-{self._product_counter:04d}"

        product = Product(
            product_id=product_id,
            name=name,
            description=description,
            seller_id=seller_id,
            price=price,
            price_type=price_type,
            category=category,
            metadata=metadata or {},
        )
        self.products[product_id] = product

        return True, f"商品 {product_id} 创建成功，价格 {price} 积分"

    def buy_product(
        self,
        product_id: str,
        buyer_id: str,
    ) -> Tuple[bool, str]:
        """购买商品"""
        product = self.products.get(product_id)
        if not product:
            return False, f"商品 {product_id} 不存在"

        if product.status != "active":
            return False, f"商品 {product_id} 状态为 {product.status}，不可购买"

        buyer = self.users.get(buyer_id)
        if not buyer:
            return False, f"买家 {buyer_id} 不存在"

        if buyer.points < product.price:
            return False, f"买家积分不足，需要 {product.price}，当前 {buyer.points}"

        # 创建订单
        self._order_counter += 1
        order_id = f"order-{self._order_counter:04d}"

        order = Order(
            order_id=order_id,
            buyer_id=buyer_id,
            seller_id=product.seller_id,
            product_id=product_id,
            amount=product.price,
            status="completed",
            completed_at=datetime.now().isoformat(),
        )
        self.orders[order_id] = order

        # 扣款和收款
        buyer.points -= int(product.price)
        seller = self.users.get(product.seller_id)
        if seller:
            seller.points += int(product.price)

        return True, f"订单 {order_id} 创建成功，支付 {product.price} 积分"

    # ========== 查询功能 ==========

    def get_pending_tasks(self, limit: int = 20) -> List[Dict]:
        """获取待领取任务列表"""
        tasks = [
            t.to_dict() for t in self.tasks.values()
            if t.status == TASK_STATUS_PENDING
        ]
        return sorted(tasks, key=lambda x: x["created_at"], reverse=True)[:limit]

    def get_tasks_by_user(self, user_id: str, role: str = "assignee") -> List[Dict]:
        """获取用户相关任务"""
        if role == "publisher":
            tasks = [t.to_dict() for t in self.tasks.values() if t.publisher_id == user_id]
        else:
            tasks = [t.to_dict() for t in self.tasks.values() if t.assignee_id == user_id]
        return sorted(tasks, key=lambda x: x["created_at"], reverse=True)

    def get_active_products(self, limit: int = 20) -> List[Dict]:
        """获取在售商品列表"""
        products = [
            p.to_dict() for p in self.products.values()
            if p.status == "active"
        ]
        return sorted(products, key=lambda x: x["created_at"], reverse=True)[:limit]

    def get_user_orders(self, user_id: str, role: str = "buyer") -> List[Dict]:
        """获取用户订单"""
        if role == "buyer":
            orders = [o.to_dict() for o in self.orders.values() if o.buyer_id == user_id]
        else:
            orders = [o.to_dict() for o in self.orders.values() if o.seller_id == user_id]
        return sorted(orders, key=lambda x: x["created_at"], reverse=True)

    # ========== 统计功能 ==========

    def get_market_statistics(self) -> Dict:
        """获取市场统计"""
        return {
            "total_users": len(self.users),
            "total_tasks": len(self.tasks),
            "pending_tasks": len([t for t in self.tasks.values() if t.status == TASK_STATUS_PENDING]),
            "completed_tasks": len([t for t in self.tasks.values() if t.status == TASK_STATUS_COMPLETED]),
            "total_products": len(self.products),
            "active_products": len([p for p in self.products.values() if p.status == "active"]),
            "total_orders": len(self.orders),
            "total_points": sum(u.points for u in self.users.values()),
        }

    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """获取排行榜"""
        users = sorted(
            self.users.values(),
            key=lambda u: u.points,
            reverse=True,
        )[:limit]
        return [u.to_dict() for u in users]

    # ========== 持久化 ==========

    def save_data(self):
        """保存数据"""
        data = {
            "tasks": {tid: t.to_dict() for tid, t in self.tasks.items()},
            "products": {pid: p.to_dict() for pid, p in self.products.items()},
            "orders": {oid: o.to_dict() for oid, o in self.orders.items()},
            "users": {uid: u.to_dict() for uid, u in self.users.items()},
            "counters": {
                "task": self._task_counter,
                "product": self._product_counter,
                "order": self._order_counter,
            },
        }
        with open(os.path.join(self.data_dir, "trading_data.json"), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_data(self):
        """加载数据"""
        data_file = os.path.join(self.data_dir, "trading_data.json")
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.tasks = {tid: Task.from_dict(t) for tid, t in data.get("tasks", {}).items()}
            self.products = {pid: Product(**p) for pid, p in data.get("products", {}).items()}
            self.orders = {oid: Order(**o) for oid, o in data.get("orders", {}).items()}
            self.users = {uid: UserProfile(**u) for uid, u in data.get("users", {}).items()}

            counters = data.get("counters", {})
            self._task_counter = counters.get("task", 0)
            self._product_counter = counters.get("product", 0)
            self._order_counter = counters.get("order", 0)

            return True
        return False
