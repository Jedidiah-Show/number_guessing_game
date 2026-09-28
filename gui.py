"""Run the local browser interface: python gui.py."""

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import secrets
from http.cookies import SimpleCookie
import threading
import webbrowser

from internal.cmd.cli import engine, leaderboard
from internal.config import database_cfg, session_cfg

ROOT = Path(__file__).resolve().parent
database_cfg.database = str(ROOT / "database.json")
session_cfg.filename = str(ROOT / "game_data.json")
leaderboard.filename = session_cfg.filename


class GameSession:
    """Browser-friendly state around the existing game and persistence helpers."""

    def __init__(self, user_name):
        self.user_name = user_name
        self.phase = "setup"
        self.feedback = ""
        self.last_result = None
        self.secret_number = None
        self.level = 1
        self.attempts = 1
        self.score = 0
        self.saved_game = session_cfg.load_ongoing_game(user_name)
        self.best_score, self.max_level = self._profile_records()

    def _profile_records(self):
        try:
            profiles = json.loads(Path(session_cfg.filename).read_text(encoding="utf-8"))
            profile = profiles.get(self.user_name, {})
            return profile.get("high_score", 0), profile.get("max_level", 1)
        except (OSError, ValueError, AttributeError):
            return 0, 1

    def _persist(self):
        session_cfg.save_ongoing_game(
            self.user_name, self.secret_number, self.level, self.attempts, self.score
        )
        self.saved_game = {
            "secret_number": self.secret_number,
            "level": self.level,
            "attempts": self.attempts,
            "score": self.score,
        }

    def _update_records(self):
        self.max_level, self.best_score = session_cfg.update_best_record(
            self.user_name, self.max_level, self.best_score, self.level, self.score
        )

    def start_new(self):
        self.secret_number, self.level, self.attempts, self.score = engine.new_game_config(1)
        self.phase = "playing"
        self.feedback = "A number is waiting between 1 and 25."
        self.last_result = None
        self._persist()

    def resume(self):
        saved = session_cfg.load_ongoing_game(self.user_name)
        if not isinstance(saved, dict):
            raise ValueError("There is no saved game to resume.")
        level = saved.get("level")
        attempts = saved.get("attempts")
        secret_number = saved.get("secret_number")
        score = saved.get("score")
        if (
            type(level) is not int or level < 1
            or type(attempts) is not int or not 1 <= attempts <= 10
            or type(secret_number) is not int or not 1 <= secret_number <= 25 * level
            or type(score) is not int or score < 0
        ):
            raise ValueError("The saved game is invalid. Start a new game instead.")
        self.level, self.attempts = level, attempts
        self.secret_number, self.score = secret_number, score
        self.phase = "playing"
        self.feedback = "Your saved game is ready to continue."
        self.last_result = None
        self._update_records()

    def guess(self, raw_guess):
        if self.phase != "playing":
            raise ValueError("Start or resume a game before guessing.")
        if not isinstance(raw_guess, str) or not raw_guess.strip():
            raise ValueError("Enter a whole number to make a guess.")
        try:
            guess = int(raw_guess.strip())
        except ValueError as error:
            raise ValueError("Enter a whole number to make a guess.") from error

        maximum = 25 * self.level
        if not 1 <= guess <= maximum:
            raise ValueError(f"Choose a number from 1 to {maximum}.")

        if guess == self.secret_number:
            points = 5 if self.attempts <= 5 else 2
            self.score += points
            self.last_result = {"kind": "correct", "guess": guess, "points": points}
            self.level += 1
            self.secret_number, _, self.attempts, _ = engine.new_game_config(self.level)
            self.feedback = f"Correct. You earned {points} points and reached level {self.level}."
            self._update_records()
            self._persist()
            return self.state()

        self.last_result = {
            "kind": "low" if guess < self.secret_number else "high",
            "guess": guess,
        }
        if self.attempts >= 10:
            self.phase = "game_over"
            self.feedback = f"No attempts remain. The number was {self.secret_number}."
            self.save_message = session_cfg.handle_game_over(
                self.user_name, self.level, self.score
            )
            self.saved_game = None
        else:
            self.attempts += 1
            self.feedback = "Too low. Try a higher number." if guess < self.secret_number else "Too high. Try a lower number."
            self._update_records()
            self._persist()
        return self.state()

    def state(self):
        scores, levels = leaderboard.load_leaderboard()
        data = {
            "authenticated": True,
            "user": self.user_name,
            "phase": self.phase,
            "has_saved_game": bool(self.saved_game),
            "score": self.score,
            "level": self.level,
            "attempts": self.attempts,
            "attempt_limit": 10,
            "maximum": 25 * self.level,
            "best_score": self.best_score,
            "max_level": self.max_level,
            "feedback": self.feedback,
            "last_result": self.last_result,
            "save_message": getattr(self, "save_message", ""),
            "leaderboard": {
                "scores": [{"user": user, "value": value} for user, value in scores],
                "levels": [{"user": user, "value": value} for user, value in levels],
            },
        }
        if self.phase == "setup":
            data["saved_level"] = self.saved_game.get("level") if self.saved_game else None
            data["saved_score"] = self.saved_game.get("score") if self.saved_game else None
        return data


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def reply(self, status, data, extra_headers=()):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; frame-ancestors 'none'")
        for key, value in extra_headers:
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def allowed(self):
        expected = f"127.0.0.1:{self.server.server_port}"
        origin = self.headers.get("Origin")
        return self.headers.get("Host") == expected and origin in (None, f"http://{expected}")

    def current_user(self):
        cookies = SimpleCookie()
        cookies.load(self.headers.get("Cookie", ""))
        morsel = cookies.get("number_game_session")
        return self.server.tokens.get(morsel.value) if morsel else None

    def do_GET(self):
        if not self.allowed():
            self.reply(403, {"error": "Open the game using its 127.0.0.1 address."})
            return
        if self.path in ("/", "/index.html", "/app.js", "/style.css"):
            files = {
                "/": ("index.html", "text/html"),
                "/index.html": ("index.html", "text/html"),
                "/app.js": ("app.js", "text/javascript"),
                "/style.css": ("style.css", "text/css"),
            }
            filename, content_type = files[self.path]
            body = (ROOT / "web" / filename).read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", f"{content_type}; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path == "/api/state":
            with self.server.lock:
                user = self.current_user()
                state = self.server.sessions[user].state() if user in self.server.sessions else {"authenticated": False}
            self.reply(200, state)
        elif self.path == "/api/leaderboard":
            scores, levels = leaderboard.load_leaderboard()
            self.reply(200, {
                "scores": [{"user": user, "value": value} for user, value in scores],
                "levels": [{"user": user, "value": value} for user, value in levels],
            })
        else:
            self.reply(404, {"error": "Not found."})

    def do_POST(self):
        if not self.allowed() or not self.headers.get("Content-Type", "").startswith("application/json"):
            self.reply(403, {"error": "Use the local game interface to make requests."})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 8192:
                raise ValueError("Request is empty or too large.")
            payload = json.loads(self.rfile.read(size))
            if not isinstance(payload, dict):
                raise ValueError("Invalid request data.")
            with self.server.lock:
                if self.path == "/api/register":
                    first = payload.get("first_name", "")
                    last = payload.get("last_name", "")
                    username = payload.get("username", "")
                    password = payload.get("password", "")
                    if not all(isinstance(value, str) and value.isalpha() for value in (first, last, username)):
                        raise ValueError("Names and usernames must contain letters only.")
                    if len(password) < 6 or not password.isalnum():
                        raise ValueError("Password must be at least six letters or numbers.")
                    created, message = database_cfg.register_user(
                        username, f"{first.title()} {last.title()}", password
                    )
                    if not created:
                        raise ValueError(message.replace("Error: ", ""))
                    return self.login_response(username)
                if self.path == "/api/login":
                    username = payload.get("username", "")
                    password = payload.get("password", "")
                    if not isinstance(username, str) or not isinstance(password, str):
                        raise ValueError("Enter a valid username and password.")
                    valid, message = database_cfg.verify_username(username)
                    if not valid:
                        raise ValueError(message.replace("Error: ", ""))
                    valid, message = database_cfg.verify_password(username, password)
                    if not valid:
                        raise ValueError(message.replace("Error: ", ""))
                    return self.login_response(username)
                if self.path == "/api/logout":
                    token = self._session_token()
                    if token:
                        self.server.tokens.pop(token, None)
                    self.reply(200, {"authenticated": False}, (("Set-Cookie", "number_game_session=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0"),))
                    return
                username = self.current_user()
                if not username:
                    raise ValueError("Please sign in to continue.")
                session = self.server.sessions.setdefault(username, GameSession(username))
                if self.path == "/api/new":
                    session.start_new()
                elif self.path == "/api/resume":
                    session.resume()
                elif self.path == "/api/guess":
                    session.guess(payload.get("guess", ""))
                else:
                    self.reply(404, {"error": "Not found."})
                    return
                self.reply(200, session.state())
        except (ValueError, TypeError, json.JSONDecodeError) as error:
            self.reply(400, {"error": str(error)})

    def _session_token(self):
        cookies = SimpleCookie()
        cookies.load(self.headers.get("Cookie", ""))
        morsel = cookies.get("number_game_session")
        return morsel.value if morsel else None

    def login_response(self, username):
        token = secrets.token_urlsafe(32)
        self.server.tokens[token] = username
        session = self.server.sessions.setdefault(username, GameSession(username))
        cookie = f"number_game_session={token}; HttpOnly; SameSite=Strict; Path=/"
        self.reply(200, session.state(), (("Set-Cookie", cookie),))


def make_server(port=8000):
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    server.sessions = {}
    server.tokens = {}
    server.lock = threading.RLock()
    return server


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    try:
        server = make_server(args.port)
    except OSError as error:
        parser.exit(1, f"Could not start: {error}\nTry: python gui.py --port 8001\n")
    url = f"http://127.0.0.1:{server.server_port}"
    print(f"\nNumber Guessing Game is ready: {url}\nKeep this window open. Press Ctrl+C to stop.\n")
    if not args.no_browser:
        threading.Timer(0.4, webbrowser.open, args=(url,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nThanks for playing!")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()