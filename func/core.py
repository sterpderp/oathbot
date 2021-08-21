import json
import discord
import asyncio
import copy
from discord.ext import commands
from clss.CharSheet import CharSheet
from discord_components import DiscordComponents, Button, ButtonStyle, Select, SelectOption, Interaction

resistances = ['Insight', 'Prowess', 'Resolve']
insight = ['Hunt', 'Study', 'Survey', 'Tinker']
prowess = ['Finesse', 'Prowl', 'Skirmish', 'Wreck']
resolve = ['Aether', 'Command', 'Consort', 'Sway']
skills = insight+prowess+resolve

quickMenu = [
    [Button(style=ButtonStyle.green, label='-1 Stress', id='-1stress'), 
    Button(style=ButtonStyle.blue, label="Edit", id="edit"),
    Button(style=ButtonStyle.red, label='+1 Stress', id='+1stress')]
]
editMenu = [[
    Select(placeholder="Select field to edit.", options = [
        SelectOption(label = "Finish Editing", value="finish"),
        SelectOption(label = "Stress", value="stress"),
        SelectOption(label = "Rerolls", value="rerolls"),
        SelectOption(label = "Skills", value="skills"),
        SelectOption(label = "Recover (Reduce all Harm by 1)", value="recover")
    ])
]]
editButtons = [
    [
        Button(style=ButtonStyle.red, label='-1', id='-1'),
        Button(style=ButtonStyle.blue, label='Finish', id='finish'),
        Button(style=ButtonStyle.green, label='+1', id='+1')
    ]
]

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
    _data = [s for s in _data if '\u2014' not in s]
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
    _player = filter(str.isdigit, raw_id)
    _player = "".join(_player)
    print(_player)
    return _player

#Function meant to abstract the +1/-1 edit loop when a specific field has been chosen for edit.
async def runEditLoop(minusOne, plusOne, charsheet, originalMessage, oathbot, statusButton=None) -> bool:
    while(True):
        #Setup a 10s timeout which pops us back out to the top-level menu if it triggers
        try:
            act = await oathbot.wait_for("button_click", check=lambda inter: inter.message.id == originalMessage.id, timeout=10)
        except asyncio.TimeoutError:
            await originalMessage.edit(content=charsheet.print(), components=quickMenu)
            return False
        if act.component.id == "finish":
            await act.respond(type=7, content=charsheet.print(), components=editMenu)
            return True
        elif act.component.id == "-1":
            minusOne(charsheet)
            components = editButtons
            if statusButton != None:
                components = copy.copy(editButtons)
                components.append([statusButton])
            await act.respond(type=7, content=charsheet.print(), components=components)
        elif act.component.id == "+1":
            plusOne(charsheet)
            components = editButtons
            if statusButton != None:
                components = copy.copy(editButtons)
                components.append([statusButton])
            await act.respond(type=7, content=charsheet.print(), components=components)
    return False

