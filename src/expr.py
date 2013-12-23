from util import *

class ParseError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Expr(object):

    def __init__(self, expr):
        self.data = fixParens(expr.strip())
        self.parsed = False

    def parse(self):
        if self.parsed:
            return []
        self.parsed = True

        if self.data[0] == '\\':
            pos = self.data.find('.')
            if pos == -1:
                raise ParseError("Invalid function: missing '.'")

            v = self.data[1:pos].strip()
            e = self.data[pos+1:].strip()

            if ' ' in v:
                v = v.split()
                e = '\\%s.%s' % (' '.join(v[1:]), e)
                v = v[0]
            self.validateVar(v)

            self.typ = 1 #Lambda
            self.v = v
            self.e = Expr(e)
            return [self.e]

        if ' ' in self.data or hasParens(self.data):
            self.typ = 2 #Apply
        else:
            self.validateVar(self.data)

            self.typ = 0 #Var
            self.v = self.data
            return []

    def validateVar(self, v):
        if any(c in v for c in ('(', ')', '\\', '.')):
            raise ParseError("Invalid variable name")