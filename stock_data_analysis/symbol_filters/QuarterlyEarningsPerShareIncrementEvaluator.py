import math

from .ISymbolEvaluator import ISymbolEvaluator
from ..data_sources.IDataSourceAdapter import IDataSourceAdapter
from ..utilities.Logger import Logger

QUARTERS_IN_A_YEAR = 4


class QuarterlyEarningsPerShareIncrementEvaluator(ISymbolEvaluator):
    def __init__(self,
                 data_source_adapter: IDataSourceAdapter,
                 quarterly_earnings_per_share_increment_threshold: float = 0.25,
                 number_of_quarters_to_check: int = 3):
        self._data_source_adapter = data_source_adapter

        assert quarterly_earnings_per_share_increment_threshold > 0
        self._quarterly_earnings_per_share_increment_threshold = quarterly_earnings_per_share_increment_threshold

        assert number_of_quarters_to_check >= 2
        self._number_of_quarters_to_check = number_of_quarters_to_check

        # need to check same quarter of previous year
        self._number_of_quarters_needed = math.ceil(self._number_of_quarters_to_check / QUARTERS_IN_A_YEAR
                                                    ) * QUARTERS_IN_A_YEAR + self._number_of_quarters_to_check

        self._logger = Logger(self.__class__.__name__)

    def __str__(self):
        return '{}[data_source_adapter={}, threshold={}, number_of_quarters_to_check={}]'.format(
            self.__name__, self._data_source_adapter.__name__, self._quarterly_earnings_per_share_increment_threshold,
            self._number_of_quarters_to_check)

    def evaluate(self, symbol: str) -> bool:
        quarterly_earnings_per_share = self._data_source_adapter.get_quarterly_earnings_per_share(
            symbol, self._number_of_quarters_needed)

        if len(quarterly_earnings_per_share) < self._number_of_quarters_needed:
            self._logger.log_info('{} disapproved symbol {} with only {} quarter earnings per share data points'.format(
                str(self), symbol, len(quarterly_earnings_per_share)))
            return False

        for i in range(0, self._number_of_quarters_to_check):
            current = quarterly_earnings_per_share[-1 - i]
            previous = quarterly_earnings_per_share[-1 - i - QUARTERS_IN_A_YEAR]

            if previous == 0:
                self._logger.log_info('{} disapproved symbol {} with 0 earnings per share in history'.format(
                    str(self), symbol))
                return False

            if (current - previous) / previous < self._quarterly_earnings_per_share_increment_threshold:
                self._logger.log_info(
                    '{} disapproved symbol {} with earnings per share growth ({} - {}) / {} = {} less than threshold'.
                    format(str(self), symbol, current, previous, previous, (current - previous) / previous))
                return False

        self._logger.log_info('{} disapproved symbol {}'.format(str(self), symbol))
        return True
