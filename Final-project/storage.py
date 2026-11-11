"""Storage layer: handles safe cross-platform file persistence."""

import csv
from pathlib import Path
from typing import List, Dict

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "tasks.csv"
FIELDNAMES = ["name", "priority", "status"]


def load_tasks_from_file(file_path: Path = DATA_PATH) -> List[Dict[str, str]]:
    """Loads tasks safely from a CSV file. Returns an empty list if file doesn't exist."""
    if not file_path.exists():
        return []

    tasks: List[Dict[str, str]] = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                tasks.append({
                    "name": row.get("name", "").strip(),
                    "priority": row.get("priority", "").strip(),
                    "status": row.get("status", "Pending").strip()
                })
    except (OSError, csv.Error) as err:
        raise RuntimeError(f"Error reading from file '{file_path}': {err}") from err

    return tasks


def save_tasks_to_file(tasks: List[Dict[str, str]], file_path: Path = DATA_PATH) -> None:
    """Saves tasks to a CSV file using a context manager and explicit UTF-8 encoding."""
    try:
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            for task in tasks:
                writer.writerow({
                    "name": task.get("name", ""),
                    "priority": task.get("priority", ""),
                    "status": task.get("status", "Pending")
                })
    except OSError as err:
        raise RuntimeError(f"Error saving to file '{file_path}': {err}") from err

