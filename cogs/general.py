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

    @commands.command()
    async def chamar(self, ctx: commands.Context, member: discord.Member, qnt: int):
        if qnt < 1:
            await ctx.send('Se você quer chamar alguém, com certeza é para chamar mais de uma vez, né?')
            return
        if qnt > 50:
            await ctx.send('Zero é pouco e 50 é demais, vamos manter a quantidade entre 1 e 50 para evitar spam.')
            return
        if member == ctx.author:
            await ctx.send('Você não pode se mencionar, escolha outra pessoa para chamar!')
            return
        if member == self.bot.user:
            await ctx.send('Eu sou um bot, não posso ser mencionado dessa forma! Escolha outra pessoa para chamar!')
            return
        await ctx.send(f'Vítima da vez: {member.mention}, mencionado {qnt} vezes! \n{member.mention * qnt}')

    @chamar.error
    async def chamar_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("Esse usuário não está no servidor.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Quantidade de argumentos insuficiente. Use: |chamar @usuário quantidade.")


async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))
