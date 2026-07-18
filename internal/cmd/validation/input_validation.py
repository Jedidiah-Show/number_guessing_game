# User input validation logic

from internal.ui.ui import error, choice, entry
from internal.cmd.helpers.helpers import is_exit, sleep_time


def validinput(prompt_name= ""):
    err = f"Invalid {prompt_name} name. Please use letters only and do not leave any empty field"
    while True:
        name = entry(prompt_name).strip()
        if name.lower() == "exit":
            is_exit()
        if name.lower() == "back":
            return "back"
        if prompt_name == "password":
            if len(name) < 6:
                error("Password must be at least 6 characters long.")
                continue
            if not name.isalnum():
                error("Password must be alphanumeric.")
                continue
            return name
        if not name.isalpha():
            error(err)
            continue
        return name


def select_index(options):
    if options <=0 :
        error("No options available to select.")
        return None
    while True:
        try:
            user_input = choice(f"Select an option from 1 to {options}: ").strip()
            if user_input.lower() == "exit":
                is_exit()
            index = int(user_input)
            if 1 <= index <= options:
                return index - 1 
            else:
                error(f"Please enter a number between 1 and {options}.")
        except ValueError:
            error("Invalid input. Please enter a valid number.")

def valid_guess(guess, max_num= 25):
    try:
        user_guess = int(guess)
        if 0 < user_guess <= max_num:
            return user_guess
        else:
            error(f"Error: number above range. Please input between 1 and {max_num}")
            sleep_time(1)
            return -1
    except ValueError:
        error("Invalid number")
        sleep_time(1)
        return -1

   
   



    