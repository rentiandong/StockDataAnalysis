import abc


class IDataSourceAdapter(abc.ABC):
    @abc.abstractmethod
    def get_all_symbols(self) -> [str]:
        pass

    @abc.abstractmethod
    def get_quarterly_earnings_per_share(self, symbol: str, number_of_quarters: int) -> [float]:
        pass

    @abc.abstractmethod
    def get_yearly_earnings_per_share(self, symbol: str, number_of_years: int) -> [float]:
        pass
