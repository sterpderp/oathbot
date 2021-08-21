import discord
import time
import os
from discord.ext import commands

from func import core, image
from clss.CharSheet import CharSheet

from discord_components import *

class CoreCommands(commands.Cog):
    quickMenu = [[Button(style=ButtonStyle.green, label='-1 Stress', id='-1stress'), Button(style=ButtonStyle.blue, label="Edit", id="edit"), Button(style=ButtonStyle.red, label='+1 Stress', id='+1stress')]]
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

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def testimage(self, ctx):
        start = time.time()
        channel = discord.utils.get(ctx.guild.channels, name='oath-sheets')
        path = image.test()
        afterImage = time.time()
        await channel.send(file=discord.File(path))
        end = time.time()
        await channel.send(f'Image generated in {afterImage - start} seconds and took {end - afterImage} seconds to post to discord.')

    @commands.command()
    async def render(self, ctx, char_id):
        channel = discord.utils.get(ctx.guild.channels, name='oath-sheets')

        _id = f'ID: {char_id}'
        _found = False
        _charsheet = CharSheet()
        assetsPath = os.path.abspath("assets")

        msg = await core.find_message(channel, char_id)
        if msg and (msg.author.id == self.bot.user.id):
            _charsheet = core.create_charsheet(msg)

        attachFP = ""

        if any(msg.attachments):
            for attachment in msg.attachments:
                if attachment.filename.lower().endswith(".png"):
                    attachFP = assetsPath + f"\\{char_id}_portrait.png"
                    await attachment.save(attachFP)

        path = image.render(_charsheet, "ornate coords", attachFP)
        await channel.send(file=discord.File(path))

        

    @commands.command()
    async def findsheet(self, ctx, char_id):
        channel = discord.utils.get(ctx.guild.channels, name='oath-sheets')

        _id = f'ID: {char_id}'
        _number_msg = 0
        _charsheet = ''
        _found = False
        _msg_id = []

        async for msg in channel.history(limit=1000):
            _number_msg += 1

            if _id in msg.content:
                _charsheet = msg.content.split('\n')
                _ipr = core.ipr_split(_charsheet[2])



                _found = True
                _msg_id.append(msg.id)

            else:
                pass

        print(f'{_number_msg} messages parsed!')

        if _found:
            await ctx.send(f'Character ID **{char_id}** found!\n'
                           f'Message ID {_msg_id}\n'
                           f'{_number_msg} messages parsed!')
        else:
            await ctx.send(f'Character ID **{char_id}** not found!\n'
                           f'{_number_msg} messages parsed!')

    @commands.command()
    async def register(self, ctx, char_id):
        channel = discord.utils.get(ctx.guild.channels, name='oath-sheets')
        _id = f'ID: {char_id}'
        _found = False
        assetsPath = os.path.abspath("assets")

        async for msg in channel.history(limit=1000):

            if (msg.author.id != self.bot.user.id) and _id in msg.content:
                _data = msg.content.split('\n')
                _charsheet = CharSheet()
                _charsheet.parse(_data)

                if any(msg.attachments):
                    for attachment in msg.attachments:
                        if attachment.filename.lower().endswith(".png"):
                            await attachment.save(assetsPath + f"\\{char_id}.png")

                discFile = discord.File(assetsPath + f"\\{char_id}.png")
                await channel.send(_charsheet.print(), components=CoreCommands.quickMenu, file=discFile)
                await msg.delete()

    @commands.command()
    async def echo(self, ctx, char_id):
        channel = discord.utils.get(ctx.guild.channels, name='oath-sheets')
        _id = f'ID: {char_id}'
        _found = False

        async for msg in channel.history(limit=1000):

            if _id in msg.content:
                _data = msg.content.split('\n')
                _charsheet = CharSheet()
                _charsheet.parse(_data)

                print(f'Raw data: {_data}')

                await channel.send(f'Echoing character sheet with {_id}\n' + _charsheet.print())
    
    #generic resistance command that expects the name of the resistance being edited as an argument
    @commands.command(name="resistance", aliases=['resist', 'resistances', 'res', 'Resistance', 'Resist', 'Resistances', 'Res'])
    async def resistance(self, ctx, char_id:str, resistance_name:str, amount:int):
        channel = discord.utils.get(ctx.guild.channels, name='oath-sheets')
        msg = await core.find_message(channel, char_id)
        if msg and (msg.author.id == self.bot.user.id):
            charsheet = core.create_charsheet(msg)
            resistance_name = resistance.name.title()
            if amount >= 0 and resistance_name in core.resistances:
                if resistance_name == 'Insight':
                    charsheet.i_pips = amount
                elif resistance_name == 'Prowess':
                    charsheet.p_pips = amount
                elif resistance_name == 'Resolve':
                    charsheet.r_pips = amount
                
            await msg.edit(content=charsheet.print())

    #passthrough utility commands for modifying insight, prowess, or resolve
    @commands.command(name='insight', aliases=['Insight', 'I', 'i'])
    async def insight(self, ctx, char_id:str, amount:int):
        await resistance(ctx, char_id, 'Insight', amount)

    @commands.command(name='prowess', aliases=['Prowess', 'P', 'p'])
    async def prowess(self, ctx, char_id:str, amount:int):
        await resistance(ctx, char_id, 'Prowess', amount)

    @commands.command(name='resolve', aliases=['Resolve', 'R', 'r'])
    async def resolve(self, ctx, char_id:str, amount:int):
        await resistance(ctx, char_id, 'Resolve', amount)

    @commands.command(name="skill", aliases=core.skills + [s.lower() for s in core.skills])
    async def skill(self, ctx, char_id:str, amount:int):
        channel = discord.utils.get(ctx.guild.channels, name='oath-sheets')
        msg = await core.find_message(channel, char_id)
        if msg and (msg.author.id == self.bot.user.id):
            charsheet = core.create_charsheet(msg)
            
            #setup data to find the alias they used to call this command (saves us from having 12 identical passthrough functions)
            stringlist = ctx.message.content.split(' ')
            print(stringlist)

            #check whether the first word passed (alias of command) exists in list of all skill names
            if amount >= 0 and len(stringlist) > 1 and stringlist[1].title() in core.skills:
                skillname = stringlist[1].title()

                lastamount = charsheet.skills[skillname]
                charsheet.skills[skillname] = amount

                #using lastAmount compared to the newAmount, we can also determine whether resistance pips should be updated
                resistancemod = 0
                if amount > 0 and lastamount == 0: resistancemod = 1
                elif amount == 0 and lastamount > 0: resistancemod = -1

                if resistancemod != 0:
                    if skillname in core.insight:
                        charsheet.i_pips += resistancemod
                    if skillname in core.prowess:
                        charsheet.p_pips += resistancemod
                    if skillname in core.resolve:
                        charsheet.r_pips += resistancemod
                
                await msg.edit(content=charsheet.print())

    @commands.command(name="stress", aliases=['Stress'])
    async def stress(self, ctx, char_id:str, amount:int):
        channel = discord.utils.get(ctx.guild.channels, name='oath-sheets')
        msg = await core.find_message(channel, char_id)
        if msg and (msg.author.id == self.bot.user.id):
            charsheet = core.create_charsheet(msg)
            if amount >= 0:
                charsheet.stress = amount
            await msg.edit(content=charsheet.print())

    @commands.command(name="trauma", aliases=['Trauma'])
    async def trauma(self, ctx, char_id:str, *traumaName:str):
        channel = discord.utils.get(ctx.guild.channels, name='oath-sheets')
        msg = await core.find_message(channel, char_id)
        if msg and (msg.author.id == self.bot.user.id):
            charsheet = core.create_charsheet(msg)
            traumaNameList = list(traumaName)
            name = ''
            for s in traumaNameList:
                name += f'{s} '
            name = name.strip()
            name = name.title()

            if name in charsheet.trauma:
                charsheet.trauma.remove(name)
            else:
                charsheet.trauma.append(name)
            await msg.edit(content=charsheet.print())

    @commands.command(name="harm", aliases=['Harm'])
    async def harm(self, ctx, char_id:str, *nameAndLevel):
        channel = discord.utils.get(ctx.guild.channels, name='oath-sheets')
        msg = await core.find_message(channel, char_id)
        if msg and (msg.author.id == self.bot.user.id):
            charsheet = core.create_charsheet(msg)

            if core.edit_harm_rerolls(charsheet.harm, nameAndLevel):
                await msg.edit(content=charsheet.print())

    @commands.command(name="rerolls", aliases=['reroll, Rerolls, rerolls'])
    async def rerolls(self, ctx, char_id:str, *nameAndLevel):
        channel = discord.utils.get(ctx.guild.channels, name='oath-sheets')
        msg = await core.find_message(channel, char_id)
        if msg and (msg.author.id == self.bot.user.id):
            charsheet = core.create_charsheet(msg)

            if core.edit_harm_rerolls(charsheet.rerolls, nameAndLevel):
                await msg.edit(content=charsheet.print())

    # print the text of a given rule as a message
    @commands.command()
    async def rules(self, ctx, rule):
        _rule = rule.lower()
        _rules_list = core.rules_loader()
        _rules_error = f"**{rule}** is not a defined rule! {_rules_list['list']}"

        if rule in _rules_list:
            await ctx.send(_rules_list[_rule])
        else:
            await ctx.send(_rules_error)
