import discord
from discord.ext import commands

from config import CATEGORIES
from wheel import spin_wheel
from wordle import run_wordle_analysis
from wordle import scrape_wordle_history, get_all_wordle_results




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


    @commands.command(name="worlde_stats")
    async def wordle_average(self, ctx):
        """
        Plot average Wordle guesses per player and send it as an image.
        """
        await ctx.send("📊 Analyzing Wordle results… this may take a moment")

        try:
            image_path = await run_wordle_analysis(self.bot)
        except Exception as e:
            await ctx.send(f"❌ Error while analyzing Wordle data:\n```{e}```")
            return

        await ctx.send(
            content="📈 **Average Wordle guesses per player**",
            file=discord.File(image_path)
        )






