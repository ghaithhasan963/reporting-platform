import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(stored_hash, user_input):
    return stored_hash == hash_password(user_input)