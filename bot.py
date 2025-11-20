import os
import discord
from discord.ext import commands

from config import TOKEN
from commands import WheelCog  

intents = discord.Intents.default()
intents.message_content = True  # make sure this is also enabled in the Discord Dev Portal

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def setup_hook():
    """
    This runs before the bot is fully ready.
    It's the recommended place to add cogs in discord.py 2.x.
    """
    await bot.add_cog(WheelCog(bot))
    print("WheelCog loaded ✅")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")


bot.run(TOKEN)
