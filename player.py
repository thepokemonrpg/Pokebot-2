import sqlite3
import database
import time
from pokeconfig import PokeConfig
from pokemon import Pokemon
import traceback
from pprint import pprint

class Player:
	def __init__(self, uid):
		self.uID = uid

		connection = database.get_connection()
		cursor = connection.cursor()

		if not self.is_profile_setup():
			try:
				cursor.execute('''INSERT INTO playerData(playerID, gold, rewardsEpoch, startRewardsObtained) VALUES(?,?,?,?)''', (self.uID, PokeConfig.startingGold, 0, 0))
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
				cursor.execute('''INSERT INTO playerData(playerID, gold, rewardsEpoch, startRewardsObtained) VALUES(?,?,?,?)''', (self.uID, PokeConfig.startingGold + gold, 0, 0))
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
			pokemon = Pokemon(id=r[1], level=r[2], owner=r[3], moves=r[4], real=True)
			poke_obj.append(pokemon)

		return poke_obj
