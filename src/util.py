"""
Returns a list of tuples of start the starting and ending index of
all matching parenthesis in s. Returns None if input is invalid
"""
def getParens(s):
    pairs, start = [], []
    try:
        for i in xrange(len(s)):
            if s[i] == '(':
                start.append(i)
            if s[i] == ')':
                prev = start.pop()
                if prev < i - 1:
                    pairs.append((prev, i))
    except:
        return None
    if len(start) > 0:
        return None
    return pairs 

"""
Returns the indices of the last pair of parenthesis.
Returns None if there are no valid pairs. 
"""
def getLastParens(s):
    try:
        return getParens(s)[-1]
    except:
        return None

"""
Returns true if there is at least 1 valid parenthesis
"""
def hasParens(s):
    return getParens(s) is not None and len(getParens(s)) > 0

"""
Returns true if s has valid parenthesizing
"""
def validParens(s):
    return getParens(s) is not None

"""
Removes redundant outer parenthesis from an expression
"""
def fixParens(s):
    while getLastParens(s) == (0, len(s) - 1):
        if len(s) == 2:
            break
        s = s[1 : len(s) - 1].strip()
    return s

