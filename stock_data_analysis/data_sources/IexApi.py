import json

import requests

from stock_data_analysis.exceptions.BadRequestException import BadRequestException
from stock_data_analysis.exceptions.TooManyRequestsException import TooManyRequestsException
from . import HttpStatusCodes


class IexApi:
    SANDBOX_URI = 'https://sandbox.iexapis.com/stable'

    def __init__(self, public_token: str):
        self._public_token = public_token

    def get_all_symbols(self):
        http_response = requests.get('{}/ref-data/symbols?token={}'.format(IexApi.SANDBOX_URI, self._public_token))

        if http_response.status_code == HttpStatusCodes.BAD_REQUEST_STATUS_CODE:
            raise BadRequestException()

        if http_response.status_code == HttpStatusCodes.TOO_MANY_REQUESTS_STATUS_CODE:
            raise TooManyRequestsException()

        return json.loads(http_response.text)

    def get_reported_financials(self, symbol: str, number_of_periods: int, period_interval: str):
        if period_interval == 'yearly':
            period_interval_parameter = '10-Q'
        elif period_interval == 'quarterly':
            period_interval_parameter = '10-K'
        else:
            raise Exception('Invalid period interval')

        http_response = requests.get('{}/time-series/REPORTED_FINANCIALS/{}/{}?token={}&last={}'.format(
            IexApi.SANDBOX_URI, symbol, period_interval_parameter, self._public_token, number_of_periods))

        if http_response.status_code == HttpStatusCodes.BAD_REQUEST_STATUS_CODE:
            raise BadRequestException()

        if http_response.status_code == HttpStatusCodes.TOO_MANY_REQUESTS_STATUS_CODE:
            raise TooManyRequestsException()

        return json.loads(http_response.text)
