from expr import *

VERBOSE = True
GLOBALS = {}

def removeComments(s):
    return s.split('#')[0]

def copyGlobals():
    g_copy = {}
    for k in GLOBALS:
        g_copy[k] = GLOBALS[k].copy()
    return g_copy

def loadFile(filename):
    print "Loading file: %s" % filename
    f = open(filename)

    for line in f:
        evalGlobal(line)

    f.close()

def evalGlobal(s):
    if s.strip() == '=':
        for k in GLOBALS:
            print '%s : %s' % (k, str(GLOBALS[k]))
        return
    s = removeComments(s).strip()
    if '=' in s:
        pos = s.find('=')
        v = s[:pos].strip()
        e = s[pos+1:].strip()
        if len(v) == 0:
            try:
                loadFile(e)
            except:
                print "Invalid filename"
        elif len(e) == 0:
            print "Invalid Syntax"
        else:
            e = evalOne(e)
            if e is not None:
                GLOBALS[v] = e
    else:
        evalOne(s)

def evalOne(s):
    try:
        if len(s) > 0:
            e = Expr.parse(s, copyGlobals())
            incomplete = [e]
            prev = None

            while len(incomplete) > 0:
                cur = incomplete.pop()
                if cur.typ == 0:
                    if cur.l == "print":
                        cur.typ = 3
                    elif cur.l in cur.env:
                        cur.set(cur.env[cur.l].copy())
                        incomplete.append(cur)
                    elif cur.l != '()':
                        print "Unbound Variable: %s" % cur.l
                        return None
                elif cur.typ == 2:
                    if prev == cur.r:
                        if cur.l.typ == 3 and cur.l.l == "print":
                            if cur.r.typ == 3:
                                print chr(cur.r.l)
                            elif cur.r.typ == 1:
                                num = cur.r.copy()
                                cur.r.typ = 2
                                
                                cur.r.l = Expr('', num.env)
                                cur.r.l.typ = 2
                                cur.r.l.l = num
                                cur.r.l.r = Expr('', num.env)
                                cur.r.l.r.typ = 3
                                cur.r.l.r.l = 'next'

                                cur.r.r = Expr('', num.env)
                                cur.r.r.typ = 3
                                cur.r.r.v = 0
                                print(cur)
                                incomplete.append(cur)
                                incomplete.append(cur.r)
                            else:
                                print "Unable to print"
                                return None
                        elif cur.l.typ == 3 and cur.l.l == 'next':
                            cur.typ = 3
                            cur.l = cur.r.l + 1
                        elif cur.l.typ == 1:
                            cur.l.r.subst(cur.l.l, cur.r)
                            cur.set(cur.l.r.copy())
                            incomplete.append(cur)
                        else:
                            print "Unable to Apply non-function"
                            return None
                    else:
                        incomplete.append(cur)
                        incomplete.append(cur.r)
                        incomplete.append(cur.l)
                prev = cur

            if VERBOSE:
                print str(e)
            return e
    except ParseError as error:
        print error
    return None

def main():
    while True:
        userInput = raw_input('>>> ')
        evalGlobal(userInput)

main()