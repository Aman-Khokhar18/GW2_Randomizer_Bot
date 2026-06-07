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
            await ctx.send(
                f"Unknown category `{category}`.\nValid options: {valid}"
            )
            return

        options = CATEGORIES[category]

        msg = await ctx.send(
            f"🎲 Rolling a **{category.upper()}** build for you, "
            f"{ctx.author.mention}..."
        )

        await spin_wheel(msg, category, options)

    @commands.command(name="worlde_stats")
    async def wordle_average(self, ctx):
        """
        Plot average Wordle guesses per player and send it as an image.
        """
        await ctx.send(
            "📊 Analyzing Wordle results… this may take a moment"
        )

        try:
            image_path = await run_wordle_analysis(self.bot)

        except Exception as e:
            await ctx.send(
                f"❌ Error while analyzing Wordle data:\n```{e}```"
            )
            return

        await ctx.send(
            content="📈 **Average Wordle guesses per player**",
            file=discord.File(image_path)
        )

    @commands.command(name="servers")
    async def servers(self, ctx):
        """
        List all servers the bot is currently in.
        """
        if not self.bot.guilds:
            await ctx.send("Bot is not in any servers.")
            return

        lines = []

        for guild in self.bot.guilds:
            lines.append(
                f"{guild.name} ({guild.id}) - "
                f"{guild.member_count} members"
            )

        output = "\n".join(lines)

        if len(output) > 1900:
            await ctx.send(
                f"Bot is in {len(self.bot.guilds)} servers."
            )
        else:
            await ctx.send(
                f"📋 **Servers I'm in:**\n```{output}```"
            )

    @commands.command(name="servermembers")
    async def server_members(self, ctx, guild_id: int):
        """
        Force fetch all members from a guild.

        Usage:
        !servermembers <guild_id>
        """
        guild = self.bot.get_guild(guild_id)

        if guild is None:
            await ctx.send(
                "❌ Bot is not in that server or guild ID is invalid."
            )
            return

        await ctx.send(
            f"🔍 Fetching members from **{guild.name}**..."
        )

        try:
            members = []

            async for member in guild.fetch_members(limit=None):
                members.append(
                    f"{member.display_name} ({member.id})"
                )

            await ctx.send(
                f"✅ Retrieved {len(members)} members "
                f"from **{guild.name}**"
            )

            chunk = ""

            for member in members:
                line = member + "\n"

                if len(chunk) + len(line) > 1800:
                    await ctx.send(f"```{chunk}```")
                    chunk = ""

                chunk += line

            if chunk:
                await ctx.send(f"```{chunk}```")

        except discord.Forbidden:
            await ctx.send(
                "❌ Missing permissions or "
                "Server Members Intent is not enabled."
            )

        except Exception as e:
            await ctx.send(
                f"❌ Error fetching members:\n```{e}```"
            )


async def setup(bot):
    await bot.add_cog(WheelCog(bot))
