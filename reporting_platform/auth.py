from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password):
    return generate_password_hash(password)

def verify_password(input_password, stored_hash):
    return check_password_hash(stored_hash, input_password)
