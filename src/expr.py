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
    def __init__(self, expr, env):
        self.data = fixParens(expr.strip())
        self.env = env

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
                s += '(\\%s.' % cur.v
                incomplete.append(')')
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
        return fixParens(s)

    @staticmethod
    def parse(expr, env):
        if not validParens(expr):
            raise ParseError("Invalid Parenthesizing")
        
        e = Expr(expr, env)
        unparsed = [e]

        while len(unparsed) > 0:
            cur = unparsed.pop()
            for next in cur.parseOne():
                unparsed.append(next)

        return e

    def subst(self, v, e):
        incomplete = [self]

        while len(incomplete) > 0:
            cur = incomplete.pop()
            if cur.typ == 0 and cur.v == v:
                cur.set(e.copy())
            elif cur.typ == 1 and cur.v != v:
                incomplete.append(cur.e)
            elif cur.typ == 2:
                incomplete.append(cur.e1)
                incomplete.append(cur.e2)

    def set(self, e):
        if self.typ != 2:
            del self.v
        if self.typ == 1:
            del self.e
        if self.typ == 2:
            del self.e1
            del self.e2
        self.typ = e.typ
        self.env = e.env
        if self.typ != 2:
            self.v = e.v
        if self.typ == 1:
            self.e = e.e
        if self.typ == 2:
            self.e1 = e.e1
            self.e2 = e.e2

    def copy(self):
        e_copy = Expr('', self.env)
        del e_copy.data
        e_copy.typ = self.typ
        if self.typ != 2:
            e_copy.v = self.v
        if self.typ == 1:
            e_copy.e = self.e.copy()
        elif self.typ == 2:
            e_copy.e1 = self.e1.copy()
            e_copy.e2 = self.e2.copy()
        return e_copy

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

        if len(e) == 0:
            raise ParseError("Invalid function: missing body")

        if ' ' in v:
            v = v.split()
            e = '\\%s.%s' % (' '.join(v[1:]), e)
            v = v[0]
        self.validateVar(v)

        self.typ = 1 #Lambda
        self.v = v
        self.e = Expr(e, self.env)

        del self.data
        return [self.e]

    def parseApply(self):
        start = -1
        if self.data[-1] == ')' and self.data[-2] != '(':
            start = getLastParens(self.data)[0]
        else:
            for i in xrange(len(self.data)-2, -1, -1):
                if self.data[i] == ' ' or self.data[i] == ')':
                    start = i + 1
                    break

        self.typ = 2 #Apply
        self.e1 = Expr(self.data[:start], self.env)
        self.e2 = Expr(self.data[start:], self.env)

        del self.data
        return [self.e1, self.e2]

    def validateVar(self, v):
        if v == '()':
            return
        if len(v) == 0 or any(c in v for c in ('(', ')', '\\', '.', '=')):
            raise ParseError("Invalid variable name")