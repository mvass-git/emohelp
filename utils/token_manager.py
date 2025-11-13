import jwt
import datetime

SECRET_KEY = "1000-7Ghoul"

def create_access_jwt(user_id: int, role: str) -> dict:
    try:
        payload = {
            "id": user_id,
            "role": role,
            "exp": datetime.datetime.now() + datetime.timedelta(hours=2)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return {"status": "success", "token": token}
    except Exception as e:
        return {"status": "error", "msg": str(e)}


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return {"status": "success", "payload": payload}
    except jwt.ExpiredSignatureError:
        return {"error": "ExpiredToken", "msg": "Token has expired"}
    except jwt.InvalidTokenError:
        return {"error": "InvalidToken", "msg": "Invalid token"}