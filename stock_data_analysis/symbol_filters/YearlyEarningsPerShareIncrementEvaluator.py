import requests

from .ISymbolEvaluator import ISymbolEvaluator
from ..data_sources.IDataSourceAdapter import IDataSourceAdapter
from ..exceptions.TooManyRequestsException import TooManyRequestsException
from ..utilities.RetryExecutor import RetryExecutor


class YearlyEarningsPerShareIncrementEvaluator(ISymbolEvaluator):
    def __init__(self,
                 data_source_adapter: IDataSourceAdapter,
                 yearly_earnings_per_share_increment_threshold: float = 0.25,
                 number_of_years_to_check: int = 3):
        self._iex_api_adapter = data_source_adapter

        assert yearly_earnings_per_share_increment_threshold > 0
        self._quarterly_earnings_per_share_increment_threshold = yearly_earnings_per_share_increment_threshold

        assert number_of_years_to_check >= 2
        self._number_of_quarters_to_check = number_of_years_to_check

    def evaluate(self, symbol: str) -> bool:
        def can_retry(exception):
            return isinstance(exception, (TooManyRequestsException, requests.exceptions.ConnectionError))

        yearly_earnings_per_share = RetryExecutor().execute_with_exponential_backoff_retry(
            lambda: self._iex_api_adapter.get_yearly_earnings_per_share(symbol, self._number_of_quarters_to_check),
            can_retry)

        if len(yearly_earnings_per_share) < self._number_of_quarters_to_check:
            return False

        if all(previous_quarterly_earnings_per_share != 0 and
               (current_quarterly_earnings_per_share - previous_quarterly_earnings_per_share) /
               previous_quarterly_earnings_per_share > self._quarterly_earnings_per_share_increment_threshold
               for previous_quarterly_earnings_per_share, current_quarterly_earnings_per_share in zip(
                   yearly_earnings_per_share, yearly_earnings_per_share[1:])):
            return True

        return False
