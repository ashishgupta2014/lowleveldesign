from concurrent.futures import ThreadPoolExecutor, as_completed

from inventory_management.manager import SellerManager, ProductManager, InventoryManager, OrderManager


def concurrent_demo():
    seller_mgr = SellerManager()
    product_mgr = ProductManager()
    inventory_mgr = InventoryManager()
    order_mgr = OrderManager(seller_mgr, product_mgr, inventory_mgr)

    # create sample product and sellers
    product_mgr.create_product("p1", "Toy Car")
    for i in range(3):
        sid = f"seller_{i + 1}"
        pincodes = {"560001", "560002"} if i != 2 else {"560002"}  # seller_3 only 560002
        payment_modes = {"cash", "upi"} if i != 1 else {"upi", "card"}  # seller_2 supports card+upi
        seller_mgr.create_seller(sid, pincodes, payment_modes)
        # add different inventory counts
        inventory_mgr.add_inventory("p1", sid, 10 * (i + 1))  # 10,20,30

    # simulate many concurrent orders for pincode 560001 and payment 'upi'
    requests = [{"qty": 3, "payment": "upi", "pincode": "560001"} for _ in range(15)]

    results = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = [ex.submit(lambda r: order_mgr.create_order("p1", r["qty"], r["payment"], r["pincode"]), req) for req
                   in requests]
        for fut in as_completed(futures):
            results.append(fut.result())

    success = sum(1 for r in results if r is not None)
    failed = len(results) - success

    print(f"Total requests: {len(results)}; Success: {success}; Failed: {failed}")
    # show remaining inventory per seller
    for sid in ["seller_1", "seller_2", "seller_3"]:
        print(f"{sid} remaining: {inventory_mgr.get_quantity('p1', sid)}")


if __name__ == "__main__":
    concurrent_demo()
