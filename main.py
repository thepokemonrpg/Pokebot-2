import discord
import time
from player import Player
from pokeconfig import PokeConfig
from pokemon import Pokemon
from pokemon import DamageModifier
from discord.ext import commands
from Pokeball import Pokeball
import datetime
import random
import asyncio
import traceback
from pprint import pprint
from FightEmbedGUI import FightEmbedGUI

bot = commands.Bot(command_prefix='!', description='Pokemon')


class Storage:
	inCombat = []
	vsWho = {}
	timers = {}
	hpBar = {}
	embed = {}
	vsPokemon = {}
	opponentID = {}
	messages = {}
	vsWhoObj = {}


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


bot.remove_command("help")


@bot.command()
async def help(ctx, *args):
	if len(args) == 0:
		em = discord.Embed(title="Help!", description="How may I help you? The command prefix is '!'", colour=0xFFFF00)
		em.set_author(name=str(bot.user), icon_url=bot.user.avatar_url)
		em.add_field(name="!help", value="Shows this message", inline=False)
		em.add_field(name="!balance | !bal", value="Shows the amount of gold you have", inline=False)
		em.add_field(name="!rewards | !daily", value="Gives you 500g every 24 hours", inline=False)
		em.add_field(name="!shop", value="You can buy PokeBalls there", inline=False)
		em.add_field(name="!start | !starter", value="Start your pokemon journey with Dr.Oak!", inline=False)
		em.add_field(name="!pokemon | !list", value="Shows all your current pokemon", inline=False)
		em.add_field(name="!equip <id>", value="Equip your pokemon for battle.", inline=False)
		em.add_field(name="!items | !item", value="Shows all items in your possession", inline=False)
		em.add_field(name="!wild", value="Roam out in the wild and fight a Pokemon.", inline=False)
		await ctx.send(embed=em)

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
		player.add_pokemon(int(poke_obj.get_id()), 1, ','.join(starting_moves), 10)
		player.set_player_started()

		embed = discord.Embed(description="Congratulations! You got yourself a lil " + poke_obj.get_name().title() + "! Starting Moves: " + ', '.join(starting_moves), colour=0x00ff00)
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
	current_equip = player.get_equip()

	for i in range(len(pokemon_list)):
		poke = pokemon_list[i]
		if poke.get_unique_id() == current_equip:
			description = description + (str(i + 1) + ". " + ("**" + poke.get_name() + "**").title()) + " (Unique Identifier: " + str(poke.get_unique_id()) + ") (Level " + str(poke.get_level()) + ") [" + ', '.join(poke.get_moves()) + "] **Currently selected!**\n"
		else:
			description = description + (str(i + 1) + ". " + ("**" + poke.get_name() + "**").title()) + " (Unique Identifier: " + str(poke.get_unique_id()) + ") (Level " + str(poke.get_level()) + ") [" + ', '.join(poke.get_moves()) + "]\n"

	embed = discord.Embed(description=description, colour=0xffff00)
	embed.set_author(name=(await get_name(ctx.message.author) + "'s pokemon list"), icon_url=ctx.message.author.avatar_url)

	await bot.send_message(ctx.message.channel, embed=embed)


@bot.command(pass_context=True)
async def equip(ctx, pokemonID: str):
	if not pokemonID or not pokemonID.isdigit():
		embed = discord.Embed(description="Please enter a unique number as seen in !list", colour=0xff0000)
		embed.set_author(name="Error", icon_url=ctx.message.author.avatar_url)
		await bot.send_message(ctx.message.channel, embed=embed)
		return False

	pokemonID = int(pokemonID)
	player = Player(ctx.message.author.id)

	if player.get_equip() == pokemonID:
		embed = discord.Embed(description="You have already equipped this pokemon", colour=0xff0000)
		embed.set_author(name="Error", icon_url=ctx.message.author.avatar_url)
		await bot.send_message(ctx.message.channel, embed=embed)
		return False

	if not (pokemonID in player.get_pokemon_id_list()):
		embed = discord.Embed(description="Invalid ID entered", colour=0xff0000)
		embed.set_author(name="Error", icon_url=ctx.message.author.avatar_url)
		await bot.send_message(ctx.message.channel, embed=embed)
		return False

	player.set_equip(pokemonID)
	embed = discord.Embed(description="You have equipped '" + player.get_equip_pokemon().get_name().title() + "' sucessfully." , colour=0x00ff00)
	embed.set_author(name="Equip", icon_url=ctx.message.author.avatar_url)
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
		if item.get_amount() > 0:
			description = description + (str(i + 1) + ". " + ("**" + item.get_name() + "**").title()) + " **" + str(item.get_amount()) + "x** (" + item.get_description() + ")\n"

	embed = discord.Embed(description=description, colour=0xffff00)
	embed.set_author(name=(await get_name(ctx.message.author) + "'s pokemon list"), icon_url=ctx.message.author.avatar_url)

	await bot.send_message(ctx.message.channel, embed=embed)


