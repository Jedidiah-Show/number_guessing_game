# Core game logic

import random
from internal.ui.ui import correct, error, text, header, entry
from internal.cmd.helpers.helpers import clearscreen, is_exit, sleep_time, go_back
from internal.config.session_cfg import load_ongoing_game, save_ongoing_game, handle_game_over, get_highest_score, get_highest_level
from internal.cmd.validation.input_validation import valid_guess

def gameover(user_name, secret_number, level, score):
    error(f"Oops!!! You have used up your 10 attempts\nThe secret number is {secret_number}.\nGAME OVER!")
    message = handle_game_over(user_name, level, score)
    if message:
        correct(message)
        sleep_time(3)
    return

def new_game_config(level=1):
    secret_number = random.randint(1, 25*level)
    attempts = 1
    score = 0
    return secret_number, level, attempts, score

def saved_game_config(saved_game):
    try:
        if saved_game:
            choice = entry("You have an ongoing game. Would you like to resume it? (y/n): ").strip().lower()
            if choice == "yes" or choice == "y":
                score = saved_game["score"]
                secret_number = saved_game["secret_number"]
                attempts = saved_game["attempts"]
                level = saved_game["level"]
                return secret_number, level, attempts, score
            else:
                return new_game_config(level)
    except KeyboardInterrupt:
            is_exit("interrupt")

def launcher(user_name, prompt="new game"):
    if prompt == "saved game":
        saved_game = load_ongoing_game(user_name)
        if saved_game == None:
            error(f"No ongoing game found for {user_name}. Starting a new game...")
            prompt = "new game"
    highest_score = get_highest_score()
    highest_level = get_highest_level()
    try:
        match prompt:
            case prompt if prompt.lower() == "new game":
                secret_number, level, attempts, score = new_game_config(1)
                guesser(user_name, secret_number, attempts, score, level, highest_score, highest_level)
            case prompt if prompt.lower() == "saved game":
                secret_number, level, attempts, score = saved_game_config(saved_game)
                guesser(user_name, secret_number, attempts, score, level, highest_score, highest_level)
    except KeyboardInterrupt:
            is_exit("interrupt")

def guesser(user_name, secret_number, attempts, score, level, highest_score, highest_level):
    while True:
        try:
            if highest_level is None:
                highest_level = {'level': 0, 'user_name': 'No record'}
            if highest_score is None:
                highest_score = {'score': 0, 'user_name': 'No record'}
            clearscreen()
            header("Game on!")
            best_record = f"Best record: Level: {highest_level['level']} levels ({highest_level['user_name']})  | Score: {highest_score['score']} pts ({highest_score['user_name']})"
            current_level = f"level: {level}"
            current_score = f"score: {score} pts"
            current_attempt = f"attempt: {attempts}/10"
            score_line= f"Your {current_level:>2} | {current_score:>2} | {current_attempt:>2}\n"
            text(best_record)
            text(score_line)

            if attempts >= 10:
                gameover(user_name, secret_number, level, score)
                level = 1
                secret_number, level, attempts, score, = new_game_config(level)
                text("New session")
                text(f"Level {level}")
            else:
                max_num = 25 * level
                guess = entry(f"guess (1-{max_num})")
                if guess.lower() == "exit":
                    save_ongoing_game(user_name, secret_number, level, attempts, score)
                    correct(f"Game autosaved for {user_name}!")
                    sleep_time(1)
                    is_exit() 
                if guess.lower()== "back":
                    save_ongoing_game(user_name, secret_number, level, attempts, score)
                    correct(f"Game autosaved for {user_name}!")
                    sleep_time(1)
                    go_back("Main Menu")
                    return
                user_guess = valid_guess(guess, max_num)
                if user_guess == -1:
                    continue
                if user_guess < secret_number:
                    error(f"Too low! Try again. You have {10-attempts} attempts left")
                    sleep_time(2)
                    attempts += 1
                    save_ongoing_game(user_name, secret_number, level, attempts, score)
                    correct(f"Game autosaved for {user_name}!")
                    continue
                elif user_guess > secret_number:
                    error(f"Too high! Try again. You have {10-attempts} attempts left")
                    sleep_time(2)
                    attempts += 1
                    save_ongoing_game(user_name, secret_number, level, attempts, score)
                    correct(f"Game autosaved for {user_name}!")
                    continue
                else:
                    correct(f"Correct! You guessed it in {attempts} attempts.")
                    match attempts:
                        case attempts if attempts <= 5:
                            score += 5
                            correct("You have earned 5 points for being a genius")

                        case attempts if 5 < attempts <= 10:
                            score += 2
                            correct("You have earned 2 points")
                  
                    attempts = 0
                    save_ongoing_game(user_name, secret_number, level, attempts, score)
                    text("Next Level - Level {level}")
                    sleep_time(2)
                    level+=1
                    secret_number, _, attempts, _ = new_game_config(level)
                    correct(f"Game autosaved for {user_name}!") 
                    s    
                    continue 
        except KeyboardInterrupt:
            is_exit("interrupt")
        except ValueError:
            print("Please enter a valid integer.")