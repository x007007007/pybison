from bison import BisonParser

class Parser(BisonParser):


    def __init__(self, **kwargs):
        self.bisonEngineLibName = self.__class__.__name__ + '_engine'

        tokens = [[x.strip() for x in y.split('=')]
                  for y in self.__doc__.split('\n')
                  if y.strip() != '']

        self.precedences = (
        )

        attribs = dir(self)
        handlers = [getattr(self, x) for x in attribs
                    if x.startswith('on_')]
        start = [x.__name__.replace('on_', '')
                 for x in handlers if getattr(x, '__start__', False)]
        assert len(start) == 1, f'needs exactly one start node, found {len(start)}!'
        self.start = start[0]
        return_location = kwargs.pop('return_location', False)
        if return_location:
            fmt = "{} {{ returntoken_loc({}); }}"
        else:
            fmt = "{} {{ returntoken({}); }}"
        lex_rules = '\n'.join([fmt
                               .format(*x) if x[1][0] != '_' else
                               "{} {{ {} }}".format(x[0], x[1][1:])
                               for x in tokens])

        self.tokens = sorted(list(set([x[1] for x in tokens if not x[1].startswith('_')])))
        self.lexscript = r"""
%{
// Start node is: """ + self.start + r"""
#include <stdio.h>
#include <string.h>
#include "Python.h"
#define YYSTYPE void *
#include "tokens.h"
int yycolumn = 1;
int yywrap() { return(1); }
extern void *py_parser;
extern void (*py_input)(PyObject *parser, char *buf, int *result, int max_size);
#define returntoken(tok) yylval = PyUnicode_FromString(strdup(yytext)); return (tok);
#define returntoken_loc(tok) yylval = PyTuple_Pack(3, PyUnicode_FromString(strdup(yytext)), PyTuple_Pack(2, PyLong_FromLong(yylloc.first_line), PyLong_FromLong(yylloc.first_column)), PyTuple_Pack(2, PyLong_FromLong(yylloc.last_line), PyLong_FromLong(yylloc.last_column))); return (tok);
#define YY_INPUT(buf,result,max_size) { (*py_input)(py_parser, buf, &result, max_size); }
#define YY_USER_ACTION yylloc.first_line = yylloc.last_line; \
    yylloc.first_column = yylloc.last_column; \
    for(int i = 0; yytext[i] != '\0'; i++) { \
        if(yytext[i] == '\n') { \
            yylloc.last_line++; \
            yylloc.last_column = 0; \
        } \
        else { \
            yylloc.last_column++; \
        } \
    }
%}

%%
""" + lex_rules + """

%%
    """
        #print(self.lexscript)
        super(Parser, self).__init__(**kwargs)


def start(method):
    method.__start__ = True
    return method


from decimal import Decimal
class MyParser(Parser):
    r"""
        quit                               = QUIT
        [a-zA-Z0-9]+                       = WORD
        ([0-9]*\.?)([0-9]+)(e[-+]?[0-9]+)? = NUMBER
        ([0-9]+)(\.?[0-9]*)(e[-+]?[0-9]+)? = NUMBER
        \(                                 = LPAREN
        \)                                 = RPAREN
        [ \t]                              = _
        .                                  = _
    """
    @start
    def on_someTarget(self, target, option, names, values):
        """
        someTarget
        : paren_expr
        | someTarget WORD
        | someTarget NUMBER
        | someTarget quit
        """
        print("on_someTarget: %s %s %s" % (option, names, repr(values)))
        if option == 0:
            return values[0]
        if option == 1:
            return values[1]
        elif option == 2:
            return (values[0], float(values[1]))

    def on_paren_expr(self, target, option, names, values):
        """
        paren_expr : LPAREN WORD RPAREN
        """
        return (values[1], )

    def on_QUIT(self, target, option, names, values):
        """
        quit
        : QUIT
        """
        import sys
        print('exiting')
        sys.exit(1)


class JSONParser(Parser):
    r"""
        -?[0-9]+                            = INTEGER
        -?[0-9]+([.][0-9]+)?([eE]-?[0-9]+)? = FLOAT
        \"([^\"]|\\[.])*\"                  = STRING
        \{                                  = O_START
        \}                                  = O_END
        \[                                  = A_START
        \]                                  = A_END
        ,                                   = COMMA
        :                                   = COLON
        [ \t\n]                             = _
    """

    @start
    def on_value(self, target, option, names, values):
        """
        value
        : string
        | INTEGER
        | FLOAT
        | array
        | object
        """
        if option == 1:
            return int(values[0])
        if option == 2:
            return float(values[0])
        return values[0]

    def on_string(self, target, option, names, values):
        """
        string
        : STRING
        """
        return values[0][1:-1]

    def on_json(self, target, option, names, values):
        """
        json
        : object
        | value
        """
        return values[0]

    def on_object(self, target, option, names, values):
        """
        object
        : O_START O_END
        | O_START members O_END
        """
        return {} if option == 0 else dict(values[1])

    def on_members(self, target, option, names, values):
        """
        members
        : pair
        | pair COMMA members
        """
        if option == 0:
            return (values[0],)
        return (values[0], *values[2])

    def on_pair(self, target, option, names, values):
        """
        pair
        : string COLON value
        """
        return (values[0], values[2])

    def on_array(self, target, option, names, values):
        """
        array
        : A_START A_END
        | A_START elements A_END
        """
        if option == 0:
            return ()
        return values[1]

    def on_elements(self, target, option, names, values):
        """
        elements
        : value
        | value COMMA elements
        """
        if option == 0:
            return (values[0])
        return (values[0], *values[2])
        values[2].insert(0, values[0])
        return values[2]

import time
start = time.time()
j = JSONParser(verbose=False, debugSymbols=True)
duration = time.time() - start
print('instantiate parser', duration)
j = MyParser(verbose=True, debugSymbols=True)
file = 'foo'

import json
start = time.time()
with open(file) as fh:
    result = json.load(fh)
duration = time.time() - start
print('json', duration)


start = time.time()
result = j.run(file=file, debug=0)
duration = time.time() - start
print('me', duration)
import os
print(os.stat(file).st_size / 1024)
