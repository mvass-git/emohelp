import sqlite3

DB_PATH = "database.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

create_script = """
CREATE TABLE IF NOT EXISTS User_login_data (
id INTEGER PRIMARY KEY AUTOINCREMENT,
login TEXT NOT NULL,
password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Roles(
id INTEGER PRIMARY KEY AUTOINCREMENT,
role TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS User_roles (
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER NOT NULL,
role_id INTEGER NOT NULL,

FOREIGN KEY (user_id) REFERENCES User_login_data(id),
FOREIGN KEY (role_id) REFERENCES Roles(id)
);

create table if not exists User_saved_resources(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
resource_id TEXT,

FOREIGN KEY (user_id) REFERENCES User_login_data(id)
)
"""

add_roles = """
INSERT INTO Roles (role) VALUES ("user");
INSERT INTO Roles (role) VALUES ("admin");
"""



cur.executescript(create_script)
