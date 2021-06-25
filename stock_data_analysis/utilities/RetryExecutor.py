import time


class RetryExecutor:
    def __init__(self, initial_backoff_seconds: int = 1):
        self._backoff_seconds = initial_backoff_seconds

    def execute_with_exponential_backoff_retry(self, task, can_retry):
        try:
            return task()
        except Exception as exception:
            if can_retry(exception):
                time.sleep(self._backoff_seconds)
                self._backoff_seconds *= 2
                return self.execute_with_exponential_backoff_retry(task, can_retry)

            raise exception