def delete(key, dict):
	if key in dict:
		del dict[key]

async def kill_combat(key):
	if key in Storage.inCombat:
		Storage.inCombat.remove(key)

	delete(key.id, Storage.hpBar)
	delete(key.id, Storage.embed)
	delete(key.id, Storage.messages)
	delete(key.id, Storage.vsPokemon)
	delete(key.id, Storage.opponentID)
	delete("W" + key.id, Storage.opponentID)
	delete("W" + key.id, Storage.hpBar)
	delete(key, Storage.vsWhoObj)
	delete(key, Storage.timers)

	if key in Storage.vsWho:
		vsWho = Storage.vsWho.get(key)

		delete(key, Storage.vsWho)
		delete(vsWho, Storage.vsWho)
		delete(vsWho.id, Storage.hpBar)
		delete(vsWho, Storage.timers)
		delete(vsWho.id, Storage.embed)
		delete(vsWho.id, Storage.messages)
		delete(vsWho.id, Storage.opponentID)
		delete(vsWho, Storage.vsWhoObj)


async def kill_player_combat():
	await bot.wait_until_ready()

	while not bot.is_closed:
		pop_list = []

		try:
			for key, value in Storage.timers.items():
				if (time.time() - value) >= 15 and not key in pop_list:
					pop_list.append(key)

					player = Player(key.id)
					goldLost = random.randint(5, 27)
					player.set_coins(player.get_coins() - goldLost)
					embed = discord.Embed(description="You lost your game due to not responding. You also lost **" + str(goldLost) + "g**.", colour=0xff0000)

					embed.set_author(name=(await get_name(key)), icon_url=key.avatar_url)

					if key in Storage.vsWho:
						vsWho = Storage.vsWho.get(key)

						player = Player(vsWho.id)
						player.set_coins(player.get_coins() + goldLost)
						embed = discord.Embed(
							description="You won **" + str(goldLost) + "g** as your opponent failed to respond.",
							colour=0xff0000)
						embed.set_author(name=(await get_name(vsWho)), icon_url=vsWho.avatar_url)

					await kill_combat(key)

					try:
						await bot.send_message(key, embed=embed)
					except:
						print("Exception")
		except:
			print("")

		for i in pop_list:
			delete(i, Storage.timers)
		await asyncio.sleep(10)


async def do_wild_move(wild_pokemon, player_pokemon, embedGUI, author, message=False):
	moves = random.choice(wild_pokemon.get_wild_moves())
	DamageModifier_obj = DamageModifier(type=wild_pokemon.get_type())
	move_obj = wild_pokemon.get_move(moves)
	power = 50
	if move_obj.power:
		power = move_obj.power

	attack_stat = wild_pokemon.get_stat("attack", wild_pokemon.get_level())
	defense_stat = player_pokemon.get_stat("defense", player_pokemon.get_level())

	if move_obj.damage_class.name == "special":
		attack_stat = wild_pokemon.get_stat("special-attack", wild_pokemon.get_level())
		defense_stat = player_pokemon.get_stat("special-defense", player_pokemon.get_level())

	damage_done = round(DamageModifier_obj.get_move_damage(power, attack_stat, wild_pokemon.get_level(), move_obj.type.name, player_pokemon.get_type(), defense_stat, True))
	embedGUI.add_log(wild_pokemon.get_name().title() + " used **" + moves + "** and did **" + str(damage_done) + "** damage!")

	currentHP = Storage.hpBar.get(author.id)

	Storage.hpBar.update({author.id: (currentHP - damage_done)})

	hpBar = round(((currentHP - damage_done) / player_pokemon.get_stat("hp", player_pokemon.get_level())) * 8)
	hpString = "▰" * hpBar
	hpString = hpString + ("▱" * (8 - hpBar))
	embedGUI.update_opponent(0, str(currentHP - damage_done) + "/" + str(
	player_pokemon.get_stat("hp", player_pokemon.get_level())), hpString)

	if (currentHP - damage_done) <= 0:
		embedGUI.add_log(player_pokemon.get_name().title() + " has fainted. Wilderness wins.")
		if message:
			await bot.edit_message(message=Storage.messages.get(author.id), embed=embedGUI.get_embed())
		await kill_combat(author)
		return True

	Storage.timers.update({author: time.time()})
	embedGUI.set_move(author, player_pokemon)

	if message:
		try:
			await bot.edit_message(message=Storage.messages[author.id], embed=embedGUI.get_embed())
		except:
			traceback.print_exc()

