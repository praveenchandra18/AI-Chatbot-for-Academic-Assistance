from hashlib import sha256


def hash_password(password:str):
    return sha256(password.encode("utf-8")).hexdigest()

def verify_password(password,hashed_password):
    return hashed_password == hash_password(password)