import sqlite3
import uuid

NUM_STATS = 1_000_000
NUM_USERS = 100_000

# create uuid columns in users and games tables
def create_uuid():
	sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
	sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)
	con = sqlite3.connect('stats.db', detect_types=sqlite3.PARSE_DECLTYPES)
	cur = con.cursor()
	# creates uuid column in users table
	try:
		cur.execute("ALTER TABLE users ADD COLUMN uuid GUID") # it gives this error if you try running the file more than once, "sqlite3.OperationalError: duplicate column name: uuid"
	except sqlite3.IntegrityError:
		pass
	# I think we should make a dictionary for the key-value pairs: user_id and uuid
	user_id_count = {}
	# a for loop to generate uuid for each user and insert it into the uuid column
	for i in range(NUM_USERS):
		user_uuid = uuid.uuid4() # generate uuid
		user_id_count[i] = user_uuid #insert uuid into dict according the the corresponding user_id from the loop
		#print("Test: " + str([user_id_count[i], i]))
		cur.execute("UPDATE users SET uuid = ? WHERE user_id = ?", [user_uuid, i])
	#print(len(user_id_count))
	#print(user_id_count.items())
	#print("Final: " + str([user_id_count[i], i]))
	con.commit()
	# creates uuid column in games tables
	try:
		cur.execute("ALTER TABLE games ADD COLUMN uuid GUID")
	except sqlite3.IntegrityError:
		pass
	x = 0
	# should do the same thing as the above loop
	while x < NUM_STATS:
		#print("Test: " + str([user_id_count[x], x]))
		#gives KeyError
		cur.execute("UPDATE games SET uuid = ? WHERE user_id = ?", [user_id_count[x], x])
		x += 1
	con.commit()
create_uuid()

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
		cur_two = con_shard.cursor()
		cur_one.execute("SELECT * from games WHERE uuid % 3 = ?", [i])
