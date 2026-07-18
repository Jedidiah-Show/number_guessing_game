# Number Guessing Game

A terminal-based number guessing game with user accounts, persistent sessions, level progression, and a scoring/highscore system.

## Features

- **User accounts** — sign up and log in with a username and password (passwords hashed with `bcrypt`, never stored in plain text)
- **Persistent sessions** — quit mid-game and resume exactly where you left off
- **Level progression** — each level widens the guessing range (`1` to `25 × level`)
- **Scoring system** — earn points based on how many attempts it takes to guess correctly
- **Highscore tracking** — per-user best score and highest level reached, shown at the top of every game
- **Forgot password recovery** — re-verify identity via first/last name to reset access
- **Simple CLI menu** — resume saved game, start new game, check highscore, view instructions, log out, exit

## Requirements

- Python 3.13+
- [`bcrypt`](https://pypi.org/project/bcrypt/)
- [`colorama`](https://pypi.org/project/colorama/)

## Installation

```bash
git clone <your-repo-url>
cd number_guessing_game
pip install requirements.txt
```

## Usage

```bash
python number_guessing_game.py
```

You'll be prompted to log in or sign up. From the main menu you can resume a saved game, start a new one, check the highscore board, or view how-to-play instructions. You can type `exit` at almost any prompt to save your progress and quit.

## How to Play

1. The game picks a secret number between `1` and `25 × level` (level 1 starts at 1–25).
2. You have 10 attempts per level to guess it.
3. After each guess you're told whether it was too high or too low.
4. Guess correctly to advance to the next level:
   - 5 or fewer attempts: **+5 points**
   - 6–10 attempts: **+2 points**
5. Run out of attempts and it's game over — your level resets to 1, but your highscore and max level are preserved.

## Project Structure

```
number_guessing_game/
├── number_guessing_game.py        # Entry point
├── data/                          # User & session data (gitignored)
│   ├── game_data.json
│   └── database.json
└── internal/
    ├── cmd/
    │   ├── cli/
    │   │   ├── menu.py              # Main menu logic
    │   │   └── engine.py            # Game loop / launcher
    |   |   └── instructions.py      # Game play 
    |   |   └── leaderboard.py       # Leaderboad
    │   ├── validation/
    |   |   ├── auth.py              # Sign up / login flow
    │   │   └── input_validation.py  # Input validation logic
    │   └── helpers/
    │       └── helpers.py           # Screen clearing, sleep, exit handling
    ├── config/
    │   ├── session_cfg.py           # Save/load ongoing game sessions
    │   └── database_cfg.py          # User registration, login, password verification
    └── ui/
        └── ui.py                    # Terminal UI helpers (text, prompts, headers)
```

## Data & Security Notes

- User data (including password hashes and session state) is stored locally in JSON files under `data/`.
- These files are **excluded from version control** via `.gitignore` — they contain sensitive data and shouldn't be committed.
- Passwords are hashed with `bcrypt` before storage; plain-text passwords are never written to disk.
- Saves are written atomically (via a temp file + `os.replace`) to prevent data corruption if the program crashes mid-write.

## Known Limitations / Roadmap

- No password reset via email — recovery is done via name re-verification only
- Single-player only; no multiplayer or global leaderboard sync
- No difficulty customization beyond the built-in level scaling

## License

_MIT_