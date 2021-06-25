from .ISymbolEvaluator import ISymbolEvaluator


class SymbolFilter:
    def __init__(self, initial_filters: [ISymbolEvaluator]):
        self._symbol_evaluators = initial_filters

    def add_evaluator(self, evaluator: ISymbolEvaluator) -> None:
        self._symbol_evaluators.append(evaluator)

    def filter(self, symbols: list[str]) -> list[str]:  # pylint: disable=unsubscriptable-object
        filtered_symbols = []

        for symbol in symbols:
            for evaluator in self._symbol_evaluators:
                if not evaluator.evaluate(symbol):
                    continue

            filtered_symbols.append(symbol)

        return filtered_symbols
