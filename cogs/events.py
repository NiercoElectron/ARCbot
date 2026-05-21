"""Cog de listeners de eventos do Discord e inicialização do banco de dados."""

import discord
from discord.ext import commands

from utils.database import get_guild_config, init_db, save_message

REQUIRED_PERMISSIONS = [
    'manage_roles',
    'kick_members',
    'ban_members',
    'manage_messages',
    'moderate_members',
    'send_messages',
    'read_message_history',
    'view_channel',
]


class Events(commands.Cog):
    """Cog que gerencia eventos como on_ready, on_member_join e on_message."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._db_ready = False

    @commands.Cog.listener()
    async def on_ready(self):
        """Inicializa o banco de dados e indica que o bot está pronto."""
        if not self._db_ready:
            await init_db()
            self._db_ready = True
        print(f'Estamos prontos, {self.bot.user}')

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        """Verifica permissões ao entrar em um servidor e avisa o dono se faltar alguma."""
        bot_member = guild.me
        missing = [
            perm for perm in REQUIRED_PERMISSIONS
            if not getattr(bot_member.guild_permissions, perm, False)
        ]
        if not missing:
            return

        msg = (
            f'Olá! Acabei de entrar no servidor **{guild.name}** mas estou sem algumas permissões '
            f'necessárias para funcionar corretamente:\n\n'
            + '\n'.join(f'• `{p}`' for p in missing)
            + '\n\nPor favor, ajuste as permissões do meu cargo e me adicione novamente ou corrija manualmente.'
        )
        try:
            await guild.owner.send(msg)
        except discord.Forbidden:
            for channel in guild.text_channels:
                if channel.permissions_for(bot_member).send_messages:
                    await channel.send(msg)
                    break

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Aplica autorole e envia mensagem de boas-vindas ao novo membro."""
        config = await get_guild_config(member.guild.id)

        welcome_msg = config.get('welcome_message')
        if welcome_msg:
            text = welcome_msg.replace('{member}', member.display_name).replace('{server}', member.guild.name)
            try:
                await member.send(text)
            except Exception:
                pass

        if config['autorole_id']:
            role = member.guild.get_role(config['autorole_id'])
            if role:
                try:
                    await member.add_roles(role, reason='Autorole automático')
                except Exception as e:
                    print(f"Não foi possível atribuir o autorole: {e}")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Guarda mensagens no banco de dados para fornecer contexto à IA."""
        if message.author == self.bot.user:
            return

        if message.content:
            await save_message(
                channel_id=message.channel.id,
                author_name=message.author.display_name,
                content=message.content,
                created_at=message.created_at.isoformat(),
            )

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        """Trata erros de comando não capturados por handlers locais."""
        if hasattr(ctx.command, 'on_error'):
            return
        if ctx.cog and commands.Cog._get_overridden_hook(ctx.cog.cog_command_error):
            return

        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.CommandOnCooldown):
            return
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f'Argumento faltando: `{error.param.name}`. Use `|help` para ver o uso correto.')
        elif isinstance(error, commands.BadArgument):
            await ctx.send('Argumento inválido. Use `|help` para ver o uso correto.')
        elif isinstance(error, commands.CheckFailure):
            await ctx.send('Você não tem permissão para usar esse comando.')
        elif isinstance(error, discord.Forbidden):
            await ctx.send('Não tenho permissão para executar essa ação.')
        else:
            print(f'[ERRO] Comando `{ctx.command}`: {error}')


async def setup(bot: commands.Bot):
    """Adiciona o cog Events ao bot."""
    await bot.add_cog(Events(bot))
