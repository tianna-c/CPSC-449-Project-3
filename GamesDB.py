#!/usr/bin/env python3

import contextlib
import datetime
import random
import sqlite3
import uuid

import faker

DATABASE = 'gameshardone.db'
SCHEMA = 'games.sql'

NUM_STATS = 10
NUM_USERS = 10
YEAR = 2022
user_count = 1

random.seed(YEAR)
fake = faker.Faker()
fake.seed(YEAR)
with contextlib.closing(sqlite3.connect(DATABASE)) as db:
    with open(SCHEMA) as f:
        db.executescript(f.read())
    for _ in range(NUM_USERS):
        while True:
            try:
            	profile = fake.simple_profile()
            	profile["uuid"] = str(uuid.uuid4())
            	profile["user_id"] = user_count
            	db.execute('INSERT INTO users(user_id, username, uuid) VALUES(:user_id, :username, :uuid)', profile)
            	user_count += 1

            except sqlite3.IntegrityError:
                continue
            break
    db.commit()
    jan_1 = datetime.date(YEAR, 1, 1)
    today = datetime.date.today()
    num_days = (today - jan_1).days
    i = 0
    while i < NUM_STATS:
        while True:
           try:
                user_id = random.randint(1, NUM_USERS)
                game_id = random.randint(1, num_days)
                finished = jan_1 + datetime.timedelta(random.randint(0, num_days))
                # N.B. real game scores aren't uniformly distributed...
                guesses = random.randint(1, 6)
                # ... and people mostly play to win
                won = random.choice([False, True, True, True])
                db.execute(
                    """
                    INSERT INTO games(user_id, game_id, finished, guesses, won)
                    VALUES(?, ?, ?, ?, ?)
                    """,
                    [user_id, game_id, finished, guesses, won]
                )
                db.execute(
                    """
                    SELECT uuid FROM users WHERE user_id = 1
                    UPDATE games(uuid)
                    """,
                    [user_id, game_id, finished, guesses, won]) 
           except sqlite3.IntegrityError:
                continue
           i += 1
           break
    db.commit()
