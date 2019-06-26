import discord
import asyncio
import database
import sqlite3
import time
from player import Player
from pokeconfig import PokeConfig
import async_timeout
from discord.ext import commands
import datetime

bot = commands.Bot(command_prefix='!', description='Pokemon')


async def get_name(author):
	name = str(author)

	if isinstance(author, discord.Member) and isinstance(author.nick, str):
		name = author.nick

	return name


@bot.command(pass_context=True, aliases=['bal'])
async def balance(ctx):
	player = Player(ctx.message.author.id)
	coins = player.get_coins()
	desc = "You have **" + str(coins) + "g**."
	embed = discord.Embed(description=desc, colour=0x00ff00)
	embed.set_author(name=(await get_name(ctx.message.author) + "'s balance"), icon_url=ctx.message.author.avatar_url)
	await bot.send_message(ctx.message.channel, embed=embed)


@bot.command(pass_context=True, aliases=['daily'])
async def rewards(ctx):
	player = Player(ctx.message.author.id)
	rewards_time = player.get_rewards_epoch() + player.get_reward_timer()
	time_left = (rewards_time - int(time.time()))

	desc = "You have claimed your reward of **" + str(player.get_reward()) + "g**."
	colour = 0x00ff00

	if time_left > 0:
		date = datetime.timedelta(seconds=time_left)
		final_datestrp = datetime.datetime.strptime(str(date), "%H:%M:%S")
		final_date = final_datestrp.strftime("%H hours %M minutes %S seconds")
		desc = "You have **" + str(final_date) + "** left until you can claim your reward again."
		colour = 0xff0000
	else:
		player.set_reward_timestamp()
		player.set_coins(player.get_coins() + player.get_reward())

	embed = discord.Embed(description=desc, colour=colour)
	embed.set_author(name=(await get_name(ctx.message.author) + "'s rewards"), icon_url=ctx.message.author.avatar_url)
	await bot.send_message(ctx.message.channel, embed=embed)

@bot.command(pass_context=True, aliases['starter'])
async def start(ctx):
	player = Player(ctx.message.author.id)

	if player.has_player_started():
		embed = discord.Embed(description="You have already chosen a starter pokemon.", colour=0xff0000)
		embed.set_author(name=(await get_name(ctx.message.author)), icon_url=ctx.message.author.avatar_url)
		return True;


@bot.event
async def on_ready():
	print("-----------------------------------------------------")
	print("User: " + bot.user.name)
	print("User ID: " + bot.user.id)
	print("oAuth Link (Invite Link): " + discord.utils.oauth_url(bot.user.id))
	print("-----------------------------------------------------")
	await bot.change_presence(game=discord.Game(name="!", type=1))


@bot.event
async def on_message(msg):
	if msg.content == '!stop' and msg.author.id == "290316591462088706":
		await bot.logout()
		return True

	plr = Player(msg.author.id)
	plr.get_coins()
	#  plr.set_coins(500)
	await bot.process_commands(msg)
	
bot.run(PokeConfig.token)
