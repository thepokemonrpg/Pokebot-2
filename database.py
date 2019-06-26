import sqlite3


def get_connection():
	con = sqlite3.connect("database.db")
	cur = con.cursor()
	cur.execute("DROP TABLE playerData")
	cur.execute("CREATE TABLE IF NOT EXISTS playerData(playerID TEXT PRIMARY KEY, gold INTEGER, rewardsEpoch INT, startRewardsObtained INT)")
	cur.execute("CREATE TABLE IF NOT EXISTS playerData(pokemonID TEXT PRIMARY KEY, pokemonIdentifier INTEGER, level INT, owner TEXT)")
	con.commit()
	return con
