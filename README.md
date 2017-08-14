# Fork of PyBison

**(This is a fork of [eugenai/pybison](https://github.com/eugeneai/pybison)  and [smvv/pybison](https://github.com/smvv/pybison) for personal use.)**  
I just added the one-line installation-script and colorfied the syntax-errors that are found by Bison.


## One-Line Install

### Global Python Installation (sudo needed)
Needs sudo for the installation of the following dependencies:
- **apt-get:** bison, flex
- **pip3**: cython, six, pyrex, pybison itself

Install with:
```sh
curl -s https://raw.githubusercontent.com/da-h/pybison/master/install_global.sh | bash
```

### Virtualenv Python Installation (no sudo needed)
First, install the dependencies
```sh
sudo apt-get install bison flex
```
Now, install with:
```sh
curl -s https://raw.githubusercontent.com/da-h/pybison/master/install_venv.sh | bash
```




For further information, please read the following original **README**:  

# Readme

Welcome to PyBison!  
Bringing **GNU Bison/Flex**'s raw speed and power to Python  

## What is PyBison?
PyBison is a framework which effectively 'wraps' **Bison** and **Flex into** a Python class structure.

You define a parser class, define tokens and precedences as attributes, and parse targets as methods with rules in the docstrings,
then instantiate and run.

Black Magick happens in the background, whereupon you get callbacks each time ```yyparse()``` resolves a parse target.


## There are already parsers for Python. Why re-invent the wheel?

I looked at all the Python-based parsing frameworks.

IMO, the best one was **PLY** - a pure-python *lexx/yacc* implementation
(which I have borrowed from heavily in designing PyBison's OO model).

But PLY suffers some major limitations:

 * usage of 'named groups' regular expressions in the lexer creates
   a hard limit of 100 tokens - not enough to comfortably handle major
   languages
 
 * pure-python implementation is a convenience, but incurs a cruel
   performance penalty

 * the parser engine is SLR, not full LALR(1)

The other frameworks utilise a fiddly script syntax - 
   
## How do I use this?

Refer to the INSTALL file for setting up.  
Refer to the examples and the doco for usage.

