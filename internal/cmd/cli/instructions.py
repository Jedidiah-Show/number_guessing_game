from internal.ui.ui import text, header
from internal.cmd.helpers.helpers import clearscreen, go_back

def user_instructions():
    clearscreen()
    header("Instructions")
    text("Game Play\n"
         "You have 10 attempts for every single game.\n"
        "The secret number is randomly generated (between 1 and 100) and held until all 10 attempts have been exhausted.\n"
        "The faster you guess the number, the more points you will earn.\n"
        "You earn 5 points for guessing the correct number within 5 attempts and 2 points if above 5 attempts but within your 10 attempts\n"
        "if you fail to guess the number within 10 attempts. 'GAME OVER'\n"
        "\nResuming a saved game\n"
        "You can resume a saved game from the main menu if you exit the game before exhausting all 10 attempts.\n"
        "\nLeaderboard\n"
        "You can check the all-time highscore from the main menu to see how you rank against other players.\n"
        "\nExiting\n"
        "You can exit the game at any time by typing 'exit'. Don't worry if you have an ongoing session. It gets automatically saved\n")
    
    go_back()
    return