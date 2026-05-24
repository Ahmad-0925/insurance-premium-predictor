import json

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "history.json")

try:
    with open(HISTORY_FILE, "r") as f:
        history = json.load(f)
except:
    history = []