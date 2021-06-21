import requests
import json
import time
import argparse
import os

ENVIRONMENT_IEX_PUBLIC_TOKEN = os.environ.get('IEX_PUBLIC_TOKEN')
TOO_MANY_REQUESTS_STATUS_CODE = 429
BAD_REQUEST_STATUS_CODE = 400


class TooManyRequestsException(Exception):
    pass


class BadRequestException(Exception):
    pass


class IexApi:
    SANDBOX_URI = 'https://sandbox.iexapis.com/stable'

    def __init__(self, public_token: str):
        self._public_token = public_token

    def get_all_symbols(self):
        http_response = requests.get('{}/ref-data/symbols?token={}'.format(IexApi.SANDBOX_URI, self._public_token))

        if http_response.status_code == BAD_REQUEST_STATUS_CODE:
            raise BadRequestException()

        if http_response.status_code == TOO_MANY_REQUESTS_STATUS_CODE:
            raise TooManyRequestsException()

        return json.loads(http_response.text)

    def get_reported_financials(self, symbol: str, period_length: int):
        http_response = requests.get('{}/time-series/REPORTED_FINANCIALS/{}/10-Q?token={}&last={}'.format(
            IexApi.SANDBOX_URI, symbol, self._public_token, period_length))

        if http_response.status_code == BAD_REQUEST_STATUS_CODE:
            raise BadRequestException()

        if http_response.status_code == TOO_MANY_REQUESTS_STATUS_CODE:
            raise TooManyRequestsException()

        return json.loads(http_response.text)


class IexApiAdapter:
    def __init__(self, iex_api: IexApi):
        self._iex_api = iex_api

    def get_all_symbols(self):
        try:
            return [i['symbol'] for i in self._iex_api.get_all_symbols()]
        except BadRequestException:
            return []

    def get_quarterly_earnings_per_share(self, symbol: str, period_length: int):
        try:
            reported_financials = self._iex_api.get_reported_financials(symbol, period_length)
        except BadRequestException:
            return []

        earnings_per_share = []

        for report in reported_financials:
            if 'EarningsPerShareDiluted' not in report:
                return []

            earnings_per_share.append(report['EarningsPerShareDiluted'])

        return earnings_per_share


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
            else:
                raise exception


class QuarterlyEarningsPerShareIncrementFilter:
    def __init__(self,
                 iex_api_adapter: IexApiAdapter,
                 quarterly_earnings_per_share_increment_threshold: float = 0.25,
                 number_of_quarters_to_check: int = 3):
        self._iex_api_adapter = iex_api_adapter

        assert quarterly_earnings_per_share_increment_threshold > 0
        self._quarterly_earnings_per_share_increment_threshold = quarterly_earnings_per_share_increment_threshold

        assert number_of_quarters_to_check >= 2
        self._number_of_quarters_to_check = number_of_quarters_to_check

    def get_symbols_by_quarterly_earnings_per_share_increase(self, symbols):
        def can_retry(exception):
            return isinstance(exception, TooManyRequestsException) or isinstance(exception,
                                                                                 requests.exceptions.ConnectionError)

        counter = 1
        filtered_symbols = []

        for symbol in symbols:
            # TODO: Make a better progress bar
            print('{}/{}: {}'.format(counter, len(symbols), symbol))
            counter += 1

            quarterly_earnings_per_share = RetryExecutor().execute_with_exponential_backoff_retry(
                lambda: self._iex_api_adapter.get_quarterly_earnings_per_share(symbol, self._number_of_quarters_to_check
                                                                               ), can_retry)

            if len(quarterly_earnings_per_share) < self._number_of_quarters_to_check:
                continue

            if all(previous_quarterly_earnings_per_share != 0 and
                   (current_quarterly_earnings_per_share - previous_quarterly_earnings_per_share) /
                   previous_quarterly_earnings_per_share > self._quarterly_earnings_per_share_increment_threshold
                   for previous_quarterly_earnings_per_share, current_quarterly_earnings_per_share in zip(
                       quarterly_earnings_per_share, quarterly_earnings_per_share[1:])):
                filtered_symbols.append(symbol)

        return filtered_symbols


class YearlyEarningsPerShareIncrementFilter:
    def __init__(self,
                 iex_api_adapter: IexApiAdapter,
                 yearly_earnings_per_share_increment_threshold: float = 0.25,
                 number_of_years_to_check: int = 3):
        self._iex_api_adapter = iex_api_adapter

        assert yearly_earnings_per_share_increment_threshold > 0
        self._yearly_earnings_per_share_increment_threshold = yearly_earnings_per_share_increment_threshold

        assert number_of_years_to_check >= 2
        self._number_of_years_to_check = number_of_years_to_check

    def get_symbols_by_yearly_earnings_per_share_increase(self, symbols: [str]):
        def can_retry(exception):
            return isinstance(exception, TooManyRequestsException) or isinstance(exception,
                                                                                 requests.exceptions.ConnectionError)

        counter = 1
        filtered_symbols = []

        for symbol in symbols:
            # TODO: Make a better progress bar
            print('{}/{}: {}'.format(counter, len(symbols), symbol))
            counter += 1

            quarterly_earnings_per_share = RetryExecutor().execute_with_exponential_backoff_retry(
                lambda: self._iex_api_adapter.get_quarterly_earnings_per_share(symbol, self._number_of_years_to_check),
                can_retry)

            if len(quarterly_earnings_per_share) < self._number_of_years_to_check:
                continue

            if all(previous_yearly_earnings_per_share != 0 and
                   (current_yearly_earnings_per_share - previous_yearly_earnings_per_share) /
                   previous_yearly_earnings_per_share > self._yearly_earnings_per_share_increment_threshold
                   for previous_yearly_earnings_per_share, current_yearly_earnings_per_share in zip(
                       quarterly_earnings_per_share, quarterly_earnings_per_share[1:])):
                filtered_symbols.append(symbol)

        return filtered_symbols


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
    iex_api_adapter = IexApiAdapter(iex_api)

    all_symbols = RetryExecutor().execute_with_exponential_backoff_retry(
        lambda: iex_api_adapter.get_all_symbols(), lambda exception: isinstance(exception, TooManyRequestsException))

    quarterly_earnings_per_share_increment_filter = QuarterlyEarningsPerShareIncrementFilter(iex_api_adapter)
    symbols_filtered_by_quarterly_earnings_per_share_increment = quarterly_earnings_per_share_increment_filter.get_symbols_by_quarterly_earnings_per_share_increase(
        all_symbols)

    yearly_earnings_per_share_increment_filter = YearlyEarningsPerShareIncrementFilter(iex_api_adapter)
    symbols_filtered_by_yearly_earnings_per_share_increment = yearly_earnings_per_share_increment_filter.get_symbols_by_yearly_earnings_per_share_increase(
        symbols_filtered_by_quarterly_earnings_per_share_increment)

    print(symbols_filtered_by_yearly_earnings_per_share_increment)
