import discord
from discord.ext import commands

from config import MEMBER_ROLE


class General(commands.Cog):
    """Comandos gerais do bot."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx: commands.Context):
        await ctx.send('Pong!')


async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))
