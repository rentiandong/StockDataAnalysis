import abc


class ISymbolEvaluator(abc.ABC):
    @abc.abstractmethod
    def evaluate(self, symbol: str) -> bool:
        pass
