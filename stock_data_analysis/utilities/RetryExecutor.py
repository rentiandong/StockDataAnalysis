import time
from .Logger import Logger


class RetryExecutor:
    def __init__(self, initial_backoff_seconds: int = 1, max_retries: int = 5):
        self._backoff_seconds = initial_backoff_seconds
        self._remaining_retries = max_retries
        self._logger = Logger(self.__class__.__name__)

    def execute_with_exponential_backoff_retry(self, task, can_retry):
        try:
            return task()
        except Exception as exception:
            if not can_retry(exception) or not self._remaining_retries:
                self._logger.log_info('Unable to retry {}'.format(task))
                raise exception

            time.sleep(self._backoff_seconds)
            self._backoff_seconds *= 2
            self._remaining_retries -= 1

            self._logger.log_info('retrying {} with {} seconds backoff'.format(task, self._backoff_seconds))
            return self.execute_with_exponential_backoff_retry(task, can_retry)
