import sqlite3


def get_connection():
	con = sqlite3.connect("database.db")
	cur = con.cursor()
	cur.execute("DROP TABLE playerData")
	cur.execute("CREATE TABLE IF NOT EXISTS playerData(playerID TEXT PRIMARY KEY, gold INTEGER, rewardsEpoch INT, startRewardsObtained INT)")
	cur.execute("CREATE TABLE IF NOT EXISTS pokemon(pokemonID INT PRIMARY KEY AUTOINCREMENT, pokemonIdentifier INT, level INT, owner TEXT, moves TEXT, bonus INT)")  
        cur.execute("CREATE TABLE IF NOT EXISTS items(item INT AUTOINCREMENT, itemName TEXT, itemDesc TEXT, itemS my INT) 
	con.commit()
	return con
