def getParens(s):
    pairs, start = [], []
    try:
        for i in range(len(s)):
            if s[i] == '(':
                start.append(i)
            if s[i] == ')':
                pairs.append((start.pop(), i))
    except:
        return None
    if len(start) > 0:
        return None
    return pairs 

def getOuter(s):
    try:
        return getParens(s)[-1]
    except:
        return None

def fixParens(s):
    while getOuter(s) == (0, len(s) - 1):
        s = s[1 : len(s) - 1].strip()
    return s
    