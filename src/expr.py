from util import *

"""
Errors that occur during parsing
"""
class ParseError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

"""
A single expression.
Expr = | v
       | \\v.e
       | e1 e2

Expression types are stored in field typ:
typ = 0 : Variable
      1 : Lambda
      2 : Application
"""
class Expr(object):
    def __init__(self, expr):
        self.data = fixParens(expr.strip())

    def __str__(self):
        s = ""
        incomplete = [self]
        while len(incomplete) > 0:
            cur = incomplete.pop()
            if isinstance(cur, str):
                s += cur
            elif cur.typ == 0:
                s += cur.v
            elif cur.typ == 1:
                s += '\\%s.' % cur.v
                incomplete.append(cur.e)
            elif cur.typ == 2:
                if cur.e2.typ == 0:
                    incomplete.append(cur.e2)
                else:
                    incomplete.append(')')
                    incomplete.append(cur.e2)
                    incomplete.append('(')
                incomplete.append(' ')
                incomplete.append(cur.e1)
        return s

    @staticmethod
    def parse(expr):
        if not validParens(expr):
            raise ParseError("Invalid Parenthesizing")
        
        e = Expr(expr)
        unparsed = [e]

        while len(unparsed) > 0:
            cur = unparsed.pop()
            for next in cur.parseOne():
                unparsed.append(next)

        return e

    #def subst(self, x, v):

    def parseOne(self):
        if self.data[0] == '\\':
            return self.parseLambda()

        if ' ' in self.data or hasParens(self.data):
            return self.parseApply()

        return self.parseVar()

    def parseVar(self):
        self.validateVar(self.data)

        self.typ = 0 #Var
        self.v = self.data

        del self.data
        return []

    def parseLambda(self):
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

        del self.data
        return [self.e]

    def parseApply(self):
        start = -1
        if self.data[-1] == ')':
            start = getLastParens(self.data)[0]
        else:
            for i in xrange(len(self.data)-1, -1, -1):
                if self.data[i] == ' ' or self.data[i] == ')':
                    start = i
                    break

        self.typ = 2 #Apply
        self.e1 = Expr(self.data[:start])
        self.e2 = Expr(self.data[start:])

        del self.data
        return [self.e1, self.e2]

    def validateVar(self, v):
        if len(v) == 0 or any(c in v for c in ('(', ')', '\\', '.')):
            raise ParseError("Invalid variable name")