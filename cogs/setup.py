import discord
from discord.ext import commands

from utils.database import get_guild_config, set_guild_config
from utils.helpers import is_owner_or_admin


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

    @commands.command(name='setwelcome')
    @is_owner_or_admin()
    async def set_welcome(self, ctx: commands.Context, *, message: str = None):
        """Define a mensagem enviada por DM ao novo membro quando ele entra no servidor.

        Uso: |setwelcome Bem-vindo, {member}! Você entrou em {server}.
        Use {member} para o nome do membro e {server} para o nome do servidor.
        Use |setwelcome off para desativar.
        """
        if message and message.lower() == 'off':
            await set_guild_config(ctx.guild.id, welcome_message=None)
            await ctx.send('Mensagem de boas-vindas **desativada**. Novos membros não receberão DM ao entrar.')
            return

        if not message:
            await ctx.send(
                'Informe a mensagem. Exemplo:\n'
                f'`{ctx.prefix}setwelcome Bem-vindo, {{member}}! Você entrou em {{server}}.`\n'
                'Variáveis disponíveis: `{member}` (nome do membro), `{server}` (nome do servidor).\n'
                f'Para desativar: `{ctx.prefix}setwelcome off`'
            )
            return

        await set_guild_config(ctx.guild.id, welcome_message=message)
        preview = message.replace('{member}', ctx.author.display_name).replace('{server}', ctx.guild.name)
        await ctx.send(
            f'Mensagem de boas-vindas definida! Prévia:\n> {preview}'
        )

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
        from config import PREFIX
        from utils.database import get_all_pending_schedules

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

        # Mensagem de boas-vindas
        welcome_msg = config.get('welcome_message')
        embed.add_field(
            name='Mensagem de boas-vindas (DM)',
            value=f'`{welcome_msg}`' if welcome_msg else '*(não definida)*',
            inline=False,
        )

        # Agendamentos configurados via |setqueue
        all_schedules = await get_all_pending_schedules()
        guild_channel_ids = {ch.id for ch in ctx.guild.text_channels}
        active = [s for s in all_schedules if s['channel_id'] in guild_channel_ids]
        if active:
            schedule_lines = '\n'.join(
                f"`{s['time']}` → <#{s['channel_id']}> {'(diário)' if s['daily'] else s['date']}" for s in active
            )
        else:
            schedule_lines = '*(nenhum para este servidor)*'
        embed.add_field(name=f'Agendamentos ({len(active)})', value=schedule_lines, inline=False)

        await ctx.send(embed=embed)

    # ── status ────────────────────────────────────────────────────────────────

    @commands.command(name='status')
    @is_owner_or_admin()
    async def status(self, ctx: commands.Context):
        """Painel de status: latência, permissões e saúde geral do bot."""
        from cogs.events import REQUIRED_PERMISSIONS

        bot_member = ctx.guild.me
        latency = round(self.bot.latency * 1000)

        # Permissões
        ok = []
        missing = []
        for perm in REQUIRED_PERMISSIONS:
            if getattr(bot_member.guild_permissions, perm, False):
                ok.append(perm)
            else:
                missing.append(perm)

        status_color = discord.Color.green() if not missing else discord.Color.red()
        embed = discord.Embed(
            title=f'📊 Status — {ctx.guild.name}',
            color=status_color,
        )
        embed.add_field(name='Latência', value=f'`{latency}ms`', inline=True)
        embed.add_field(name='Módulos carregados', value=str(len(self.bot.extensions)), inline=True)
        embed.add_field(
            name='✅ Permissões OK',
            value='\n'.join(f'`{p}`' for p in ok) or '*(nenhuma)*',
            inline=False,
        )
        if missing:
            embed.add_field(
                name='❌ Permissões faltando',
                value='\n'.join(f'`{p}`' for p in missing),
                inline=False,
            )
        await ctx.send(embed=embed)

    # ── reload ─────────────────────────────────────────────────────────

    @commands.command(name='reload')
    @is_owner_or_admin()
    async def reload_cog(self, ctx: commands.Context, cog: str):
        """Recarrega um módulo (cog) sem reiniciar o bot.

        Uso: |reload moderation
        """
        ext = f'cogs.{cog}' if not cog.startswith('cogs.') else cog
        try:
            await self.bot.reload_extension(ext)
            await ctx.send(f'✅ `{ext}` recarregado com sucesso.')
        except commands.ExtensionNotLoaded:
            await ctx.send(f'❌ `{ext}` não está carregado.')
        except commands.ExtensionNotFound:
            await ctx.send(f'❌ Módulo `{ext}` não encontrado.')
        except Exception as e:
            await ctx.send(f'❌ Erro ao recarregar `{ext}`: {e}')

    @commands.command(name='reloadall')
    @is_owner_or_admin()
    async def reload_all(self, ctx: commands.Context):
        """Recarrega todos os módulos carregados.

        Uso: |reloadall
        """
        results = []
        for ext in list(self.bot.extensions):
            try:
                await self.bot.reload_extension(ext)
                results.append(f'✅ `{ext}`')
            except Exception as e:
                results.append(f'❌ `{ext}`: {e}')
        await ctx.send('**Reload de todos os módulos:**\n' + '\n'.join(results))

    @set_autorole.error
    @set_promote_role.error
    @show_config.error
    @reload_cog.error
    @reload_all.error
    async def setup_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CheckFailure):
            await ctx.send('Apenas o dono do servidor ou administradores podem usar esse comando.')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f'Uso correto: `{ctx.prefix}{ctx.command.name} @Cargo`')
        elif isinstance(error, commands.RoleNotFound):
            await ctx.send('Cargo não encontrado. Mencione o cargo com @.')


async def setup(bot: commands.Bot):
    await bot.add_cog(Setup(bot))
