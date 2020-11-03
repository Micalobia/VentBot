import json
from private import bot, discord_token

@bot.command()
async def ping(ctx,/):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

@bot.event
async def on_ready():
    print('------')
    print(f'{bot.user.name} is ready!')
    print(bot.user.id)
    print('------')

extensions = []
with open('./data/extensions.json','r') as file:
    extensions = json.load(file)
print('------')
for extension in extensions:
    bot.load_extension(extension)

bot.run(discord_token)