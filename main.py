from grammar.Parser import *

def main():
    easy_example()
    phrase_example()


def easy_example():
    gb = CnfGrammarBuilder(force_terminal_length_1=False, ignore_duplicate_symbol_error=True, generate_missing_symbols=True)

    # gb.add_terms(['a', 'b'])
    # gb.add_vars(['S', 'A', 'B'])
    gb.set_start_symbol('S')
    gb.add_production('S', [Var('A'), Var('B')])
    gb.add_production('A', [Var('A'), Var('A')])
    gb.add_production('B', [Var('B'), Var('B')])

    gb.add_production('A', [Term('a')])
    gb.add_production('A', [Term('a')])
    gb.add_production('B', [Term('b')])

    grammar = gb.build()
    test_string(grammar, 'aaaaaaaabbbbbbbbb')
    test_string(grammar, 'aaaaaaaabbbba')


def phrase_example():
    gb = CnfGrammarBuilder(ignore_duplicate_symbol_error=True, generate_missing_symbols=True)


    gb.set_start_symbol('S')
    gb.add_production('S', [Var('SUBJECT'), Var('V1')])
    gb.add_production('V1', [Var('VERB'), Var('V2')])
    gb.add_production('V2', [Var('OBJECT'), Var('DOT')])

    gb.add_production('SUBJECT', [Term('I')])
    gb.add_production('VERB', [Term('am')])
    gb.add_production('OBJECT', [Term('evil')])
    gb.add_production('DOT', [Term('.')])

    grammar = gb.build()
    test_string(grammar, 'I am evil.')
    test_string(grammar, 'I am evil, stop laughing.')




def test_string(grammar, string, ignore_spaces=True):
    parser = CykParser()
    response = parser.parse(grammar, string, ignore_spaces=ignore_spaces)
    print("The string '{}' is {}in the language.".format(string, '' if response else 'NOT '))

if __name__ == "__main__":
    main()
