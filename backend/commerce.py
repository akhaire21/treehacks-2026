"""
Commerce / Token Economy layer for the Agent Workflow Marketplace.

Manages:
  - User token balances (credits)
  - Purchases, transactions, and receipts
  - Workflow creator revenue / royalties
  - Shopping cart for multi-workflow purchases
  - Transaction history

Prize target: Visa — The Generative Edge: Future of Commerce
"""

import uuid
import time
from datetime import datetime
from typing import Dict, Any, List, Optional


class Transaction:
    """A single marketplace transaction."""

    def __init__(
        self,
        tx_type: str,  # "purchase", "refund", "deposit", "creator_payout"
        workflow_id: Optional[str],
        amount: int,
        buyer_id: str,
        seller_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ):
        self.tx_id = f"tx_{uuid.uuid4().hex[:12]}"
        self.tx_type = tx_type
        self.workflow_id = workflow_id
        self.amount = amount
        self.buyer_id = buyer_id
        self.seller_id = seller_id
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()
        self.status = "completed"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tx_id": self.tx_id,
            "tx_type": self.tx_type,
            "workflow_id": self.workflow_id,
            "amount": self.amount,
            "buyer_id": self.buyer_id,
            "seller_id": self.seller_id,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "status": self.status,
        }


class ShoppingCart:
    """Shopping cart for multi-workflow purchases."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.items: List[Dict[str, Any]] = []
        self.created_at = datetime.now().isoformat()

    def add_item(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        wf_id = workflow.get("workflow_id")
        # Don't add duplicates
        if any(item["workflow_id"] == wf_id for item in self.items):
            return {"error": "Workflow already in cart", "workflow_id": wf_id}

        self.items.append({
            "workflow_id": wf_id,
            "title": workflow.get("title", ""),
            "token_cost": workflow.get("token_cost", 0),
            "rating": workflow.get("rating", 0),
            "added_at": datetime.now().isoformat(),
        })
        return {"success": True, "cart_size": len(self.items), "total": self.get_total()}

    def remove_item(self, workflow_id: str) -> Dict[str, Any]:
        self.items = [i for i in self.items if i["workflow_id"] != workflow_id]
        return {"success": True, "cart_size": len(self.items), "total": self.get_total()}

    def get_total(self) -> int:
        return sum(item["token_cost"] for item in self.items)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "items": self.items,
            "item_count": len(self.items),
            "total_cost": self.get_total(),
            "created_at": self.created_at,
        }

    def clear(self):
        self.items = []


class CommerceEngine:
    """
    Manages the token economy and commerce layer.
    In production this would be backed by a real DB + payment processor.
    For the hackathon, in-memory is fine.
    """

    # Platform takes 15% commission, creator gets 85%
    PLATFORM_COMMISSION = 0.15

    def __init__(self):
        # In-memory stores (would be DB in production)
        self.user_balances: Dict[str, int] = {}
        self.transactions: List[Transaction] = []
        self.carts: Dict[str, ShoppingCart] = {}
        self.creator_earnings: Dict[str, int] = {}

        # Seed a default user
        self.user_balances["default_user"] = 5000
        self.user_balances["demo_agent"] = 10000

    # ------------------------------------------------------------------
    # User balance management
    # ------------------------------------------------------------------

    def get_balance(self, user_id: str) -> int:
        return self.user_balances.get(user_id, 0)

    def deposit(self, user_id: str, amount: int) -> Dict[str, Any]:
        """Add credits to user's balance."""
        self.user_balances[user_id] = self.user_balances.get(user_id, 0) + amount
        tx = Transaction("deposit", None, amount, user_id)
        self.transactions.append(tx)
        return {
            "success": True,
            "new_balance": self.user_balances[user_id],
            "tx_id": tx.tx_id,
        }

    # ------------------------------------------------------------------
    # Purchase flow
    # ------------------------------------------------------------------

    def purchase_workflow(
        self,
        user_id: str,
        workflow: Dict[str, Any],
        creator_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process a single workflow purchase.
        Deducts from buyer, pays creator (minus commission).
        """
        cost = workflow.get("token_cost", 0)
        balance = self.get_balance(user_id)

        if balance < cost:
            return {
                "success": False,
                "error": "Insufficient balance",
                "balance": balance,
                "cost": cost,
                "shortfall": cost - balance,
            }

        # Deduct from buyer
        self.user_balances[user_id] -= cost

        # Pay creator (if any)
        creator = creator_id or workflow.get("creator_id", "marketplace")
        creator_share = int(cost * (1 - self.PLATFORM_COMMISSION))
        self.creator_earnings[creator] = self.creator_earnings.get(creator, 0) + creator_share

        # Record transaction
        tx = Transaction(
            tx_type="purchase",
            workflow_id=workflow.get("workflow_id"),
            amount=cost,
            buyer_id=user_id,
            seller_id=creator,
            metadata={
                "title": workflow.get("title"),
                "creator_share": creator_share,
                "platform_fee": cost - creator_share,
                "token_savings": workflow.get("token_comparison", {}).get("savings_percent", 0),
            },
        )
        self.transactions.append(tx)

        return {
            "success": True,
            "tx_id": tx.tx_id,
            "workflow_id": workflow.get("workflow_id"),
            "title": workflow.get("title"),
            "cost": cost,
            "new_balance": self.user_balances[user_id],
            "creator_share": creator_share,
            "platform_fee": cost - creator_share,
        }

    def checkout_cart(self, user_id: str) -> Dict[str, Any]:
        """Purchase all items in user's cart."""
        cart = self.carts.get(user_id)
        if not cart or not cart.items:
            return {"success": False, "error": "Cart is empty"}

        total = cart.get_total()
        balance = self.get_balance(user_id)

        if balance < total:
            return {
                "success": False,
                "error": "Insufficient balance for cart",
                "balance": balance,
                "cart_total": total,
                "shortfall": total - balance,
            }

        # Process each item
        receipts = []
        for item in cart.items:
            receipt = self.purchase_workflow(user_id, item)
            receipts.append(receipt)

        cart.clear()

        return {
            "success": True,
            "items_purchased": len(receipts),
            "total_spent": total,
            "new_balance": self.get_balance(user_id),
            "receipts": receipts,
        }

    # ------------------------------------------------------------------
    # Shopping cart
    # ------------------------------------------------------------------

    def get_cart(self, user_id: str) -> ShoppingCart:
        if user_id not in self.carts:
            self.carts[user_id] = ShoppingCart(user_id)
        return self.carts[user_id]

    def add_to_cart(self, user_id: str, workflow: Dict[str, Any]) -> Dict[str, Any]:
        cart = self.get_cart(user_id)
        return cart.add_item(workflow)

    def remove_from_cart(self, user_id: str, workflow_id: str) -> Dict[str, Any]:
        cart = self.get_cart(user_id)
        return cart.remove_item(workflow_id)

    # ------------------------------------------------------------------
    # Transaction history
    # ------------------------------------------------------------------

    def get_transactions(self, user_id: Optional[str] = None, limit: int = 50) -> List[Dict]:
        txs = self.transactions
        if user_id:
            txs = [t for t in txs if t.buyer_id == user_id or t.seller_id == user_id]
        txs = sorted(txs, key=lambda t: t.timestamp, reverse=True)[:limit]
        return [t.to_dict() for t in txs]

    def get_creator_dashboard(self, creator_id: str) -> Dict[str, Any]:
        """Revenue dashboard for workflow creators."""
        creator_txs = [t for t in self.transactions if t.seller_id == creator_id]
        total_earned = self.creator_earnings.get(creator_id, 0)
        total_sales = len(creator_txs)
        workflows_sold = list(set(t.workflow_id for t in creator_txs if t.workflow_id))

        return {
            "creator_id": creator_id,
            "total_earned": total_earned,
            "total_sales": total_sales,
            "unique_workflows_sold": len(workflows_sold),
            "recent_transactions": [t.to_dict() for t in creator_txs[-10:]],
        }

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    def get_marketplace_stats(self) -> Dict[str, Any]:
        """Aggregate marketplace statistics."""
        total_txs = len(self.transactions)
        total_volume = sum(t.amount for t in self.transactions if t.tx_type == "purchase")
        unique_buyers = len(set(t.buyer_id for t in self.transactions))
        unique_creators = len(set(t.seller_id for t in self.transactions if t.seller_id))

        return {
            "total_transactions": total_txs,
            "total_volume_tokens": total_volume,
            "unique_buyers": unique_buyers,
            "unique_creators": unique_creators,
            "platform_revenue": sum(
                t.metadata.get("platform_fee", 0) for t in self.transactions if t.tx_type == "purchase"
            ),
        }
