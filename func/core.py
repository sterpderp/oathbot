# get specific character sheet
def get_sheet(ctx, char_id):

    pass


# parse character sheet
def parse_sheet():
    pass


# parse I/P/R and return pips
def ipr_split(ipr):
    i = ipr.split(' P')[0]
    i = i.count('•')

    pr = ipr.split(' P')[1]
    p = pr.split(' R')[0]
    p = p.count('•')

    r = pr.split(' R')[1]
    r = r.count('•')

    _ipr = [i, p, r]
    return _ipr
