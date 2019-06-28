import discord
from main import get_name
from player import Player
from discord.ext import commands

bot = commands.Bot(command_prefix='!', description='Pokemon')

@bot.command(pass_context=True)
async def fighting(ctx):
    player = Player(ctx.message.author.id)
    desc = "Pokemon Trainee " + await get_name(ctx.message.author) + ", \n\n"
    desc = desc + "Idk what to put here"
    desc = desc + "\nType out a number within 15 seconds or you will timeout"

    embed = discord.Embed(description=desc, colour=0x00ff00)
    embed.set_author(name="Fighting", icon_url=ctx.message.author.avatar_url)

    await bot.send_message(ctx.message.channel, embed=embed)
    msg = await bot.wait_for_message(timeout=15, author=ctx.message.author, channel=ctx.message.channel)
