# wheel.py

import random
import asyncio
import discord

from config import PROFESSION_ICONS


def build_wheel_embed(
    category_name: str,
    options,
    pointer_index: int,
    spinning: bool = True,
):

    if spinning:
        title = f"🎡 Rolling the {category_name.upper()} wheel..."
        status_line = "**Status:** DJ Spin that wheel... "
        color = discord.Color.blurple()
    else:
        title = f"✅ Result for {category_name.upper()}"
        status_line = "**Status:** Finished "
        color = discord.Color.green()

    # Build the wheel list
    wheel_lines = []
    for i, opt in enumerate(options):
        icon = PROFESSION_ICONS.get(opt, "")
        if i == pointer_index:
            # Highlight current entry
            wheel_lines.append(f"> {icon} **{opt}**")
        else:
            wheel_lines.append(f"{icon} {opt}")

    wheel_block = "\n".join(wheel_lines)

    # Description = heading + wheel + blank line + status
    description = (
        "**Wheel**\n"
        f"{wheel_block}\n\n"
        f"{status_line}"
    )

    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
    )

    return embed


async def spin_wheel(message: discord.Message, category_name: str, options):
    if not options:
        await message.edit(content="No options configured for this category!")
        return None

    n = len(options)

    # Pick final result index and value
    final_index = random.randrange(n)
    final_choice = options[final_index]

    # How many frames in the animation
    frames = 7  # 5–8 is a good range

    # Build the sequence of indices the highlight will visit.
    # Last index in seq must be final_index.
    seq = []
    idx = final_index
    for _ in range(frames):
        seq.append(idx)
        idx = (idx - 1) % n
    seq.reverse()  # seq[0] is start, seq[-1] is final_index

    delay = 0.10  # seconds between frames

    # Play animation
    for pointer_index in seq:
        embed = build_wheel_embed(category_name, options, pointer_index, spinning=True)
        await message.edit(content=None, embed=embed)
        await asyncio.sleep(delay)

    # After loop, pointer_index == final_index
    final_embed = build_wheel_embed(
        category_name,
        options,
        final_index,
        spinning=False,
    )

    # Add a spacer field for nicer separation before the result
    final_embed.add_field(name="\u200b", value="\u200b", inline=False)

    # Then the actual result
    icon = PROFESSION_ICONS.get(final_choice, "")
    final_embed.add_field(
        name="🎯 Your pick",
        value=f"{icon} **{final_choice}**",
        inline=False,
    )

    final_embed.set_thumbnail(
        url="https://static.wikia.nocookie.net/gw2/images/4/46/Guild_Wars_2_Logo.png"
    )

    await message.edit(embed=final_embed)
    return final_choice
