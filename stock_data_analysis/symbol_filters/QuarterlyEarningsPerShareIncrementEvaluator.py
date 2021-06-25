import requests
import math

from .ISymbolEvaluator import ISymbolEvaluator
from ..data_sources.IDataSourceAdapter import IDataSourceAdapter
from ..exceptions.TooManyRequestsException import TooManyRequestsException
from ..utilities.RetryExecutor import RetryExecutor

QUARTERS_IN_A_YEAR = 4


class QuarterlyEarningsPerShareIncrementEvaluator(ISymbolEvaluator):
    def __init__(self,
                 data_source_adapter: IDataSourceAdapter,
                 quarterly_earnings_per_share_increment_threshold: float = 0.25,
                 number_of_quarters_to_check: int = 3):
        self._iex_api_adapter = data_source_adapter

        assert quarterly_earnings_per_share_increment_threshold > 0
        self._quarterly_earnings_per_share_increment_threshold = quarterly_earnings_per_share_increment_threshold

        assert number_of_quarters_to_check >= 2
        self._number_of_quarters_to_check = number_of_quarters_to_check

        # need to check same quarter of previous year
        self._number_of_quarters_needed = math.ceil(self._number_of_quarters_to_check / QUARTERS_IN_A_YEAR
                                                    ) * QUARTERS_IN_A_YEAR + self._number_of_quarters_to_check

    def evaluate(self, symbol: str) -> bool:
        def can_retry(exception):
            return isinstance(exception, TooManyRequestsException) or isinstance(exception,
                                                                                 requests.exceptions.ConnectionError)

        quarterly_earnings_per_share = RetryExecutor().execute_with_exponential_backoff_retry(
            lambda: self._iex_api_adapter.get_quarterly_earnings_per_share(symbol, self._number_of_quarters_needed),
            can_retry)

        if len(quarterly_earnings_per_share) < self._number_of_quarters_needed:
            return False

        for i in range(0, self._number_of_quarters_to_check):
            current = quarterly_earnings_per_share[-1 - i]
            previous = quarterly_earnings_per_share[-1 - i - QUARTERS_IN_A_YEAR]

            if previous == 0:
                return False

            if (current - previous) / previous < self._quarterly_earnings_per_share_increment_threshold:
                return False

        return True
