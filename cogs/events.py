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
    """Listeners de eventos do Discord."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._db_ready = False

    @commands.Cog.listener()
    async def on_ready(self):
        if not self._db_ready:
            await init_db()
            self._db_ready = True
        print(f'Estamos prontos, {self.bot.user}')

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        """Verifica permissões ao entrar em um servidor e avisa o dono caso falte alguma."""
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
            # tenta enviar no primeiro canal que conseguir escrever
            for channel in guild.text_channels:
                if channel.permissions_for(bot_member).send_messages:
                    await channel.send(msg)
                    break

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        try:
            await member.send(f'Bem-vindo ao nosso café virtual, {member.name}!')
        except Exception:
            pass

        config = await get_guild_config(member.guild.id)
        if config['autorole_id']:
            role = member.guild.get_role(config['autorole_id'])
            if role:
                try:
                    await member.add_roles(role, reason='Autorole automático')
                except Exception as e:
                    print(f"Não foi possível atribuir o autorole: {e}")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return

        # Salva a mensagem no banco para contexto da IA
        if message.content:
            await save_message(
                channel_id=message.channel.id,
                author_name=message.author.display_name,
                content=message.content,
                created_at=message.created_at.isoformat(),
            )

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        # Ignora erros que já foram tratados por handlers locais
        if hasattr(ctx.command, 'on_error'):
            return
        if ctx.cog and commands.Cog._get_overridden_hook(ctx.cog.cog_command_error):
            return

        if isinstance(error, commands.CommandNotFound):
            return  # silencia comandos inexistentes
        if isinstance(error, commands.CommandOnCooldown):
            return  # tratado localmente em ai.py
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
    await bot.add_cog(Events(bot))
