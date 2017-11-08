import discord
import json
import os
import datetime
import asyncio

from discord.ext import commands
from .utils.dataIO import dataIO
from .utils import checks
from __main__ import settings as set_roles


numbs = {
    "ban": "☢",
    "kick": "📛",
    "warn": "⚠",
    "clear": "✅"
}


class uWarn:


#CREDITS: Quite a bit of this code comes from uwarn. I have just edited and changed it a little bit. 
#uwarn is quite an amazing cog and I suggest you check it out. 
#Check out all of El Laggron's cogs here -->  https://github.com/retke/Laggrons-Dumb-Cogs

    """Banana's Warn cog. Made for issue #91 on the CogBoard"""
    def __init__(self, bot):
        self.bot = bot
        self.settings = dataIO.load_json('data/uwarn/settings.json')

    async def error(self, ctx):
        
        bot_member = ctx.message.server.get_member(self.bot.user.id)
        
        folders = ['data', 'data/uwarn/', 'data/uwarn/history/']
        files = ['settings.json', 'history/{}.json'.format(ctx.message.server.id)]
        permissions = ['add_reactions', 'embed_links', 'manage_messages']
        message_perm = "Error: missing permissions. I need the following permissions to work:\n"
        message_file = "Error: some files are missing and data might be lost. New files will be recreated. The following files are missing:\n"
        error_perm = None
        error_file = None
        
        for folder in folders:
            if not os.path.exists(folder):
                message_file += "`{}` folder\n".format(folder)
                print("Creating " + folder + " folder...")
                os.makedirs(folder)
                error_file = 1

        for filename in files:
            if not os.path.isfile('data/uwarn/{}'.format(filename)):
                print("Creating empty {}".format(filename))
                dataIO.save_json('data/uwarn/{}'.format(filename), {})
                message_file += "`{}` is missing\n".format(filename)
                error_file = 1
                                   
        for permission in permissions:
            if {x[0]:x[1] for x in ctx.message.channel.permissions_for(ctx.message.server.me)}[permission] is False:
                message_perm += "`{}`\n".format(permission)
                error_perm = 1
           
        if error_perm == 1:
            message_perm += "Please give me the following permissions and try again"
            await self.bot.say(message_perm)

        if error_file == 1:
            message_file += "The files were successfully re-created. Try again your command (you may need to set your local settings again)"
            await self.bot.say(message_file)

        if ctx.message.server.id not in self.settings:
            await self.init(ctx.message.server)
                
    async def init(self, server):
        self.settings[server.id] = {
            'mod-log': '0',
            
            'thumbnail' : {
                'warning_embed_simple': 'https://cdn.discordapp.com/attachments/303988901570150401/360466192781017088/report.png',
                'warning_embed_kick': 'https://cdn.discordapp.com/attachments/303988901570150401/360466190956494858/kick.png',
                'warning_embed_ban': 'https://media.discordapp.net/attachments/303988901570150401/360466189979222017/ban.png',
                'report_embed': 'https://cdn.discordapp.com/attachments/303988901570150401/360466192781017088/report.png'
            },
            
            'colour': {
                'warning_embed_simple': None,
                'warning_embed_kick': None,
                'warning_embed_ban': None,
                'report_embed': None
            }
        }
        
        try:
            dataIO.save_json('data/uwarn/settings.json', self.settings)
        except:
            await self.error(ctx)
            return
    
    async def add_case(self, level, user, reason, timestamp, server, applied, ctx):
        if not os.path.isfile('data/uwarn/history/{}.json'.format(server.id)):
            print("Creating empty {}".format(server.id))
            try:
                dataIO.save_json('data/uwarn/history/{}.json'.format(server.id), data={})
            except:
                await self.error(ctx)
                return
        
        history = dataIO.load_json('data/uwarn/history/{}.json'.format(server.id))
        
        if user.id not in history:
            history[user.id] = {
                'simple-warn': 0,
                'kick-warn': 0,
                'ban-warn': 0,
                'total-warns': 0
            }
        
        total = history[user.id]['total-warns'] + 1

        history[user.id]['case{}'.format(total)] = {
            'level': 'None',
            'reason': 'None',
            'timestamp': 'None',
            'applied': 1,
            'deleted': 0
        }
            
        history[user.id]['case{}'.format(total)]['level'] = level
        history[user.id]['case{}'.format(total)]['reason'] = reason
        history[user.id]['case{}'.format(total)]['timestamp'] = timestamp
        
        history[user.id]['total-warns'] = total
        
        if level == 'Simple':
            simple_total = history[user.id]['simple-warn'] + 1
            history[user.id]['simple-warn'] = simple_total
        elif level == 'Kick':
            kick_total = history[user.id]['kick-warn'] + 1
            history[user.id]['kick-warn'] = kick_total
        elif level == 'Ban':
            ban_total = history[user.id]['ban-warn'] + 1
            history[user.id]['ban-warn'] = ban_total
        else:
            pass
        
        if applied == 1:
            pass
        else:
            history[user.id]['case{}'.format(total)]['applied'] = 0
        
        try:
            dataIO.save_json('data/uwarn/history/{}.json'.format(server.id), data=history)
        except:
            await self.error(ctx)
            return
            

    async def check_case(self, msg, i, ctx, user):
        
        server = ctx.message.server
        
        if not os.path.isfile('data/uwarn/history/{}.json'.format(server.id)):
            print("Creating empty {}".format(server.id))
            try:
                dataIO.save_json('data/uwarn/history/{}.json'.format(server.id), data={})
            except:
                await self.error(ctx)
                return
        
        try:
            history = dataIO.load_json('data/uwarn/history/{}.json'.format(server.id))
        except:
            await self.error(ctx)
            return
        
        if i is not None:
            if i > history[user.id]['total-warns'] or i<= 0:
                i = 1
    
        if not msg:
            
            if history[user.id]['case{}'.format(str(i))]['deleted'] == 1:
                e = discord.Embed(description="The case {} was deleted".format(str(i)))
                e.set_author(name=user.name, icon_url=user.avatar_url)
            
            else:
                e = discord.Embed(description="Case {} informations".format(str(i)))
                e.set_author(name=user.name, icon_url=user.avatar_url)
                    
                e.add_field(name="Level", value=history[user.id]['case{}'.format(str(i))]['level'], inline=True)
                    
                if history[user.id]['case{}'.format(str(i))]['applied'] == 1:
                    e.add_field(name="Applied", value="Yes", inline=True)
                else:
                    e.add_field(name="Applied", value="No", inline=True)
                    
                e.add_field(name="Date", value=history[user.id]['case{}'.format(str(i))]['timestamp'], inline=True)
                e.add_field(name="Reason", value=history[user.id]['case{}'.format(str(i))]['reason'], inline=False)
            
            try:
                msg = await self.bot.say(embed=e)
            except:
                await self.error(ctx)
                return
                
        try:
            await self.bot.add_reaction(msg, "⬅")
            await self.bot.add_reaction(msg, "❌")
            await self.bot.add_reaction(msg, "➡")
        except:
            await self.error(ctx)
            return
        
        while True:
            
            response = await self.bot.wait_for_reaction(emoji=['❌', '⬅', '➡'], user=ctx.message.author, message=msg, timeout=30)
            await asyncio.sleep(0.2)
            
            if not response:
                try:
                    await self.bot.clear_reactions(msg)
                except:
                    pass
                return
                
            if response.reaction.emoji == '❌':
                try:
                    await self.bot.delete_message(msg)
                    return
                except:
                    await self.error(ctx)
                    return

        
            elif response.reaction.emoji == '➡':
                
                try:
                    await self.bot.remove_reaction(msg, '➡', ctx.message.author)
                except:
                    pass
                
                if i is None:
                    i = 1
                else:
                    i = i + 1
            
                if i > history[user.id]['total-warns']:
                    i = 1
                
                if history[user.id]['case{}'.format(str(i))]['deleted'] == 1:
                    i = i + 1
                
                e = discord.Embed(description="Case {} informations".format(str(i)))
                e.set_author(name=user.name, icon_url=user.avatar_url)
                    
                e.add_field(name="Level", value=history[user.id]['case{}'.format(str(i))]['level'], inline=True)
                    
                if history[user.id]['case{}'.format(str(i))]['applied'] == 1:
                    e.add_field(name="Applied", value="Yes", inline=True)
                else:
                    e.add_field(name="Applied", value="No", inline=True)
    
                e.add_field(name="Date", value=history[user.id]['case{}'.format(str(i))]['timestamp'], inline=True)
                e.add_field(name="Reason", value=history[user.id]['case{}'.format(str(i))]['reason'], inline=False)
                e.add_field(name="WarnID", value=(int(i) + int(user.id)), inline=False)
                    
                msg = await self.bot.edit_message(msg, embed=e)
                
            else:
                
                try:
                    await self.bot.remove_reaction(msg, '⬅', ctx.message.author)
                except:
                    pass
                
                if i is None:
                    i = history[user.id]['total-warns']
                else:
                    i = i - 1
                    
                if i <= 0:
                    i = history[user.id]['total-warns']
                        
                if history[user.id]['case{}'.format(str(i))]['deleted'] == 1:
                    i = i - 1
            
                e = discord.Embed(description="Case {} informations".format(str(i)))
                e.set_author(name=user.name, icon_url=user.avatar_url)
                
                e.add_field(name="Level", value=history[user.id]['case{}'.format(str(i))]['level'], inline=True)
                e.add_field(name="Date", value=history[user.id]['case{}'.format(str(i))]['timestamp'], inline=True)
                e.add_field(name="Reason", value=history[user.id]['case{}'.format(str(i))]['reason'], inline=False)
                e.add_field(name="WarnID", value=(int(i) + int(user.id)), inline=False)

                msg = await self.bot.edit_message(msg, embed=e)


    @commands.group(pass_context=True)
    @checks.admin()
    async def loggingchannel(self, ctx, *, channel: discord.Channel=None):
        """Sets a channel for logging. DO NOT ALLOW THE PUBLIC TO SEE THIS CHANNEL"""
    
        if not channel:
            channel = ctx.message.channel
        else:
            pass
    
        server = ctx.message.server
        
        try:
            if server.id not in self.settings:
                await self.init(server)
        except:
            await self.error(ctx)

        self.settings[server.id]['mod-log'] = channel.id
        await self.bot.say("Warns and reports will be sent to **" + channel.name + "**.")
        try:
            dataIO.save_json('data/uwarn/settings.json', self.settings)
        except:
            await self.error(ctx)
            return

    @commands.command(pass_context=True)
    async def report(self, ctx, user: discord.Member, *, reason):
        """Report a user to the moderation team"""
    
        author = ctx.message.author
        bot = self.bot.user
        server = ctx.message.server
        userismodorhigher = True
    
        try:
            await self.bot.delete_message(ctx.message)
        except:
            pass

        try:
            if server.id not in self.settings:
                await self.init(server)
        except:
            await self.error(ctx)
        
        if self.settings[server.id]['mod-log'] == '0':
            await self.bot.say("The log channel is not set yet. Please use `" + ctx.prefix + "loggingchannel` to set it. Aborting...")
            return
        else:
            loggedchannel = self.bot.get_channel(self.settings[server.id]['mod-log'])
                
        report = discord.Embed(title="Report", description="A user reported somebody for something wrong")
        report.add_field(name="From", value=author.mention, inline=True)
        report.add_field(name="To", value=user.mention, inline=True)
        report.add_field(name="Reason", value=reason, inline=False)
        report.set_author(name="{}".format(user.name), icon_url=user.avatar_url)
        report.set_footer(text=ctx.message.timestamp.strftime("%d %b %Y %H:%M"))
        report.set_thumbnail(url=self.settings[server.id]['thumbnail']['report_embed'])
        try:
            report.color = discord.Colour(self.settings[server.id]['colour']['report_embed'])
        except:
            pass
        timeout = 120
        datmsgtho = await self.bot.send_message(loggedchannel, embed=report)
        await self.bot.add_reaction(datmsgtho, "📛")
        await self.bot.add_reaction(datmsgtho, "☢")
        await self.bot.add_reaction(datmsgtho, "⚠")
        await self.bot.add_reaction(datmsgtho, "✅")
        fvgh = await self.bot.send_message(loggedchannel, "A user has been reported! You have two minutes to take action via these reactions. If you choose to ignore this message, the reactions will be removed and the message will stay.\n •⚠ - warns the user for whatever reason you specify.\n•📛 - Kicks the user who was reported. •☢ - Bans the user who was reported. •✅ - Manually clears the reactions of the report embed")
        await self.bot.send_message(author, "Your report has been sent to the moderation team")
        react = await self.bot.wait_for_reaction(
            message=datmsgtho, timeout=timeout,
            emoji=["📛", "⚠", "✅", "☢"]
        )
        if react is None:
            try:
                try:
                    await self.bot.clear_reactions(datmsgtho)
                except:
                    await self.bot.remove_reaction(datmsgtho, "📛", self.bot.user)
                    await self.bot.remove_reaction(datmsgtho, "⚠", self.bot.user)
                    await self.bot.remove_reaction(datmsgtho, "✅", self.bot.user)
                    await self.bot.remove_reaction(datmsgtho, "☢", self.bot.user)
            except:
                pass
            return None
        reacts = {v: k for k, v in numbs.items()}
        react = reacts[react.reaction.emoji]
        if react == "warn":
            if userismodorhigher is True:
                await self.bot.send_message(loggedchannel, "Please say the warn reason in chat. To cancel, say Cancel")
                await asyncio.sleep(1)
                answer = await self.bot.wait_for_message(timeout=120)
                if answer is None:
                    await self.bot.send_message(loggedchannel, 'Warn has been cancelled.')
                    await self.bot.clear_reactions(datmsgtho)
                    return
                elif answer is "Cancel" or "cancel":
                    await self.bot.send_message(loggedchannel, "Warn has been cancelled.")
                    await self.bot.clear_reactions(datmsgtho)
                    return
                else:
                    warnmsg = answer.content
                server = ctx.message.server
                author = ctx.message.author
                warninggif = "https://media.giphy.com/media/GvKfRYEJTULKg/giphy.gif"
                if self.settings[server.id]['mod-log'] == '0':
                    await self.bot.send_message(loggedchannel, "The log channel is not set yet. Please use `" + ctx.prefix + "loggingchannel` to set it. Aborting...")
                    return
                else:
                    channel = self.bot.get_channel(self.settings[server.id]['mod-log'])

                if user == self.bot.user:
                    await self.bot.send_message(loggedchannel, "Why tho, you can't warn me cuz i'm a savage.")
                    return

                elif user.bot:
                    await self.bot.send_message(loggedchannel, "Fucking moron, bots don't accept DM's from other bots")
                    return
                try:
                    history = dataIO.load_json('data/uwarn/history/{}.json'.format(server.id))
                except:
                    await self.error(ctx)
                    return
        
                if user.id not in history:
                    history[user.id] = {
                        'simple-warn': 0,
                        'kick-warn': 0,
                        'ban-warn': 0,
                        'total-warns': 0
                    }
        
                total = history[user.id]['total-warns'] + 1
                i = None
                if i is not None:
                    if i > history[user.id]['total-warns'] or i<= 0:
                        i = 1
                if i is None:
                    i = history[user.id]['total-warns']
                else:
                    i = i - 1
                    
                if i <= 0:
                    i = history[user.id]['total-warns']                        
                try:
                    if server.id not in self.settings:
                        await self.init(server)
                except:
                    await self.error(ctx)
                # This is the embed sent in the moderator log channel
                modlog = discord.Embed(title="Warning", description="A user was warned")
                modlog.add_field(name="User", value=user.mention, inline=True)
                modlog.add_field(name="Moderator", value=author.mention, inline=True)
                modlog.add_field(name="Reason", value=warnmsg, inline=False)
                modlog.add_field(name="WarnID", value=(int(i) + int(user.id)), inline=False)
                modlog.set_author(name=user.name, icon_url=user.avatar_url)
                modlog.set_footer(text=ctx.message.timestamp.strftime("%d %b %Y %H:%M"))
                modlog.set_thumbnail(url=str(warninggif))
                try:
                    report.color = discord.Colour(self.settings[server.id]['colour']['warning_embed_simple'])
                except:
                    pass
                target = discord.Embed(description="You have been warned in {}!".format(str(server)))
                target.add_field(name="Moderator", value=author.mention, inline=False)
                target.add_field(name="Reason", value=warnmsg, inline=False)
                target.add_field(name="WarnID", value=(int(i) + int(user.id)), inline=False)
                target.set_footer(text=ctx.message.timestamp.strftime("%d %b %Y %H:%M"))
                target.set_thumbnail(url=str(warninggif))
                try:
                    report.color = discord.Colour(self.settings[server.id]['colour']['warning_embed_simple'])
                except:
                    pass

                try:
                    msg = await self.bot.send_message(user, embed=target)
                except:
                    modlog.set_footer(text="I couldn't send a message to this user. He may has blocked messages from this server.")
                dmedmsg = await self.bot.send_message(loggedchannel, embed=modlog)
                await self.add_case(level='Normal', user=user, reason=reason, timestamp=ctx.message.timestamp.strftime("%d %b %Y %H:%M"), server=server, applied=1, ctx=ctx)
                await self.bot.clear_reactions(datmsgtho)
                await self.bot.delete_message(fvgh)
                return
            else:
                await self.bot.say(ctx.message.author.mention + " that was a good try, but you aren't staff.")
                return react
        elif react == "ban":
            if userismodorhigher is True:
                await self.bot.send_message(loggedchannel, "Are you absolutley sure you want to ban {}? yes or no ***MUST BE yes OR no***".format(user.name))
                answer = await self.bot.wait_for_message(timeout=30,
                                                         author=ctx.message.author)
                if answer is None:
                    await self.bot.send_message(loggedchannel, 'Time\'s up! User will *not* be banned.')
                    await self.bot.clear_reactions(datmsgtho)
                    return
                elif "yes" not in answer.content.lower():
                    await self.bot.send_message(loggedchannel, 'User will not be banned.')
                    await self.bot.clear_reactions(datmsgtho)
                    return
                else:
                    try:
                        await self.bot.send_message(user, "You have been banned from {}! I hope this teaches you a lesson.".format(ctx.message.server.name))
                        await self.bot.ban(user, 2)
                        await self.bot.send_message(loggedchannel, "Banned user and deleted 2 days worth of messages from them. This was permanent!")
                        await self.bot.clear_reactions(datmsgtho)
                    except discord.HTTPException:
                        await self.bot.send_message(loggedchannel, "I need the ban permission.. Aborting!")
                        await self.bot.clear_reactions(datmsgtho)
                        await self.bot.delete_message(fvgh)
            else:
                await self.bot.say(ctx.message.author.mention + " that was a good try, but you aren't staff.")
                return react
        elif react == "kick":
            if userismodorhigher is True:
                await self.bot.send_message(loggedchannel, "Are you sure you want to kick {}? yes or no ***MUST BE yes OR no***".format(user.name))
                answer = await self.bot.wait_for_message(timeout=30,
                                                     author=ctx.message.author)
                if answer is None:
                    await self.bot.send_message(loggedchannel, 'Times up! User will *not* be kicked.')
                    return
                elif "yes" not in answer.content.lower():
                    await self.bot.send_message(loggedchannel, 'User will not be kicked.')
                    return
                else:
                    try:
                        await self.bot.send_message(user, "You have been kicked from {}! I hope you come back with a better attitude.".format(ctx.message.server.name))
                        await self.bot.kick(user)
                        await self.bot.send_message(loggedchannel, "The user has been kicked. They can rejoin with an invite link,")
                        await self.bot.clear_reactions(datmsgtho)
                    except discord.HTTPException:
                        await self.bot.send_message(loggedchannel, "I need the kick permission.. Aborting!")
                        await self.bot.clear_reactions(datmsgtho)
                        await self.bot.delete_message(fvgh)
                        return
            else:
                await self.bot.say(ctx.message.author.mention + " that was a good try, but you aren't staff.")
                return react
        elif react == "clear":
            if userismodorhigher is True:     
                await self.bot.clear_reactions(datmsgtho)
                await self.bot.send_message(loggedchannel, "Reactions have been cleared.")
                await self.bot.delete_message(fvgh)
            else:
                await self.bot.say(ctx.message.author.mention + " that was a good try, but you aren't staff.")
                return react

    @commands.command(pass_context=True, no_pm=True)
    @checks.mod()
    async def warn(self, ctx, user: discord.Member, *, reason: str):
        """Send a warning to a user."""
        try:
            await self.bot.delete_message(ctx.message)
        except:
            pass

        server = ctx.message.server
        author = ctx.message.author
        warninggif = "https://media.giphy.com/media/GvKfRYEJTULKg/giphy.gif"
        if self.settings[server.id]['mod-log'] == '0':
            await self.bot.say("The log channel is not set yet. Please use `" + ctx.prefix + "loggingchannel` to set it. Aborting...")
            return
        else:
            channel = self.bot.get_channel(self.settings[server.id]['mod-log'])

        if user == self.bot.user:
            await self.bot.say("Why tho, you can't warn me cuz i'm a savage.")
            return

        elif user.bot:
            await self.bot.say("Fucking moron, bots don't accept DM's from other bots")
            return
        try:
            history = dataIO.load_json('data/uwarn/history/{}.json'.format(server.id))
        except:
            await self.error(ctx)
            return
        
        if user.id not in history:
            history[user.id] = {
                'simple-warn': 0,
                'kick-warn': 0,
                'ban-warn': 0,
                'total-warns': 0
            }
        
        total = history[user.id]['total-warns'] + 1
        i = None
        if i is not None:
            if i > history[user.id]['total-warns'] or i<= 0:
                i = 1
        if i is None:
            i = history[user.id]['total-warns']
        else:
            i = i - 1
                    
        if i <= 0:
            i = history[user.id]['total-warns']                        
        try:
            if server.id not in self.settings:
                await self.init(server)
        except:
            await self.error(ctx)
        # This is the embed sent in the moderator log channel
        modlog = discord.Embed(title="Warning", description="A user was warned")
        modlog.add_field(name="User", value=user.mention, inline=True)
        modlog.add_field(name="Moderator", value=author.mention, inline=True)
        modlog.add_field(name="Reason", value=reason, inline=False)
        modlog.add_field(name="WarnID", value=(int(i) + int(user.id)), inline=False)
        modlog.set_author(name=user.name, icon_url=user.avatar_url)
        modlog.set_footer(text=ctx.message.timestamp.strftime("%d %b %Y %H:%M"))
        modlog.set_thumbnail(url=str(warninggif))
        try:
            report.color = discord.Colour(self.settings[server.id]['colour']['warning_embed_simple'])
        except:
            pass
        target = discord.Embed(description="You have been warned in {}!".format(str(server)))
        target.add_field(name="Moderator", value=author.mention, inline=False)
        target.add_field(name="Reason", value=reason, inline=False)
        target.add_field(name="WarnID", value=(int(i) + int(user.id)), inline=False)
        target.set_footer(text=ctx.message.timestamp.strftime("%d %b %Y %H:%M"))
        target.set_thumbnail(url=str(warninggif))
        try:
            report.color = discord.Colour(self.settings[server.id]['colour']['warning_embed_simple'])
        except:
            pass

        try:
            msg = await self.bot.send_message(user, embed=target)
        except:
            modlog.set_footer(text="I couldn't send a message to this user. He may has blocked messages from this server.")
        dmedmsg = await self.bot.send_message(channel, embed=modlog)
        await self.add_case(level='Normal', user=user, reason=reason, timestamp=ctx.message.timestamp.strftime("%d %b %Y %H:%M"), server=server, applied=1, ctx=ctx)

    @commands.command(pass_context=True, no_pm=True)
    async def warnings(self, ctx, user: discord.Member, *, case: int=None):
        """Give the reason behind a case"""
        
        server = ctx.message.server
        author = ctx.message.author
        if not case:
            case = 0
        
        if not os.path.isfile('data/uwarn/history/{}.json'.format(server.id)):
            print("Creating empty {}".format(server.id))
            try:
                dataIO.save_json('data/uwarn/history/{}.json'.format(server.id), data={})
            except:
                await self.error(ctx)
                return
                    
        try:
            history = dataIO.load_json('data/uwarn/history/{}.json'.format(server.id))
        except:
            await self.erro(ctx)
            return
        
        if user.id not in history:
            await self.bot.say("User does not have any warnings yet")
            return

        if case < 0 or case > history[user.id]['total-warns']:
            await self.bot.say("That case does not exist")
            return

        if case == 0:

            e = discord.Embed(description="General user infos")
            e.set_author(name=user, icon_url=user.avatar_url)

            e.add_field(name=u"\u2063", value="Total warns: {}".format(str(history[user.id]['total-warns'])))

            e.set_footer(text="Click on the reaction to see all of the cases")
            
            try:
                msg = await self.bot.say(embed=e)
            except:
                await self.error(ctx)
                return
            
            i = None
            await self.check_case(msg, i, ctx=ctx, user=user)

        else:
            i = case
            await self.check_case(msg=None, i=i, ctx=ctx, user=user)

        try:
            dataIO.save_json('data/uwarn/settings.json', self.settings)
        except:
            await self.error(ctx)
            return


    @checks.is_owner()
    @commands.command(pass_context=True, no_pm=True)
    async def infostatus(self, ctx):
        """TEST"""
        users = len(set(self.bot.get_all_members()))
        servers = len(self.bot.servers)
        myvariable = "{} servers | {} users".format(servers, users)
        await self.bot.change_presence(game=discord.Game(type=1, url="https://www.twitch.tv/pleasejustignorethis", name=("{} servers | {} users".format(servers, users))))
        await self.bot.say("Done.")
        
        
    @checks.admin()
    @commands.comman(pass_context=True, no_pm=True)
    async def csay(self, ctx, channel: discord.Channel, *, text):
        await self.bot.send_message(channel, text)
        

def check_folders():
    folders = ('data', 'data/uwarn/', 'data/uwarn/history/')
    for folder in folders:
        if not os.path.exists(folder):
            print("Creating " + folder + " folder...")
            os.makedirs(folder)

def check_files():
    ignore_list = {'SERVERS': [], 'CHANNELS': []}
    
    files = {
        'settings.json'         : {}
    }

    for filename, value in files.items():
        if not os.path.isfile('data/uwarn/{}'.format(filename)):
            print("Creating empty {}".format(filename))
            dataIO.save_json('data/uwarn/{}'.format(filename), value)


def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(uWarn(bot))
