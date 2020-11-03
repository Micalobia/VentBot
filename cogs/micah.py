import sys
from discord.ext import commands

class Micah(commands.Cog):
    def __init__(self,bot: commands.Bot,/):
        self.bot = bot
        print("Loaded Micah Cog")
    def cog_unload(self):
        print("Unloaded Micah Cog")
    def cog_check(self,ctx):
        return ctx.author.id == 299740962035335168 # Das me
    @commands.command("load")
    async def load_(self,ctx,*args):
        self.bot.load_extension(' '.join(args))
    @commands.command("unload")
    async def unload_(self,ctx,*args):
        self.bot.unload_extension(' '.join(args))
    @commands.command("reload")
    async def reload_(self,ctx,*args):
        self.bot.reload_extension(' '.join(args))
    @commands.command("shutdown")
    async def shutdown_(self,ctx,*args):
        sys.exit()

def setup(bot: commands.Bot):
    bot.add_cog(Micah(bot))

def teardown(bot: commands.Bot):
    bot.remove_cog("Micah")