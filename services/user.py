from functools import wraps
from flask import session, redirect, url_for, abort, g, render_template
import utils.token_manager
import db_manager.user_manager



def authorize_user(login: str, password: str):
    """
    Авторизує користувача за логіном і паролем:
    - перевіряє користувача
    - визначає роль
    - створює JWT-токен
    - зберігає токен у Flask-сесії
    """
    login_data = db_manager.user_manager.log_in(login, password)
    if login_data.get("status") != "success":
        return {"status": "error", "msg": "Invalid credentials"}

    user = login_data.get("data")
    role_data = db_manager.user_manager.get_user_role(user[0])

    if role_data.get("status") != "success":
        return {"status": "error", "msg": "Cannot get user role"}

    token = utils.token_manager.create_access_jwt(user[0], role_data["data"][0]).get("token")
    session["token"] = token
    return {"status": "success", "token": token}

def login_required(role: list[str] | None = None):
    """
    Декоратор для перевірки авторизації і опціонально ролі користувача.
    Використання:
        @login_required() — просто перевірка логіну
        @login_required("admin") — перевірка логіну + ролі
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            token = session.get("token")
            if not token:
                return redirect(url_for("signin"))

            result = utils.token_manager.decode_access_token(token)

            if result.get("status") != "success":
                # токен недійсний або прострочений
                session.pop("token", None)
                return redirect(url_for("signin"))

            payload = result["payload"]

            # якщо роль передана — перевіряємо
            if role and payload.get("role") not in role:
                print(payload.get("role"), role)
                abort(403)  # Forbidden

            # зберігаємо payload у g, щоб можна було використовувати в маршруті
            g.user = payload

            return func(*args, **kwargs)
        return wrapper
    return decorator

def redirect_if_logged_in(redirect):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            token = utils.token_manager.decode_access_token(session.get("token"))
            if token.get("status") != "success":
                return func(*args, **kwargs)
            else:
                return render_template(redirect)
        return wrapper
    return decorator