def pokemon_check_levelup_msg(msg):
	char = (ord(msg.content.lower()[:1]) - 96)
	if char < 1 or char > 4:
		return False
	return True

async def award_victory(player, channel):
	p = Player(player.id)
	pokemon = p.get_equip_pokemon()
	xpReward = random.randint(10, 30)
	goldReward = random.randint(5, 16)
	currXP = pokemon.get_exp()
	requiredXP = pokemon.get_exp_for_levelup()

	p.set_coins(p.get_coins() + goldReward)

	extra = "\n"
	desc = "You have won a battle and earned: \n\n**" + str(goldReward) + "g**\n**" + str(xpReward) + " XP** for " + pokemon.get_name()
	newMove = ""
	awaitMessage = False

	if (currXP + xpReward) >= requiredXP:
		newMoves = pokemon.get_new_moves(pokemon.get_level() + 1)
		pprint(newMoves)
		if len(newMoves) > 0:
			newMove = random.choice(pokemon.get_new_moves(pokemon.get_level() + 1))
		currentMoves = pokemon.get_moves()
		extra = extra + "\nYour " + pokemon.get_name() + " has leveled up to level " + str(pokemon.get_level() + 1) + "\n\n"
		p.set_exp_pokemon(pokemon.get_unique_id(), (currXP + xpReward) - requiredXP)
		p.set_level_pokemon(pokemon.get_unique_id(), pokemon.get_level() + 1)

		if len(currentMoves) < 4 and newMove != "":
			extra = extra + "Your pokemon has learned the move: **" + newMove + "**\n"
			p.set_moves(pokemon.get_unique_id(), ','.join(currentMoves) + "," + newMove)
		if len(currentMoves) == 4 and newMove != "":
			extra = extra + "Your pokemon can learn the move **" + newMove + "**\nCurrent Moves: " + pokemon.get_beauty_moves() + "\n\nChoose **1** letter to replace the move. You have 10 seconds."
			awaitMessage = True
	else:
		player.set_exp_pokemon(pokemon.get_unique_id(), currXP + xpReward)

	embed = discord.Embed(description=desc + extra, colour=0x00ff00)
	embed.set_author(name=(await get_name(player)), icon_url=player.avatar_url)
	await bot.send_message(channel, embed=embed)

	if awaitMessage:
		msg = await bot.wait_for_message(timeout=15, author=player, channel=channel, check=pokemon_check_levelup_msg)
		if not (msg is None):
			chosenOption = (ord(msg.content.lower()[:1]) - 96)
			movesTbl = pokemon.get_moves()
			movesTbl[chosenOption] = newMove
			p.set_moves(pokemon.get_unique_id(), ','.join(movesTbl))

			embed = discord.Embed(description=pokemon.get_name().title() + " successfully learnt the move **" + newMove + "**.", colour=0x00ff00)
			embed.set_author(name="Moves", icon_url=player.avatar_url)

			await bot.send_message(channel, embed=embed)


