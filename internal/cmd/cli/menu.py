# Main Menu

from internal.ui.ui import text, header
from internal.cmd.validation.input_validation import select_index
from internal.cmd.helpers.helpers import clearscreen, is_exit
from internal.cmd.cli.engine import launcher
from internal.cmd.cli.leaderboard import view_leaderboard
from internal.cmd.cli.instructions import user_instructions

def main_menu(user_name):
    while True:
        clearscreen()
        header("Main Menu")
        try:
            options= ("1. Resume saved game", "2. Start a new game", "3. Check highscore", "4. How to play", "5. log out", "6. Exit")
            text("\n".join(map(str,options)))
            choice = select_index(len(options)) 
            match choice:
                case choice if choice == 0:
                    text(f"Resuming from last checkpoint with {user_name}...")
                    launcher(user_name, "saved game")
                case choice if choice == 1:
                    text("Starting a new game...")
                    launcher(user_name)
                case choice if choice == 2:
                    text("Loading all-time highscores...")
                    view_leaderboard()
                case choice if choice == 3:
                    text("Loading game instructions...")
                    user_instructions()
                case choice if choice == 4:
                    text(f"Logging out {user_name}...")
                    return
                case _:
                    is_exit()
        except KeyboardInterrupt:
            is_exit("interrupt")
            
            
            
                