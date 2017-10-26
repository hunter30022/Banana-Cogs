import discord
from discord.ext import commands
from cogs.utils.dataIO import dataIO
from collections import namedtuple, defaultdict, deque
from datetime import datetime
from copy import deepcopy
from cogs.utils import checks
from cogs.utils.chat_formatting import pagify, box
from enum import Enum
from __main__ import send_cmd_help
import os
import time
import logging
from random import choice


class Economy:
        """Created so I could call the economy API"""



        def __init__(self, bot):
            self.bot = bot
            self.settings = dataIO.load_json('data/autoeconomy/settings.json')
            self.banksettings = dataIO.load_json('data/economy/settings.json')
            self.version = "0.1.1b"

        async def save_settings(self):
            dataIO.save_json('data/autoeconomy/settings.json', self.settings)

        async def _data_check(self, ctx):
            server = ctx.message.server
            if server.id not in self.settings:
                self.settings[server.id] = deepcopy(default_settings)
                self.settings[server.id]["CHANNEL"] = ctx.message.channel.id
                await self.save_settings()
            econ_cog = self.bot.get_cog('Economy')
            if not econ_cog:
                await self.bot.say("You must have Economy loaded to use this cog. \nAny settings saved will not work until the cog is loaded.")
                return

        def account_exists(self, user):
            try:
                self._get_account(user)
            except NoAccount:
                return False
            return True


class Whois:

    """Some random utilities that I threw together for school"""
    def __init__(self, bot):
        self.bot = bot

    def fetch_joined_at(self, user, server):
        """Just a special case for someone special :^)"""
        if user.id == "96130341705637888" and server.id == "133049272517001216":
            return datetime.datetime(2016, 1, 10, 6, 8, 4, 443000)
        else:
             return user.joined_at

    @commands.command(pass_context=True, no_pm=True)
    async def whois(self, ctx, *, user: discord.Member=None):
        """Gives you some info on a user"""
        author = ctx.message.author
        server = ctx.message.server

        if not user:
            user = author

        bot = self.bot
        realname = str(user)
        bank = self.bot.get_cog('Economy').bank
        useravatarurl = user.avatar_url
        joined_at = self.fetch_joined_at(user, server)
        since_created = (ctx.message.timestamp - user.created_at).days
        since_joined = (ctx.message.timestamp - joined_at).days
        user_joined = joined_at.strftime("%d %b %Y %H:%M")
        user_created = user.created_at.strftime("%d %b %Y %H:%M")
        member_number = sorted(server.members,
                               key=lambda m: m.joined_at).index(user) + 1

        created_on = "{}\n({} days ago)".format(user_created, since_created)
        joined_on = "{}\n({} days ago)".format(user_joined, since_joined)
        userid = user.id
        highestrole = user.top_role
        displayname = user.nick
        author = ctx.message.author.name
        server = ctx.message.server
        joined = user.joined_at
        userstatus = user.status
        playinggame = user.game
        userisbot = user.bot
        roles = [x.name for x in user.roles if x.name != "@everyone"]
        if roles:
            roles = sorted(roles, key=[x.name for x in server.role_hierarchy
                                       if x.name != "@everyone"].index)
            roles = ", ".join(roles)
        else:
            roles = "None"
        if user.bot is False:
            userisbot = "Requested user is not a bot"
        else:
            userisbot = "Requested user is a bot"
        if user.nick is None:
            displayname = "User currently has no nickname"
        else:
            displayname = user.nick
        if user.top_role is "@everyone":
            highestrole = "User does not have any roles"
        else:
            highestrole = user.top_role
        if user.nick is None:
            displayname = "User currently has no nickname"
        else:
            displayname = user.nick
        if bank.account_exists(user) is False:
        	economystatus = "User is not registered"
        else:
        	economystatus = "User is registered and has {} credits".format(bank.get_balance(user))
        color = ''.join([choice('0123456789ABCDEF') for x in range(6)])
        color = int(color, 16)
        embed=discord.Embed(title="Username", description=realname, color=color)
        embed.set_thumbnail(url=str(useravatarurl))
        embed.add_field(name="User's ID", value=userid, inline=False)
        embed.add_field(name="Highest Role", value=highestrole, inline=False)
        embed.add_field(name="All user roles", value=roles, inline=False)
        embed.add_field(name="Current Nickname", value=displayname, inline=False)
        embed.add_field(name="Status", value=userstatus, inline=False)
        embed.add_field(name="User is a bot", value=userisbot, inline=False)
        embed.add_field(name="Playing", value=playinggame, inline=False)
        embed.add_field(name="Economy status.", value=economystatus, inline=False)
        embed.add_field(name="Joined Discord on", value=created_on, inline=False)
        embed.add_field(name="Joined this server on", value=joined_on, inline=True)
        embed.set_footer(text="Member #{} | User ID:{}"
                             "".format(member_number, user.id))
        try :
            await self.bot.say(embed=embed)
        except discord.HTTPException:
            await self.bot.say("I need the `Embed links` permission "
                               "to send this")


def setup(bot):
    bot.add_cog(Whois(bot))
