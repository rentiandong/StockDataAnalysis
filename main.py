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
