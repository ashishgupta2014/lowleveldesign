import time
import requests


class CircuitBreaker:
    def __init__(self, failure_threshold=3, recovery_timeout=10):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = 'CLOSED'
        self.last_failure_time = None

    def call(self, func, *args, **kwargs):
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = 'HALF_OPEN'
            else:
                raise Exception("Circuit is OPEN")

        try:
            result = func(*args, **kwargs)
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = 'OPEN'
            raise e
        else:
            if self.state == 'HALF_OPEN':
                self.state = 'CLOSED'
                self.failure_count = 0
            return result


# Sample HTTP call wrapped in circuit breaker
def get_google():
    return requests.get("https://www.google.com", timeout=1)


breaker = CircuitBreaker()

for _ in range(10):
    try:
        res = breaker.call(get_google)
        print(res.status_code)
    except Exception as e:
        print(f"Error: {e}, State: {breaker.state}")
    time.sleep(2)
