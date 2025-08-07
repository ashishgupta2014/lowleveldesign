import time
from abc import ABC, abstractmethod
from collections import defaultdict, deque


class RateLimiterStrategy(ABC):
    @abstractmethod
    def allow_request(self, user_id: str) -> bool:
        pass


class FixedWindowRateLimiter(RateLimiterStrategy):
    def __init__(self, max_requests: int, window_size_sec: int):
        self.max_requests = max_requests
        self.window_size_sec = window_size_sec
        self.storage = defaultdict(lambda: [0, int(time.time())])  # [count, window_start]

    def allow_request(self, user_id: str) -> bool:
        count, window_start = self.storage[user_id]
        now = int(time.time())

        if now - window_start >= self.window_size_sec:
            self.storage[user_id] = [1, now]
            return True
        elif count < self.max_requests:
            self.storage[user_id][0] += 1
            return True
        return False


class SlidingWindowRateLimiter(RateLimiterStrategy):
    def __init__(self, max_requests: int, window_size_sec: int):
        self.max_requests = max_requests
        self.window_size_sec = window_size_sec
        self.storage = defaultdict(deque)

    def allow_request(self, user_id: str) -> bool:
        now = time.time()
        q = self.storage[user_id]

        while q and now - q[0] > self.window_size_sec:
            q.popleft()

        if len(q) < self.max_requests:
            q.append(now)
            return True
        return False


class TokenBucketRateLimiter(RateLimiterStrategy):
    def __init__(self, rate: float, capacity: int):
        self.rate = rate  # tokens per second
        self.capacity = capacity
        self.storage = defaultdict(lambda: [capacity, time.time()])  # [tokens, last_checked]

    def allow_request(self, user_id: str) -> bool:
        tokens, last_checked = self.storage[user_id]
        now = time.time()
        elapsed = now - last_checked
        new_tokens = min(self.capacity, tokens + elapsed * self.rate)

        if new_tokens >= 1:
            self.storage[user_id] = [new_tokens - 1, now]
            return True
        else:
            self.storage[user_id] = [new_tokens, now]
            return False


class LeakyBucketRateLimiter(RateLimiterStrategy):
    def __init__(self, rate: float, capacity: int):
        self.rate = rate  # leak rate: requests per second
        self.capacity = capacity
        self.storage = defaultdict(lambda: {"water": 0.0, "last_checked": time.time()})

    def allow_request(self, user_id: str) -> bool:
        bucket = self.storage[user_id]
        now = time.time()
        leaked = (now - bucket["last_checked"]) * self.rate
        bucket["water"] = max(0.0, bucket["water"] - leaked)
        bucket["last_checked"] = now

        if bucket["water"] + 1 <= self.capacity:
            bucket["water"] += 1
            return True
        return False


class RateLimiter:
    def __init__(self, strategy: RateLimiterStrategy):
        self.strategy = strategy

    def set_strategy(self, strategy: RateLimiterStrategy):
        self.strategy = strategy

    def allow_request(self, user_id: str) -> bool:
        return self.strategy.allow_request(user_id)


class RateLimiterObserver:
    def notify(self, user_id: str, allowed: bool):
        print(f"[OBSERVE] User: {user_id}, Allowed: {allowed}")


def test_rate_limiter(name, limiter: RateLimiter, user_id: str = "user1", interval=0.5, total=10):
    print(f"\n=== Testing {name} ===")
    observer = RateLimiterObserver()
    for i in range(total):
        allowed = limiter.allow_request(user_id)
        observer.notify(user_id, allowed)
        time.sleep(interval)


if __name__ == "__main__":
    user = "test-user"

    strategies = {
        "Fixed Window": FixedWindowRateLimiter(max_requests=5, window_size_sec=5),
        "Sliding Window": SlidingWindowRateLimiter(max_requests=5, window_size_sec=5),
        "Token Bucket": TokenBucketRateLimiter(rate=1, capacity=5),
        "Leaky Bucket": LeakyBucketRateLimiter(rate=1, capacity=5),
    }

    for name, strategy in strategies.items():
        limiter = RateLimiter(strategy)
        test_rate_limiter(name, limiter, user_id=user)
