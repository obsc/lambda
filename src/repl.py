import sys
from expr import *

VERBOSE = True
GLOBALS = {}

"""
Removes the comments from a line of code
"""
def removeComments(s):
    return s.split('#')[0]

"""
Makes a deep copy of the globals
"""
def copyGlobals():
    g_copy = {}
    for k in GLOBALS:
        g_copy[k] = GLOBALS[k].copy()
    return g_copy

"""
Loads and runs a single file
"""
def loadFile(filename):
    print "Loading file: %s" % filename
    f = open(filename)

    for line in f:
        evalGlobal(line)

    f.close()

"""
Evaluates a single expression on the global scope
"""
def evalGlobal(s):
    s = removeComments(s).strip()
    if s == '=':
        for k in GLOBALS:
            print '%s : %s' % (k, str(GLOBALS[k]))
        return
    if '=' in s:
        pos = s.find('=')
        v = s[:pos].strip()
        e = s[pos+1:].strip()
        if len(v) == 0:
            try:
                loadFile(e)
            except IOError:
                print "Invalid filename"
            except RuntimeError:
                print "Recursion depth exceeded"
        elif len(e) == 0:
            print "Invalid Syntax"
        else:
            e = evalOne(e)
            if e is not None:
                GLOBALS[v] = e
    else:
        evalOne(s)

"""
Evaluates a single expression
"""
def evalOne(s):
    if len(s) == 0:
        return None
    try:
        expr = Expr.parse(s, copyGlobals())
        exprs = [(expr, False)]
        while len(exprs) > 0:
            (e, flag) = exprs.pop()
            if e.typ == 0:
                if e.l in e.env:
                    e.replace(e.env[e.l])
                    exprs.append((e, False))
                elif e.l != '()':
                    print "Unbound Variable: %s" % e.l
                    return None
            elif e.typ == 2:
                if flag:
                    if e.l.typ == 1:
                        e.l.r.subst(e.l.l, e.r)
                        e.set(e.l.r.copy())
                        exprs.append((e, False))
                    # elif plugins
                    else:
                        print "Unable to Apply non-function"
                        return None
                else:
                    exprs.extend([(e, True), (e.r, False), (e.l, False)])
        if VERBOSE:
            print str(expr)
        return expr
    except (ParseError, FreeVariableException) as error:
        print error
    return None

"""
Evaluates a single expression
"""
# def evalOne(s):
#     try:
#         if len(s) > 0:
#             e = Expr.parse(s, copyGlobals())
#             incomplete = [e]
#             prev = None

#             while len(incomplete) > 0:
#                 cur = incomplete.pop()
#                 if cur.typ == 0:
#                     if cur.l == "print":
#                         cur.typ = 3
#                     elif cur.l in cur.env:
#                         cur.set(cur.env[cur.l].copy())
#                         incomplete.append(cur)
#                     elif cur.l != '()':
#                         print "Unbound Variable: %s" % cur.l
#                         return None
#                 elif cur.typ == 2:
#                     if prev == cur.r:
#                         if cur.l.typ == 3 and cur.l.l == "print":
#                             if cur.r.typ == 3:
#                                 print chr(cur.r.l)
#                             elif cur.r.typ == 1:
#                                 num = cur.r.copy()
#                                 cur.r.typ = 2
                                
#                                 cur.r.l = Expr('', num.env)
#                                 cur.r.l.typ = 2
#                                 cur.r.l.l = num
#                                 cur.r.l.r = Expr('', num.env)
#                                 cur.r.l.r.typ = 3
#                                 cur.r.l.r.l = 'next'

#                                 cur.r.r = Expr('', num.env)
#                                 cur.r.r.typ = 3
#                                 cur.r.r.v = 0
#                                 print(cur)
#                                 incomplete.append(cur)
#                                 incomplete.append(cur.r)
#                             else:
#                                 print "Unable to print"
#                                 return None
#                         elif cur.l.typ == 3 and cur.l.l == 'next':
#                             cur.typ = 3
#                             cur.l = cur.r.l + 1
#                         elif cur.l.typ == 1:
#                             cur.l.r.subst(cur.l.l, cur.r)
#                             cur.set(cur.l.r.copy())
#                             incomplete.append(cur)
#                         else:
#                             print "Unable to Apply non-function"
#                             return None
#                     else:
#                         incomplete.append(cur)
#                         incomplete.append(cur.r)
#                         incomplete.append(cur.l)
#                 prev = cur

#             if VERBOSE:
#                 print str(e)
#             return e
#     except (ParseError, FreeVariableException) as error:
#         print error
#     return None

"""
The repl
"""
def main():
    while True:
        userInput = raw_input('>>> ')
        evalGlobal(userInput)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print '\nExiting...'
        sys.exit(0)