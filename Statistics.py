from typing import List
import sqlite3
import datetime
import uuid

#Required to create a request and response body for data
from pydantic import BaseModel, Field
#Define FastAPI HTTP Methods
from fastapi import Depends, FastAPI, status

class user(BaseModel):
	user: str
	gameID: int
	
class results(BaseModel):
	gameID: int
	result: str
	timestamp: str
	guesses: int

class guesses(BaseModel):
	guess1: int = Field(..., alias="1:")
	guess2: int = Field(..., alias="2:")
	guess3: int = Field(..., alias="3:")
	guess4: int = Field(..., alias="4:")
	guess5: int = Field(..., alias="5:")
	guess6: int = Field(..., alias="6:")
	fail: int
	
class statistics(BaseModel):
	gameID: int
	currentStreak: int
	maxStreak: int
	#guess: Field(None, alias='counter') #idk how to make store this one #guess: List[int](alias='counter') = [] //nested object w/ alias for integer keys
	guesses: guesses
	winPercentage: int
	gamesPlayed: int
	gamesWon: int
	averageGuesses: int
	
app = FastAPI()

# Dependencies
async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}

#Checking Pydantic Model is accurate for Guesses and Aliases
@app.get('/checkAnswer/guessModelCheck/')
def guessChecker():
	print(statistics.schema_json(indent=2))

@app.post('/checkAnswer/result/')
def results(input: gameID):
	#Posting a win or loss for a particular game, along with a timestamp and number of guesses.
	#user enters a gameID to retrieve the results of that game?
	
	#Retrieve the current game statistics based on the passed in Game ID
    con = sqlite3.connect("statistics.db")
    cur = con.cursor()
    server = ""
    	
    try:
        fetch = cur.execute("SELECT * FROM a WHERE ID = ?", (input.gameID,)).fetchall()
        con.commit()

        server = fetch[0][0]

        print("The game stats are: " + server)
    except:
        print("Game # " + str(input.gameID) + " does not exist in this database!")

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
