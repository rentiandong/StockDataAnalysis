import unittest

from unittest import mock
from ..context import stock_data_analysis


class QuarterlyEarningsPerShareIncrementEvaluatorTest(unittest.TestCase):
    def test_evaluate_should_return_true_with_increments_above_threshold(self):
        stub_data_source_adapter = mock.Mock(stock_data_analysis.data_sources.IDataSourceAdapter)
        stub_data_source_adapter.get_quarterly_earnings_per_share = mock.Mock(return_value=[1, 2, 3, 4, 5, 6, 7])

        quarterly_earnings_per_share_increment_evaluator = stock_data_analysis.symbol_filters.QuarterlyEarningsPerShareIncrementEvaluator(
            stub_data_source_adapter)
        self.assertTrue(quarterly_earnings_per_share_increment_evaluator.evaluate('APPL'))

    def test_evaluate_should_return_false_with_increments_below_threshold(self):
        stub_data_source_adapter = mock.Mock(stock_data_analysis.data_sources.IDataSourceAdapter)
        stub_data_source_adapter.get_quarterly_earnings_per_share = mock.Mock(return_value=[5, 6, 7, 4, 5, 6, 7])

        quarterly_earnings_per_share_increment_evaluator = stock_data_analysis.symbol_filters.QuarterlyEarningsPerShareIncrementEvaluator(
            stub_data_source_adapter)
        self.assertFalse(quarterly_earnings_per_share_increment_evaluator.evaluate('APPL'))


if __name__ == '__main__':
    unittest.main()
