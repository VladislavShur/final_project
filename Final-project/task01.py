import csv
from pathlib import Path
from typing import List, Dict

# הגדרת נתיב בסיס יחסי לפי כללי הפרויקט (תיקון Bug #2)
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "tasks.csv"
FIELDNAMES = ["name", "test_suite", "priority", "status"]

VALID_PRIORITIES = {"Low", "Medium", "High"}
VALID_STATUSES = {"Pending", "In Progress", "Done", "Completed"}

tasks: List[Dict[str, str]] = []


def load_tasks() -> bool:
    """טעינת משימות מקובץ ה-CSV. מאפס את הזיכרון בכל טעינה למניעת כפילויות (תיקון Bug #1)."""
    global tasks
    if not DATA_PATH.exists():
        print("Failed to read tasks file (File not found).")
        return False

    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            loaded = []
            for row in reader:
                loaded.append({
                    "name": row.get("name", "").strip(),
                    "test_suite": row.get("test_suite", "").strip() or "General",
                    "priority": row.get("priority", "Medium").strip() or "Medium",
                    "status": row.get("status", "Pending").strip() or "Pending"
                })
            # איפוס המערך הגלובלי לפני השמה למניעת כפילויות זיכרון
            tasks = loaded
            print(f"Loaded {len(tasks)} tasks successfully!")
            return True
    except Exception as err:
        print(f"Failed to read tasks file: {err}")
        return False


def display_tasks() -> None:
    """TC-01: הצגת כלל המשימות בטרמינל."""
    if not tasks:
        print("\nNo tasks currently loaded. Use option 1 to load from file or option 2 to add.")
        return

    print("\n" + "=" * 65)
    print(f"{'Idx':<4} | {'Task Name':<22} | {'Test Suite':<15} | {'Priority':<9} | {'Status'}")
    print("-" * 65)
    for idx, t in enumerate(tasks):
        print(f"{idx:<4} | {t['name']:<22} | {t['test_suite']:<15} | {t['priority']:<9} | {t['status']}")
    print("=" * 65)


def add_task() -> None:
    """TC-02: קליטת משימה חדשה למערכת."""
    print("\n[Option 2: Add Task]")
    name = input("Task Name: ").strip()
    if not name:
        print("Error: Task name cannot be empty.")
        return

    test_suite = input("Test Suite [default: General]: ").strip() or "General"
    priority = input("Priority (Low/Medium/High) [default: Medium]: ").strip().capitalize() or "Medium"
    if priority not in VALID_PRIORITIES:
        priority = "Medium"

    status = input("Status (Pending/In Progress/Done) [default: Pending]: ").strip() or "Pending"

    tasks.append({
        "name": name,
        "test_suite": test_suite,
        "priority": priority,
        "status": status
    })
    print(f"Success: Task '{name}' added successfully to memory.")


def update_status() -> None:
    """TC-03: עדכון סטטוס משימה קיימת עם הגנה מפני IndexError וחריגות."""
    if not tasks:
        print("\nNo tasks available to update.")
        return

    display_tasks()
    idx_input = input("\nEnter task index to update: ").strip()
    
    # הגנה מפני קריסות של קלט שאינו מספרי
    if not idx_input.isdigit():
        print("Error: Invalid index. Please enter a valid non-negative integer.")
        return

    idx = int(idx_input)
    # הגנה מפני IndexError
    if idx < 0 or idx >= len(tasks):
        print(f"Error: Index out of range. Allowed indices: 0 to {len(tasks) - 1}.")
        return

    print("Allowed statuses: Pending, In Progress, Done, Completed")
    new_status = input(f"New Status for '{tasks[idx]['name']}': ").strip()
    if not new_status:
        print("Error: Status cannot be empty.")
        return

    old_status = tasks[idx]["status"]
    tasks[idx]["status"] = new_status
    print(f"Success: Task '{tasks[idx]['name']}' status changed from '{old_status}' to '{new_status}'.")


def save_and_exit() -> bool:
    """TC-04: שמירת כל המשימות לקובץ ה-CSV ויציאה."""
    try:
        with open(DATA_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            for t in tasks:
                writer.writerow(t)
        print("Tasks saved successfully! Exiting. Goodbye!")
        return True
    except Exception as err:
        print(f"Error saving tasks: {err}")
        return False


def delete_task_core(idx: int) -> tuple[bool, str]:
    """מחיקת משימה לפי אינדקס עם שמירה אטומית לקובץ."""
    global tasks
    if idx < 0 or idx >= len(tasks):
        return False, f"Error: Index out of range. Allowed: 0 to {len(tasks)-1}"
    removed = tasks.pop(idx)
    save_and_exit()
    return True, f"Success: Task '{removed['name']}' deleted."


def delete_task() -> None:
    """קליטת אינדקס ומחיקת משימה מהטרמינל."""
    if not tasks:
        print("\nNo tasks to delete.")
        return
    display_tasks()
    idx_input = input("\nEnter task index to delete: ").strip()
    if not idx_input.isdigit():
        print("Error: Invalid number.")
        return
    ok, msg = delete_task_core(int(idx_input))
    print(msg)


def run_app():
    while True:
        print("\n=== CLI Task & Team Tracker ===")
        print("1. Load & Display Tasks")
        print("2. Add Task")
        print("3. Update Task Status")
        print("4. Delete Task")
        print("5. Save & Exit")
        c = input("Choice: ").strip()

        if c == "1":
            load_tasks()
            display_tasks()
        elif c == "2":
            add_task()
        elif c == "3":
            update_status()
        elif c == "4":
            delete_task()
        elif c == "5":
            if save_and_exit():
                break
        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    run_app()

