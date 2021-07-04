import json

import requests

from stock_data_analysis.exceptions.BadRequestException import BadRequestException
from . import HttpStatusCodes
from ..exceptions.TooManyRequestsException import TooManyRequestsException
from ..utilities.RetryExecutor import RetryExecutor


class AlphaVantageApi:
    DEMO_API_KEY = 'demo'
    URI = 'https://www.alphavantage.co/query?function={}&symbol={}&apikey={}'
    RATE_THROTTLED_RESPONSE = {
        "Note": "Thank you for using Alpha Vantage! Our standard API call frequency is 5 calls per minute and 500 calls "
            "per day. Please visit https://www.alphavantage.co/premium/ if you would like to target a higher API call "
            "frequency."
    }

    def __init__(self, api_key: str = DEMO_API_KEY):
        self._api_key = api_key

    def get_quarterly_and_annual_earnings_per_share(self, symbol: str) -> dict:
        def execute_api_request():
            http_response = requests.get(AlphaVantageApi.URI.format('EARNINGS', symbol, self._api_key))

            if http_response.status_code == HttpStatusCodes.BAD_REQUEST_STATUS_CODE:
                raise BadRequestException()

            json_response = json.loads(http_response.text)
            if json_response == AlphaVantageApi.RATE_THROTTLED_RESPONSE:
                # TODO add logging
                print('rate-throttle-detected')
                raise TooManyRequestsException()

            return json_response

        def can_retry(exception):
            return isinstance(exception, TooManyRequestsException)

        return RetryExecutor().execute_with_exponential_backoff_retry(execute_api_request, can_retry)