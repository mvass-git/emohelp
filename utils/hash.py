import bcrypt

def create_hash(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password, salt)

def verify(password_entered, password_hashed):
    return bcrypt.checkpw(password_entered, password_hashed)
