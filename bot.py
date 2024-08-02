import asyncio
import json
import os
import platform
import random
import sys
import io

import aiosqlite
import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot, Context

import exceptions

# Ensure the configuration file exists
config_path = f"{os.path.realpath(os.path.dirname(__file__))}/config.json"
if not os.path.isfile(config_path):
    sys.exit("'config.json' not found! Please add it and try again.")
else:
    with open(config_path) as file:
        config = json.load(file)

# Set up Discord intents
intents = discord.Intents.default()
intents.message_content = True

# Create bot instance
bot = Bot(command_prefix=commands.when_mentioned_or(config["prefix"]), intents=intents, help_command=None)

# Initialize the database
async def init_db():
    db_path = f"{os.path.realpath(os.path.dirname(__file__))}/database/database.db"
    schema_path = f"{os.path.realpath(os.path.dirname(__file__))}/database/schema.sql"
    async with aiosqlite.connect(db_path) as db:
        with open(schema_path) as file:
            await db.executescript(file.read())
        await db.commit()

bot.config = config

# Handle bot readiness event
@bot.event
async def on_ready() -> None:
    status_task.start()
    if config.get("sync_commands_globally", False):
        print(f"Logged in as {bot.user.name}")
        print(f"discord.py API version: {discord.__version__}")
        print(f"Python version: {platform.python_version()}")
        print("---------------------------------------------------------------------------------")
        print("Made by : Dexv")
        print(f" GitHub: https://github.com/Dexiikk ")
        print(f" Description: Simple open source discord bot made with python ")
        print("-------------------")
        print("Syncing commands globally...")
        await bot.tree.sync()

# Define the status task
@tasks.loop(minutes=1.0)
async def status_task() -> None:
    statuses = ["Status 1", "Made with 💗 by Dexik"]
    await bot.change_presence(activity=discord.Game(random.choice(statuses)))

# Process commands
@bot.event
async def on_message(message: discord.Message) -> None:
    if message.author == bot.user or message.author.bot:
        return
    await bot.process_commands(message)

# Handle command completion
@bot.event
async def on_command_completion(context: Context) -> None:
    full_command_name = context.command.qualified_name
    split = full_command_name.split(" ")
    executed_command = str(split[0])
    if context.guild is not None:
        print(f"Executed {executed_command} command in {context.guild.name} (ID: {context.guild.id}) by {context.author} (ID: {context.author.id})")
    else:
        print(f"Executed {executed_command} command by {context.author} (ID: {context.author.id}) in DMs")

# Handle command errors
@bot.event
async def on_command_error(context: Context, error) -> None:
    if isinstance(error, commands.CommandOnCooldown):
        minutes, seconds = divmod(error.retry_after, 60)
        hours, minutes = divmod(minutes, 60)
        hours = hours % 24
        embed = discord.Embed(
            title="Slow down!",
            description=f"You can use this command in {f'{round(hours)} h' if round(hours) > 0 else ''} {f'{round(minutes)} m' if round(minutes) > 0 else ''} {f'{round(seconds)} s' if round(seconds) > 0 else ''}.",
            color=0xE02B2B
        )
        await context.send(embed=embed)
    elif isinstance(error, exceptions.UserBlacklisted):
        embed = discord.Embed(
            title="You are blacklisted",
            description="You cannot use this bot.",
            color=0xE02B2B
        )
        await context.send(embed=embed)
    elif isinstance(error, exceptions.UserNotOwner):
        embed = discord.Embed(
            title="Error!",
            description="You are not the developer!",
            color=0xE02B2B
        )
        await context.send(embed=embed)
    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="Error!",
            description="You lack the permissions `" + ", ".join(error.missing_permissions) + "` to use this command.",
            color=0xE02B2B
        )
        await context.send(embed=embed)
    elif isinstance(error, commands.BotMissingPermissions):
        embed = discord.Embed(
            title="Error!",
            description="I am missing the permission(s) `" + ", ".join(error.missing_permissions) + "` to fully perform this command!",
            color=0xE02B2B
        )
        await context.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="Error!",
            description=str(error).capitalize(),
            color=0xE02B2B
        )
        await context.send(embed=embed)
    raise error

# Load cogs
async def load_cogs() -> None:
    cog_dir = f"{os.path.realpath(os.path.dirname(__file__))}/cogs"
    for file in os.listdir(cog_dir):
        if file.endswith(".py"):
            extension = file[:-3]
            try:
                await bot.load_extension(f"cogs.{extension}")
                print(f"Loaded extension '{extension}'")
            except Exception as e:
                exception = f"{type(e).__name__}: {e}"
                print(f"Failed to load extension {extension}\n{exception}")

# Initialize database and load cogs
asyncio.run(init_db())
asyncio.run(load_cogs())
bot.run(config["token"])
