import sys
from discord.ext import commands
import utility

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
        try:
            self.bot.load_extension(s := ' '.join(args))
            await ctx.send(embed=utility.Embed(None,"Loaded `%s`" % s))
        except Exception as err:
            await ctx.send(embed=utility.Embed("Something went wrong", str(err)))
    @commands.command("unload")
    async def unload_(self,ctx,*args):
        try:
            self.bot.unload_extension(s := ' '.join(args))
            await ctx.send(embed=utility.Embed(None,"Unloaded `%s`" % s))
        except Exception as err:
            await ctx.send(embed=utility.Embed("Something went wrong", str(err)))
    @commands.command("reload")
    async def reload_(self,ctx,*args):
        try:
            self.bot.reload_extension(s := ' '.join(args))
            await ctx.send(embed=utility.Embed(None,"Reloaded `%s`" % s))
        except Exception as err:
            await ctx.send(embed=utility.Embed("Something went wrong", str(err)))
    @commands.command("shutdown")
    async def shutdown_(self,ctx,*args):
        await self.bot.logout()

def setup(bot: commands.Bot):
    bot.add_cog(Micah(bot))

def teardown(bot: commands.Bot):
    bot.remove_cog("Micah")