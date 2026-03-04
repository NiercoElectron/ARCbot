import discord
from discord.ext import commands

from config import MEMBER_ROLE
from utils.database import init_db, save_message
from utils.helpers import get_role


class Events(commands.Cog):
    """Listeners de eventos do Discord."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await init_db()
        print(f'Estamos prontos, {self.bot.user}')

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        try:
            await member.send(f'Bem-vindo ao nosso café virtual, {member.name}!')
        except Exception:
            pass

        role = get_role(member.guild, MEMBER_ROLE)
        if role:
            try:
                await member.add_roles(role, reason='Atribuição automática de Sócio')
            except Exception as e:
                print(f"Não foi possível atribuir o role: {e}")

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

        if message.content.startswith('<>'):
            await message.channel.send('Comando recebido!')
        # Não precisa chamar process_commands aqui — o bot já faz isso automaticamente
        # quando on_message é registrado via Cog.listener()


async def setup(bot: commands.Bot):
    await bot.add_cog(Events(bot))
