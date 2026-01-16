# main.py
import logging
from discord import Intents
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="!",intents=Intents.all())


@bot.event
async def on_ready():
    await bot.load_extension("commands.user")
    await bot.tree.sync(guild=discord.Object(id=1404817877504229426))
    logging.getLogger("discord").info("Ready.")

@bot.command(name="reload")
async def reload_module(ctx: commands.Context,name: str):
    await bot.reload_extension(f"commands.{name}")
    await ctx.send(f"Module {name} reloaded")

bot.run("REMOVE")