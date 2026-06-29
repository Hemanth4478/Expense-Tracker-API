from passlib.hash import bcrypt

def hash_password(password: str):
    return bcrypt.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.verify(
        plain_password,
        hashed_password
    )
