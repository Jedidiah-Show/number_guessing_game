# Persistent game session and info storage

import json
import os

filename = "game_data.json"

def init_storage():
    if not os.path.exists(filename):
        with open(filename, "w") as file:
            json.dump({}, file, indent=4)
 
def ensure_user_profile(data, username):
    if username not in data:
        data[username] = {
            "current_session": None,
            "high_score": 0,
            "max_level": 1
        }
    return data

def save_ongoing_game(username, secret_number, level, attempts, score):
    init_storage()
    with open(filename, "r") as file:
        data = json.load(file)
    
    data = ensure_user_profile(data, username)
    
    data[username]["current_session"] = {
        "secret_number": secret_number,
        "level": level,
        "score": score,
        "attempts": attempts,
    }
    
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

def load_ongoing_game(username):
    init_storage()
    with open(filename, "r") as file:
        data = json.load(file)
    if username in data:
        return data[username]["current_session"]
    return None

def handle_game_over(username, final_level, final_score):
    init_storage()
    with open(filename, "r") as file:
        data = json.load(file)
        
    data = ensure_user_profile(data, username)

    data[username]["current_session"] = None

    message = []
    if final_score > data[username]["high_score"]:
        data[username]["high_score"] = final_score
        message.append(f"New Personal Best for {username}: {final_score}!") 
    
    if "max_level" not in data[username]:  # Guard code for older profiles missing this key
        data[username]["max_level"] = 1   

    if final_level > data[username]["max_level"]:
        data[username]["max_level"] = final_level
        message.append(f"Highest level Reached: level {final_level}")

    with open(filename, "w") as file:
        json.dump(data, file, indent=4)
    
    return f"Well done {username}!\n" + "\n".join(message) if message else "" 


def get_highest_score():

    if not os.path.exists(filename):
        return None
        
    with open(filename, "r") as file:
        data = json.load(file)
    if not data:
        return None

    top_user = max(data, key=lambda user: data[user]["high_score"])
    
    return {"username": top_user, "score": data[top_user]["high_score"]}

def get_highest_level():
    if not os.path.exists(filename):
        return None
        
    with open(filename, "r") as file:
        data = json.load(file)
    if not data:
        return None

    top_user = max(data, key=lambda user: data[user]["max_level"])
    
    return {"username": top_user, "level": data[top_user]["max_level"]}