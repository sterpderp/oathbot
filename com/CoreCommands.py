import discord
from discord.ext import commands

from func import core
from clss.CharSheet import CharSheet


class CoreCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

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
                print(_charsheet)
                print(_ipr)
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

        async for msg in channel.history(limit=1000):

            if _id in msg.content:
                _data = msg.content.split('\n')
                _charsheet = CharSheet()
                _charsheet.parse(_data)

                print(_charsheet.skills)

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

                await channel.send(f'Echoing character sheet with ID: {_id}\n' + _charsheet.print())

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
