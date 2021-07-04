from .ISymbolEvaluator import ISymbolEvaluator
from ..data_sources.IDataSourceAdapter import IDataSourceAdapter
from ..utilities.Logger import Logger


class YearlyEarningsPerShareIncrementEvaluator(ISymbolEvaluator):
    def __init__(self,
                 data_source_adapter: IDataSourceAdapter,
                 yearly_earnings_per_share_increment_threshold: float = 0.25,
                 number_of_years_to_check: int = 3):
        self._data_source_adapter = data_source_adapter

        assert yearly_earnings_per_share_increment_threshold > 0
        self._quarterly_earnings_per_share_increment_threshold = yearly_earnings_per_share_increment_threshold

        assert number_of_years_to_check >= 2
        self._number_of_quarters_to_check = number_of_years_to_check

        self._logger = Logger(self.__class__.__name__)

    def __str__(self):
        return '{}[data_source_adapter={}, threshold={}, number_of_quarters_to_check={}]'.format(
            self.__class__.__name__, str(self._data_source_adapter),
            self._quarterly_earnings_per_share_increment_threshold, self._number_of_quarters_to_check)

    def evaluate(self, symbol: str) -> bool:
        yearly_earnings_per_share = self._data_source_adapter.get_yearly_earnings_per_share(
            symbol, self._number_of_quarters_to_check)

        if len(yearly_earnings_per_share) < self._number_of_quarters_to_check:
            self._logger.log_info('{} disapproved symbol {} with only {} yearly earnings per share data points'.format(
                str(self), symbol, len(yearly_earnings_per_share)))
            return False

        evaluation_result = all(
            previous_quarterly_earnings_per_share != 0 and
            (current_quarterly_earnings_per_share - previous_quarterly_earnings_per_share) /
            previous_quarterly_earnings_per_share > self._quarterly_earnings_per_share_increment_threshold
            for previous_quarterly_earnings_per_share, current_quarterly_earnings_per_share in zip(
                yearly_earnings_per_share, yearly_earnings_per_share[1:]))

        self._logger.log_info('{} symbol {} with yearly earnings per share history {} evaluated to {}'.format(
            str(self), symbol, yearly_earnings_per_share, evaluation_result))
        return evaluation_result
