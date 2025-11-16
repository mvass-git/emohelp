import sqlite3
from neo4j import GraphDatabase
from flask import g, current_app

app = current_app

DB_PATH ="database.db"

neo4j_uri, neo4j_user, neo4j_password = "bolt://localhost:7687", "neo4j", "testpassword"
driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
    return g.db, g.db.cursor()

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
    
    if hasattr(app, 'neo4j_driver'):
        driver.close()