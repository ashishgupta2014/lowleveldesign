import time
import random
import logging


# Custom exception types
class TransientError(Exception):
    pass


class FatalError(Exception):
    pass


# RetryHandler with exponential backoff
class RetryHandler:
    def __init__(self, max_attempts=3, initial_delay=1, backoff_factor=2):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.backoff_factor = backoff_factor

    def call(self, func, *args, **kwargs):
        attempt = 0
        delay = self.initial_delay

        while attempt < self.max_attempts:
            try:
                return func(*args, **kwargs)
            except TransientError as e:
                logging.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                attempt += 1
                if attempt >= self.max_attempts:
                    logging.error("Max attempts reached. Giving up.")
                    raise
                time.sleep(delay)
                delay *= self.backoff_factor
            except FatalError:
                logging.error("Fatal error encountered. No retries.")
                raise


# Simulated external service
class ExternalAPI:
    def unstable_call(self):
        result = random.choice(["success", "transient", "fatal"])
        if result == "success":
            return "Data loaded"
        elif result == "transient":
            raise TransientError("Temporary failure")
        else:
            raise FatalError("Critical issue")


# Client usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    api = ExternalAPI()
    retry_handler = RetryHandler(max_attempts=5, initial_delay=1)

    try:
        data = retry_handler.call(api.unstable_call)
        print("API call succeeded:", data)
    except Exception as e:
        print("API call failed:", str(e))
