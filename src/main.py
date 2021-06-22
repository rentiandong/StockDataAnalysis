import argparse
import os

from stock_data_analysis.data_sources.IexDataSourceAdapter import IexDataSourceAdapter
from stock_data_analysis.data_sources.IexApi import IexApi
from stock_data_analysis.exceptions.TooManyRequestsException import TooManyRequestsException
from stock_data_analysis.utilities.RetryExecutor import RetryExecutor
from stock_data_analysis.symbol_filters.SymbolFilter import SymbolFilter
from stock_data_analysis.symbol_filters.QuarterlyEarningsPerShareIncrementEvaluator import QuarterlyEarningsPerShareIncrementEvaluator
from stock_data_analysis.symbol_filters.YearlyEarningsPerShareIncrementEvaluator import YearlyEarningsPerShareIncrementEvaluator

ENVIRONMENT_IEX_PUBLIC_TOKEN = os.environ.get('IEX_PUBLIC_TOKEN')

# class RetryExecutor:
#     def __init__(self, initial_backoff_seconds: int = 1):
#         self._backoff_seconds = initial_backoff_seconds
#
#     def execute_with_exponential_backoff_retry(self, task, can_retry):
#         try:
#             return task()
#         except Exception as exception:
#             if can_retry(exception):
#                 time.sleep(self._backoff_seconds)
#                 self._backoff_seconds *= 2
#                 return self.execute_with_exponential_backoff_retry(task, can_retry)
#             else:
#                 raise exception

# class QuarterlyEarningsPerShareIncrementFilter:
#     def __init__(self,
#                  data_source_adapter: IDataSourceAdapter,
#                  quarterly_earnings_per_share_increment_threshold: float = 0.25,
#                  number_of_quarters_to_check: int = 3):
#         self._iex_api_adapter = data_source_adapter
#
#         assert quarterly_earnings_per_share_increment_threshold > 0
#         self._quarterly_earnings_per_share_increment_threshold = quarterly_earnings_per_share_increment_threshold
#
#         assert number_of_quarters_to_check >= 2
#         self._number_of_quarters_to_check = number_of_quarters_to_check
#
#     def get_symbols_by_quarterly_earnings_per_share_increase(self, symbols):
#         def can_retry(exception):
#             return isinstance(exception, TooManyRequestsException) or isinstance(exception,
#                                                                                  requests.exceptions.ConnectionError)
#
#         counter = 1
#         filtered_symbols = []
#
#         for symbol in symbols:
#             # TODO: Make a better progress bar
#             print('{}/{}: {}'.format(counter, len(symbols), symbol))
#             counter += 1
#
#             quarterly_earnings_per_share = RetryExecutor().execute_with_exponential_backoff_retry(
#                 lambda: self._iex_api_adapter.get_quarterly_earnings_per_share(symbol, self._number_of_quarters_to_check
#                                                                                ), can_retry)
#
#             if len(quarterly_earnings_per_share) < self._number_of_quarters_to_check:
#                 continue
#
#             if all(previous_quarterly_earnings_per_share != 0 and
#                    (current_quarterly_earnings_per_share - previous_quarterly_earnings_per_share) /
#                    previous_quarterly_earnings_per_share > self._quarterly_earnings_per_share_increment_threshold
#                    for previous_quarterly_earnings_per_share, current_quarterly_earnings_per_share in zip(
#                        quarterly_earnings_per_share, quarterly_earnings_per_share[1:])):
#                 filtered_symbols.append(symbol)
#
#         return filtered_symbols
#
#
# class YearlyEarningsPerShareIncrementFilter:
#     def __init__(self,
#                  data_source_adapter: IDataSourceAdapter,
#                  yearly_earnings_per_share_increment_threshold: float = 0.25,
#                  number_of_years_to_check: int = 3):
#         self._iex_api_adapter = data_source_adapter
#
#         assert yearly_earnings_per_share_increment_threshold > 0
#         self._yearly_earnings_per_share_increment_threshold = yearly_earnings_per_share_increment_threshold
#
#         assert number_of_years_to_check >= 2
#         self._number_of_years_to_check = number_of_years_to_check
#
#     def get_symbols_by_yearly_earnings_per_share_increase(self, symbols: [str]):
#         def can_retry(exception):
#             return isinstance(exception, TooManyRequestsException) or isinstance(exception,
#                                                                                  requests.exceptions.ConnectionError)
#
#         counter = 1
#         filtered_symbols = []
#
#         for symbol in symbols:
#             # TODO: Make a better progress bar
#             print('{}/{}: {}'.format(counter, len(symbols), symbol))
#             counter += 1
#
#             quarterly_earnings_per_share = RetryExecutor().execute_with_exponential_backoff_retry(
#                 lambda: self._iex_api_adapter.get_quarterly_earnings_per_share(symbol, self._number_of_years_to_check),
#                 can_retry)
#
#             if len(quarterly_earnings_per_share) < self._number_of_years_to_check:
#                 continue
#
#             if all(previous_yearly_earnings_per_share != 0 and
#                    (current_yearly_earnings_per_share - previous_yearly_earnings_per_share) /
#                    previous_yearly_earnings_per_share > self._yearly_earnings_per_share_increment_threshold
#                    for previous_yearly_earnings_per_share, current_yearly_earnings_per_share in zip(
#                        quarterly_earnings_per_share, quarterly_earnings_per_share[1:])):
#                 filtered_symbols.append(symbol)
#
#         return filtered_symbols

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--public_token', type=str, nargs='?', help='public token to IEX Cloud')
    args = parser.parse_args()
    public_token = args.public_token
    if public_token is None:
        public_token = os.environ.get('IEX_PUBLIC_TOKEN')

    if public_token is None:
        raise Exception('Missing IEX public token')

    iex_api = IexApi(public_token)
    iex_api_adapter = IexDataSourceAdapter(iex_api)

    quarterly_earnings_per_share_increment_evaluator = QuarterlyEarningsPerShareIncrementEvaluator(iex_api_adapter)
    yearly_earnings_per_share_increment_evaluator = YearlyEarningsPerShareIncrementEvaluator(iex_api_adapter)
    symbol_filter = SymbolFilter(
        [yearly_earnings_per_share_increment_evaluator, quarterly_earnings_per_share_increment_evaluator])

    all_symbols = RetryExecutor().execute_with_exponential_backoff_retry(
        lambda: iex_api_adapter.get_all_symbols(), lambda exception: isinstance(exception, TooManyRequestsException))

    filtered_symbols = symbol_filter.filter(all_symbols)
    print(filtered_symbols)
