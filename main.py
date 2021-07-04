import argparse
import os
import sys

from stock_data_analysis.data_sources.IexDataSourceAdapter import IexDataSourceAdapter
from stock_data_analysis.data_sources.IexApi import IexApi
from stock_data_analysis.data_sources.AlphaVantageDataSourceAdapter import AlphaVantageDataSourceAdapter
from stock_data_analysis.data_sources.AlphaVantageApi import AlphaVantageApi
from stock_data_analysis.exceptions.TooManyRequestsException import TooManyRequestsException
from stock_data_analysis.utilities.RetryExecutor import RetryExecutor
from stock_data_analysis.symbol_filters.SymbolFilter import SymbolFilter
from stock_data_analysis.symbol_filters.QuarterlyEarningsPerShareIncrementEvaluator import QuarterlyEarningsPerShareIncrementEvaluator
from stock_data_analysis.symbol_filters.YearlyEarningsPerShareIncrementEvaluator import YearlyEarningsPerShareIncrementEvaluator
from stock_data_analysis.utilities.Logger import Logger

if __name__ == "__main__":
    logger = Logger('root')
    logger.log_info('running with command line arguments ' + str(sys.argv))

    parser = argparse.ArgumentParser()
    parser.add_argument('--iex-public-token', type=str, nargs='?', help='public token to IEX Cloud')
    parser.add_argument('--alpha-vantage-token', type=str, nargs='?', help='API token of Alpha Vantage')
    args = parser.parse_args()

    iex_public_token = args.iex_public_token if args.iex_public_token else os.environ.get('IEX_PUBLIC_TOKEN')
    alpha_vantage_token = args.alpha_vantage_token if args.alpha_vantage_token else os.environ.get('ALPHA_VANTAGE_TOKEN')

    if iex_public_token is None:
        raise Exception('Missing IEX public token')

    if alpha_vantage_token is None:
        raise Exception('Missing Alpha Vantage token')

    iex_api = IexApi(iex_public_token)
    iex_api_adapter = IexDataSourceAdapter(iex_api)

    alpha_vantage_api = AlphaVantageApi(alpha_vantage_token)
    alpha_vantage_api_adapter = AlphaVantageDataSourceAdapter(alpha_vantage_api)

    quarterly_earnings_per_share_increment_evaluator = QuarterlyEarningsPerShareIncrementEvaluator(alpha_vantage_api_adapter)
    yearly_earnings_per_share_increment_evaluator = YearlyEarningsPerShareIncrementEvaluator(alpha_vantage_api_adapter)
    symbol_filter = SymbolFilter(
        [yearly_earnings_per_share_increment_evaluator, quarterly_earnings_per_share_increment_evaluator])

    all_symbols = RetryExecutor().execute_with_exponential_backoff_retry(
        lambda: iex_api_adapter.get_all_symbols(), lambda exception: isinstance(exception, TooManyRequestsException))

    logger.log_info('retrieved [{}] symbols'.format(len(all_symbols)))
    for symbol in all_symbols:
        logger.log_info('processing symbol {}'.format(symbol))

        if symbol_filter.filter(symbol):
            # TODO write info to file
            print(symbol)
