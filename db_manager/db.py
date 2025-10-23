import sqlite3
from flask import g

DB_PATH =""

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
    return g.db, g.db.cursor()

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()