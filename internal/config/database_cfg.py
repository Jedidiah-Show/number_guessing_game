# User log in configuration and validation

import json
import os
import bcrypt

database = "database.json"

def load_database():
    if not os.path.exists(database):
        return {}
    try:
        with open(database, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return {}

def save_database(data):
    tmp = database + ".tmp"
    with open(tmp, "w") as file:
        json.dump(data, file, indent=4)
    os.replace(tmp, database)

def register_user(user_name, fullname, password):
    db = load_database()

    if user_name in db:
        err = "Error: Username already taken!"
        return False, err

    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)

    hashed_string = hashed_bytes.decode('utf-8')

    db[user_name] = {
        "fullname": fullname,
        "password_hash": hashed_string,
    }

    save_database(db)
    return True, ""

def verify_username(user_name): 
    db = load_database()

    if user_name not in db:
        err = "Error: Unknown user or wrong username"
        return False, err
    return True, ""

def verify_password(user_name, password):
    db = load_database()

    stored_hash_bytes = db[user_name]["password_hash"].encode('utf-8')
    
    input_password_bytes = password.encode('utf-8')

    if bcrypt.checkpw(input_password_bytes, stored_hash_bytes):
        return True, ""
    else:
        err = "Error: Invalid password."
        return False, err

def forgot_password(user_name, fullname):
        db = load_database()
        
        data  = db.get(user_name)
        if not fullname == data["fullname"]:
            err = "Account not found in database"
            return False, err
        return True, ""
        