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
		cur.execute("ALTER TABLE users ADD COLUMN uuid GUID") # it gives this error if you try running the file more than once, "sqlite3.OperationalError: duplicate column name: uuid", idk if we need to fix that later # maybe we can drop user_id and make uuid the primary key???
	except sqlite3.IntegrityError:
		pass
	user_id_count = {}
	i = 1
	for i in range(NUM_USERS):
		while True:
			try:
				user_uuid = uuid.uuid4()
				user_id_count[i] = user_uuid
				cur.execute("UPDATE users SET uuid = ? WHERE user_id = ?", [user_uuid, i])  #uuid is NULL
				
			except sqlite3.IntegrityError:
				continue
			i += 1
			break
	try:
		cur.execute("ALTER TABLE games ADD COLUMN uuid GUID")
	except sqlite3.IntegrityError:
		pass
	x = 0
	for x in range(NUM_STATS):
	     while True:
	     		try:
	     			cur.execute("UPDATE games SET uuid = ? WHERE user_id = ?", [user_id_count[x], x]) #gives me an error: KeyError: 100000
	     			
	     		except sqlite3.IntegrityError:
	     			continue
	     		x += 1
	     		break
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
