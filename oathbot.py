import os
import discord
import asyncio
import copy
from discord.ext import commands
from dotenv import load_dotenv

from com.CoreCommands import CoreCommands
from discord_components import DiscordComponents, Button, ButtonStyle, Select, SelectOption, Interaction

from clss.CharSheet import CharSheet

load_dotenv("data/.env")

TOKEN = os.getenv('DISCORD_TOKEN')

oathbot = commands.Bot(command_prefix='!o ')

# add command cogs to runtime
oathbot.add_cog(CoreCommands(oathbot))

@oathbot.event
async def on_ready():
    print('////////////////////////////////////////')
    print(f'{oathbot.user} has connected to Discord!')
    print(f'Running discord.py version {discord.__version__}')
    print('////////////////////////////////////////')
    DiscordComponents(oathbot)

@oathbot.event
async def on_button_click(interaction:Interaction):
    _user = interaction.author.id
    if interaction.component.id == '-1stress':
        _data = interaction.message.content.split('\n')
        charsheet = CharSheet()
        charsheet.parse(_data)
        if charsheet.stress - 1 >= 0:
            charsheet.stress -= 1
        await interaction.respond(type=7, content=charsheet.print(), components=CoreCommands.quickMenu)

    if interaction.component.id == '+1stress':
        _data = interaction.message.content.split('\n')
        charsheet = CharSheet()
        charsheet.parse(_data)
        if charsheet.stress + 1 <= 9:
            charsheet.stress += 1
        await interaction.respond(type=7, content=charsheet.print(), components=CoreCommands.quickMenu)

    if interaction.component.id == "edit":
        _data = interaction.message.content.split('\n')
        _originalMessage = interaction.message
        charsheet = CharSheet()
        charsheet.parse(_data)
        await interaction.respond(type=7, content=charsheet.print(), components=CoreCommands.editMenu)
        while(True):
            try:
                select = await oathbot.wait_for("select_option", check=lambda inter: inter.message.id == _originalMessage.id, timeout=10)
            except asyncio.TimeoutError:
                await _originalMessage.edit(content=charsheet.print(), components=CoreCommands.quickMenu)
                return
            if select.values[0] == "finish":
                await select.respond(type=7, content=charsheet.print(), components=CoreCommands.quickMenu)
                break

            elif select.values[0] == "stress":
                statusButton = statusButton = Button(label = f"Current stress: {charsheet.stress}", disabled=True)
                components = copy.copy(CoreCommands.editButtons)
                components.append([statusButton])

                await select.respond(type=7, content=charsheet.print(), components=components)
                def minusStress(sheet):
                    sheet.stress -= (1 if sheet.stress > 0 else 0)
                    statusButton.label = f"Current stress: {sheet.stress}"
                def plusStress(sheet):
                    sheet.stress += (1 if sheet.stress < 9 else 0)
                    statusButton.label = f"Current stress: {sheet.stress}"
                if not await runEditLoop(minusOne = minusStress, plusOne = plusStress, charsheet = charsheet, originalMessage = _originalMessage, statusButton = statusButton):
                    return

            elif select.values[0] == "rerolls":
                rerollButtons = [
                    [Button(style=ButtonStyle.gray, label="Go Back", id="back"), Button(style=ButtonStyle.green, label="Finish Editing", id="finish")],
                    [Button(style=ButtonStyle.blue, label="Insight", id="Insight"), Button(style=ButtonStyle.blue, label="Prowess", id="Prowess"),
                    Button(style=ButtonStyle.blue, label="Resolve", id="Resolve"), Button(style=ButtonStyle.green, label="Any (crit)", id="Any")]
                ]
                await select.respond(type=7, content=charsheet.print(), components=rerollButtons)
                try:
                    rerollInter = await oathbot.wait_for("button_click", check=lambda inter: inter.message.id == _originalMessage.id, timeout=10)
                except asyncio.TimeoutError:
                    await _originalMessage.edit(content=charsheet.print(), components=CoreCommands.quickMenu)
                    return
                id = rerollInter.component.id
                if id == "back":
                    await rerollInter.respond(type=7, content=charsheet.print(), components=CoreCommands.editMenu)
                elif id == "finish":
                    await rerollInter.respond(type=7, content=charsheet.print(), components=CoreCommands.quickMenu)
                elif id == "Any" or id == "Insight" or id == "Prowess" or id == "Resolve":
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

                    components = copy.copy(CoreCommands.editButtons)
                    components.append([statusButton])

                    await rerollInter.respond(type=7, content=charsheet.print(), components=components)
                    if not await runEditLoop(minusOne = minusReroll, plusOne = plusReroll, charsheet = charsheet, originalMessage = _originalMessage, statusButton=statusButton):
                        return

            elif select.values[0] == "skills":
                insight = ['Hunt', 'Study', 'Survey', 'Tinker']
                prowess = ['Finesse', 'Prowl', 'Skirmish', 'Wreck']
                resolve = ['Aether', 'Command', 'Consort', 'Sway']
                skills = insight+prowess+resolve

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
                try:
                    skillInter = await oathbot.wait_for("button_click", check=lambda inter: inter.message.id == _originalMessage.id, timeout=10)
                except asyncio.TimeoutError:
                    await _originalMessage.edit(content=charsheet.print(), components=CoreCommands.quickMenu)
                    return
                id = skillInter.component.id
                if id == "back":
                    await skillInter.respond(type=7, content=charsheet.print(), components=CoreCommands.editMenu)
                elif id == "finish":
                    await skillInter.respond(type=7, content=charsheet.print(), components=CoreCommands.quickMenu)   
                elif id in skills:
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

                    components = copy.copy(CoreCommands.editButtons)
                    components.append([statusButton])

                    await skillInter.respond(type=7, content=charsheet.print(), components=components)
                    if not await runEditLoop(minusOne = minusSkill, plusOne = plusSkill, charsheet = charsheet, originalMessage = _originalMessage, statusButton = statusButton):
                        return

            elif select.values[0] == "recover":
                keys = copy.deepcopy(list(charsheet.harm.keys()))
                for key in keys:
                    value = charsheet.harm[key]
                    if value - 1 == 0:
                       del charsheet.harm[key]
                    else:
                        charsheet.harm[key] = value - 1
                await select.respond(type=7, content=charsheet.print(), components=CoreCommands.editMenu)

async def runEditLoop(minusOne, plusOne, charsheet, originalMessage, statusButton=None) -> bool:
    while(True):
        try:
            act = await oathbot.wait_for("button_click", check=lambda inter: inter.message.id == originalMessage.id, timeout=10)
        except asyncio.TimeoutError:
            await originalMessage.edit(content=charsheet.print(), components=CoreCommands.quickMenu)
            return False
        if act.component.id == "finish":
            await act.respond(type=7, content=charsheet.print(), components=CoreCommands.editMenu)
            return True
        elif act.component.id == "-1":
            minusOne(charsheet)
            components = CoreCommands.editButtons
            if statusButton != None:
                components = copy.copy(CoreCommands.editButtons)
                components.append([statusButton])
            await act.respond(type=7, content=charsheet.print(), components=components)
        elif act.component.id == "+1":
            plusOne(charsheet)
            components = CoreCommands.editButtons
            if statusButton != None:
                components = copy.copy(CoreCommands.editButtons)
                components.append([statusButton])
            await act.respond(type=7, content=charsheet.print(), components=components)
    return False

oathbot.run(TOKEN)
