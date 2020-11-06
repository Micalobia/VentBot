import discord
from discord.ext import commands
import utility
import asyncio

class Venting(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_users = {}
    def cog_check(self, ctx: commands.Context):
        return ctx.guild is None
    async def monitor(self,msg: discord.Message):
        if msg.guild is not None: return
        aid = msg.author.id
        if not aid in self.active_users: return
        prefix = await discord.utils.maybe_coroutine(self.bot.get_prefix,msg)
        if msg.content.startswith(tuple(prefix)): return
        settings = self.bot.get_cog("Settings")
        gid = self.active_users[aid]["id"]
        guild = self.bot.get_guild(gid) or await self.bot.fetch_guild(gid)
        cid = settings[guild]["channel"]

        channel = self.bot.get_channel(cid) or await self.bot.fetch_channel(cid)
        await channel.send(msg.content)
        self.active_users[aid]["timer"].cancel()
        self.active_users[aid]["timer"] = asyncio.create_task(self.timer(self.active_users[aid]["event"]))
    async def timer(self,event: asyncio.Event):
        try:
            await asyncio.sleep(30)
            event.set()
        except asyncio.CancelledError:
            pass
    async def wait_to_stop(self,ctx: commands.Context,event: asyncio.Event):
        await event.wait()
        await ctx.invoke(self.stop_)
    @commands.command("stop")
    async def stop_(self,ctx: commands.Context):
        timer = self.active_users[ctx.author.id]["timer"]
        #if not (timer.done() and timer.cancelled()):
        timer.cancel()
        del timer
        del self.active_users[ctx.author.id]
        if len(self.active_users) == 0:
            self.bot.remove_listener(self.monitor, "on_message")
        await ctx.send(embed=utility.Embed(None,"Stopped watching for messages"))
    @commands.command("continue")
    async def continue_(self,ctx: commands.Context):
        timer = self.active_users[ctx.author.id]["timer"]
        if not (timer.done() and timer.cancelled()): timer.cancel()
        del timer
        self.active_users[ctx.author.id]["timer"] = asyncio.create_task(self.timer(self.active_users[ctx.author.id]["event"]))
    @commands.command("start")
    async def start_(self,ctx: commands.Context,arg):
        if ctx.author.id in self.active_users: ctx.invoke(self.stop_)
        try:
            gid = int(arg)
        except:
            embed = utility.Embed(None,"That isn't a valid server ID!")
            await ctx.send(embed=embed)
            return
        try:
            guild = self.bot.get_guild(gid) or await self.bot.fetch_guild(gid)
            member = guild.get_member(ctx.author.id) or await guild.fetch_member(ctx.author.id)
        except discord.Forbidden:
            embed = utility.Embed(None,"I couldn't find that server, are you sure I'm in it?")
            await ctx.send(embed=embed)
            return
        except:
            raise
        embed = utility.Embed("Monitoring your messages","Will go until you run `..stop` or 10 minutes of silence, use `..continue` to refresh timer")
        await ctx.send(embed=embed)
        event = asyncio.Event()
        self.active_users[ctx.author.id] = { "id":gid, "timer": asyncio.create_task(self.timer(event)), "event": event } 
        if len(self.active_users) == 1:
            self.bot.add_listener(self.monitor, "on_message")
        asyncio.create_task(self.wait_to_stop(ctx, event))

def setup(bot):
    bot.add_cog(Venting(bot))

def teardown(bot):
    bot.remove_cog("Venting")