.PHONY: all module install clean develop java_test

PYTHON=python

JAVAS=javaparser.y javaparser.l 

all: module

module:
	$(PYTHON) setup.py build

install:
	$(PYTHON) setup.py install

clean:
	rm -rf *~ *.output tokens.h *.tab.* *.yy.c java-grammar new.* *.o *.so dummy build *.pxi *-lexer.c
	rm -rf *-parser.y *-parser.c *-parser.h pybison.c pybison.h
	rm -rf bison.c bison.h
	rm -rf *.pyc
	rm -rf tmp.*
	rm -f src/pyrex/bison_.pxi src/pyrex/bison_.c src/pyrex/bison_.h

develop:
	$(PYTHON) setup.py develop
	
	
java_test: develop 
	cd examples/java && bison2py $(JAVAS) javaparser.py && $(PYTHON) run.py
	