import discord
from discord.ext import commands

from config import PREFIX


class General(commands.Cog):
    """Comandos gerais do bot."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ── ping ──────────────────────────────────────────────────────────────

    @commands.command()
    async def ping(self, ctx: commands.Context):
        """Verifica a latência do bot."""
        await ctx.send(f'Pong! `{round(self.bot.latency * 1000)}ms`')

    # ── serverinfo ────────────────────────────────────────────────────────

    @commands.command()
    async def serverinfo(self, ctx: commands.Context):
        """Exibe informações sobre o servidor."""
        guild = ctx.guild
        embed = discord.Embed(
            title=guild.name,
            color=discord.Color.blurple(),
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        embed.add_field(name='Dono', value=guild.owner.mention, inline=True)
        embed.add_field(name='ID', value=str(guild.id), inline=True)
        embed.add_field(name='Membros', value=str(guild.member_count), inline=True)
        embed.add_field(name='Cargos', value=str(len(guild.roles)), inline=True)
        embed.add_field(name='Canais de texto', value=str(len(guild.text_channels)), inline=True)
        embed.add_field(name='Canais de voz', value=str(len(guild.voice_channels)), inline=True)
        embed.add_field(
            name='Criado em',
            value=discord.utils.format_dt(guild.created_at, style='D'),
            inline=True,
        )
        if guild.description:
            embed.add_field(name='Descrição', value=guild.description, inline=False)

        await ctx.send(embed=embed)

    # ── userinfo ───────────────────────────────────────────────────────────

    @commands.command()
    async def userinfo(self, ctx: commands.Context, member: discord.Member = None):
        """Exibe informações sobre um membro. Se não informado, mostra o seu próprio perfil."""
        target = member or ctx.author
        roles = [r.mention for r in reversed(target.roles) if r.name != '@everyone']

        embed = discord.Embed(
            title=str(target),
            color=target.color if target.color.value else discord.Color.blurple(),
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name='ID', value=str(target.id), inline=True)
        embed.add_field(name='Apelido', value=target.display_name, inline=True)
        embed.add_field(name='Bot', value='Sim' if target.bot else 'Não', inline=True)
        embed.add_field(
            name='Conta criada em',
            value=discord.utils.format_dt(target.created_at, style='D'),
            inline=True,
        )
        embed.add_field(
            name='Entrou no servidor em',
            value=discord.utils.format_dt(target.joined_at, style='D') if target.joined_at else 'Desconhecido',
            inline=True,
        )
        embed.add_field(
            name=f'Cargos ({len(roles)})',
            value=' '.join(roles) if roles else '*(nenhum)*',
            inline=False,
        )
        await ctx.send(embed=embed)

    # ── avatar ─────────────────────────────────────────────────────────────

    @commands.command()
    async def avatar(self, ctx: commands.Context, member: discord.Member = None):
        """Mostra o avatar de um membro em tamanho grande."""
        target = member or ctx.author
        embed = discord.Embed(
            title=f'Avatar de {target.display_name}',
            color=discord.Color.blurple(),
        )
        embed.set_image(url=target.display_avatar.with_size(1024).url)
        await ctx.send(embed=embed)

    # ── help ───────────────────────────────────────────────────────────────

    @commands.command(name='help')
    async def help_command(self, ctx: commands.Context):
        """Lista todos os comandos disponíveis para você."""
        is_privileged = (
            ctx.author == ctx.guild.owner
            or ctx.author.guild_permissions.administrator
        )

        embed = discord.Embed(
            title='Comandos disponíveis',
            description=f'Prefixo: `{PREFIX}`',
            color=discord.Color.blurple(),
        )

        for cog_name, cog in self.bot.cogs.items():
            visible = []
            for cmd in cog.get_commands():
                if cmd.hidden:
                    continue
                # Verifica se o comando tem check de admin
                has_admin_check = bool(cmd.checks)
                if has_admin_check and not is_privileged:
                    continue
                sig = f'`{PREFIX}{cmd.name}`'
                doc = (cmd.help or cmd.brief or '').split('\n')[0].strip()
                visible.append(f'{sig} — {doc}' if doc else sig)

            if visible:
                embed.add_field(
                    name=cog_name,
                    value='\n'.join(visible),
                    inline=False,
                )

        if is_privileged:
            embed.set_footer(text='Você está vendo todos os comandos, incluindo os de admin.')
        else:
            embed.set_footer(text='Comandos de moderação e configuração são visíveis apenas para admins.')

        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))
