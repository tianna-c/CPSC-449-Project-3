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

fake = faker.Faker()
with contextlib.closing(sqlite3.connect(DATABASE)) as db:
    with open(SCHEMA) as f:
        db.executescript(f.read())
    for _ in range(NUM_USERS):
        while True:
            try:
            	profile = fake.simple_profile()
            	profile["uuid"] = str(uuid.uuid4())
            	db.execute('INSERT INTO users(username, uuid) VALUES(:username, :uuid)', profile)

            except sqlite3.IntegrityError:
                continue
            break
    db.commit()
