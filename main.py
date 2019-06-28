import discord
import time
from player import Player
from pokeconfig import PokeConfig
from pokemon import Pokemon
from discord.ext import commands
import datetime
import random
import asyncio
from pprint import pprint
from FightEmbedGUI import FightEmbedGUI

bot = commands.Bot(command_prefix='!', description='Pokemon')

class Storage:
	inCombat = []
	vsWho = {}
	timers = {}

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
	embed.set_author(name="Daily Rewards", icon_url=ctx.message.author.avatar_url)
	await bot.send_message(ctx.message.channel, embed=embed)


def pokemon_shop_check(msg):
	if not msg.content.isdigit():
		return False;

	if int(msg.content) < 1:
		return False

	return int(msg.content) <= len(PokeConfig.shopItems)


@bot.command(pass_context=True)
async def shop(ctx):
	player = Player(ctx.message.author.id)
	shop_items = PokeConfig.shopItems

	description = "Pokemon Trainee " + await get_name(ctx.message.author) + ", \n\n"
	for i in range(len(shop_items)):
		v = shop_items[i]
		description = description + (str(i + 1) + ". " + ("**" + v["name"] + "**").title()) + ": **" + str(v["cost"]) + "g**\n"
	description = description + "\nType out a number within 15 seconds or you will timeout"

	embed = discord.Embed(description=description, colour=0x00ff00)
	embed.set_author(name="Shop", icon_url=ctx.message.author.avatar_url)

	await bot.send_message(ctx.message.channel, embed=embed)
	msg = await bot.wait_for_message(timeout=15, author=ctx.message.author, channel=ctx.message.channel, check=pokemon_shop_check)
	if not (msg is None):
		player_bal = player.get_coins()
		selected_item = shop_items[int(msg.content) - 1]

		if player_bal < selected_item["cost"]:
			embed = discord.Embed(description="You do not have enough gold. You need **" + str(selected_item["cost"] - player_bal) + "g** more", colour=0xff0000)
			embed.set_author(name=(await get_name(ctx.message.author)), icon_url=ctx.message.author.avatar_url)

			await bot.send_message(ctx.message.channel, embed=embed)

			return True

		player.set_coins(player_bal - selected_item["cost"])
		player.add_item(selected_item["name"], selected_item["description"], 1)

		embed = discord.Embed(description="You successfully bought a **" + selected_item["name"] + "** for **" + str(selected_item["cost"]) + "g**.", colour=0x00ff00)
		embed.set_author(name="Bought Notification", icon_url=ctx.message.author.avatar_url)

		await bot.send_message(ctx.message.channel, embed=embed)


def pokemon_starter_predicate_check(msg):
	if not msg.content.isdigit():
		return False

	if int(msg.content) < 1:
		return False

	return int(msg.content) <= len(PokeConfig.startingPokemon)


@bot.command(pass_context=True, aliases=['starter'])
async def start(ctx):
	player = Player(ctx.message.author.id)

	if player.has_player_started():
		embed = discord.Embed(description="You have already chosen a starter pokemon.", colour=0xff0000)
		embed.set_author(name=(await get_name(ctx.message.author)), icon_url=ctx.message.author.avatar_url)

		await bot.send_message(ctx.message.channel, embed=embed)
		return True

	description = "Pokemon Trainee " + await get_name(ctx.message.author) + ", \n\n"
	for i in range(len(PokeConfig.startingPokemon)):
		poke = Pokemon(id=int(PokeConfig.startingPokemon[i]))
		description = description + (str(i + 1) + ". " + ("**" + poke.get_name() + "**").title()) + "\n"
	description = description + "\nType the number of the item listed above (e.g 1) to buy the item."

	embed = discord.Embed(description=description, colour=0x00ff00)
	embed.set_author(name="Choose a starter pokemon", icon_url=ctx.message.author.avatar_url)

	await bot.send_message(ctx.message.channel, embed=embed)

	msg = await bot.wait_for_message(timeout=15, author=ctx.message.author, channel=ctx.message.channel, check=pokemon_starter_predicate_check)
	if not (msg is None):
		poke = PokeConfig.startingPokemon[int(msg.content) - 1]
		poke_obj = Pokemon(id=poke)
		starting_moves = poke_obj.get_starting_moves()
		pprint(starting_moves)
		player.add_pokemon(int(poke_obj.get_id()), 1, ','.join(starting_moves), 10)
		player.set_player_started()

		embed = discord.Embed(description="Congratulations! You got yourself a lil " + poke_obj.get_name() + "! Starting Moves: " + ', '.join(starting_moves), colour=0x00ff00)
		await bot.send_message(ctx.message.channel, embed=embed)


