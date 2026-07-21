# Persistent game session and info storage

import json
import os

filename = "data/game_data.json"

def init_storage():
    if not os.path.exists(filename):
        with open(filename, "w") as file:
            json.dump({}, file, indent=4)
 
def ensure_user_profile(data, user_name):
    if user_name not in data:
        data[user_name] = {
            "current_session": None,
            "high_score": 0,
            "max_level": 1
        }
    return data

def save_json(data, filename):
    tmp = filename + ".tmp"
    with open(tmp, "w") as file:
        json.dump(data, file, indent=4)
    os.replace(tmp, filename) 

def save_ongoing_game(user_name, secret_number, level, attempts, score):
    init_storage()
    with open(filename, "r") as file:
        data = json.load(file)
    
    data = ensure_user_profile(data, user_name)
    
    data[user_name]["current_session"] = {
        "secret_number": secret_number,
        "level": level,
        "score": score,
        "attempts": attempts,
    }

    if "high_score" not in data[user_name]:
        data[user_name]["high_score"] = 0
    if "max_level" not in data[user_name]:
        data[user_name]["max_level"] = 1
    
    save_json(data, filename) 

def load_ongoing_game(user_name):
    init_storage()
    try:
        with open(filename, "r") as file:
            data = json.load(file)
    except json.JSONDecodeError:
        data = {}
    if user_name in data:
        return data[user_name]["current_session"]
    return None

def handle_game_over(user_name, final_level, final_score):
    init_storage()
    with open(filename, "r") as file:
        data = json.load(file)
        
    data = ensure_user_profile(data, user_name)

    data[user_name]["current_session"] = None

    if "max_level" not in data[user_name]:  # Guard code for older profiles missing this key
        data[user_name]["max_level"] = 1   

    message = []
    if final_score > data[user_name]["high_score"]:
        data[user_name]["high_score"] = final_score
        message.append(f"New Personal High score: {final_score} pts")
        
    if final_level > data[user_name]["max_level"]:
        data[user_name]["max_level"] = final_level
        message.append(f"Highest level reached so far: level {final_level}")

    with open(filename, "w") as file:
        json.dump(data, file, indent=4)
    
    return f"Well done {user_name}!\n" + "\n".join(message) if message else "" 

def update_best_record(user_name, highest_level, highest_score, level, score):
    with open(filename, "r") as file:
        data = json.load(file)
    data = ensure_user_profile(data, user_name)
    
    top_level= max(highest_level, level)
    top_score= max(highest_score, score)
    if top_score > highest_score:
        data[user_name]["high_score"] = top_score
    if top_level > highest_level:
        data[user_name]["max_level"] = top_level
    
    save_json(data, filename)
    
    return top_level, top_score
