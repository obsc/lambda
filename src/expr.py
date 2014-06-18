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
Free variables inside expression
"""
class FreeVariableException(Exception):
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
        s = ''
        exprs = [self]

        while len(exprs) > 0:
            e = exprs.pop()
            if isinstance(e, str):
                s += e
            elif e.typ == 0:
                s += e.l
            elif e.typ == 1:
                exprs.extend([')', e.r])
                s += '(\\%s.' % e.l
            elif e.typ == 2:
                exprs.extend([e.r, ' ', e.l] if e.r.typ == 0 
                                else [')', e.r, ' (', e.l])

        return fixParens(s)

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

        expr.validateFreeVars()
        return expr

    """
    Substitutes the expression e for the variable v
    """
    def subst(self, v, expr):
        exprs = [self]
        while len(exprs) > 0:
            e = exprs.pop()
            if e.typ == 0 and e.l == v:
                e.set(expr.copy())
            elif e.typ == 1 and e.l != v:
                exprs.append(e.r)
            elif e.typ == 2:
                exprs.extend([e.l, e.r])

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
        expr_copy = Expr('', self.env)
        exprs = [(expr_copy, self)]

        while len(exprs) > 0:
            e_copy, e = exprs.pop()
            e_copy.typ = e.typ

            if e.typ == 0 or e.typ == 1:
                e_copy.l = e.l
            else:
                e_copy.l = Expr('', e.l.env)
                exprs.append((e_copy.l, e.l))

            if e.typ == 0:
                e_copy.r = e.r
            else:
                e_copy.r = Expr('', e.r.env)
                exprs.append((e_copy.r, e.r))

        return expr_copy

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

    """
    Checks that there are no free variables
    """
    def validateFreeVars(self):
        exprs = [(self, [])]
        while len(exprs) > 0:
            e, bound = exprs.pop()

            if e.typ == 0:
                if e.l not in e.env and e.l not in bound:
                    raise FreeVariableException("%s is a free variable" % e.l)
            elif e.typ == 1:
                new_bound = bound[:]
                new_bound.append(e.l)
                exprs.append((e.r, new_bound))
            elif e.typ == 2:
                exprs.extend([(e.l, bound), (e.r, bound)])