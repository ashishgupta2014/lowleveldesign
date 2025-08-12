from abc import ABC, abstractmethod
from collections import defaultdict
import heapq


# ======================
# Observer Interfaces
# ======================

class RatingObserver(ABC):
    @abstractmethod
    def update(self, order_id, restaurant_id, food_item_id, rating):
        pass


# ======================
# Subject Interface
# ======================

class OrderRatingSubject(ABC):
    def __init__(self):
        self._observers = []

    def attach(self, observer: RatingObserver):
        self._observers.append(observer)

    def detach(self, observer: RatingObserver):
        self._observers.remove(observer)

    def notify_observers(self, order_id, restaurant_id, food_item_id, rating):
        for observer in self._observers:
            observer.update(order_id, restaurant_id, food_item_id, rating)


# ======================
# Concrete Subject
# ======================

class OrderService(OrderRatingSubject):
    def __init__(self):
        super().__init__()
        self.orders = {}  # order_id -> (restaurant_id, food_item_id)

    def order_food(self, order_id, restaurant_id, food_item_id):
        self.orders[order_id] = (restaurant_id, food_item_id)

    def rate_order(self, order_id, rating):
        if order_id not in self.orders:
            print(f"Order {order_id} not found.")
            return
        restaurant_id, food_item_id = self.orders[order_id]
        # Notify all observers
        self.notify_observers(order_id, restaurant_id, food_item_id, rating)


# ======================
# Concrete Observers
# ======================

class RestaurantRatingTracker(RatingObserver):
    def __init__(self):
        self.restaurant_ratings = defaultdict(lambda: [0, 0])  # restaurant_id -> [total_rating, count]

    def update(self, order_id, restaurant_id, food_item_id, rating):
        total, count = self.restaurant_ratings[restaurant_id]
        self.restaurant_ratings[restaurant_id] = [total + rating, count + 1]

    def get_avg_rating(self, restaurant_id):
        total, count = self.restaurant_ratings[restaurant_id]
        return total / count if count > 0 else 0


class FoodItemRatingTracker(RatingObserver):
    def __init__(self):
        self.food_item_ratings = defaultdict(lambda: [0, 0])  # (restaurant_id, food_item_id) -> [total_rating, count]

    def update(self, order_id, restaurant_id, food_item_id, rating):
        total, count = self.food_item_ratings[(restaurant_id, food_item_id)]
        self.food_item_ratings[(restaurant_id, food_item_id)] = [total + rating, count + 1]

    def get_avg_rating(self, restaurant_id, food_item_id):
        total, count = self.food_item_ratings[(restaurant_id, food_item_id)]
        return total / count if count > 0 else 0


class TopRestaurantsProvider(RatingObserver):
    def __init__(self, food_item_tracker: FoodItemRatingTracker):
        self.food_item_tracker = food_item_tracker
        self.top_cache = defaultdict(list)  # food_item_id -> sorted heap of (avg_rating, restaurant_id)

    def update(self, order_id, restaurant_id, food_item_id, rating):
        avg_rating = self.food_item_tracker.get_avg_rating(restaurant_id, food_item_id)
        # Update heap for that food item
        heap = self.top_cache[food_item_id]
        heapq.heappush(heap, (-avg_rating, restaurant_id))  # negative for max-heap behavior

    def get_top_restaurants_by_food(self, food_item_id, top_n=5):
        heap = self.top_cache.get(food_item_id, [])
        # Get top_n largest elements efficiently
        top_entries = heapq.nlargest(top_n, heap)  # O(n log k)
        result = [(rest_id, -rating) for rating, rest_id in top_entries]
        return result


# ======================
# Example Usage
# ======================

# Create service and trackers
order_service = OrderService()
restaurant_tracker = RestaurantRatingTracker()
food_item_tracker = FoodItemRatingTracker()
top_provider = TopRestaurantsProvider(food_item_tracker)

# Attach observers
order_service.attach(restaurant_tracker)
order_service.attach(food_item_tracker)
order_service.attach(top_provider)

# Simulate flow
order_service.order_food("O1", "R1", "Pizza")
order_service.order_food("O2", "R2", "Pizza")
order_service.order_food("O3", "R3", "Pizza")

order_service.rate_order("O1", 5)
order_service.rate_order("O2", 4)
order_service.rate_order("O3", 3)

# Fetch top restaurants for "Pizza"
print("Top Pizza Restaurants:", top_provider.get_top_restaurants_by_food("Pizza"))
