import sqlite3
import random
import uuid
import contextlib

#Required to create a request and response body for data
from pydantic import BaseModel, Field
#Define FastAPI HTTP Methods
from fastapi import Depends, FastAPI, status

NUM_STATS = 1_000_000
NUM_USERS = 100_000

class user(BaseModel):
	user: str
	gameID: int

# create uuid columns in users and games tables
def create_uuid():
	sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
	sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)
	con = sqlite3.connect('stats.db', detect_types=sqlite3.PARSE_DECLTYPES)
	cur = con.cursor()

	# creates uuid column in users table
	try:
		cur.execute("ALTER TABLE users ADD COLUMN uuid GUID") 
	except:
		#Skip error if the column already exists
		pass
	

	# a dictionary for the key-value pairs: user_id and uuid
	user_id_count = {}
	# for loop to generate uuid for each user and insert it into the uuid column
	for i in range(NUM_USERS+1):
		user_uuid = uuid.uuid4() # generate uuid
		user_id_count[i] = user_uuid #insert uuid into dict according the the corresponding user_id from the loop
		cur.execute("UPDATE users SET uuid = ? WHERE user_id = ?", [user_uuid, i])
	con.commit()

#Only uncomment for 1st time run where Stats.db hasn't been altered yet
#create_uuid()

def sharding():
	sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
	sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)
	con = sqlite3.connect('stats.db', detect_types=sqlite3.PARSE_DECLTYPES)
	cur = con.cursor()

	con_User= sqlite3.connect('userShard.db')
	cur_User= con_User.cursor()
	cur_User.execute("CREATE TABLE IF NOT EXISTS users(user_id INTEGER, username VARCHAR UNIQUE, uuid VARCHAR PRIMARY KEY)")

	userID = ""

	for i in range(3):
		con_temp = sqlite3.connect('shard_' + str(i+1) + '.db')
		cur_temp = con_temp.cursor()
		cur_temp.execute("CREATE TABLE IF NOT EXISTS games(user_id INTEGER NOT NULL, game_id INTEGER NOT NULL, finished DATE DEFAULT CURRENT_TIMESTAMP, guesses INTEGER, won BOOLEAN, PRIMARY KEY(user_id, game_id))")
	
	try:
		#Iterate through user DB, calculate shard using UUID, then
		#fetch all game records for that user from games DB and shard
		#into respective shard DB
		fetch = cur.execute("SELECT * FROM users").fetchall()
		#con.commit()
		for row in fetch:
			#Debugging
			print("User ID: " + str(row[0]))
			print("User UUID: " + str(row[2]))

			#Retrieve the shard number for this row's user based on UUID value
			uuid_shard_num = int(row[2]) % 3 + 1

			print("The user shard DB is: " + str(uuid_shard_num))

			#Connect to corresponding shard DB
			con_temp = sqlite3.connect('shard_' + str(uuid_shard_num) + '.db', detect_types=sqlite3.PARSE_DECLTYPES)
			cur_temp = con_temp.cursor()

			#Insert this row into User Shard
			cur_User.execute("INSERT INTO users VALUES(?, ?, ?)", (str(row[0]), str(row[1]), str(row[2])))
			con_User.commit()
			
			#Fetch the corresponding user's game data then insert into shard DB
			fetch_games = cur.execute("SELECT * FROM games WHERE user_id = ?", (row[0],)).fetchall()
			for gameData in fetch_games:
				print(gameData)

				#Insert a row of game stats associated with this user into the corresponding shard DB
				cur_temp.execute("INSERT INTO games VALUES(?, ?, ?, ?, ?)", (gameData[0], gameData[1], gameData[2], gameData[3], gameData[4]))
				con_temp.commit()
			con_temp.close()
		con.close()
		con_User.close()
	except:
		print("ERROR!")

sharding()