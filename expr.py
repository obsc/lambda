from util import *

class Expr(object):

    def __init__(self, expr):
        self.data = fixParens(expr.strip())
        self.parsed = False

    def parse(self):
        if self.parsed:
            return
        

        self.parsed = True