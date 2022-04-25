PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS users;

CREATE TABLE users(
    user_id INTEGER,
    username VARCHAR UNIQUE,
    uuid VARCHAR PRIMARY KEY
);

PRAGMA analysis_limit=1000;
PRAGMA optimize;
