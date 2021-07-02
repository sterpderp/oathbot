import json
import discord
from discord.ext import commands
from clss.CharSheet import CharSheet

resistances = ['Insight', 'Prowess', 'Resolve']
insight = ['Hunt', 'Study', 'Survey', 'Tinker']
prowess = ['Finesse', 'Prowl', 'Skirmish', 'Wreck']
resolve = ['Aether', 'Command', 'Consort', 'Sway']
skills = insight+prowess+resolve

# get specific character sheet (placeholder)
def get_sheet(ctx, char_id):

    pass


# parse character sheet (placeholder)
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
    _data = [s.title() for s in _data]
    return _data


# counts pips of harms and rerolls
def harm_count(raw_data):
    clean_data = {}
    dot = '\u2022'
    for i in raw_data:
        _pips = i.count('•')
        i = i.replace('•', '')
        i = i.strip(' ')
        i = i.title()
        clean_data[i] = _pips

    return clean_data


# load rules json for rule post command
def rules_loader(): 
    with open('./data/rules.json', encoding='utf-8') as json_file:
        rules = json.loads(json_file.read())
        return rules

async def find_message(channel, id):
    _id = f'ID: {id}'
    _found = False

    async for msg in channel.history(limit=1000):

        if _id in msg.content:
            return msg
    
    print(f'could not find message with id {id} in channel {channel}')
    return None

#generic function that can edit the dict of either harm or rerolls given a tuple argument, as both commands use to allow for names with spaces
def edit_harm_rerolls(dictToModify, inputTuple) -> bool:
    inputList = list(inputTuple)
    #basic input validation: we need at least two arguments, the last of which is parseable as an int
    if len(inputList) < 2 or not inputList[-1].isdigit():
        return False
    
    #using varargs, we assume the level was the last element passed
    level = int(inputList.pop(-1))
    if level < 0:
        return False

    #then, concat all remaining strings together, strip whitespace, and capitalize
    name = ''
    for string in inputList:
        name += f'{string} '
    name = name.strip()
    name = name.title()

    #if level 0, we want to remove the key:value pair from dict. otherwise, we just edit
    if level == 0 and name in dictToModify:
        del dictToModify[name]
        return True
    elif level > 0:
        dictToModify[name] = level
        return True
    else:
        return False


def create_charsheet(msg):
    _data = msg.content.split('\n')
    _charsheet = CharSheet()
    _charsheet.parse(_data)
    return _charsheet


# return player ID number from <@!number> format
def strip_id(raw_id):
    print(raw_id)
    _player = raw_id.split('<@!')
    _player = _player[1].split('>')
    _player = _player[0]
    return _player
