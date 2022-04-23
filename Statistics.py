from typing import List
import sqlite3
import datetime
import uuid

#Required to create a request and response body for data
from pydantic import BaseModel
#Define FastAPI HTTP Methods
from fastapi import FastAPI, status

class user(BaseModel):
	user: str
	gameID: int
	
class results(BaseModel):
	gameID: int
	result: str
	timestamp: str
	guesses: int
	
class statistics(BaseModel):
	gameID: int
	currentStreak: int
	maxStreak: int
	guess: Field(None, alias='counter') #idk how to make store this one #guess: List[int](alias='counter') = []
	winPercentage: int
	gamesPlayed: int
	gamesWon: int
	averageGuesses: int
	
app = FastAPI()

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
        print("User " + str(input.user) + " does not exist in this database!")
	
@app.post('/toptens/')
def toptens():
	#Retrieving the top 10 users by number of wins. Retrieving the top 10 users by longest streak
	#user can select how they want to retrieve the top 10 users?

