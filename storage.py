import json
import os

FILE_NAME = "saved_profiles.json"


def load_saved_profiles():
    if not os.path.exists(FILE_NAME):
        return {}

    try:
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_saved_profiles(data):
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
