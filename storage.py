import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROFILES_FILE = BASE_DIR / "saved_profiles.json"


def load_saved_profiles():
    if not PROFILES_FILE.exists():
        return {}

    try:
        with open(PROFILES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_saved_profiles(profiles: dict):
    try:
        with open(PROFILES_FILE, "w", encoding="utf-8") as f:
            json.dump(profiles, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
