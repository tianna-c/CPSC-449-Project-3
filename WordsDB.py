import fileinput
import sqlite3

#Setup DB for word strings
con = sqlite3.connect("words_ms.db")
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS t (Words TEXT, UNIQUE(Words))")

#Filter out the strings for Words Microservice from defined source as per Project Reqs
#and import into sqlite3 DB
try:
    with fileinput.input(files=('/usr/share/dict/words')) as f:
        for line in f:
            if line.islower():
                if line.isascii():
                    if not('\'' in line):
                        #Need to remove \n from end of string
                        cleaned_line = line.replace("\n", "")

                        if len(cleaned_line) == 5:
                            cur.execute("INSERT INTO t VALUES(?)", (cleaned_line,))
                            con.commit()
except:
    print("DB is already populated with pre-defined words!")

con.close()