from grammar import *
from abc import ABCMeta, abstractmethod
from collections import defaultdict

class TokenizationError(RuntimeError):
    pass

class Parser(metaclass=ABCMeta):
    def __init__(self):
        pass

    def parse(self, grammar, string_of_terms, ignore_spaces=False, raise_token_error=False, print_token_error=False):
        # type: (Grammar, str) -> bool

        try:
            token_list = self.tokenization(grammar, string_of_terms, ignore_spaces)
        except TokenizationError as e:
            if raise_token_error:
                raise e
            else:
                if print_token_error:
                    print(e)
                return False
        else:
            return self._parse(grammar, token_list)

    @abstractmethod
    def _parse(self, grammar, list_of_tokens):
        # type: (Grammar, list[Token]) -> bool
        pass

    def tokenization(self, grammar, string_of_terms, ignore_spaces=False):
        # type: (Grammar, str) -> list
        sort_terms = grammar.terminals[:]
        sort_terms.sort(key=len)

        token_list = [] # type: Symbol
        parse_str = string_of_terms
        tokenized_something = True

        if len(parse_str) == 0:    # If the parse string is empty:
            for term in sort_terms:
                if term == '':
                    token_list.append(Term(term))

        else:
            while len(parse_str) > 0 and tokenized_something is True:
                tokenized_something = False
                for term in sort_terms:
                    if ignore_spaces and parse_str.startswith(' '):
                        parse_str = parse_str[1:]
                    if parse_str.startswith(term) and term is not '':
                        token_list.append(Term(term))
                        parse_str = parse_str[len(term):]
                        tokenized_something = True
                        break
            if len(parse_str) > 0:
                    raise TokenizationError("Cannot finish tokenization of input string: '{}': can't tokenize '{}'"
                                     " (one or more undefined terminals in the string)".format(string_of_terms, parse_str))


        return token_list




class CykParser(Parser):
    def _parse(self, grammar, list_of_tokens):
        import numpy as np
        # type: (Grammar, list[Token]) -> bool
        if not isinstance(grammar, CnfGrammar):
            raise TypeError("CykParser needs a Chomsky-Normal-Form Grammar (CnfGrammar class).")



        term_production_dict = defaultdict(list)
        for term in grammar.terminals:
            for prod in grammar.productions:
                if term == prod.r_symbols[0].name:
                    term_production_dict[term].append(prod)

        terminal_prods = []
        variable_prods = []
        for prod in grammar.productions:
            if len(prod.r_symbols) == 1:
                terminal_prods.append(prod)
            elif len(prod.r_symbols) == 2:
                variable_prods.append(prod)

        variables = grammar.variables
        variables_map = {key: value for value, key in enumerate(variables)}

        ntokens = len(list_of_tokens)
        nvars = len(variables)

        mat = np.zeros([ntokens, ntokens, nvars], dtype=np.bool)

        for s in range (0, ntokens):
            for prod in terminal_prods:
                if prod.r_symbols[0].name == list_of_tokens[s].name:
                    mat[0, s, variables_map[prod.l_var]] = True

        for l in range(2, ntokens+1):  # l = length of span
            for s in range(0, ntokens-l+1):  # s = start of span
                for p in range(1, l):  # p = partition of span
                    for prod in variable_prods:
                        r0 = prod.r_symbols[0].name
                        r1 = prod.r_symbols[1].name
                        if mat[p-1, s, variables_map[r0]] and mat[l-p-1, s+p, variables_map[r1]]:
                            mat[l-1, s, variables_map[prod.l_var]] = True

        for index, truth in enumerate(mat[ntokens-1, 0]):
            if truth and variables[index] == grammar.start_symbol:
                return True
        return False

