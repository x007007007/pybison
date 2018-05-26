from bison import BisonParser

class Parser(BisonParser):


    def __init__(self, **kwargs):
        self.bisonEngineLibName = self.__class__.__name__ + '_engine'

        tokens = [[x.strip() for x in y.split('=')]
                  for y in self.__doc__.split('\n')
                  if y.strip() != '']

        self.precedences = (
        )

        self.start = "someTarget"

        lex_rules = '\n'.join(["{} {{ returntoken({}); }}"
                               .format(*x) if x[1][0] != '_' else
                               "{} {{ {} }}".format(x[0], x[1][1:])
                               for x in tokens])

        self.tokens = list(set([x[1] for x in tokens if not x[1].startswith('_')]))
        self.lexscript = r"""
%{
#include <stdio.h>
#include <string.h>
#include "Python.h"
#define YYSTYPE void *
#include "tokens.h"
//int yylineno = 0;
int yywrap() { return(1); }
extern void *py_parser;
extern void (*py_input)(PyObject *parser, char *buf, int *result, int max_size);
#define returntoken(tok) yylval = PyUnicode_FromString(strdup(yytext)); return (tok);
#define YY_INPUT(buf,result,max_size) { (*py_input)(py_parser, buf, &result, max_size); }
%}

%%
""" + lex_rules + """

%%
    """
        print(self.lexscript)
        super(Parser, self).__init__(**kwargs)




class MyParser(Parser):
    r"""
        quit                               = QUIT
        [a-zA-Z0-9]+                       = WORD
        ([0-9]*\.?)([0-9]+)(e[-+]?[0-9]+)? = NUMBER
        ([0-9]+)(\.?[0-9]*)(e[-+]?[0-9]+)? = NUMBER
        \(                                 = LPAREN
        \)                                 = RPAREN
        \n                                 = _yylineno++;
        [ \t]                              = _
        .                                  = _
    """

    def on_someTarget(self, target, option, names, values):
        """
        someTarget
        : paren_expr
        | someTarget WORD
        | someTarget QUIT
        """
        print("on_someTarget: %s %s %s" % (option, names, repr(values)))
        if option == 1:
            return values[1]
        elif option == 2:
            print("quit!")
            return 0

    def on_paren_expr(self, target, option, names, values):
        """
        paren_expr : LPAREN WORD RPAREN
        """
        print("PARENTHESISED", values)
        return values[1]



p = MyParser(verbose=False, debugSymbols=True)
p.run(file='foo', debug=0)
