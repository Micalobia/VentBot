import discord
import json
from discord.ext import commands
from discord.embeds import EmptyEmbed
from private import bot
from typing import Union, TextIO
from datetime import datetime

def Embed(title: str=None, description: str=None, /) -> discord.Embed:
    ret = discord.Embed()
    ret.color = discord.Color(0x6FA9DE)
    ret.set_author(name="VentBot",icon_url=bot.user.avatar_url)
    if title is not None: ret.title = title
    if description is not None: ret.description = description
    return ret

def JSONEmbed(guild: discord.Guild, path: str) -> discord.Embed:
    with open(path) as file:
        data = json.load(file)
    ret = Embed(data.get("title"), data.get("description"))
    if "color" in data: ret.color = discord.Color(int(data["color"],base=16))
    if "url" in data: ret.url = data["url"]
    if "author" in data:
        ret.set_author(
            name=data["author"].get("name"),
            icon_url=data["author"].get("icon_url",EmptyEmbed),
            url=data["author"].get("url",EmptyEmbed)
        )
    if "description" in data: ret.description = data["description"]
    if "thumbnail" in data:
        ret.set_thumbnail(
            url=data["thumbnail"].get("url")
        )
    if "fields" in data:
        for field in data["fields"]:
            ret.add_field(
                name=field.get("name"),
                value=field.get("value"),
                inline=field.get("inline",True)
            )
    if "image" in data:
        ret.set_image(
            url=data["image"].get("url")
        )
    if "timestamp" in data:
        if data["timestamp"] == True:
            ret.timestamp = datetime.now()
        else:
            ret.timestamp = datetime.utcfromtimestamp(data["timestamp"])
    if "footer" in data:
        ret.set_footer(
            text=data["footer"].get("text",EmptyEmbed),
            icon_url=data["footer"].get("icon_url",EmptyEmbed)
        )
    return ret