import discord
from discord.ext import commands

from config import CATEGORIES
from wheel import spin_wheel


class WheelCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="random")
    async def random_role(self, ctx, category: str = None):
        if category is None:
            await ctx.send(
                "Usage: `!random dps`, `!random alacheal`, `!random quickheal`, "
                "`!random qdps`, `!random adps`"
            )
            return

        category = category.lower()
        if category not in CATEGORIES:
            valid = ", ".join(f"`{c}`" for c in CATEGORIES.keys())
            await ctx.send(f"Unknown category `{category}`.\nValid options: {valid}")
            return

        options = CATEGORIES[category]

        # Initial message
        msg = await ctx.send(
            f"🎲 Rolling a **{category.upper()}** build for you, {ctx.author.mention}..."
        )

        # Run the spin animation and show the result
        await spin_wheel(msg, category, options)
