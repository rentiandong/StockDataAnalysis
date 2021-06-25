from . import IDataSourceAdapter
from ..exceptions.BadRequestException import BadRequestException
from . import IexApi


class IexDataSourceAdapter(IDataSourceAdapter):
    def __init__(self, iex_api: IexApi):
        self._iex_api = iex_api

    def get_all_symbols(self):
        try:
            return [i['symbol'] for i in self._iex_api.get_all_symbols()]
        except BadRequestException:
            return []

    def get_quarterly_earnings_per_share(self, symbol: str, number_of_quarters: int) -> [float]:
        try:
            reported_financials = self._iex_api.get_reported_financials(symbol, number_of_quarters, 'quarterly')
        except BadRequestException:
            return []

        earnings_per_share = []

        for report in reported_financials:
            if 'EarningsPerShareDiluted' not in report:
                return []

            earnings_per_share.append(report['EarningsPerShareDiluted'])

        return earnings_per_share

    def get_yearly_earnings_per_share(self, symbol: str, number_of_years: int) -> [float]:
        try:
            reported_financials = self._iex_api.get_reported_financials(symbol, number_of_years, 'yearly')
        except BadRequestException:
            return []

        earnings_per_share = []

        for report in reported_financials:
            if 'EarningsPerShareDiluted' not in report:
                return []

            earnings_per_share.append(report['EarningsPerShareDiluted'])

        return earnings_per_share
