from expr import *

VERBOSE = True
GLOBALS = {}

def removeComments(s):
    return s.split('#')[0]

def loadFile(filename):
    print "Loading file: %s" % filename
    f = open(filename)

    for line in f:
        evalGlobal(line.strip())

    f.close()

def evalGlobal(s):
    if s.strip() == '=':
        print GLOBALS
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
            e = Expr.parse(s, GLOBALS.copy())
            incomplete = [e]
            prev = None

            while len(incomplete) > 0:
                cur = incomplete.pop()
                if cur.typ == 0:
                    if cur.v == "print":
                        cur.typ = 3
                    elif cur.v in cur.env:
                        cur.set(cur.env[cur.v].copy())
                        incomplete.append(cur)
                    elif cur.v != '()':
                        print "Unbound Variable: %s" % cur.v
                        return None
                elif cur.typ == 2:
                    if prev == cur.e2:
                        if cur.e1.typ == 3 and cur.e1.v == "print":
                            if cur.e2.typ == 3:
                                print chr(cur.e2.v)
                            elif cur.e2.typ == 1:
                                num = cur.e2.copy()
                                cur.e2.typ = 2
                                del cur.e2.e
                                
                                cur.e2.e1 = Expr('', num.env)
                                del cur.e2.e1.data
                                cur.e2.e1.typ = 2
                                cur.e2.e1.e1 = num
                                cur.e2.e1.e2 = Expr('', num.env)
                                del cur.e2.e1.e2.data
                                cur.e2.e1.e2.typ = 3
                                cur.e2.e1.e2.v = 'next'

                                cur.e2.e2 = Expr('', num.env)
                                del cur.e2.e2.data
                                cur.e2.e2.typ = 3
                                cur.e2.e2.v = 0
                                print(cur)
                                incomplete.append(cur)
                                incomplete.append(cur.e2)
                            else:
                                print "Unable to print"
                                return None
                        elif cur.e1.typ == 3 and cur.e1.v == 'next':
                            cur.typ = 3
                            cur.v = cur.e2.v + 1
                            del cur.e1
                            del cur.e2
                        elif cur.e1.typ == 1:
                            cur.e1.e.subst(cur.e1.v, cur.e2)
                            cur.set(cur.e1.e.copy())
                            incomplete.append(cur)
                        else:
                            print "Unable to Apply non-function"
                            return None
                    else:
                        incomplete.append(cur)
                        incomplete.append(cur.e2)
                        incomplete.append(cur.e1)
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