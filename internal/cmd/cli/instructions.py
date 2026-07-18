from internal.ui.ui import text, header
from internal.cmd.helpers.helpers import clearscreen, go_back

def user_instructions():
    clearscreen()
    header("Instructions")
    text(
        "Core Gameplay & Rules\n"
        "• For each game session, you are granted exactly 10 attempts.\n"
        "• A secret target number is randomly generated (between 1 and specified number based on the level) and held until guessed or until your attempts run out.\n"
        "• If you fail to guess the secret number within 10 attempts, it's 'GAME OVER' for that session.\n"
        "\n"
        "Dynamic Scoring & Points\n"
        "• The faster you lock down the secret number, the higher your score reward!\n"
        "• Earn 5 points for an elite guess within your first 5 attempts.\n"
        "• Earn 2 points for a successful guess between attempts 6 and 10.\n"
        "\n"
        "Persistent Profiles & Saves\n"
        "• Never lose your progress! Your unique username tracks your global metrics natively.\n"
        "• Feel free to drop out at any point by typing 'exit'. Ongoing sessions automatically serialize your remaining attempts, levels, and points straight to our persistent database backend.\n"
        "• You can seamlessly pick up right where you left off by choosing 'Resume Saved Game' from the main menu.\n"
        "\n"
        "Level Scaling & The Leaderboard\n"
        "• Build momentum! Successfully beating a game advances your current level rank, scaling the difficulty parameters dynamically.\n"
        "• Compete against the community! Access the 'Leaderboard' view from the main menu to see the all-time records for peak Levels and total Scores to see exactly how you rank against the best players.\n"
    )
    go_back()
    return