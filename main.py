from grammar.Grammar import *
from grammar.Parser import *


gb = CnfGrammarBuilder(force_terminal_length_1=False,
                       ignore_duplicate_symbol_error=True,
                       generate_missing_symbols=True)


gb.add_terms('a', 'b')
gb.add_vars('S', 'A', 'B')
gb.set_start_symbol('S')


gb.add_production('S', [Var('A'), Var('A')])
gb.add_production('S', [Var('A'), Var('B')])
gb.add_production('A', [Var('A'), Var('A')])
gb.add_production('A', [Term('a')])
gb.add_production('B', [Term('b')])


grammar = gb.build()

parser = CykParser()
parser.parse(grammar, "abaaa")
