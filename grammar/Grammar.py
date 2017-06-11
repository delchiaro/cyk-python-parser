import copy
import itertools
from enum import Enum
from typing import List, Dict


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
    def __init__(self, lft_var, rgt_symbols: List[Symbol]):
        if isinstance(lft_var, Var):
            lft_var = lft_var.name
        elif not isinstance(lft_var, str):
            raise TypeError("Production lft_var must be a string or a Var class instance.")
        self.lft_var = lft_var
        self.rgt_symbols = rgt_symbols

    def __str__(self):
        rgt_str = ""
        for s in self.rgt_symbols:
            rgt_str += s.name
        return "{} --> {}".format(self.lft_var, rgt_str)








class GrammarBuilder:

    def __init__(self, force_terminal_length_1=False, ignore_duplicate_symbol_error=True, generate_missing_symbols=False):
        self._start_symbol = None #  type: str
        self._variables = [] # type: List[str]
        self._terminals = [] # type: List[str]
        self._productions = [] # type: List[Production]

        self._built_terminals = []  # type: List[str]
        self._aggr_productions_dict = None
        self._force_terminal_length_1=force_terminal_length_1
        self._ignore_duplicate_symbol_error=ignore_duplicate_symbol_error
        self._generate_missing_symbols = generate_missing_symbols
        self._built = False

    def set_start_symbol(self, start_symbol_name):
        if self._start_symbol is not None:
            self._variables.remove(start_symbol_name)
        self._start_symbol = start_symbol_name
        self._variables.append(start_symbol_name)

    def add_production(self, var_name, list_of_symbols: List[Symbol]):
        production = Production(var_name, list_of_symbols)
        self._productions.append(production)


    def add_vars(self, variables):
        for var in variables:
            self.add_var(var)

    def add_terms(self, terminals):
        for term in terminals:
            self.add_term(terminals)


    def add_var(self, variable):
        if isinstance(variable, Var):
            variable = variable.name
        elif not isinstance(variable, str):
            raise TypeError("variable must be a string or an instance of Var class")

        if variable in self._variables:
            if not self._ignore_duplicate_symbol_error:
                raise ValueError("Can't add variable '{}': another variable with the same name exists.")
        else:
            self._variables.append(variable)


    def add_term(self, terminal):
        # type: (str) -> None
        if isinstance(terminal, Term):
            terminal = terminal.name
        elif not isinstance(terminal, str):
            raise TypeError("terminal must be a string or an instance of Terminal class")

        if terminal in self._terminals:
            if not self._ignore_duplicate_symbol_error:
                raise ValueError("Can't add terminal '{}': another terminal with the same name exists.".format(terminal))
        else:
            self._terminals.append(terminal)

    def _build_terminals(self):
        if self._force_terminal_length_1 == True:
            self._built_terminals = self._terminals[:]
            for term in self._built_terminals:
                if len(term) > 1:
                    raise ValueError("Terminal '{}' has a length > 1 but this GrammarBuilder instance is forcing to use "
                                     "terminals with length 1.".format(term))
        else:
            warning_terminals = {} # type: Dict[str, List[str]] # dizionario di terminali a rischio di essere confuse con altri terminali più corti
            sorted_terms = self._terminals
            sorted_terms.sort(key=len)
            sorted_terms = list(reversed(sorted_terms))
            # we want to start building the terminals with more chars
            for terminal in sorted_terms:
                for already_build_term in self._built_terminals:
                    if terminal in already_build_term:  # if a subsequence of already_build_term is equal to terminal
                        if already_build_term not in warning_terminals.keys():
                            warning_terminals[already_build_term] = [terminal]
                        else:
                            warning_terminals[already_build_term].append(terminal)

                        combs = []
                        for i in range(1, len(already_build_term)+1):
                            for p in itertools.combinations_with_replacement(warning_terminals[already_build_term], i):
                                combs.append("".join(p))
                        if already_build_term in combs:
                            raise ValueError("Terminal '{}' has ambiguity with smaller terminals."
                                    .format(already_build_term))

                self._built_terminals.append(terminal)



    def build(self):


        self._build_terminals()
        # dict  { LEFT_VAR -> LIST_OF_RIGHT_SYMBOLS_LIST }
        # "A" -> [ ["A", "B], ["t"], ["C"] ]
        #  A -> AB | t | C
        self._aggr_productions_dict = {}

        for i, prod in enumerate(self._productions):
            rgt = prod.rgt_symbols
            if prod.lft_var not in self._variables:
                if self._generate_missing_symbols:
                    self.add_var(prod.lft_var)
                else:
                    raise ValueError("Error building the grammar, left part of production {} is not a defined variable: {}"
                                     .format(i, prod.lft_var))

            for rgt_sym in prod.rgt_symbols:
                if rgt_sym.type == SymbolType.VARIABLE:
                    if rgt_sym.name not in self._variables:
                        if self._generate_missing_symbols:
                            self.add_var(rgt_sym.name)
                        else:
                            raise ValueError("Error building the grammar, right part of production {} uses an undefined variable: {}"
                                .format(i, rgt))
                elif rgt_sym.type == SymbolType.TERMINAL:
                    if rgt_sym.name not in self._terminals:
                        if self._generate_missing_symbols:
                            self.add_term(rgt_sym.name)
                        else:
                            raise ValueError("Error building the grammar, right part of production {} uses an undefined terminal: {}"
                                .format(i, rgt_sym))
                else:
                    ValueError("Right Symbol has an unkown SymbolType: {}".format(rgt_sym.type))

            if prod.lft_var in self._aggr_productions_dict.keys():
                self._aggr_productions_dict[prod.lft_var].append(rgt)
            else:
                self._aggr_productions_dict[prod.lft_var] = [rgt]
        self._built = True
        return Grammar(self)


