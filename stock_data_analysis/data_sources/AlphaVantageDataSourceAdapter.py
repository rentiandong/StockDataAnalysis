from .IDataSourceAdapter import IDataSourceAdapter
from ..exceptions.NotSupportedByApiException import NotSupportedByApiException
from .AlphaVantageApi import AlphaVantageApi


class AlphaVantageDataSourceAdapter(IDataSourceAdapter):
    def __init__(self, alpha_vantage_api: AlphaVantageApi):
        self._alpha_vantage_api = alpha_vantage_api

    def get_all_symbols(self):
        raise NotSupportedByApiException()

    def get_quarterly_earnings_per_share(self, symbol: str, number_of_quarters: int) -> [float]:
        quarterly_and_yearly_earnings_per_share = self._alpha_vantage_api.get_quarterly_and_annual_earnings_per_share(
            symbol)

        return [
            float(i['reportedEPS']) for i in quarterly_and_yearly_earnings_per_share['quarterlyEarnings'][-number_of_quarters:]
        ]

    def get_yearly_earnings_per_share(self, symbol: str, number_of_years: int) -> [float]:
        quarterly_and_yearly_earnings_per_share = self._alpha_vantage_api.get_quarterly_and_annual_earnings_per_share(
            symbol)

        if not len(quarterly_and_yearly_earnings_per_share):
            return []

        return [float(i['reportedEPS']) for i in quarterly_and_yearly_earnings_per_share['annualEarnings'][-number_of_years:]]
