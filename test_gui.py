"""Focused tests for the local browser adapter."""

from http.cookiejar import CookieJar
from http.server import ThreadingHTTPServer
from pathlib import Path
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import HTTPCookieProcessor, build_opener, Request
from unittest.mock import patch

import gui


class GameSessionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.database_patch = patch.object(gui.database_cfg, "database", str(root / "database.json"))
        self.session_patch = patch.object(gui.session_cfg, "filename", str(root / "game_data.json"))
        self.board_patch = patch.object(gui.leaderboard, "filename", str(root / "game_data.json"))
        self.database_patch.start()
        self.session_patch.start()
        self.board_patch.start()

    def tearDown(self):
        self.database_patch.stop()
        self.session_patch.stop()
        self.board_patch.stop()
        self.temp.cleanup()

    def test_guess_feedback_persistence_and_level_score(self):
        with patch("gui.engine.new_game_config", side_effect=[(7, 1, 1, 0), (40, 2, 1, 0)]):
            session = gui.GameSession("Ada")
            session.start_new()
            low_state = session.guess("4")
            self.assertEqual(low_state["last_result"]["kind"], "low")
            self.assertEqual(low_state["attempts"], 2)
            self.assertNotIn("secret_number", low_state)
            won_state = session.guess("7")

        self.assertEqual(won_state["level"], 2)
        self.assertEqual(won_state["score"], 5)
        self.assertEqual(won_state["maximum"], 50)
        saved = gui.session_cfg.load_ongoing_game("Ada")
        self.assertEqual(saved["secret_number"], 40)
        self.assertEqual(saved["score"], 5)

    def test_tenth_wrong_guess_ends_run_and_clears_save(self):
        with patch("gui.engine.new_game_config", return_value=(25, 1, 1, 0)):
            session = gui.GameSession("Ada")
            session.start_new()
            for _ in range(10):
                state = session.guess("1")

        self.assertEqual(state["phase"], "game_over")
        self.assertEqual(state["attempts"], 10)
        self.assertEqual(gui.session_cfg.load_ongoing_game("Ada"), None)

    def test_invalid_guesses_do_not_consume_attempts(self):
        with patch("gui.engine.new_game_config", return_value=(7, 1, 1, 0)):
            session = gui.GameSession("Ada")
            session.start_new()
            for guess in ("", "abc", "0", "26"):
                with self.assertRaises(ValueError):
                    session.guess(guess)
        self.assertEqual(session.attempts, 1)


class HttpApiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.database_patch = patch.object(gui.database_cfg, "database", str(root / "database.json"))
        self.session_patch = patch.object(gui.session_cfg, "filename", str(root / "game_data.json"))
        self.board_patch = patch.object(gui.leaderboard, "filename", str(root / "game_data.json"))
        self.database_patch.start()
        self.session_patch.start()
        self.board_patch.start()
        self.server = gui.make_server(0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f"http://127.0.0.1:{self.server.server_port}"
        self.client = build_opener(HTTPCookieProcessor(CookieJar()))

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.session_patch.stop()
        self.database_patch.stop()
        self.board_patch.stop()
        self.temp.cleanup()

    def request(self, path, payload=None):
        data = None
        headers = {}
        if payload is not None:
            import json
            data = json.dumps(payload).encode()
            headers["Content-Type"] = "application/json"
        request = Request(self.base + path, data=data, headers=headers)
        with self.client.open(request) as response:
            if path == "/":
                return response.read().decode()
            import json
            return json.loads(response.read())

    def test_browser_page_register_and_game_actions(self):
        page = self.request("/")
        self.assertIn("Find the number", page)
        auth_state = self.request("/api/register", {
            "first_name": "Ada", "last_name": "Lovelace",
            "username": "Ada", "password": "Logic123",
        })
        self.assertTrue(auth_state["authenticated"])

        with patch("gui.engine.new_game_config", return_value=(15, 1, 1, 0)):
            started = self.request("/api/new", {})
            guessed = self.request("/api/guess", {"guess": "20"})
        self.assertEqual(started["phase"], "playing")
        self.assertEqual(guessed["last_result"]["kind"], "high")
        self.assertEqual(guessed["attempts"], 2)

    def test_api_rejects_other_hosts(self):
        request = Request(self.base + "/api/state", headers={"Host": "example.com"})
        with self.assertRaises(HTTPError) as raised:
            self.client.open(request)
        self.assertEqual(raised.exception.code, 403)


if __name__ == "__main__":
    unittest.main()