@bot.command(pass_context=True)
async def wild(ctx):
	if ctx.message.author.id in Storage.inCombat:
		embed = discord.Embed(description="You are currently in combat.", colour=0xff0000)
		embed.set_author(name=(await get_name(ctx.message.author)), icon_url=ctx.message.author.avatar_url)
		await bot.send_message(ctx.message.channel, embed=embed)
		return False

	player = Player(ctx.message.author.id)
	player_pokemon = player.get_equip_pokemon()

	if not player_pokemon:
		embed = discord.Embed(description="Please !equip a pokemon first.", colour=0xff0000)
		embed.set_author(name=(await get_name(ctx.message.author)), icon_url=ctx.message.author.avatar_url)
		await bot.send_message(ctx.message.channel, embed=embed)
		return False
	wild_pokemon = Pokemon(id=random.randint(1, 151), level=player_pokemon.get_level() + random.randint(0, 3))
	first_pokemon = wild_pokemon
	first_move = "Wilderness"

	Storage.hpBar.update({ctx.message.author.id: player_pokemon.get_stat("hp", player_pokemon.get_level())})
	Storage.hpBar.update({"W" + ctx.message.author.id: wild_pokemon.get_stat("hp", wild_pokemon.get_level())})
	if wild_pokemon.get_stat("speed", wild_pokemon.get_level()) < player_pokemon.get_stat("speed", player_pokemon.get_level()):
		first_pokemon = player_pokemon
		first_move = ctx.message.author

	embedGUI = FightEmbedGUI(challenger=ctx.message.author, firstMove=first_move, fpokemon=first_pokemon, opponent="Wilderness", wild=True, cpokemon=player_pokemon, opokemon=wild_pokemon)
	Storage.embed.update({ctx.message.author.id: embedGUI})
	Storage.inCombat.append(ctx.message.author)
	Storage.opponentID.update({ctx.message.author: 0})
	Storage.opponentID.update({"W" + ctx.message.author.id: 1})
	Storage.vsPokemon.update({ctx.message.author.id: wild_pokemon})
	if not first_move == ctx.message.author:
		await do_wild_move(wild_pokemon, player_pokemon, embedGUI, ctx.message.author)
	else:
		Storage.timers.update({ctx.message.author: time.time()})

	msg = await bot.send_message(ctx.message.channel, embed=embedGUI.get_embed())
	Storage.messages.update({ctx.message.author.id: msg})


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

	player = Player(msg.author.id)

	if msg.author in Storage.inCombat:
		if not (msg.author in Storage.timers):
			return False

		message = Storage.messages[msg.author.id]

		if msg.channel != message.channel:
			return False

		if msg.content == "1":
			if msg.author in Storage.vsWho:
				embed = discord.Embed(description="You cannot use pokeballs in a trainer battle!", colour=0xff0000)
				embed.set_author(name=(await get_name(msg.author)), icon_url=msg.author.avatar_url)
				await bot.send_message(msg.channel, embed=embed)
				return False
			if not player.does_have_item("Pokeball"):
				embed = discord.Embed(description="You do not have a pokeball!", colour=0xff0000)
				embed.set_author(name=(await get_name(msg.author)), icon_url=msg.author.avatar_url)
				await bot.send_message(msg.channel, embed=embed)
				return False

			amount = player.get_item_amount("Pokeball")
			if amount <= 0:
				embed = discord.Embed(description="You do not have a pokeball!", colour=0xff0000)
				embed.set_author(name=(await get_name(msg.author)), icon_url=msg.author.avatar_url)
				await bot.send_message(msg.channel, embed=embed)
				return False

			player.add_item("Pokeball", "", -1)

			chance = Pokeball(chance=30).is_successful()
			wild_pokemon = Storage.vsPokemon.get(msg.author.id)
			embedGUI = Storage.embed[msg.author.id]
			player_pokemon = player.get_equip_pokemon()

			if (chance):
				embedGUI.add_log(player_pokemon.get_name().title() + "'s pokeball succeeded.")
				player.add_pokemon(wild_pokemon.get_id(), wild_pokemon.get_level(), ','.join(wild_pokemon.get_wild_moves()), 0)
				await bot.edit_message(message=message, embed=embedGUI.get_embed())
				await kill_combat(msg.author)
				return True
			else:
				embedGUI.add_log(player_pokemon.get_name().title() + "'s pokeball failed.")
				await bot.edit_message(message=message, embed=embedGUI.get_embed())
				del Storage.timers[msg.author]

				await do_wild_move(wild_pokemon, player_pokemon, embedGUI, msg.author, True)

		elif msg.content == "2":
			chance = random.randint(0, 100)
			embedGUI = Storage.embed[msg.author.id]
			player_pokemon = player.get_equip_pokemon()
			wild_pokemon = Storage.vsPokemon.get(msg.author.id)

			if chance <= 25:
				await kill_combat(msg.author)
				embedGUI.add_log(player_pokemon.get_name().title() + "'s escape was successful.")
				await bot.edit_message(message=message, embed=embedGUI.get_embed())
				return True
			else:
				embedGUI.add_log(player_pokemon.get_name().title() + "'s attempt to escape was unsuccessful.")
				await bot.edit_message(message=message, embed=embedGUI.get_embed())
				await do_wild_move(wild_pokemon, player_pokemon, embedGUI, msg.author, True)
				return True
		else:
			embedGUI = Storage.embed[msg.author.id]
			player_pokemon = player.get_equip_pokemon()
			number_of_moves = len(player_pokemon.get_moves())
			selected_move = ord(msg.content.lower()[:1]) - 96
			hpBarKey = False
			wild_pokemon = False

			if msg.author.id in Storage.vsPokemon:
				hpBarKey = "W" + msg.author.id
				wild_pokemon = Storage.vsPokemon.get(msg.author.id)
			else:
				hpBarKey = Storage.vsWho.get(msg.author.id)
				wild_pokemon = Player(Storage.vsWho.get(msg.author.id)).get_equip_pokemon()

			if selected_move > 0 and selected_move < 5 and selected_move <= number_of_moves:
				DamageModifier_obj = DamageModifier(type=player_pokemon.get_type())
				move_obj = player_pokemon.get_move(player_pokemon.get_moves()[selected_move - 1])
				power = 50
				if move_obj.power:
					power = move_obj.power

				attack_stat = player_pokemon.get_stat("attack", player_pokemon.get_level())
				defense_stat = wild_pokemon.get_stat("defense", wild_pokemon.get_level())

				if move_obj.damage_class.name == "special":
					attack_stat = player_pokemon.get_stat("special-attack", player_pokemon.get_level())
					defense_stat = wild_pokemon.get_stat("special-defense", wild_pokemon.get_level())

				damage_done = round(DamageModifier_obj.get_move_damage(power, attack_stat, player_pokemon.get_level(), move_obj.type.name, wild_pokemon.get_type(), defense_stat))
				embedGUI.add_log(player_pokemon.get_name().title() + " used **" + player_pokemon.get_moves()[selected_move - 1] + "** and did **" + str(damage_done) + "** damage!")

				currentHP = Storage.hpBar.get(hpBarKey)

				Storage.hpBar.update({hpBarKey: (currentHP - damage_done)})

				hpBar = round(((currentHP - damage_done) / wild_pokemon.get_stat("hp", wild_pokemon.get_level())) * 8)
				hpString = "▰" * hpBar
				hpString = hpString + ("▱" * (8 - hpBar))
				embedGUI.update_opponent(Storage.opponentID.get(hpBarKey), str(currentHP - damage_done) + "/" + str(
					wild_pokemon.get_stat("hp", wild_pokemon.get_level())), hpString)

				if (currentHP - damage_done) <= 0:
					embedGUI.add_log(wild_pokemon.get_name().title() + " has fainted. " + player_pokemon.get_name().title() + " wins.")
					if message:
						await bot.edit_message(message=Storage.messages[msg.author.id], embed=embedGUI.get_embed())
					await award_victory(msg.author, msg.channel)
					await kill_combat(msg.author)
					return True

				if msg.author in Storage.timers:
					del Storage.timers[msg.author]

				if message:
					await bot.edit_message(message=Storage.messages.get(msg.author.id), embed=embedGUI.get_embed())

				if hpBarKey.startswith("W"):
					await do_wild_move(wild_pokemon, player_pokemon, embedGUI, msg.author, True)
				else:
					Storage.timers.update({hpBarKey: time.time()})
					embedGUI.set_move(Storage.vsWhoObj.get(hpBarKey), Player(Storage.vsWhoObj.get(hpBarKey)).get_equip_pokemon())

				return True

			embed = discord.Embed(description="Invalid input entered!", colour=0xff0000)
			embed.set_author(name=(await get_name(msg.author)), icon_url=msg.author.avatar_url)
			await bot.send_message(msg.channel, embed=embed)
		return True

	await bot.process_commands(msg)

bot.run(PokeConfig.token)
