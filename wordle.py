import re
import discord
import pandas as pd
import matplotlib.pyplot as plt



WORDLE_CHANNEL_ID = 1402203061820194920


async def scrape_wordle_history(bot: discord.Client) -> list[discord.Message]:
    channel = bot.get_channel(WORDLE_CHANNEL_ID)
    if channel is None:
        raise RuntimeError("Wordle channel not found")

    messages = []

    async for message in channel.history(limit=None, oldest_first=True):
        if not message.author.bot:
            continue
        if "Here are yesterday's results:" not in message.content:
            continue

        messages.append(message)

    return messages



STREAK_RE = re.compile(r"(\d+)\s+day streak")
SCORE_RE = re.compile(r"(\d)/6:")


MENTION_ID_RE = re.compile(r"<@(\d+)>")
PLAIN_NAME_RE = re.compile(r"@([^(@]+)")


def resolve_plain_name(name: str, guild: discord.Guild):
    """
    Try to resolve a plain-text @name to a guild member.
    Returns discord.Member or None.
    """
    name = name.strip()

    matches = [
        m for m in guild.members
        if m.display_name == name or m.name == name
    ]

    # Only accept unambiguous matches
    if len(matches) == 1:
        return matches[0]

    return None


def parse_wordle_message(message: discord.Message) -> dict:
    lines = message.content.splitlines()
    game_date = message.created_at.date().isoformat()

    # --------------------
    # Extract streak
    # --------------------
    streak = None
    for line in lines:
        m = STREAK_RE.search(line)
        if m:
            streak = int(m.group(1))
            break

    results = []

    for line in lines:
        score_match = SCORE_RE.search(line)
        if not score_match:
            continue

        guesses = int(score_match.group(1))

        # --------------------
        # 1️⃣ Real mentions
        # --------------------
        for user in message.mentions:
            if f"<@{user.id}>" in line:
                results.append({
                    "date": game_date,
                    "user_id": user.id,
                    "username": user.display_name,
                    "guesses": guesses,
                })

        # --------------------
        # 2️⃣ Plain-text @names
        # --------------------
        plain_names = PLAIN_NAME_RE.findall(line)

        for name in plain_names:
            member = resolve_plain_name(name, message.guild)

            if member:
                results.append({
                    "date": game_date,
                    "user_id": member.id,
                    "username": member.display_name,
                    "guesses": guesses,
                })
            else:
                results.append({
                    "date": game_date,
                    "user_id": None,           # explicitly unknown
                    "username": name.strip(),
                    "guesses": guesses,
                })

    return {
        "date": game_date,
        "streak": streak,
        "results": results,
    }




async def get_all_wordle_results(bot) -> list[dict]:
    raw_messages = await scrape_wordle_history(bot)

    parsed_days = []
    seen_dates = set()

    for message in raw_messages:
        parsed = parse_wordle_message(message)
        if parsed["date"] in seen_dates:
            continue

        seen_dates.add(parsed["date"])
        parsed_days.append(parsed)

    return parsed_days


def wordle_results_to_df(wordle_results: list[dict]) -> pd.DataFrame:
    rows = []
    for day in wordle_results:
        rows.extend(day["results"])
    return pd.DataFrame(rows)


def average_guesses_per_player(df: pd.DataFrame) -> pd.DataFrame:
    avg_df = (
        df
        .groupby(["user_id", "username"], as_index=False)
        .agg(
            avg_guesses=("guesses", "mean"),
            games_played=("guesses", "count"),
        )
        .sort_values("avg_guesses")
    )

    # Filter players with at least 5 games
    avg_df = avg_df[avg_df["games_played"] >= 5]

    avg_df["avg_guesses"] = avg_df["avg_guesses"].round(2)
    return avg_df



def plot_average_guesses(avg_df: pd.DataFrame, output_path="wordle_avg_guesses.png"):
    # Wordle-inspired colors
    WORDLE_GREEN = "#6aaa64"
    WORDLE_DARK = "#121213"
    WORDLE_TEXT = "#d7dadc"

    plt.figure(figsize=(12, 6))
    ax = plt.gca()

    # Background styling
    ax.set_facecolor(WORDLE_DARK)
    plt.gcf().patch.set_facecolor(WORDLE_DARK)

    bars = ax.bar(
        avg_df["username"],
        avg_df["avg_guesses"],
        color=WORDLE_GREEN,
        edgecolor="none"
    )

    # Labels & title
    ax.set_title(
        "Average Wordle Guesses per Player (min 5 games)",
        color=WORDLE_TEXT,
        fontsize=14,
        pad=15,
        weight="bold"
    )
    ax.set_xlabel("Player", color=WORDLE_TEXT, fontsize=11)
    ax.set_ylabel("Average guesses", color=WORDLE_TEXT, fontsize=11)

    # Axis styling
    ax.tick_params(axis="x", colors=WORDLE_TEXT, rotation=45)
    ax.tick_params(axis="y", colors=WORDLE_TEXT)
    ax.spines["bottom"].set_color(WORDLE_TEXT)
    ax.spines["left"].set_color(WORDLE_TEXT)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.03,
            f"{height:.2f}",
            ha="center",
            va="bottom",
            color=WORDLE_TEXT,
            fontsize=9,
            weight="bold"
        )

    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()

    return output_path


async def run_wordle_analysis(bot):
    wordle_results = await get_all_wordle_results(bot)

    df = wordle_results_to_df(wordle_results)
    avg_df = average_guesses_per_player(df)

    image_path = plot_average_guesses(avg_df)
    return image_path