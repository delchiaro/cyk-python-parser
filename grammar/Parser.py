from grammar import Grammar
from grammar.Grammar import SymbolType, CnfGrammar, Term, Symbol
from abc import ABCMeta, abstractmethod




class Parser(metaclass=ABCMeta):

    def parse(self, grammar, string_of_terms):
        # type: (Grammar, str) -> bool
        token_list = self.tokenization(grammar, string_of_terms)
        return self._parse(grammar, token_list)

    @abstractmethod
    def _parse(self, grammar, list_of_tokens):
        # type: (Grammar, list[Token]) -> bool
        pass

    def tokenization(self, grammar, string_of_terms):
        # type: (Grammar, str) -> list
        sort_terms = grammar.terminals[:]
        sort_terms.sort(key=len)

        token_list = [] # type: Symbol
        parse_str = string_of_terms
        tokenized_something = True
        while len(parse_str) > 0 and tokenized_something is True:
            tokenized_something = False
            for term in sort_terms:
                if parse_str.startswith(term):
                    token_list.append(Term(term))
                    parse_str = parse_str[len(term):]
                    tokenized_something = True
                    break
        if len(parse_str) > 0:
            ValueError("Cannot finish tokenization of input string: '{}'"
                       "\nCan't tokenize '{}'".format(string_of_terms, parse_str))

        return token_list



class CykParser(Parser):
    def _parse(self, grammar, list_of_tokens):
        # type: (Grammar, list[Token]) -> bool
        if not isinstance(grammar, CnfGrammar):
            raise TypeError("CykParser needs a Chomsky-Normal-Form Grammar (CnfGrammar class).")

