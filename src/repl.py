from expr import *

GLOBALS = {}

def removeComments(s):
    return s.split('#')[0]

def loadFile(filename):
    print "Loading file: %s" % filename
    f = open(filename)

    for line in f:
        evalGlobal(line)

    f.close()

def evalGlobal(s):
    s = removeComments(s)
    if '=' in s:
        pos = s.find('=')
        v = s[:pos].strip()
        e = s[pos+1:].strip()
        if len(v) == 0:
            loadFile(e)
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
            e = Expr.parse(s)
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