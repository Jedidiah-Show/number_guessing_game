import os
import json
from internal.ui.ui import error, text, header, GOLD, SILVER, BRONZE, RESET
from internal.config.session_cfg import filename
from internal.cmd.helpers.helpers import go_back, sleep_time, clearscreen

def load_leaderboard():
    if not os.path.exists(filename):
        error("No high scores recorded yet!")
        sleep_time(2)
        return

    with open(filename, "r") as file:
        data = json.load(file)

    leaderboard_list = []
    for user_name, profile in data.items():
        score = profile.get("high_score", 0)
        if score > 0:
            leaderboard_list.append((user_name, score))

    sorted_leaderboard = sorted(leaderboard_list, key=lambda x: x[1], reverse=True)
    top_five = sorted_leaderboard[:5]
    return top_five
   
def view_leaderboard():
    top_five = load_leaderboard()
    clearscreen()
    header("Global Top 5 Leaderboard")
    msg_len = 0
    for rank, (user, score) in enumerate(top_five, start=1):
        if rank == 1:
            color = GOLD
            medal = "👑"
        elif rank == 2:
            color = SILVER
            medal = "🥈"
        elif rank == 3:
            color = BRONZE
            medal = "🥉"
        else:
            color = "" 
            medal = "  "
    
        rank_str = f"#{rank}"
        score_line = f"{medal} {rank_str:<2} | {user:<15} | Score: {score:>5}"
        msg_len= len(score_line)
        if color:
            text(f"{color}{score_line}{RESET}")
        else:
            text(score_line)
    
    text("\n")
    if msg_len > 0:
        text("=" * (msg_len))
        text("\n")

    go_back("Main Menu")
    return
    
