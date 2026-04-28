import discord
from discord.ext import commands

from utils.database import get_guild_config, set_guild_config


def is_owner_or_admin():
    """Check: apenas o dono do servidor ou administradores podem usar esses comandos."""
    async def predicate(ctx: commands.Context) -> bool:
        return (
            ctx.author == ctx.guild.owner
            or ctx.author.guild_permissions.administrator
        )
    return commands.check(predicate)


class Setup(commands.Cog):
    """Comandos de configuração do servidor (apenas dono/admin)."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='setautorole')
    @is_owner_or_admin()
    async def set_autorole(self, ctx: commands.Context, role: discord.Role):
        """Define o cargo atribuído automaticamente quando um membro entra.

        Uso: |setautorole @Cargo
        """
        await set_guild_config(ctx.guild.id, autorole_id=role.id)
        await ctx.send(f'Autorole definido para **{role.name}**. Novos membros receberão esse cargo ao entrar.')

    @commands.command(name='setpromoterole')
    @is_owner_or_admin()
    async def set_promote_role(self, ctx: commands.Context, role: discord.Role):
        """Define o cargo usado pelo comando |promote.

        Uso: |setpromoterole @Cargo
        """
        await set_guild_config(ctx.guild.id, promote_role_id=role.id)
        await ctx.send(f'Promote role definido para **{role.name}**.')

    @commands.command(name='showconfig')
    @is_owner_or_admin()
    async def show_config(self, ctx: commands.Context):
        """Mostra a configuração atual do servidor."""
        config = await get_guild_config(ctx.guild.id)

        autorole = ctx.guild.get_role(config['autorole_id']) if config['autorole_id'] else None
        promote_role = ctx.guild.get_role(config['promote_role_id']) if config['promote_role_id'] else None

        embed = discord.Embed(title='Configuração do servidor', color=discord.Color.blurple())
        embed.add_field(name='Autorole', value=autorole.mention if autorole else '*(não definido)*', inline=False)
        embed.add_field(name='Promote role', value=promote_role.mention if promote_role else '*(não definido)*', inline=False)
        await ctx.send(embed=embed)

    @set_autorole.error
    @set_promote_role.error
    async def setup_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CheckFailure):
            await ctx.send('Apenas o dono do servidor ou administradores podem usar esse comando.')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f'Uso correto: `{ctx.prefix}{ctx.command.name} @Cargo`')
        elif isinstance(error, commands.RoleNotFound):
            await ctx.send('Cargo não encontrado. Mencione o cargo com @.')


async def setup(bot: commands.Bot):
    await bot.add_cog(Setup(bot))
