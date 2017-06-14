import copy
import itertools
from enum import Enum
from typing import List, Dict
from .GrammarBuilder import GrammarBuilder, CnfGrammarBuilder






class Grammar:
    def __init__(self, grammar_builder: GrammarBuilder):
        if isinstance(grammar_builder, GrammarBuilder):
            if grammar_builder._built == False:
                raise RuntimeError("In order to create a Grammar instance you have to call build() method over a "
                                   "GrammarBuilder instance. You don't want to use the Grammar constructor.")
            self.variables = grammar_builder._variables[:]  # type: List[str]
            self.terminals = grammar_builder._built_terminals[:] # type: List[str]
            self.productions = grammar_builder._productions[:]  # type: List[Production]
            self.aggr_productions_dict = copy.deepcopy(grammar_builder._aggr_productions_dict)
            self.start_symbol = grammar_builder._start_symbol
        else:
            raise TypeError("Grammar must be created using a GrammarBuilder")

    def get_symbols_list(self):
        ls = []
        for var in self.variables:
            ls.append(Var(var))
        for ter in self.terminals:
            ls.append((Term(ter)))
        return ls

class CnfGrammar(Grammar):
    def __init__(self, grammar_builder: CnfGrammarBuilder):
        super().__init__(grammar_builder)
        if not isinstance(grammar_builder, CnfGrammarBuilder):
            raise TypeError("CnfGrammar must be created using a CnfGrammarBuilder")










