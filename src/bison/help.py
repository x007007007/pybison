import hashlib

def hashParserObject(parser):
    """
    Calculates an sha1 hex 'hash' of the lex script
    and grammar rules in a parser class instance.

    This is based on the raw text of the lex script attribute,
    and the grammar rule docstrings within the handler methods.

    Used to detect if someone has changed any grammar rules or
    lex script, and therefore, whether a shared parser lib rebuild
    is required.
    """
    hasher = hashlib.new('sha1')

    def update(o):
        if type(o) == type(""):
            o=o.encode("utf-8")
        hasher.update(o)

    # add the lex script
    update(parser.lexscript)

    # add the tokens
    # workaround pyrex weirdness
    # tokens = list(parser.tokens)
    tokens = parser.tokens[0]
    update(",".join(tokens))

    # add the precedences
    for direction, tokens in parser.precedences:
        tokens = tokens[0]
        update(direction + "".join(tokens))

    # extract the parser target handler names
    handlerNames = dir(parser)

    #handlerNames = filter(lambda m: m.startswith('on_'), dir(parser))
    tmp = []
    for name in handlerNames:
        if name.startswith('on_'):
            tmp.append(name)
    handlerNames = tmp
    handlerNames.sort()

    # extract method objects, filter down to callables
    #handlers = [getattr(parser, m) for m in handlerNames]
    #handlers = filter(lambda h: callable(h), handlers)
    tmp = []
    for m in handlerNames:
        attr = getattr(parser, m)
        if callable(attr):
            tmp.append(attr)
    handlers = tmp

    # now add in the methods' docstrings
    for h in handlers:
        docString = h.__doc__
        update(docString)

    # done
    return hasher.hexdigest()


def cmpLines(meth1, meth2):
    """
    Used as a sort() argument for sorting parse target handler methods by
    the order of their declaration in their source file.
    """
    try:
        line1 = meth1.__code__.co_firstlineno
        line2 = meth2.__code__.co_firstlineno
    except:
        line1 = meth1.__init__.__code__.co_firstlineno
        line2 = meth2.__init__.__code__.co_firstlineno

    return (line1 > line2) - (line1 < line2)


def keyLines(meth):
    """
    Used as a sort() 'key' argument for sorting parse target handler methods by
    the order of their declaration in their source file.
    """
    try:
        line = meth.__code__.co_firstlineno
    except:
        line = meth.__init__.__code__.co_firstlineno

    return line

