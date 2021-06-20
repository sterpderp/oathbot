import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

from com.CoreCommands import CoreCommands

load_dotenv("data/.env")

TOKEN = os.getenv('DISCORD_TOKEN')

oathbot = commands.Bot(command_prefix='!b ')

# add command cogs to runtime
oathbot.add_cog(CoreCommands(oathbot))


@oathbot.event
async def on_ready():
    print('////////////////////////////////////////')
    print(f'{oathbot.user} has connected to Discord!')
    print(f'Running discord.py version {discord.__version__}')
    print('////////////////////////////////////////')

oathbot.run(TOKEN)