@bot.command(pass_context=True, aliases=['list'])
async def pokemon(ctx):
	player = Player(ctx.message.author.id)

	pokemon_list = player.get_pokemon_list()

	if len(pokemon_list) == 0:
		embed = discord.Embed(description="You do not have any pokemon currently. Try doing !start", colour=0xff0000)
		embed.set_author(name=(await get_name(ctx.message.author) + "'s pokemon list"), icon_url=ctx.message.author.avatar_url)
		await bot.send_message(ctx.message.channel, embed=embed)
		return True

	description = "Your pokemon list:\n\n"

	for i in range(len(pokemon_list)):
		poke = pokemon_list[i]
		description = description + (str(i + 1) + ". " + ("**" + poke.get_name() + "**").title()) + " (Level " + str(poke.get_level()) + ") [" + poke.get_moves() + "]\n"

	embed = discord.Embed(description=description, colour=0xffff00)
	embed.set_author(name=(await get_name(ctx.message.author) + "'s pokemon list"), icon_url=ctx.message.author.avatar_url)

	await bot.send_message(ctx.message.channel, embed=embed)


@bot.command(pass_context=True, aliases=['item'])
async def items(ctx):
	player = Player(ctx.message.author.id)

	item_list = player.get_item_list()

	if len(item_list) == 0:
		embed = discord.Embed(description="You do not have any items currently. You can buy items at !shop.", colour=0xff0000)
		embed.set_author(name=(await get_name(ctx.message.author) + "'s item list"), icon_url=ctx.message.author.avatar_url)
		await bot.send_message(ctx.message.channel, embed=embed)
		return True

	description = "Your item list:\n\n"

	for i in range(len(item_list)):
		item = item_list[i]
		description = description + (str(i + 1) + ". " + ("**" + item.get_name() + "**").title()) + " **" + str(item.get_amount()) + "x** (" + item.get_description() + ")\n"

	embed = discord.Embed(description=description, colour=0xffff00)
	embed.set_author(name=(await get_name(ctx.message.author) + "'s pokemon list"), icon_url=ctx.message.author.avatar_url)

	await bot.send_message(ctx.message.channel, embed=embed)


async def kill_player_combat():
	await bot.wait_until_ready()

	while not bot.is_closed:
		pop_list = []

		for key, value in Storage.timers.items():
			if (time.time() - value) >= 15:
				pop_list.append(key)
				Storage.inCombat.remove(key)

				if key in Storage.vsWho:
					del Storage.vsWho[key]

				player = Player(key.id)
				goldLost = random.randint(5, 27)
				player.set_coins(player.get_coins() - goldLost)
				embed = discord.Embed(description="You lost your game due to not responding. You also lost **" + str(goldLost) + "g**.", colour=0xff0000)

				embed.set_author(name=(await get_name(key)), icon_url=key.avatar_url)

				try:
					await bot.send_message(key, embed=embed)
				except:
					print("Exception")

		for i in pop_list:
			del Storage.timers[i]
		await asyncio.sleep(10)

@bot.command(pass_context=True)
async def wild(ctx):
	if ctx.message.author.id in Storage.inCombat:
		embed = discord.Embed(description="You are currently in combat.", colour=0xff0000)
		embed.set_author(name=(await get_name(ctx.message.author)), icon_url=ctx.message.author.avatar_url)
		await bot.send_message(ctx.message.channel, embed=embed)
		return False

	player = Player(ctx.message.author.id)
	level = 115
	player_pokemon = Pokemon(name="Pikachu", real=True, level=level, owner=ctx.message.author.id, moves="tackle,quick_attack")
	wild_pokemon = Pokemon(id=random.randint(1, 151), level=level + 10)
	first_pokemon = wild_pokemon
	first_move = "Wilderness"

	if wild_pokemon.get_stat("speed", level) < player_pokemon.get_stat("speed", level):
		first_pokemon = player_pokemon
		first_move = ctx.message.author

	embedGUI = FightEmbedGUI(challenger=ctx.message.author, firstMove=first_move, fpokemon=first_pokemon, opponent="Wilderness", wild=True, cpokemon=player_pokemon, opokemon=wild_pokemon)

	Storage.inCombat.append(ctx.message.author)
	Storage.timers.update({ctx.message.author: time.time()})
	await bot.send_message(ctx.message.channel, embed=embedGUI.get_embed())


@bot.event
async def on_ready():
	print("-----------------------------------------------------")
	print("User: " + bot.user.name)
	print("User ID: " + bot.user.id)
	print("oAuth Link (Invite Link): " + discord.utils.oauth_url(bot.user.id))
	print("-----------------------------------------------------")
	await bot.change_presence(game=discord.Game(name="!", type=1))
	bot.loop.create_task(kill_player_combat())

@bot.event
async def on_message(msg):
	if msg.author.id == "593408190364778517":
		return False

	if msg.content == '!stop' and msg.author.id == "290316591462088706":
		await bot.logout()
		return True

	await bot.process_commands(msg)
	
bot.run(PokeConfig.token)
