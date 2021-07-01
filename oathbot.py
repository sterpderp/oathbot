import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

from com.CoreCommands import CoreCommands
from discord_components import *

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
    if interaction.component.id == '-1stress':
        _data = interaction.message.content.split('\n')
        charsheet = CharSheet()
        charsheet.parse(_data)
        if charsheet.stress - 1 >= 0:
            charsheet.stress -= 1
        await interaction.respond(type=InteractionType.UpdateMessage, content=charsheet.print(), components=[[Button(style=ButtonStyle.green, label='-1 Stress', id='-1stress'), Button(style=ButtonStyle.red, label='+1 Stress', id='+1stress')]])

    if interaction.component.id == '+1stress':
        _data = interaction.message.content.split('\n')
        charsheet = CharSheet()
        charsheet.parse(_data)
        if charsheet.stress + 1 <= 9:
            charsheet.stress += 1
        await interaction.respond(type=InteractionType.UpdateMessage, content=charsheet.print(), components=[[Button(style=ButtonStyle.green, label='-1 Stress', id='-1stress'), Button(style=ButtonStyle.red, label='+1 Stress', id='+1stress')]])
    

oathbot.run(TOKEN)
