# Number Guessing Game

from internal.ui.ui import header, text
from internal.cmd.validation.input_validation import select_index
from internal.cmd.validation.authentication import signup, login
from internal.cmd.helpers.helpers import clearscreen, is_exit
from internal.cmd.cli.menu import main_menu

def home():
    while True:
        clearscreen()
        header("Let's do some brain exercise!")
        text("Please Sign up/log in to continue.")
        try:
            options = ("1. Sign up", "2. Log in", "3. Exit")
            text("\n".join(map(str, options)))
            choice = select_index(len(options))
            username = ""
            match choice:
                case choice if choice == 0:
                    text("Sign up selected.")
                    username = signup()
                case choice if choice == 1:
                    text("Log in selected.")
                    username = login()
                case _ :
                    is_exit()
        except KeyboardInterrupt:
            is_exit("interrupt")
        else:
            clearscreen()
            text(f"Welcome, {username}!")
            main_menu(username)
            continue
        
home()