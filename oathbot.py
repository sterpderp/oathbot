import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

from com.CoreCommands import CoreCommands
from func import core
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
        await core.runEditMenu(interaction, oathbot)
        


oathbot.run(TOKEN)
