import discord
from discord.ext import commands

from func import core

class CoreCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def findsheet(self, ctx, char_id):
        _id = f'ID: {char_id}'
        _number_msg = 0
        _charsheet = ''
        _found = False
        _msg_id = []

        async for msg in ctx.channel.history(limit=1000):
            _number_msg += 1

            if _id in msg.content:
                _charsheet = msg.content.split('\n')
                print(_charsheet)
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
