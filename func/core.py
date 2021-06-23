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


# splits harm/trauma/rerolls into list elements
def bracket_split(data):
    _data = data.split('[')
    _data = [e.replace(']', '') for e in _data]
    _data = [e.strip(' ') for e in _data]
    del _data[0]
    return _data


# counts pips of harms and rerolls
def harm_count(raw_data):
    clean_data = {}
    dot = '\u2022'
    for i in raw_data:
        _pips = i.count('•')
        i = i.replace('•', '')
        i = i.strip(' ')
        clean_data[i] = _pips

    return clean_data
