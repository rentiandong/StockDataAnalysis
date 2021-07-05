import requests

from . import RetryExecutor


class HttpRequestHandler:
    @staticmethod
    def get(url: str):
        return RetryExecutor().execute_with_exponential_backoff_retry(
            lambda: requests.get(url), lambda exception: isinstance(exception, requests.exceptions.ConnectionError))
