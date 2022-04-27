import sqlite3
import uuid

# create uuid columns in users and games tables
def create_uuid():
	sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
	sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)
	con = sqlite3.connect('stats.db', detect_types=sqlite3.PARSE_DECLTYPES)
	cur = con.cursor()
	# creates uuid column in users table
	try:
		cur.execute("ALTER TABLE users ADD COLUMN uuid GUID") # it gives this error if you try running the file more than once, "sqlite3.OperationalError: duplicate column name: uuid", idk if we need to fix that later # maybe we can drop user_id and make uuid the primary key???
	except sqlite3.IntegrityError:
		pass
	# retreive data from users
	cur.execute("SELECT * from users")
	# create a counter from fetching all the data
	user_count = cur.fetchall()
	# create a dictionary to store key-value pair: user_id and uuid
	user_id_count = {}
	# for loop to generate and insert uuid for each user
	for c in user_count:
		user_uuid = uuid.uuid4()
		user_id_count[c[0]] = user_uuid
		cur.execute("UPDATE users SET uuid = ? WHERE user_id = ?", [user_uuid, c[0]])
	# creates uuid column in games table
	try:
		cur.execute("ALTER TABLE games ADD COLUMN uuid GUID")
	except sqlite3.IntegrityError:
		pass
	# retreive data from games
	cur.execute("SELECT * from games")
	# create a counter from fetching all the data
	user_count = cur.fetchall()
	# for loop to insert correct uuid into games based on the dictionary we created above
	for c in user_count:
		cur.execute("UPDATE games SET uuid = ? WHERE user_id = ?", [user_id_count[c[0]], c[0]])
	con.commit()
#create_uuid() #calls it and it works, but it displays uuid as a BLOB??? idk what that is but it works!!!

def sharding():
	#sharding time!!!!
	sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
	sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)
	con_one = sqlite3.connect('stats.db', detect_types=sqlite3.PARSE_DECLTYPES)
	cur_one = con_one.cursor()
	#creates three database files named shard_one, shard_two, and shard_three
	for i in range(3):
		con_shard = sqlite3.connect('shard_' + str(i+1) + '.db')
	#hash uuid/user_id and insert game data into corresponding shards
#sharding() #calls it and it creates the database shards
