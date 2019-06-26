import discord
import asyncio
from pokeconfig import pokeconfig
import async_timeout
from discord.ext import commands

bot = commands.Bot(command_prefix='broken prefix lul lul ulul', description='Relerx\'s CIT2 Bot')

@bot.event
async def on_ready():
	print("yo")

bot.run(pokeconfig.token)