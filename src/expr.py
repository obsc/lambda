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
A single expression divided into left and right.
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
        self.l = fixParens(expr.strip())
        self.env = env

    """
    Converts an expression tree to a string
    """
    def __str__(self):
        def toString(exprs, s):
            if len(exprs) == 0:
                return fixParens(s)
            expr = exprs.pop()
            if isinstance(expr, str):
                return (lambda : toString(exprs, s + expr))
            if expr.typ == 0:
                return (lambda : toString(exprs, s + expr.l))
            if expr.typ == 1:
                exprs.extend([')', expr.r])
                return (lambda : toString(exprs, s + '(\\%s.' % expr.l))
            if expr.typ == 2:
                exprs.extend([expr.r, ' ', expr.l] if expr.r.typ == 0 
                                else [')', expr.r, ' (', expr.l])
                return (lambda : toString(exprs, s))
        return tail(toString)([self], '')

    """
    Parses and generates an expression tree from a string
    """
    @staticmethod
    def parse(expr, env):
        if not validParens(expr):
            raise ParseError("Invalid Parenthesizing")

        expr = Expr(expr, env)
        exprs = [expr]

        while len(exprs) > 0:
            e = exprs.pop()
            exprs.extend(e.parseOne())

        return expr

    """
    Substitutes the expression e for the variable v
    """
    def subst(self, v, e):
        exprs = [self]
        while len(exprs) > 0:
            expr = exprs.pop()
            if expr.typ == 0 and expr.l == v:
                expr.set(e.copy())
            elif expr.typ == 1 and expr.l != v:
                exprs.append(expr.r)
            elif expr.typ == 2:
                exprs.append(expr.l)
                exprs.append(expr.r)

    """
    Sets one expression to the same data as another
    """
    def set(self, expr):
        self.typ = expr.typ
        self.env = expr.env
        self.l = expr.l
        self.r = expr.r

    """
    Makes a deep copy of an expression
    """
    def copy(self):
        e_copy = Expr('', self.env)

        def copyExprs(exprs):
            if len(exprs) == 0:
                return
            e_copy, expr = exprs.pop()
            e_copy.typ = expr.typ

            if expr.typ == 0 or expr.typ == 1:
                e_copy.l = expr.l
            else:
                e_copy.l = Expr('', expr.l.env)
                exprs.append((e_copy.l, expr.l))

            if expr.typ == 0:
                e_copy.r = expr.r
            else:
                e_copy.r = Expr('', expr.r.env)
                exprs.append((e_copy.r, expr.r))

            return (lambda : copyExprs(exprs))

        tail(copyExprs)([(e_copy, self)])
        return e_copy

    """
    Parses a single expression
    """
    def parseOne(self):
        if self.l[0] == '\\':
            return self.parseLambda()

        if ' ' in self.l or hasParens(self.l):
            return self.parseApply()

        return self.parseVar()

    """
    Parses a single variable
    typ : 0
    """
    def parseVar(self):
        Expr.validateVar(self.l)

        self.typ = 0 #Var
        self.r = None

        return []

    """
    Parses a lambda function
    type : 1
    """
    def parseLambda(self):
        pos = self.l.find('.')
        if pos == -1:
            raise ParseError("Invalid function: missing '.'")

        v = self.l[1:pos].strip()
        e = self.l[pos+1:].strip()

        if len(e) == 0:
            raise ParseError("Invalid function: missing body")

        if ' ' in v:
            v = v.split()
            e = '\\%s.%s' % (' '.join(v[1:]), e)
            v = v[0]
        Expr.validateVar(v)

        self.typ = 1 #Lambda
        self.l = v
        self.r = Expr(e, self.env)

        return [self.r]

    """
    Parses a function application
    typ : 2
    """
    def parseApply(self):
        start = -1
        if self.l[-1] == ')' and self.l[-2] != '(':
            start = getLastParens(self.l)[0]
        else:
            for i in xrange(len(self.l)-2, -1, -1):
                if self.l[i] == ' ' or self.l[i] == ')':
                    start = i + 1
                    break

        self.typ = 2
        l,r = self.l[:start], self.l[start:]
        self.l, self.r = Expr(l, self.env), Expr(r, self.env)

        return [self.l, self.r]

    """
    Checks that v is a valid variable name
    """
    @staticmethod
    def validateVar(v):
        if v == '()':
            return
        if len(v) == 0 or any(c in v for c in ('(', ')', '\\', '.', '=')):
            raise ParseError("Invalid variable name")