# spear_game/services.py
"""Service layer abstractions for configuration and scores.
Decouples game logic from raw file I/O.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import List, Tuple

CONFIG_PATH = Path("config.json")
GAME_SETTINGS_PATH = Path("game_settings.json")
HIGH_SCORES_PATH = Path("high_scores.json")

class ConfigService:
    def __init__(self, path: Path = CONFIG_PATH):
        self.path = path

    def load(self) -> dict:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def save(self, data: dict) -> None:
        try:
            self.path.write_text(json.dumps(data, indent=4), encoding="utf-8")
        except Exception as e:
            print(f"[CONFIG WARN] Unable to save config: {e}")

class GameSettingsService:
    def __init__(self, path: Path = GAME_SETTINGS_PATH):
        self.path = path

    def load(self) -> dict:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def save(self, data: dict) -> None:
        try:
            self.path.write_text(json.dumps(data, indent=4), encoding="utf-8")
        except Exception as e:
            print(f"[SETTINGS WARN] Unable to save game settings: {e}")

class ScoreService:
    def __init__(self, path: Path = HIGH_SCORES_PATH):
        self.path = path

    def load_scores(self) -> List[Tuple[str,int]]:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                # expect {name: score}
                return sorted([(k, int(v)) for k,v in data.items()], key=lambda x: x[1], reverse=True)
            if isinstance(data, list):
                return [tuple(item) for item in data if isinstance(item, list|tuple) and len(item)==2]
        except Exception:
            pass
        return []

    def append_score(self, name: str, score: int) -> None:
        scores = self.load_scores()
        scores.append((name, score))
        # keep top 50
        scores = sorted(scores, key=lambda x: x[1], reverse=True)[:50]
        try:
            # store as dict for simplicity
            data = {n: s for n,s in scores}
            self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception as e:
            print(f"[SCORE WARN] Unable to write scores: {e}")
