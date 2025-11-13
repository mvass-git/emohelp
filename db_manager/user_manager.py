from db_manager import db
import json
import utils.hash

def add_user(login,country, birthday, password, repassword):
    conn, cur = db.get_db()
    cur.execute("""
                SELECT * from User_login_data
                WHERE login = ?
                """, (login,))
    
    if cur.fetchall():
        msg = {"status":"error", "msg":"user with this login already exists"}
        return msg
    if password != repassword:
        msg = {"status":"error", "msg":"passwords should be the same"}
        return msg
    
    hashed = utils.hash.create_hash(password)

    cur.execute(
        """
        INSERT INTO User_login_data (login, password) VALUES (?, ?)
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

    conn.commit()
    msg = {"status":"success", "msg":"user registered successfuly"}
    return msg

def log_in(login, password):
    conn, cur = db.get_db()

    cur.execute(
        """
        SELECT * 
        FROM User_login_data
        WHERE login = ?
        """,
        (login,)
    )
    user = cur.fetchone()
    if user and utils.hash.verify(password, user[2]):
        return {"status":"success", "data":user}
    else:
        return {"status":"error", "msg":"login or password is incorrect"}

def get_user_role(id):
    conn, cur = db.get_db()

    cur.execute(
        """
        SELECT role 
        FROM Roles
        INNER JOIN User_roles
        ON Roles.id = User_roles.user_id
        WHERE User_roles.user_id = ?
        """,
        (id,)
    )

    role = cur.fetchone()

    if role:
        return {"status":"success", "data":role}
    else:
        return {"status":"error", "msg":"role not found or user doesn`t exist"}