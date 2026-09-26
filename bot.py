"""
GrimNukeBot - Personal Discord bot
/grimnuke command: deletes the current channel and recreates it identically
(same name, category, position, permissions, topic, nsfw, slowmode, etc.)
"""

import os
import logging

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError(
        "Missing DISCORD_TOKEN environment variable. "
        "Create a .env file based on .env.example."
    )

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("grimnukebot")

# The bot doesn't need any privileged intents for this feature.
intents = discord.Intents.default()

bot = commands.Bot(command_prefix="!grimnuke-unused!", intents=intents)


@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        log.info("Synced %d slash command(s).", len(synced))
    except Exception:
        log.exception("Failed to sync commands.")
    log.info("Logged in as %s (id: %s)", bot.user, bot.user.id)


SUPPORTED_CHANNEL_TYPES = (
    discord.TextChannel,
    discord.VoiceChannel,
    discord.StageChannel,
    discord.ForumChannel,
)


@bot.tree.command(
    name="grimnuke",
    description="Deletes this channel and recreates it identically (name, permissions, position...).",
)
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.guild_only()
async def grimnuke(interaction: discord.Interaction):
    channel = interaction.channel
    guild = interaction.guild

    if guild is None or channel is None:
        await interaction.response.send_message(
            "This command must be used in a server channel.",
            ephemeral=True,
        )
        return

    if not isinstance(channel, SUPPORTED_CHANNEL_TYPES):
        await interaction.response.send_message(
            "This channel type is not supported by GrimNukeBot.",
            ephemeral=True,
        )
        return

    # Make sure the bot actually has permission to manage channels here.
    me = guild.me
    if not channel.permissions_for(me).manage_channels:
        await interaction.response.send_message(
            "I don't have the `Manage Channels` permission on this channel.",
            ephemeral=True,
        )
        return

    # Respond right away (we have 3s before Discord times out); the
    # ephemeral message stays valid even if the original channel
    # disappears right after.
    await interaction.response.send_message(
        "💣 GrimNuke in progress...", ephemeral=True
    )

    original_position = channel.position
    original_name = channel.name
    reason = f"GrimNuke triggered by {interaction.user} ({interaction.user.id})"

    log.info(
        "GrimNuke requested by %s on #%s (id=%s) in %s",
        interaction.user,
        original_name,
        channel.id,
        guild.name,
    )

    try:
        # clone() copies over: name, category, permission overwrites,
        # topic/nsfw/slowmode (text) or bitrate/user_limit (voice), etc.
        new_channel = await channel.clone(reason=reason)

        # Position isn't guaranteed to be preserved by clone(), so we
        # fix it explicitly.
        await new_channel.edit(position=original_position, reason=reason)

        await channel.delete(reason=reason)

    except discord.Forbidden:
        # The initial ephemeral response has already been sent, and we
        # can't reliably respond again on a potentially deleted channel,
        # so we just log the error.
        log.exception("Insufficient permissions to complete the GrimNuke.")
        return
    except discord.HTTPException:
        log.exception("Discord error during GrimNuke.")
        return

    try:
        if isinstance(new_channel, (discord.TextChannel, discord.ForumChannel)):
            await new_channel.send(
                f"✅ Channel recreated by {interaction.user.mention} via `/grimnuke`."
            )
    except discord.HTTPException:
        pass

    log.info("GrimNuke complete: new channel id=%s", new_channel.id)


@grimnuke.error
async def grimnuke_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            "You need the `Manage Channels` permission to use this command.",
            ephemeral=True,
        )
    else:
        log.exception("Unexpected error in /grimnuke", exc_info=error)
        if interaction.response.is_done():
            await interaction.followup.send("An error occurred.", ephemeral=True)
        else:
            await interaction.response.send_message(
                "An error occurred.", ephemeral=True
            )


if __name__ == "__main__":
    bot.run(TOKEN)