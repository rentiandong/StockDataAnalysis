from . import AlphaVantageApi
from ..data_sources import IDataSourceAdapter
from ..exceptions import NotSupportedByApiException
from ..utilities import Logger


class AlphaVantageDataSourceAdapter(IDataSourceAdapter):
    def __init__(self, alpha_vantage_api: AlphaVantageApi):
        self._alpha_vantage_api = alpha_vantage_api
        self._logger = Logger(str(self))

    def __str__(self):
        return self.__class__.__name__

    def get_all_symbols(self):
        raise NotSupportedByApiException()

    def get_quarterly_earnings_per_share(self, symbol: str, number_of_quarters: int) -> [float]:
        quarterly_and_yearly_earnings_per_share = self._alpha_vantage_api.get_quarterly_and_annual_earnings_per_share(
            symbol)

        if not quarterly_and_yearly_earnings_per_share:
            self._logger.log_info('{} obtained empty quarterly and yearly earnings response for symbol {}'.format(
                str(self), symbol))
            return []

        if 'quarterlyEarnings' not in quarterly_and_yearly_earnings_per_share:
            self._logger.log_info('{} quarterly earnings not present in API response'.format(str(self)))
            return []

        return [
            float(i['reportedEPS'])
            for i in quarterly_and_yearly_earnings_per_share['quarterlyEarnings'][-number_of_quarters:]
        ]

    def get_yearly_earnings_per_share(self, symbol: str, number_of_years: int) -> [float]:
        quarterly_and_yearly_earnings_per_share = self._alpha_vantage_api.get_quarterly_and_annual_earnings_per_share(
            symbol)

        if not quarterly_and_yearly_earnings_per_share:
            self._logger.log_info('{} obtained empty quarterly and yearly earnings response for symbol {}'.format(
                str(self), symbol))
            return []

        if 'annualEarnings' not in quarterly_and_yearly_earnings_per_share:
            self._logger.log_info('{} yearly earnings not present in API response'.format(str(self)))
            return []

        return [
            float(i['reportedEPS'])
            for i in quarterly_and_yearly_earnings_per_share['annualEarnings'][-number_of_years:]
        ]
