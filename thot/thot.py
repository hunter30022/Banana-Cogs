import discord
from discord.ext import commands
from .utils.dataIO import fileIO
from random import choice as randchoice
import os

class Thot:
    """Banana's Thot Cog (Based off of Airenkun's Insult Cog)"""
    def __init__(self, bot):
        self.bot = bot
        self.thotchoices = fileIO("data/thot/thotchoices.json","load")

    @commands.command(pass_context=True, no_pm=True)
    async def thot(self, ctx, user : discord.Member=None):
        If not user:
            user = ctx.message.author
        """Determines if a user is a thot or not"""
        await self.bot.say("{} {}".format(user.mention, randchoice(self.thotchoices)))

def setup(bot):
    bot.add_cog(Thot(bot))
