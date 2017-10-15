import discord
import random
from discord.ext import commands

class PenisRem:
    """Penis related commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def penis(self, *, user : discord.Member):
        """Detects user's penis length

        This is 100% accurate."""
        owner = self.bot.settings.owner
        if user.id == owner:
            dong = "8{}D".format("===========================================================================")
        else:
            state = random.getstate()
            random.setstate(state)
            dong = "8{}D".format("=" * random.randint(15, 40))
        await self.bot.say("Size: " + dong)


def setup(bot):
    bot.add_cog(PenisRem(bot))
