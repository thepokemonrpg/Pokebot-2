import sqlite3
import database
import time
from pokeconfig import PokeConfig
from pokemon import Pokemon
import traceback
from pprint import pprint
from Item import Item

class Player:
	def __init__(self, uid):
		self.uID = uid

		connection = database.get_connection()
		cursor = connection.cursor()

		if not self.is_profile_setup():
			try:
				cursor.execute('''INSERT INTO playerData(playerID, gold, rewardsEpoch, startRewardsObtained, equipPokemon) VALUES(?,?,?,?,?)''', (self.uID, PokeConfig.startingGold, 0, 0, 0))
				connection.commit()
			except:
				print("Error setting up player, ID: " + uid)
				traceback.print_exc()

			connection.close()

	def is_profile_setup(self):
		connection = database.get_connection()
		cursor = connection.cursor()
		cursor.execute('''SELECT gold FROM playerData WHERE playerID = ?''', (self.uID,))
		rows = cursor.fetchone()
		connection.close()

		try:
			if not isinstance(rows[0], int):
				return False
		except:
			return False

		return True

	def set_coins(self, gold):
		connection = database.get_connection()
		cursor = connection.cursor()

		try:
			with connection:
				cursor.execute('''INSERT INTO playerData(playerID, gold, rewardsEpoch, startRewardsObtained, equipPokemon) VALUES(?,?,?,?,?)''', (self.uID, PokeConfig.startingGold + gold, 0, 0, 0))
				connection.commit()
		except sqlite3.IntegrityError:
			cursor.execute('''UPDATE playerData SET gold = ? WHERE playerID = ? ''', (gold, self.uID))
			connection.commit()

		connection.close()

	def get_coins(self):
		connection = database.get_connection()
		cursor = connection.cursor()
		cursor.execute('''SELECT gold FROM playerData WHERE playerID = ?''', (self.uID,))
		rows = cursor.fetchone()
		connection.close()

		try:
			if not isinstance(rows[0], int):
				return 0
		except:
			return 0

		return rows[0]

	def get_reward(self):
		return PokeConfig.plrReward

	def get_reward_timer(self):
		return PokeConfig.rewardsTimer

	def set_reward_timestamp(self):
		connection = database.get_connection()
		cursor = connection.cursor()

		cursor.execute('''UPDATE playerData SET rewardsEpoch = ? WHERE playerID = ? ''', (int(time.time()), self.uID))
		connection.commit()

		connection.close()

	def get_rewards_epoch(self):
		connection = database.get_connection()
		cursor = connection.cursor()
		cursor.execute('''SELECT rewardsEpoch FROM playerData WHERE playerID = ?''', (self.uID,))
		rows = cursor.fetchone()
		connection.close()

		if not isinstance(rows[0], int):
			return 0

		return rows[0]

	def has_player_started(self):
		connection = database.get_connection()
		cursor = connection.cursor()
		cursor.execute('''SELECT startRewardsObtained FROM playerData WHERE playerID = ?''', (self.uID,))
		rows = cursor.fetchone()
		connection.close()

		try:
			if not isinstance(rows[0], int):
				return False
		except:
			return False

		if rows[0] == 0:
			return False

		return True

	def set_player_started(self):
		connection = database.get_connection()
		cursor = connection.cursor()

		cursor.execute('''UPDATE playerData SET startRewardsObtained = ? WHERE playerID = ? ''', (1, self.uID))
		connection.commit()

		connection.close()

	def add_pokemon(self, pokemon_id, level, moves, bonus):
		connection = database.get_connection()
		cursor = connection.cursor()
		cursor.execute('''INSERT INTO pokemon(pokemonIdentifier, level, owner, moves, bonus) VALUES(?,?,?,?,?)''', (pokemon_id, level, self.uID, moves, bonus))
		connection.commit()

	def get_pokemon_list(self):
		connection = database.get_connection()
		cursor = connection.cursor()
		cursor.execute('''SELECT * FROM pokemon WHERE owner = ?''', (self.uID,))
		rows = cursor.fetchall()
		connection.close()

		poke_obj = []

		for r in rows:
			pokemon = Pokemon(unique=r[0], id=r[1], level=r[2], xp=r[3], owner=r[4], moves=r[5], real=True)
			poke_obj.append(pokemon)

		return poke_obj

	def get_pokemon_id_list(self):
		connection = database.get_connection()
		cursor = connection.cursor()
		cursor.execute('''SELECT * FROM pokemon WHERE owner = ?''', (self.uID,))
		rows = cursor.fetchall()
		connection.close()

		id_s = []

		for r in rows:
			id_s.append(r[0])

		return id_s

	def get_equip_pokemon(self):
		equip_id = self.get_equip()
		poke_obj = self.get_pokemon_list()

		for i in poke_obj:
			if i.get_unique_id() == equip_id:
				return i

		return False

	def set_moves(self, unique, moves):
		connection = database.get_connection()
		cursor = connection.cursor()

		cursor.execute('''UPDATE pokemon SET moves = ? WHERE pokemonID = ? ''', (moves, unique))
		connection.commit()

		connection.close()

	def set_exp_pokemon(self, unique, xp):
		connection = database.get_connection()
		cursor = connection.cursor()

		cursor.execute('''UPDATE pokemon SET exp = ? WHERE pokemonID = ? ''', (xp, unique))
		connection.commit()

		connection.close()

	def set_level_pokemon(self, unique, level):
		connection = database.get_connection()
		cursor = connection.cursor()

		cursor.execute('''UPDATE pokemon SET level = ? WHERE pokemonID = ? ''', (level, unique))
		connection.commit()

		connection.close()

	def get_equip(self):
		connection = database.get_connection()
		cursor = connection.cursor()
		cursor.execute('''SELECT equipPokemon FROM playerData WHERE playerID = ?''', (self.uID,))
		rows = cursor.fetchone()
		connection.close()

		try:
			if not isinstance(rows[0], int):
				return 0
		except:
			return 0

		return rows[0]

	def set_equip(self, equip):
		ids = self.get_pokemon_id_list()

		if not (equip in ids):
			return False

		connection = database.get_connection()
		cursor = connection.cursor()

		cursor.execute('''UPDATE playerData SET equipPokemon = ? WHERE playerID = ? ''', (equip, self.uID))
		connection.commit()

		connection.close()
		return True

	def does_have_item(self, name):
		connection = database.get_connection()
		cursor = connection.cursor()
		cursor.execute('''SELECT * FROM items WHERE owner = ? AND itemName = ?''', (self.uID, name))
		rows = cursor.fetchone()
		connection.close()

		if rows is None:
			return False

		return True

	def get_item_amount(self, name):
		has_item = self.does_have_item(name)

		if not has_item:
			return 0

		connection = database.get_connection()
		cursor = connection.cursor()
		cursor.execute('''SELECT * FROM items WHERE owner = ? AND itemName = ?''', (self.uID, name))
		rows = cursor.fetchone()
		connection.close()

		return rows[4]

	def add_item(self, name, desc, uses=1):
		has_item = self.does_have_item(name)

		connection = database.get_connection()
		cursor = connection.cursor()

		if has_item:
			cursor.execute('''UPDATE items SET itemAmt = ? WHERE owner = ? AND itemName = ?''', (self.get_item_amount(name) + uses, self.uID, name))
		else:
			cursor.execute('''INSERT INTO items(owner, itemName, itemDesc, itemAmt) VALUES(?,?,?,?)''', (self.uID, name, desc, uses))
		connection.commit()

	def get_item_list(self):
		connection = database.get_connection()
		cursor = connection.cursor()
		cursor.execute('''SELECT * FROM items WHERE owner = ?''', (self.uID,))
		rows = cursor.fetchall()
		connection.close()

		item_obj = []

		for r in rows:
			item = Item(name=r[2], description=r[3], amount=r[4])
			item_obj.append(item)

		return item_obj
