import db
import json

def add_user(login,country, birthday, password, repassword):
    conn, cur = db.get_db()
    cur.execute("""
                SELECT * from Users
                WHERE login = ?
                """, (login,))
    
    if cur.fetchall():
        msg = {"status":"error", "msg":"user with this login already exists"}
        return json.dumps(msg)
    if password != repassword:
        msg = {"status":"error", "msg":"passwords should be the same"}
        return json.dumps(msg)
    
    #need to hash password

    cur.execute(
        """
        INSERT INTO Users (login, password) VALUES (?, ?)
        """,
        (login, password)
    )
    db.commit()
    msg = {"status":"ok", "msg":"user registered successfuly"}
    return json.dumps(msg)

def log_in(login, password):
    conn, cur = db.get_db()

    cur.execute(
        """
        SELECT login, password 
        FROM Users
        WHERE login = ? AND password = ?
        """,
        (login, password)
    )
    user = cur.fetchone()
    if user:
        return user
    else:
        return {"status":"error", "msg":"login or password is incorrect"}