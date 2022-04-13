import json
import sqlite3

#Setup DB for answer strings
con = sqlite3.connect("answers.db")
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS a (ID INTEGER, Answers TEXT, UNIQUE(ID, Answers))")

f = open('answers.json')
data = json.load(f)

try:
    for count, value in enumerate(data):
        cur.execute("INSERT INTO a VALUES(?, ?)", (count, value))
        con.commit()
except:
    print("DB is already populated with pre-defined answers!")

con.close()