# ---------- Domain Entities ----------
import threading
from typing import Set


class Seller:
    def __init__(self, seller_id: str, pincodes: Set[str], payment_modes: Set[str]):
        self.seller_id = seller_id
        self.pincodes = set(pincodes)
        self.payment_modes = set(payment_modes)


class Product:
    def __init__(self, product_id: str, name: str = ""):
        self.product_id = product_id
        self.name = name


class Order:
    def __init__(self, order_id: str, product_id: str, seller_id: str, qty: int, payment_mode: str, pincode: str):
        self.order_id = order_id
        self.product_id = product_id
        self.seller_id = seller_id
        self.qty = qty
        self.payment_mode = payment_mode
        self.pincode = pincode


# ---------- Inventory Item (per seller-product) ----------

class InventoryItem:
    def __init__(self, product_id: str, seller_id: str, initial_qty: int = 0):
        self.product_id = product_id
        self.seller_id = seller_id
        self._qty = int(initial_qty)
        self._lock = threading.Lock()

    def add(self, amount: int) -> int:
        if amount < 0:
            raise ValueError("amount must be non-negative")
        with self._lock:
            self._qty += amount
            return self._qty

    def get_quantity(self) -> int:
        with self._lock:
            return self._qty

    def try_reserve(self, amount: int) -> bool:
        """Atomically check and reduce inventory by amount if available.
           Returns True if reserved (reduced), False otherwise."""
        if amount <= 0:
            raise ValueError("amount must be positive")
        with self._lock:
            if self._qty >= amount:
                self._qty -= amount
                return True
            return False