class CnfGrammarBuilder(GrammarBuilder):
    def __init__(self, force_terminal_length_1=False, ignore_duplicate_symbol_error=True, generate_missing_symbols=False):
        super().__init__(force_terminal_length_1, ignore_duplicate_symbol_error, generate_missing_symbols)

    def _assert_production(self, prod):
        if prod.lft_var == self._start_symbol:
            start_prod=True
        else:
            start_prod=False

        if len(prod.rgt_symbols) == 1:
            if start_prod:
                if prod.rgt_symbols[0].type == SymbolType.TERMINAL and prod.rgt_symbols[0].name != '':
                    raise ValueError("Error in production {}: CNF Grammar's productions containings start symbol must "
                                     "contain two variables in the right side or must contain an empty terminal.".format(prod))

            if prod.rgt_symbols[0].type != SymbolType.TERMINAL:
                raise ValueError(
                    "Error in production {}: CNF Grammar's productions with 1 symbols must contains a terminal.".format(
                        prod))
            elif prod.rgt_symbols[0].name == "":
                raise ValueError(
                    "Error in production {}: CNF Grammar's productions with 1 symbols must contains a NON-EMPTY terminal.".format(
                        prod))


        elif len(prod.rgt_symbols) == 2:
            if prod.rgt_symbols[0].type != SymbolType.VARIABLE or prod.rgt_symbols[1].type != SymbolType.VARIABLE:
                raise ValueError(
                    "Error in production {}: CNF Grammar's productions with 2 symbols must contains 2 variables.".format(
                        prod))
            if prod.rgt_symbols[0].name == self._start_symbol or prod.rgt_symbols[1].name == self._start_symbol:
                raise ValueError("Error in production {}: in CNF productions, starting symbol ('{}') can't appear "
                                 "in the right side.".format(prod, self._start_symbol))


        elif len(prod.rgt_symbols) > 2:
            raise ValueError(
                "Error in production {}: CNF Grammar can't contains productions with 3 or more symbols.".format(prod))


    def build(self):
        super().build()
        for prod in self._productions:
            self._assert_production(prod)

        return CnfGrammar(self)









class Grammar:
    def __init__(self, grammar_builder: GrammarBuilder):
        if isinstance(grammar_builder, GrammarBuilder):
            if grammar_builder._built == False:
                raise RuntimeError("In order to create a Grammar instance you have to call build() method over a "
                                   "GrammarBuilder instance. You don't want to use the Grammar constructor.")
            self.variables = grammar_builder._variables[:]
            self.terminals = grammar_builder._built_terminals[:]
            self.productions = grammar_builder._productions[:]
            self.aggr_productions_dict = copy.deepcopy(grammar_builder._aggr_productions_dict)
        else:
            raise TypeError("Grammar must be created using a GrammarBuilder")

class CnfGrammar(Grammar):
    def __init__(self, grammar_builder: CnfGrammarBuilder):
        super().__init__(grammar_builder)
        if not isinstance(grammar_builder, CnfGrammarBuilder):
            raise TypeError("CnfGrammar must be created using a CnfGrammarBuilder")










