import json
import os

FILE_NAME = "saved_profiles.json"

def load_profiles():
    if not os.path.exists(FILE_NAME):
        return {}

    try:
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_profiles(data):
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_profile(name, payload):
    data = load_profiles()
    data[name] = payload
    save_profiles(data)

def delete_profile(name):
    data = load_profiles()
    if name in data:
        del data[name]
        save_profiles(data)
