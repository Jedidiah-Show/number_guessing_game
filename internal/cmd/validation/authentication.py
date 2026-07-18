# Sign up/Login page

from internal.ui.ui import error, header, correct, text, entry, choice
from internal.cmd.validation.input_validation import validinput
from internal.config.database_cfg import register_user, verify_username, verify_password, forgot_password
from internal.cmd.helpers.helpers import clearscreen, sleep_time, is_exit

def username():
    fname = validinput("first name")
    if fname == "back":
        return "back"
    lname = validinput("last name")
    fullname = fname.title() + " " + lname.title()
    text(fullname)
    user_name = ""
    selection = entry("Would you like me to generate a username for you? y/n ").strip()
    if selection.lower == "y" or selection.lower() == "yes":
        user_name = fname[0].lower() + lname.lower()
        return user_name, fullname
    user_name = validinput("username")
    return user_name, fullname

def password():
    pass_word = validinput("password")
    return pass_word

def signup():
    clearscreen()
    header("User registration")
    text("Please sign up to continue")
    while True:
        try:
            user_name, fullname = username()
            pass_word = password()
            registered, err = register_user(user_name, fullname, pass_word)
            if not registered:
                error(err)
                continue
        except KeyboardInterrupt:
            is_exit("interrupt")
        except Exception as e:
            error(f"An error occurred: {e}")
            continue
        else:
            correct("Sign up successful!")
            sleep_time(2)
            return user_name

def login():
    clearscreen()
    header("User Authentication")
    text("Please log in to continue")
    count = 1
    try:
        while True:
            user_name = entry("username").strip()
            if user_name == "exit":
                is_exit()
            if user_name == "back":
                return
            verified, err = verify_username(user_name)
            if not verified:
                if count < 3:
                    count +=1
                    error(err)
                    continue
                selection = choice("Seems you don't have an account yet! Wanna sign up? y/n ").strip()
                if selection.lower() == "y" or selection.lower() == "yes":
                    signup()
                continue
            count = 1
            break
        while True:
            pass_word = entry("password")
            if pass_word == "exit":
                is_exit()
            if pass_word == "back":
                return
            verified, err = verify_password(user_name, pass_word)
            if not verified:
                if count < 3:
                    count+=1
                    error(err)
                    continue
                selection = choice("Oops, looks like you forgotten your password!? y/n ").strip()
                if user_name == "exit":
                    is_exit()
                if user_name == "back":
                    return
                if selection.lower() == "y" or selection.lower() == "yes":
                    count = 1
                    while True:
                        if count < 3:
                            fname = validinput("first name")
                            lname = validinput("last name")
                            fullname = fname.title() + " " + lname.title()
                            verified, err = forgot_password(user_name, fullname)
                            if not verified:
                                count += 1
                                error(err)
                                continue
                            text(f"Identity verified! Welcome back {fullname}!")
                            sleep_time(2)
                            count = 1
                            return user_name
                        error("Cannot find your record in the database!")
                        break
                continue
            else:
                correct(f"Log in successful! Welcome {user_name}")
                count = 0
                sleep_time(2)
                return user_name
    except KeyboardInterrupt:
        is_exit("interrupt")
        


