import discord
from discord.ext import commands
import os
from random import choice, randint

class WhoIs:

    """Some randome utilities that I threw together for school"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=True)
    async def userid(self, ctx, user: discord.Member):
        """Gives you the specified user's id"""
        await self.bot.say(user.id)

    @commands.command(pass_context=True)
    async def roles(self, ctx, user: discord.Member):
        """Lists all of a users roles"""
        await self.bot.say(user.roles)

    @commands.command(pass_context=True, no_pm=True)
    async def whois(self, ctx, user: discord.Member):
        """Gives you some info on a user"""
        realname = str(user)
        useravatarurl = user.avatar_url
        userid = user.id
        highestrole = user.top_role
        displayname = user.display_name
        author = ctx.message.author.name
        joined = user.joined_at
        userstatus = user.status
        userisbot = user.bot
        embed=discord.Embed(title="Username", description=realname, color=0xffb7b7)
        embed.set_thumbnail(url=str(useravatarurl))
        embed.add_field(name="User's ID", value=userid, inline=True)
        embed.add_field(name="Highest Role", value=highestrole, inline=False)
        embed.add_field(name="Current NIckname", value=displayname, inline=True)
        embed.add_field(name="Joined", value=joined, inline=False)
        embed.add_field(name="Status", value=userstatus, inline=True)
        embed.add_field(name="User is a bot", value=userisbot, inline=False)
        embed.set_footer(text="This command was called by " + author)
        await self.bot.say(embed=embed)

def setup(bot):
    bot.add_cog(WhoIs(bot))
