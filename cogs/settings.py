import discord
from discord.ext import commands
from discord.ext import tasks
import sqlite3 as sq
import shutil as sh
import utility
import re

class Settings(commands.Cog):
    def __init__(self,bot: commands.Bot):
        self.bot = bot
        self.bot.command_prefix = self.command_prefix
        self.__cache = {}
        self.path = "./data/settings/%s"
        self.default_settings = {
            "channel": 0,
            "adminrole": 0,
            "prefix": ".."
        }
        self.backup_index = 0
        self.clear_cache.start() # pylint: disable=no-member
        self.backup.start()      # pylint: disable=no-member
        print("Loaded Settings Cog")
    def cog_unload(self):
        self.backup.stop()       # pylint: disable=no-member
        self.clear_cache.restart()  # pylint: disable=no-member
        self.clear_cache.stop()
        self.command_prefix = ["..",f"<@{self.bot.user.id}> ", f"<@!{self.bot.user.id}> "]
        print("Unloaded Settings Cog")
    def command_prefix(self, bot: commands.Bot, msg: discord.Message):
        ret = []
        if msg.guild is None:
            ret = [".."]
        else:
            ret = [self[msg.guild]["prefix"]]
        ret.extend([f"<@{self.bot.user.id}> ", f"<@!{self.bot.user.id}> "])
        return ret
    @tasks.loop(minutes=15)
    async def clear_cache(self,/):
        conn = sq.connect(self.path % "settings.db")
        cursor = conn.cursor()
        cursor.execute("BEGIN;")
        for gid in self.__cache:
            s = self.__cache[gid]
            cursor.execute("REPLACE INTO guilds (id,channel,adminrole,prefix) VALUES (?,?,?,?);", (gid, s['channel'], s['adminrole'], s['prefix']))
        cursor.execute('COMMIT;')
        cursor.close()
        conn.close()
        self.__cache = {}
        print("Cleared cache")
    @tasks.loop(hours=1)
    async def backup(self,/):
        try:
            sh.copyfile(self.path % "settings.db", self.path % ("settings.%s.backup" % self.backup_index))
        except:
            pass
        print("Backed up into backup #%s" % (self.backup_index + 1))
        self.backup_index = (self.backup_index + 1) % 3
    def __fetch(self,guild: discord.Guild,/):
        gid = guild.id
        if gid in self.__cache: return
        conn = sq.connect(self.path % "settings.db")
        cursor = conn.cursor()
        cursor.execute("SELECT channel,adminrole,prefix FROM guilds WHERE id==%s" % gid)
        fetched = cursor.fetchall()
        cursor.close()
        conn.close()
        if len(fetched) == 0:
            self.__cache[gid] = self.default_settings.copy()
            self.__cache[gid]["channel"] = guild.system_channel.id if guild.system_channel is not None else 0
            return
        ret = {}
        ret["channel"] = fetched[0][0]
        ret["adminrole"] = fetched[0][1]
        ret["prefix"] = fetched[0][2]
        self.__cache[gid] = ret
    def __getitem__(self,guild: discord.Guild,/) -> dict:
        self.__fetch(guild)
        return self.__cache[guild.id]
    def __setitem__(self,guild: discord.Guild,value: dict,/):
        self.__cache[guild.id] = value
    @commands.group("settings",aliases=["setting"])
    async def settings_(self,ctx: commands.Context):
        if ctx.invoked_subcommand is not None: return
        if ctx.guild is None: return
        settings = self[ctx.guild]
        channel = "No Channel Selected" if settings["channel"] == 0 else "<#%s>" % settings["channel"]
        adminrole = "Owner" if settings["adminrole"] == 0 else "<@&%s>" % settings["adminrole"]
        prefix = "`%s`" % settings["prefix"]
        embed = utility.Embed("Settings","Channel: %s\nAdmin Role: %s\nPrefix: %s" % (channel, adminrole, prefix))
        await ctx.send(embed=embed)
    @settings_.command("channel")
    async def settings_channel_(self,ctx: commands.Context,arg: str = None):
        if ctx.guild is None: return
        if arg is None:
            channel = "No Channel Selected" if self[ctx.guild]["channel"] == 0 else "<#%s>" % self[ctx.guild]["channel"]
            embed = utility.Embed("Settings","Channel: %s" % channel)
            await ctx.send(embed=embed)
            return
        adminrole = self[ctx.guild]["adminrole"]
        userroles = [_.id for _ in ctx.author.roles]
        if ctx.author.id == ctx.guild.owner.id or adminrole in userroles:
            reg = r"(?<=<#)\d{7,19}(?=>)"
            match = re.search(reg, arg)
            if match is None:
                try:
                    ID = int(arg)
                except:
                    embed = utility.Embed("Settings","That isn't a valid channel! Try typing #`channel-name`, or use the ID!")
                    await ctx.send(embed)
            else:
                ID = int(match[0])
            self[ctx.guild]["channel"] = ID
            embed = utility.Embed("Settings", "Set channel to: <#%s>" % ID)
            await ctx.send(embed=embed)
        else:
            embed = utility.Embed("Settings","You aren't in the admin role or the owner!")
            await ctx.send(embed=embed)
    @settings_.command("adminrole",aliases=["admin"])
    async def settings_adminrole_(self,ctx: commands.Context, arg: str = None):
        if ctx.guild is None: return
        if arg is None:
            admin = "Owner" if self[ctx.guild]["adminrole"] == 0 else "<@&%s>" % self[ctx.guild]["adminrole"]
            embed = utility.Embed("Settings","Admin Role: %s" % admin)
            await ctx.send(embed=embed)
            return
        adminrole = self[ctx.guild]["adminrole"]
        userroles = [_.id for _ in ctx.author.roles]
        if ctx.author.id == ctx.guild.owner.id or adminrole in userroles:
            reg = r"(?<=<@&)\d{7,19}(?=>)"
            match = re.search(reg, arg)
            if match is None:
                try:
                    ID = int(arg)
                except:
                    embed = utility.Embed("Settings","That isn't a valid role! Try pinging the role, or use the ID!")
                    await ctx.send(embed)
            else:
                ID = int(match[0])
            self[ctx.guild]["adminrole"] = ID
            embed = utility.Embed("Settings", "Set adminrole to: <@&%s>" % ID)
            await ctx.send(embed=embed)
        else:
            embed = utility.Embed("Settings","You aren't in the admin role or the owner!")
            await ctx.send(embed=embed)
    @settings_.command("prefix")
    async def settings_prefix_(self,ctx,*args):
        if ctx.guild is None: return
        pref = " ".join(args)
        if len(pref) == 0:
            pref = self[ctx.guild]["prefix"]
            embed = utility.Embed("Settings","Prefix: `%s`" % pref)
            await ctx.send(embed=embed)
            return
        adminrole = self[ctx.guild]["adminrole"]
        userroles = [_.id for _ in ctx.author.roles]
        if ctx.author.id == ctx.guild.owner.id or adminrole in userroles:
            if len(pref) > 4:
                embed = utility.Embed("Settings","Prefix can't be more than 4 characters!")
                await ctx.send(embed=embed)
                return
            self[ctx.guild]["prefix"] = pref
            embed = utility.Embed("Settings", "Set prefix to: `%s`" % pref)
            await ctx.send(embed=embed)
        else:
            embed = utility.Embed("Settings","You aren't in the admin role or the owner!")
            await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Settings(bot))

def teardown(bot: commands.Bot):
    bot.remove_cog("Settings")