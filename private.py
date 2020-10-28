from discord.ext.commands import Bot

bot = Bot(command_prefix='..', help_command=None)

discord_token = None
with open('./data/tokens/discord.token','r') as file:
    discord_token = file.read()