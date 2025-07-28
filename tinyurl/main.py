import threading
import time
import string


class URLShortener:
    def __init__(self, db, persist_interval=1000):
        self.characters = string.digits + string.ascii_lowercase + string.ascii_uppercase
        self.base = len(self.characters)
        self.lock = threading.Lock()

        # Load current counter from DB
        self.db = db
        self.counter = self.db.load_counter()
        self.persist_interval = persist_interval
        self.generated_since_last_save = 0

    def encode_base62(self, number):
        """Convert integer to base62 string"""
        if number == 0:
            return self.characters[0]
        result = []
        while number > 0:
            number, remainder = divmod(number, self.base)
            result.append(self.characters[remainder])
        return ''.join(reversed(result))

    def get_next_short_url(self, long_url):
        """Generate short URL"""
        with self.lock:
            short_code = self.encode_base62(self.counter)
            self.db.store_mapping(short_code, long_url)

            self.counter += 1
            self.generated_since_last_save += 1

            # Periodically persist to DB
            if self.generated_since_last_save >= self.persist_interval:
                self.db.save_counter(self.counter)
                self.generated_since_last_save = 0

        return f"https://short.ly/{short_code}"

    def shutdown(self):
        """Save counter to DB on shutdown"""
        self.db.save_counter(self.counter)


class MockDB:
    def __init__(self):
        self.url_map = {}
        self.counter = 1000000000  # starting from 1B to keep URL length short

    def load_counter(self):
        return self.counter

    def save_counter(self, value):
        self.counter = value
        print(f"Persisted counter: {self.counter}")

    def store_mapping(self, short_code, long_url):

        self.url_map[short_code] = long_url


if __name__ == "__main__":
    db = MockDB()
    shortener = URLShortener(db)

    print(shortener.get_next_short_url("https://example.com/very-long-url-1"))
    print(shortener.get_next_short_url("https://example.com/very-long-url-2"))

    # simulate shutdown
    shortener.shutdown()
