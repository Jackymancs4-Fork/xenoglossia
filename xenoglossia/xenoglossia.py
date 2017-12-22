from __future__ import absolute_import

from . import builtins

from pyparsing import ParseException, Group, OneOrMore, Word, QuotedString, ZeroOrMore, alphas, alphanums, printables
import six


class NameError(Exception):
    pass


class ParseError(Exception):
    pass

sq_string = QuotedString( quoteChar="'" )
dq_string = QuotedString( quoteChar='"' )
STRING = sq_string ^ dq_string

IDENTIFIER = Word( alphas + "_", alphanums + "_" )
BAD_IDENTIFIER = Word (printables, printables)

FUNCTION_CALL = Group( IDENTIFIER  + ZeroOrMore( STRING ) )
BAD_FUNCTION_CALL = Group( BAD_IDENTIFIER + ZeroOrMore( STRING ) )

PROGRAM = OneOrMore(BAD_FUNCTION_CALL)

def tokenize(program):
    # String literals are defined as being UTF-8;
    # skip any characters that don't decode.
    def decode(s):
        if six.PY2:
            return s.decode('utf-8', errors='ignore')
        else:
            return s

    try:
        return [{'function': IDENTIFIER.parseString(el[0])[0],'arguments': map(decode, el[1:])} for el in PROGRAM.parseString(program)]
    except ParseException as e:
        # wrap the orginal exception in a local type
        raise ParseError(e, el)


def run_program(input, program):
    tokens = tokenize(program)

    for token in tokens:
        try:
            func = getattr(builtins, token['function'])
        except AttributeError:
            raise NameError(token['function'])
        input = func(input, *token['arguments'])

    if isinstance(input, list):
        input = ''.join(input)

    return input
