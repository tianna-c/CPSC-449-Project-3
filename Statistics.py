import sqlite3
import contextlib
import uuid

from typing import List
from pydantic import BaseModel, Field, BaseSettings
from fastapi import Depends, FastAPI

class Settings(BaseSettings):
	database1: str
	database2: str
	database3: str
	databaseUser: str

	class Config:
		env_file = ".env"

class user(BaseModel):
	user: str
	gameID: int
	
class results(BaseModel):
	userID: int
	gameID: int
	result: str
	timestamp: str
	guesses: int

class guessesMod(BaseModel):
	guess1: int = Field(0, alias="1")
	guess2: int = Field(0, alias="2")
	guess3: int = Field(0, alias="3")
	guess4: int = Field(0, alias="4")
	guess5: int = Field(0, alias="5")
	guess6: int = Field(0, alias="6")
	fail: int = Field(0)
	
class userStats(BaseModel):
	currentStreak: int = Field(0)
	maxStreak: int = Field(0)
	guesses: guessesMod = Field(None)
	winPercentage: int = Field(0)
	gamesPlayed: int = Field(0)
	gamesWon: int = Field(0)
	averageGuesses: int = Field(0)
	
app = FastAPI()
settings = Settings()

def get_db():
    with contextlib.closing(sqlite3.connect(settings.database1)) as db:
        db.row_factory = sqlite3.Row
        yield db

def get_db2():
    with contextlib.closing(sqlite3.connect(settings.database2)) as db:
        db.row_factory = sqlite3.Row
        yield db

def get_db3():
    with contextlib.closing(sqlite3.connect(settings.database3)) as db:
        db.row_factory = sqlite3.Row
        yield db

def get_db_user():
    with contextlib.closing(sqlite3.connect(settings.databaseUser)) as db:
        db.row_factory = sqlite3.Row
        yield db

def calcShardNum(user, userDB):
	con = userDB

	try:
		fetch = con.execute("SELECT * FROM users WHERE user_id = ?", (user,))
	except:
		print("ERROR FETCHING")
	
	for row in fetch:
		num = int(uuid.UUID(row[2])) % 3

	con.close()
	return num

def calculateStats(database_name, userInput):
	sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
	sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)
	
	con = database_name
	user = userInput

	userGuesses = guessesMod()
	userStatistics = userStats()

	try:
		fetch = con.execute("SELECT * FROM games WHERE user_id = ? ORDER BY finished ASC", (user,)).fetchall()
	except:
		print("ERROR FETCHING")
	
	cStreak = 0
	mStreak = 0
	guessList = [0 for i in range(7)]
	wPercent = 0
	totalGames = 0

	for row in fetch:
		guessList[int(row[3])-1] += 1

		if(row[4] == 0):
			guessList[6] += 1

		#Calculate streaks
		#If won == 1 then we add one to the streak. Otherwise we compare
		#to max streak and replace values as necessary	
		if(int(row[4]) == 1):
			cStreak += 1

			if(cStreak > mStreak):
				mStreak = cStreak
		else:
			cStreak = 0

	numPlayed = 0
	for i in range(len(guessList)):
		if(i < 6):
			numPlayed+= guessList[i]
	
	wPercent = round(100 * (numPlayed - guessList[6]) / numPlayed)
	totalGames = numPlayed
	
	for i in range(len(guessList)):
		if(i == 0):
			userGuesses.guess1 = int(guessList[i])
		if(i == 1):
			userGuesses.guess2 = guessList[i]
		if(i == 2):
			userGuesses.guess3 = guessList[i]
		if(i == 3):
			userGuesses.guess4 = guessList[i]
		if(i == 4):
			userGuesses.guess5 = guessList[i]
		if(i == 5):
			userGuesses.guess6 = guessList[i]
		if(i == 6):
			userGuesses.fail = guessList[i]

	userStatistics.currentStreak = cStreak
	userStatistics.maxStreak = mStreak
	userStatistics.guesses = userGuesses
	userStatistics.winPercentage = wPercent
	userStatistics.gamesPlayed = totalGames
	userStatistics.gamesWon = numPlayed - guessList[6]
	
	averageCounter = 0
	for i in range(len(guessList)-1):
		averageCounter += (i+1) * guessList[i]

	average = round(averageCounter / totalGames, 0)

	if(average < (averageCounter / totalGames)):
		average += 1

	userStatistics.averageGuesses = int(average)

	return userStatistics
	

@app.post('/result/{current_user}')
def postResults(currUser: user, dbUser: sqlite3.Connection = Depends(get_db_user), db1: sqlite3.Connection = Depends(get_db), db2: sqlite3.Connection = Depends(get_db2), db3: sqlite3.Connection = Depends(get_db3)):
	sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
	sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)
	
	num = calcShardNum(currUser.user, dbUser)
	shardSelection = None

	if(num == 0):
		shardSelection = db1
	elif(num == 1):
		shardSelection = db2
	elif(num == 2):
		shardSelection = db3
		
	con = shardSelection
	user = userInput
	result = results()
	
	if(win == True):
		result.won() == 1
	else:
		result.won() == 0

	try:
		submitResult = con.execute(
			"""
			INSERT INTO games(user_id, game_id, finished, guesses, won)
			VALUES(?, ?, ?, ?, ?)
                    """, user, result
                    )
		con.commit()
	except sqlite3.IntegrityError:
		print("ERROR FETCHING")

	#return(shardSelection, currUser.user)

@app.get('/getStats/')
def retrieveStats(currUser: user, dbUser: sqlite3.Connection = Depends(get_db_user), db1: sqlite3.Connection = Depends(get_db), db2: sqlite3.Connection = Depends(get_db2), db3: sqlite3.Connection = Depends(get_db3)):
	num = calcShardNum(currUser.user, dbUser)
	shardSelection = None

	if(num == 0):
		shardSelection = db1
	elif(num == 1):
		shardSelection = db2
	elif(num == 2):
		shardSelection = db3

	return calculateStats(shardSelection, currUser.user)

@app.post('/toptens/')
def toptens():
	#Retrieving the top 10 users by number of wins. Retrieving the top 10 users by longest streak
	#user can select how they want to retrieve the top 10 users?
	
	#idea: check all 3 shards for their top tens, and sort those top tens to find the true top tens and output them
	
	return 0
