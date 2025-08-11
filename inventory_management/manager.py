import threading
import uuid
from collections import defaultdict
from typing import Dict, Set, Optional, List

from inventory_management.model import Seller, Product, InventoryItem, Order


class SellerManager:
    def __init__(self):
        self._sellers: Dict[str, Seller] = {}
        self._lock = threading.RLock()

    def create_seller(self, seller_id: str, pincodes: Set[str], payment_modes: Set[str]) -> Seller:
        with self._lock:
            if seller_id in self._sellers:
                raise KeyError(f"Seller {seller_id} exists")
            s = Seller(seller_id, pincodes, payment_modes)
            self._sellers[seller_id] = s
            return s

    def get(self, seller_id: str) -> Optional[Seller]:
        with self._lock:
            return self._sellers.get(seller_id)

    def list_all(self) -> List[Seller]:
        with self._lock:
            return list(self._sellers.values())


class ProductManager:
    def __init__(self):
        self._products: Dict[str, Product] = {}
        self._lock = threading.RLock()

    def create_product(self, product_id: str, name: str = "") -> Product:
        with self._lock:
            if product_id in self._products:
                raise KeyError(f"Product {product_id} exists")
            p = Product(product_id, name)
            self._products[product_id] = p
            return p

    def get(self, product_id: str) -> Optional[Product]:
        with self._lock:
            return self._products.get(product_id)


class InventoryManager:
    def __init__(self):
        # top-level lock for safely inserting new nested dicts / items
        self._top_lock = threading.RLock()
        self._items: Dict[str, Dict[str, InventoryItem]] = defaultdict(dict)

    def add_inventory(self, product_id: str, seller_id: str, amount: int) -> int:
        if amount <= 0:
            raise ValueError("amount must be positive")
        with self._top_lock:
            seller_map = self._items[product_id]
            if seller_id not in seller_map:
                seller_map[seller_id] = InventoryItem(product_id, seller_id, 0)
            item = seller_map[seller_id]
        return item.add(amount)

    def get_quantity(self, product_id: str, seller_id: str) -> int:
        with self._top_lock:
            seller_map = self._items.get(product_id)
            if not seller_map:
                return 0
            item = seller_map.get(seller_id)
            if not item:
                return 0
        return item.get_quantity()

    def try_reserve(self, product_id: str, seller_id: str, amount: int) -> bool:
        with self._top_lock:
            seller_map = self._items.get(product_id)
            if not seller_map:
                return False
            item = seller_map.get(seller_id)
            if not item:
                return False
        return item.try_reserve(amount)

    def get_sellers_with_stock(self, product_id: str, min_qty: int = 1) -> List[str]:
        with self._top_lock:
            seller_map = self._items.get(product_id, {})
            # snapshot
            sellers = list(seller_map.keys())
        # check quantities without holding top lock for long
        result = []
        for sid in sellers:
            qty = self.get_quantity(product_id, sid)
            if qty >= min_qty:
                result.append(sid)
        return result


class OrderManager:
    def __init__(self, seller_mgr: SellerManager, product_mgr: ProductManager, inventory_mgr: InventoryManager):
        self.seller_mgr = seller_mgr
        self.product_mgr = product_mgr
        self.inventory_mgr = inventory_mgr
        self._orders: Dict[str, Order] = {}
        self._lock = threading.RLock()

    def _eligible_sellers(self, product_id: str, qty: int, payment_mode: str, pincode: str) -> List[str]:
        # Start from sellers who have stock
        sellers_with_stock = self.inventory_mgr.get_sellers_with_stock(product_id, min_qty=qty)
        eligible = []
        for sid in sellers_with_stock:
            seller = self.seller_mgr.get(sid)
            if not seller:
                continue
            if pincode not in seller.pincodes:
                continue
            if payment_mode not in seller.payment_modes:
                continue
            eligible.append(sid)
        return eligible

    def create_order(self, product_id: str, qty: int, payment_mode: str, pincode: str) -> Optional[Order]:
        if qty <= 0:
            raise ValueError("qty must be > 0")
        if not self.product_mgr.get(product_id):
            raise KeyError(f"Product {product_id} not found")

        eligible = self._eligible_sellers(product_id, qty, payment_mode, pincode)
        # simple strategy: pick first eligible seller (could be improved: lowest price, nearest, etc.)
        for seller_id in eligible:
            reserved = self.inventory_mgr.try_reserve(product_id, seller_id, qty)
            if reserved:
                order_id = str(uuid.uuid4())
                order = Order(order_id, product_id, seller_id, qty, payment_mode, pincode)
                with self._lock:
                    self._orders[order_id] = order
                return order
            # else another thread might have taken it — continue to next eligible seller
        # no seller could reserve
        return None

    def get_order(self, order_id: str) -> Optional[Order]:
        with self._lock:
            return self._orders.get(order_id)

