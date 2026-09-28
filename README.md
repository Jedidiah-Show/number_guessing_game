# Number Guessing Game

A number guessing game with a terminal mode and a local browser interface, user accounts, persistent sessions, level progression, and a scoring/highscore system.

## Features

- **User accounts** — sign up and log in with a username and password (passwords hashed with `bcrypt`, never stored in plain text)
- **Persistent sessions** — quit mid-game and resume exactly where you left off
- **Level progression** — each level widens the guessing range (`1` to `25 × level`)
- **Scoring system** — earn points based on how many attempts it takes to guess correctly
- **Highscore tracking** — per-user best score and highest level reached, shown at the top of every game
- **Forgot password recovery** — re-verify identity via first/last name to reset access
- **Simple CLI menu** — resume saved game, start new game, check highscore, view instructions, log out, exit
- **Local browser GUI** — play through a browser served by a loopback-only Python HTTP server

## Requirements

- Python 3.13+
- [`bcrypt`](https://pypi.org/project/bcrypt/)
- [`colorama`](https://pypi.org/project/colorama/)

## Installation

```bash
git clone https://github.com/Jedidiah-Show/number_guessing_game.git
cd number_guessing_game
python -m pip install -r requirements.txt
```

## Usage

```bash
python number_guessing_game.py
```

You'll be prompted to log in or sign up. From the main menu you can resume a saved game, start a new one, check the highscore board, or view how-to-play instructions. You can type `exit` at almost any prompt to save your progress and quit.

### Browser interface

Run the local HTTP server from the project folder:

```bash
python gui.py
```

The launcher opens `http://127.0.0.1:8000` in your browser. Keep the terminal open while playing; press **Ctrl+C** to stop the server. If port 8000 is busy, choose another with `python gui.py --port 8001`. Use `python gui.py --no-browser` to start without opening a tab.

The browser interface uses the existing account and game-data JSON files, and autosaves after each guess. The server only accepts connections through `127.0.0.1`; it is intended for play on the same computer, not public hosting. Sign-in sessions last until the server stops, while saved game progress remains on disk.

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
├── gui.py                         # Local browser server and JSON API
├── web/                           # Browser interface files
│   ├── index.html
│   ├── app.js
│   └── style.css
├── database.json                  # Created locally; gitignored
├── game_data.json                 # Created locally; gitignored
├── test_gui.py                    # Browser adapter tests
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

- User data (including password hashes and session state) is stored locally in `database.json` and `game_data.json` beside the launchers.
- These files are **excluded from version control** via `.gitignore` — they contain sensitive data and shouldn't be committed.
- Passwords are hashed with `bcrypt` before storage; plain-text passwords are never written to disk.
- Saves are written atomically (via a temp file + `os.replace`) to prevent data corruption if the program crashes mid-write.

## Known Limitations / Roadmap

- No password reset via email — recovery is done via name re-verification only
- Single-player only; no multiplayer or global leaderboard sync
- No difficulty customization beyond the built-in level scaling

## License

_MIT_
