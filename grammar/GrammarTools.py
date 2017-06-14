from enum import Enum
from typing import List


class SymbolType(Enum):
    UNKOWN=-1
    TERMINAL=0
    VARIABLE=1

class Symbol:
    def __init__(self, name: str, type: SymbolType):
        self.name = name
        self.type = type

    def __str__(self):
        return self.name

class Var(Symbol):
    def __init__(self, name: str):
        super().__init__(name=name, type=SymbolType.VARIABLE)

class Term(Symbol):
    def __init__(self, name: str):
        super().__init__(name=name, type=SymbolType.TERMINAL)

class Production:
    def __init__(self, lft, r_symbols: List[Symbol]):
        if isinstance(lft, Var):
            lft = lft.name
        elif not isinstance(lft, str):
            raise TypeError("Production lft must be a string or a Var class instance.")
        self.l_var = lft
        self.r_symbols = r_symbols

    def __str__(self):
        rgt_str = ""
        for s in self.r_symbols:
            rgt_str += s.name
        return "{} --> {}".format(self.l_var, rgt_str)