async def runEditMenu(interaction:Interaction, oathbot):
    #setup variables and respond to Edit button press
    _data = interaction.message.content.split('\n')
    _originalMessage = interaction.message
    charsheet = CharSheet()
    charsheet.parse(_data)
    await interaction.respond(type=7, content=charsheet.print(), components=editMenu)

    #Core input loop that runs when the field select dropdown shows.
    while(True):
        #await response from select dropdown, lockout of 10 seconds, after which the original buttons will be edited back onto post.
        try:
            select = await oathbot.wait_for("select_option", check=lambda inter: inter.message.id == _originalMessage.id, timeout=10)
        except asyncio.TimeoutError:
            await _originalMessage.edit(content=charsheet.print(), components=quickMenu)
            return

        #When "Finish Editing" select option is picked, edit original buttons back onto post.
        if select.values[0] == "finish":
            await select.respond(type=7, content=charsheet.print(), components=quickMenu)
            break

        #When Stress select option is picked, enter an edit loop where user clicks -1/+1 buttons until they're finished.
        elif select.values[0] == "stress":
            #StatusButton is a little grey disabled button that shows the current value of the field you are editing.
            #This is useful for mobile users with small screens, or just people who dont wanna look up to the post being edited.
            statusButton = statusButton = Button(label = f"Current stress: {charsheet.stress}", disabled=True)
            components = copy.copy(editButtons)
            components.append([statusButton])

            #respond by editing editButtons and appended statusbutton onto the original post
            await select.respond(type=7, content=charsheet.print(), components=components)

            #These are callback functions for what happens when the -1 and +1 buttons are pressed in the loop
            def minusStress(sheet):
                sheet.stress -= (1 if sheet.stress > 0 else 0)
                statusButton.label = f"Current stress: {sheet.stress}"
            def plusStress(sheet):
                sheet.stress += (1 if sheet.stress < 9 else 0)
                statusButton.label = f"Current stress: {sheet.stress}"

            #run loop -- if it times out, it will return False, and thus we should return out of the func as well.
            if not await runEditLoop(minusOne = minusStress, plusOne = plusStress, charsheet = charsheet, originalMessage = _originalMessage, oathbot=oathbot, statusButton = statusButton):
                return

        #When rerolls option is picked, first we must display an intermediate step where the user picks which type of reroll they want to edit.
        elif select.values[0] == "rerolls":
            rerollButtons = [
                [Button(style=ButtonStyle.gray, label="Go Back", id="back"), Button(style=ButtonStyle.green, label="Finish Editing", id="finish")],
                [Button(style=ButtonStyle.blue, label="Insight", id="Insight"), Button(style=ButtonStyle.blue, label="Prowess", id="Prowess"),
                Button(style=ButtonStyle.blue, label="Resolve", id="Resolve"), Button(style=ButtonStyle.green, label="Any (crit)", id="Any")]
            ]
            await select.respond(type=7, content=charsheet.print(), components=rerollButtons)
            
            #Process intermediate step callback
            try:
                rerollInter = await oathbot.wait_for("button_click", check=lambda inter: inter.message.id == _originalMessage.id, timeout=10)
            except asyncio.TimeoutError:
                await _originalMessage.edit(content=charsheet.print(), components=quickMenu)
                return
            id = rerollInter.component.id
            if id == "back":
                await rerollInter.respond(type=7, content=charsheet.print(), components=editMenu)
            elif id == "finish":
                await rerollInter.respond(type=7, content=charsheet.print(), components=quickMenu)
            elif id == "Any" or id == "Insight" or id == "Prowess" or id == "Resolve":
                #When a valid reroll type is selected, we setup the statusButton and callbacks for the editLoop, edit them onto the post, then enter the edit loop.
                statusButton = Button(label = f"Current {id} rerolls: {charsheet.rerolls[id] if id in charsheet.rerolls else 0}", disabled=True)
                def minusReroll(sheet):
                    if id in sheet.rerolls:
                        value = sheet.rerolls[id] - 1
                        if value == 0:
                            del sheet.rerolls[id]
                        else:
                            sheet.rerolls[id] = value
                        statusButton.label = f"Current {id} rerolls: {sheet.rerolls[id] if id in sheet.rerolls else 0}"
                def plusReroll(sheet):
                    if id in sheet.rerolls:
                        sheet.rerolls[id] = sheet.rerolls[id] + 1
                    else:
                        sheet.rerolls[id] = 1
                    statusButton.label = f"Current {id} rerolls: {sheet.rerolls[id] if id in sheet.rerolls else 0}"

                components = copy.copy(editButtons)
                components.append([statusButton])

                await rerollInter.respond(type=7, content=charsheet.print(), components=components)
                if not await runEditLoop(minusOne = minusReroll, plusOne = plusReroll, charsheet = charsheet, originalMessage = _originalMessage, oathbot=oathbot, statusButton=statusButton):
                    return

        #When skills option is picked, much like rerolls, we enter an intermediate step where we give them the option of which of the 12 skills they want to edit
        elif select.values[0] == "skills":
            skillButtons = [
                [Button(style=ButtonStyle.gray, label="Go Back", id="back"), Button(style=ButtonStyle.green, label="Finish Editing", id="finish"),],
                [Button(style=ButtonStyle.blue, label="Hunt", id="Hunt"), Button(style=ButtonStyle.blue, label="Study", id="Study"),
                Button(style=ButtonStyle.blue, label="Survey", id="Survey"),Button(style=ButtonStyle.blue, label="Tinker", id="Tinker")],
                [Button(style=ButtonStyle.red, label="Finesse", id="Finesse"), Button(style=ButtonStyle.red, label="Prowl", id="Prowl"),
                Button(style=ButtonStyle.red, label="Skirmish", id="Skirmish"),Button(style=ButtonStyle.red, label="Wreck", id="Wreck")],
                [Button(style=ButtonStyle.green, label="Aether", id="Aether"), Button(style=ButtonStyle.green, label="Command", id="Command"),
                Button(style=ButtonStyle.green, label="Consort", id="Consort"),Button(style=ButtonStyle.green, label="Sway", id="Sway")],
            ]
            await select.respond(type=7, content=charsheet.print(), components=skillButtons)

            #process intermediate step
            try:
                skillInter = await oathbot.wait_for("button_click", check=lambda inter: inter.message.id == _originalMessage.id, timeout=10)
            except asyncio.TimeoutError:
                await _originalMessage.edit(content=charsheet.print(), components=quickMenu)
                return
            id = skillInter.component.id
            if id == "back":
                await skillInter.respond(type=7, content=charsheet.print(), components=editMenu)
            elif id == "finish":
                await skillInter.respond(type=7, content=charsheet.print(), components=quickMenu)   
            elif id in skills:
                #When a valid skill is picked, we setup the callbacks and status button, edit them onto the post, then enter the edit loop
                statusButton = Button(label = f"Current {id} pips: {charsheet.skills[id] if id in charsheet.skills else 0}", disabled=True)

                def minusSkill(sheet):
                    if id in sheet.skills:
                        value = sheet.skills[id]
                        if value - 1 > 0:
                            sheet.skills[id] = value - 1
                        elif value - 1 == 0:
                            sheet.skills[id] = value - 1
                            if id in insight:
                                sheet.i_pips -= 1
                            elif id in prowess:
                                sheet.p_pips -= 1
                            elif id in resolve:
                                sheet.r_pips -= 1
                        statusButton.label = f"Current {id} pips: {sheet.skills[id] if id in sheet.skills else 0}"
                            
                def plusSkill(sheet):
                    if id in sheet.skills:
                        value = sheet.skills[id]
                        if value == 0:
                            if id in insight:
                                sheet.i_pips += 1
                            elif id in prowess:
                                sheet.p_pips += 1
                            elif id in resolve:
                                sheet.r_pips += 1
                        sheet.skills[id] = value + 1
                        statusButton.label = f"Current {id} pips: {sheet.skills[id] if id in sheet.skills else 0}"

                components = copy.copy(editButtons)
                components.append([statusButton])

                await skillInter.respond(type=7, content=charsheet.print(), components=components)
                if not await runEditLoop(minusOne = minusSkill, plusOne = plusSkill, charsheet = charsheet, originalMessage = _originalMessage, oathbot=oathbot, statusButton = statusButton):
                    return

        #This one's really easy. Simply iterate through all the harms in the dict, reduce them by 1, delete them if they hit 0, then respond to the interaction.
        elif select.values[0] == "recover":
            keys = copy.deepcopy(list(charsheet.harm.keys()))
            for key in keys:
                value = charsheet.harm[key]
                if value - 1 == 0:
                    del charsheet.harm[key]
                else:
                    charsheet.harm[key] = value - 1
            await select.respond(type=7, content=charsheet.print(), components=editMenu)