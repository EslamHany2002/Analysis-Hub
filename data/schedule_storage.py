"""
Schedule JSON Storage
"""

import json
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
SCHEDULE_JSON_PATH = DATA_DIR / "schedule_data.json"


def save_schedule_json(data, path=SCHEDULE_JSON_PATH):
    """Save instructors data to JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_schedule_json(path=SCHEDULE_JSON_PATH):
    """Load instructors data from JSON file if it exists."""
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def load_initial_schedule_data(excel_bytes=None):
    """
    Load schedule data with priority:
    1) JSON file if exists
    2) Excel file, then save as JSON
    """
    from data.scheduler_data import load_schedule_excel
    
    json_data = load_schedule_json()
    if json_data is not None:
        return json_data

    if excel_bytes is not None:
        data = load_schedule_excel(excel_bytes)
        save_schedule_json(data)
        return data

    return {}