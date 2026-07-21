import os
import json
from internal.ui.ui import error, text, header, GOLD, SILVER, BRONZE, RESET
from internal.config.session_cfg import filename
from internal.cmd.helpers.helpers import go_back, sleep_time, clearscreen

def load_leaderboard():
    if not os.path.exists(filename):
        return [], []

    with open(filename, "r") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            return [], []

    # Build individual lists so players can rank on one board even if they are 0 on the other
    score_list = []
    level_list = []

    for user_name, profile in data.items():
        
        high_score = profile.get("high_score", 0)
        max_level = profile.get("max_level", 1) 
        session = profile.get("current_session") or {}
        current_score = session.get("score", 0)
        current_level = session.get("level", 1)

        best_user_score = max(high_score, current_score)
        best_user_level = max(max_level, current_level)

        score_list.append((user_name, best_user_score))
        level_list.append((user_name, best_user_level))


    # Sort both boards independently
    sorted_score = sorted(score_list, key=lambda x: x[1], reverse=True)
    sorted_level = sorted(level_list, key=lambda x: x[1], reverse=True)

    return sorted_score[:5], sorted_level[:5]
   
def get_medal_and_color(rank):
    if rank == 1:
        return GOLD, "👑"
    elif rank == 2:
        return SILVER, "🥈"
    elif rank == 3:
        return BRONZE, "🥉"
    return "", "  "

def view_leaderboard():
    top_five_score, top_five_level = load_leaderboard()
    
    if not top_five_score and not top_five_level:
        clearscreen()
        header("Leaderboards")
        error("No high scores recorded yet!")
        sleep_time(2)
        go_back("Main Menu")
        return

    clearscreen()
    header("Global Top 5 Leaderboard")

    msg = "  Top 5 Highest Scores"
    text(msg)
    submsg = f"  Rank | {'Player':<15} | {'Score':>10}"
    text(submsg)
    text("-" * len(submsg))
    
    for rank, (user, score) in enumerate(top_five_score, start=1):
        color, medal = get_medal_and_color(rank)
        score_line = f"{medal} #{rank:<2} | {user:<15} | {score:>6} pts"
        if color:
            text(f"{color}{score_line}{RESET}")
        else:
            text(score_line)
            
    text("\n" + "="* len(score_line) + "\n")

   
    msg = "  Top 5 Peak Levels"
    text(msg)
    submsg = f"  Rank | {'Player':<15} | {'Max Level':>10}"
    text(submsg)
    text("-" * len(submsg))
    
    for rank, (user, level) in enumerate(top_five_level, start=1):
        color, medal = get_medal_and_color(rank)
        level_line = f"{medal} #{rank:<2} | {user:<15} | Lvl {level:>5}"
        if color:
            text(f"{color}{level_line}{RESET}")
        else:
            text(level_line)
            
    text("\n" + "="*len(level_line) + "\n")

    go_back("Main Menu")
    return