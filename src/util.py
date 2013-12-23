def getParens(s):
    """
    Returns a list of tuples of start the starting and ending index of
    all matching parenthesis in s. Returns None if input is invalid
    """

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

def getLast(s):
    """
    Returns the indices of the last pair of parenthesis.
    Returns None if there are no valid pairs. 
    """
    try:
        return getParens(s)[-1]
    except:
        return None

def hasParens(s):
    """
    Returns true if there are valid parenthesizing.
    """
    if getParens(s) is not None and len(getParens(s)) > 0:
        return True
    return False

def fixParens(s):
    """
    Removes redundant outer parenthesis from an expression
    """
    while getLast(s) == (0, len(s) - 1):
        s = s[1 : len(s) - 1].strip()
    return s

