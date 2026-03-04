import os

from discord.ext import commands
from openai import AsyncOpenAI

from config import SYSTEM_PROMPT
from utils.database import get_recent_messages

DISCORD_MAX_LENGTH = 2000


class AI(commands.Cog):
    """Integração com a OpenAI — comando |sec."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.client = AsyncOpenAI(api_key=os.getenv('API_KEY'))

    def _build_context(self, messages: list[dict]) -> str:
        """Formata as últimas mensagens do canal como contexto legível."""
        if not messages:
            return ''
        lines = [f'[{m["created_at"]}] {m["author"]}: {m["content"]}' for m in messages]
        return (
            'Aqui estão as últimas mensagens do canal para contexto:\n'
            + '\n'.join(lines)
        )

    @staticmethod
    def _split_message(text: str, limit: int = DISCORD_MAX_LENGTH) -> list[str]:
        """Divide o texto em pedaços que cabem no limite do Discord."""
        if len(text) <= limit:
            return [text]
        chunks = []
        while text:
            if len(text) <= limit:
                chunks.append(text)
                break
            # Tenta cortar em uma quebra de linha
            cut = text.rfind('\n', 0, limit)
            if cut == -1:
                # Senão, corta no último espaço
                cut = text.rfind(' ', 0, limit)
            if cut == -1:
                # Último recurso: corta no limite
                cut = limit
            chunks.append(text[:cut])
            text = text[cut:].lstrip('\n')
        return chunks

    @commands.command()
    async def sec(self, ctx: commands.Context, *, question: str):
        recent = await get_recent_messages(ctx.channel.id)
        context_block = self._build_context(recent)

        system_content = SYSTEM_PROMPT
        if context_block:
            system_content += '\n\n' + context_block

        try:
            async with ctx.typing():
                resp = await self.client.responses.create(
                    model="gpt-5-mini",
                    input=[
                        {"role": "system", "content": system_content},
                        {"role": "user", "content": question},
                    ],
                    temperature=1.0,
                    max_output_tokens=10000,
                )

            text = (resp.output_text or '').strip()
            if not text:
                await ctx.send('Não consegui gerar uma resposta. Tenta de novo!')
                return

            for chunk in self._split_message(text):
                await ctx.send(chunk)

        except Exception as e:
            await ctx.send(f'Erro ao consultar a IA: {e}')


async def setup(bot: commands.Bot):
    await bot.add_cog(AI(bot))