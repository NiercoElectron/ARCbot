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
        """Mostra a configuração modular atual do bot neste servidor."""
        from config import PREFIX, SCHEDULES

        config = await get_guild_config(ctx.guild.id)

        autorole = ctx.guild.get_role(config['autorole_id']) if config['autorole_id'] else None
        promote_role = ctx.guild.get_role(config['promote_role_id']) if config['promote_role_id'] else None

        embed = discord.Embed(
            title=f'⚙️ Configuração do bot — {ctx.guild.name}',
            color=discord.Color.blurple(),
        )

        # Geral
        embed.add_field(name='Prefixo', value=f'`{PREFIX}`', inline=True)
        loaded_cogs = ', '.join(f'`{name}`' for name in self.bot.cogs) or '*(nenhum)*'
        embed.add_field(name='Módulos carregados', value=loaded_cogs, inline=False)

        # Roles configurados via banco
        embed.add_field(
            name='Autorole (entrada)',
            value=autorole.mention if autorole else '*(não definido)*',
            inline=True,
        )
        embed.add_field(
            name='Promote role',
            value=promote_role.mention if promote_role else '*(não definido)*',
            inline=True,
        )

        # Agendamentos ativos para este servidor (canais que existem no guild)
        guild_channel_names = {ch.name for ch in ctx.guild.text_channels}
        guild_channel_ids = {ch.id for ch in ctx.guild.text_channels}
        active = [
            s for s in SCHEDULES
            if s.get('channel') in guild_channel_names
            or s.get('channel_id') in guild_channel_ids
        ]
        if active:
            schedule_lines = '\n'.join(
                f"`{s['time']}` → #{s.get('channel') or s.get('channel_id')}" for s in active
            )
        else:
            schedule_lines = '*(nenhum para este servidor)*'
        embed.add_field(name=f'Agendamentos ({len(active)})', value=schedule_lines, inline=False)

        await ctx.send(embed=embed)

    @set_autorole.error
    @set_promote_role.error
    @show_config.error
    async def setup_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CheckFailure):
            await ctx.send('Apenas o dono do servidor ou administradores podem usar esse comando.')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f'Uso correto: `{ctx.prefix}{ctx.command.name} @Cargo`')
        elif isinstance(error, commands.RoleNotFound):
            await ctx.send('Cargo não encontrado. Mencione o cargo com @.')


async def setup(bot: commands.Bot):
    await bot.add_cog(Setup(bot))
