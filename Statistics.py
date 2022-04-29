from asyncio import streams
from sqlite3 import dbapi2
from typing import List
import sqlite3
import datetime
import contextlib
import uuid

#Required to create a request and response body for data
from pydantic import BaseModel, Field, BaseSettings
#Define FastAPI HTTP Methods
from fastapi import Depends, FastAPI, status
response_model = List[BaseModel]
class Settings(BaseSettings):
	database1: str
	database2: str
	database3: str

	class Config:
		env_file = ".env"

class user(BaseModel):
	user: str
	gameID: int
	
class results(BaseModel):
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

# def get_settings():
# 	settings = Settings()
# 	print(settings.database1)
# 	print(settings.database2)
# 	print(settings.database3)

settings = Settings()
# get_settings()

# # Dependencies
# async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
#     return {"q": q, "skip": skip, "limit": limit}

#calculate_statistics(settings.database1, 1)

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

@app.get('/getStats/')
def retrieveStats(currUser: user, db1: sqlite3.Connection = Depends(get_db), db2: sqlite3.Connection = Depends(get_db2), db3: sqlite3.Connection = Depends(get_db3)):
	sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
	sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)
	con = db2

	user = currUser.user

	userGuesses = guessesMod()
	userStatistics = userStats()

	try:
		fetch = con.execute("SELECT * FROM games WHERE user_id = ? ORDER BY finished ASC", (user,)).fetchall()
	except:
		print("ERROR FETCHING")
	
	cStreak = 0
	mStreak = 0
	guessList = []
	guessList = [0 for i in range(7)]
	wPercent = 0
	totalGames = 0

	for row in fetch:
		print("The current date is: " + str(row[2]))
		print("Won: " + str(row[4]))
		#print(row[3])
		guessList[int(row[3])-1] += 1
		# print("Current index is: " + str(row[3] - 1))
		# print("Current index value is: " + str(guessList[row[3] - 1]))
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
	
	# if(cStreak > mStreak):
	# 	mStreak = cStreak

	numPlayed = 0
	for i in range(len(guessList)):
		if(i < 6):
			numPlayed+= guessList[i]
	
	wPercent = round(100 * (numPlayed - guessList[6]) / numPlayed)
	totalGames = numPlayed
	
	print(cStreak)
	print(mStreak)
	
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

	

	print(wPercent)
	print(totalGames)	
	
	#print(counterTest)
	# gameID: int
	# currentStreak: int
	# maxStreak: int
	# guesses: guesses
	# winPercentage: int
	# gamesPlayed: int
	# gamesWon: int
	# averageGuesses: int

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
	print(average)
	print(averageCounter)
	if(average < (averageCounter / totalGames)):
		average += 1

	userStatistics.averageGuesses = int(average)

	return userStatistics

	#return("It was a success!")


#Checking Pydantic Model is accurate for Guesses and Aliases
@app.get('/checkAnswer/guessModelCheck/')
def guessChecker():
	print(statistics.schema_json(indent=2))

# @app.post('/checkAnswer/result/')
# def results(input: gameID):
# 	#Posting a win or loss for a particular game, along with a timestamp and number of guesses.
# 	#user enters a gameID to retrieve the results of that game?
	
# 	#Retrieve the current game statistics based on the passed in Game ID
#     con = sqlite3.connect("statistics.db")
#     cur = con.cursor()
#     server = ""
    	
#     try:
#         fetch = cur.execute("SELECT * FROM a WHERE ID = ?", (input.gameID,)).fetchall()
#         con.commit()

#         server = fetch[0][0]

#         print("The game stats are: " + server)
#     except:
#         print("Game # " + str(input.gameID) + " does not exist in this database!")

@app.post('/statistics/')
def statistics(input: user):
	#Retrieving the statistics for a user.
	
	#Retrieve the user stats based on entered username?
    con = sqlite3.connect("statistics.db")
    cur = con.cursor()
    server = ""
    	
    try:
        fetch = cur.execute("SELECT * FROM a WHERE ID = ?", (input.user,)).fetchall()
        con.commit()

        server = fetch[0][0]

        print("The game stats are: " + server)
    except:
        print("Game # " + str(input.user) + " does not exist in this database!")
	
@app.post('/toptens/')
def toptens():
	#Retrieving the top 10 users by number of wins. Retrieving the top 10 users by longest streak
	#user can select how they want to retrieve the top 10 users?
	
	#idea: check all 3 shards for their top tens, and sort those top tens to find the true top tens and output them
	
	return 0
