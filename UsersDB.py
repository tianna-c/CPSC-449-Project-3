#!/usr/bin/env python3

import contextlib
import datetime
import random
import sqlite3
import uuid

import faker

DATABASE = 'users.db'
SCHEMA = 'users.sql'

NUM_USERS = 100_000
user_count = 1

fake = faker.Faker()
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
