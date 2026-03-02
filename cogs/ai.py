import os

from discord.ext import commands
from openai import AsyncOpenAI

from config import SYSTEM_PROMPT


class AI(commands.Cog):
    """Integração com a OpenAI — comando |sec."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.client = AsyncOpenAI(api_key=os.getenv('API_KEY'))

    @commands.command()
    async def sec(self, ctx: commands.Context, *, question: str):
        async with ctx.typing():
            resp = await self.client.responses.create(
                model="gpt-5-mini",
                input=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": question},
                ],
                temperature=1.0,
                max_output_tokens=500,
            )
        await ctx.send(resp.output_text)


async def setup(bot: commands.Bot):
    await bot.add_cog(AI(bot))
