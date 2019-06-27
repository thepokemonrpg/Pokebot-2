import sqlite3


def get_connection():
	con = sqlite3.connect("database.db")
	cur = con.cursor()
	cur.execute("CREATE TABLE IF NOT EXISTS playerData(playerID TEXT PRIMARY KEY, gold INTEGER, rewardsEpoch INTEGER, startRewardsObtained INTEGER)")
	cur.execute("CREATE TABLE IF NOT EXISTS pokemon(pokemonID INTEGER PRIMARY KEY, pokemonIdentifier INTEGER, level INTEGER, owner TEXT, moves TEXT, bonus INTEGER)")
	cur.execute("CREATE TABLE IF NOT EXISTS items(item INTEGER PRIMARY KEY, itemName TEXT, itemDesc TEXT, itemAmt INTEGER)")
	con.commit()
	return con
