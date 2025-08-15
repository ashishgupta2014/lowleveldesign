import threading

class HitCounter:
    def __init__(self):
        self.counts = []
        self.locks = []  # One lock per page

    def init(self, total_pages: int):
        self.counts = [0] * total_pages
        self.locks = [threading.Lock() for _ in range(total_pages)]

    def increment_visit_count(self, page_index: int):
        # Lock only for the specific page
        with self.locks[page_index]:
            self.counts[page_index] += 1

    def get_visit_count(self, page_index: int) -> int:
        # Lock only for the specific page
        with self.locks[page_index]:
            return self.counts[page_index]


# Example usage
if __name__ == "__main__":
    counter = HitCounter()
    counter.init(2)

    counter.increment_visit_count(0)
    counter.increment_visit_count(1)
    counter.increment_visit_count(1)
    counter.increment_visit_count(1)
    counter.increment_visit_count(0)

    print(counter.get_visit_count(0))  # 2
    print(counter.get_visit_count(1))  # 3
