import db
import json
import utils.hash

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
    
    hashed = utils.hash.create_hash(password)

    cur.execute(
        """
        INSERT INTO Users (login, password) VALUES (?, ?)
        """,
        (login, hashed)
    )

    cur.execute(
        """
        INSERT INTO User_roles (user_id, role_id) VALUES (
            (SELECT id FROM User_login_data WHERE login = ?),
            (SELECT id FROM roles WHERE role = ?)
        )
        """, (login, "user")
    )

    db.commit()
    msg = {"status":"success", "msg":"user registered successfuly"}
    return json.dumps(msg)

def log_in(login, password):
    conn, cur = db.get_db()

    cur.execute(
        """
        SELECT login, password 
        FROM Users
        WHERE login = ?
        """,
        (login)
    )
    user = cur.fetchone()
    if user and utils.hash.verify(password, user[1]):
        return {"status":"success", "data":user}
    else:
        return {"status":"error", "msg":"login or password is incorrect"}