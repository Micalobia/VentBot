from discord import Intents
from discord.ext.commands import Bot

intents = Intents.default()
intents.members = True
bot = Bot(command_prefix='..', help_command=None, intents=intents)

discord_token = None
with open('./data/tokens/discord.token','r') as file:
    discord_token = file.read()