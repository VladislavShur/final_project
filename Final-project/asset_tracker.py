import csv
from pathlib import Path
from typing import List, Dict, Optional

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "assets.csv"
REPORT_PATH = BASE_DIR / "missing_report.txt"

FIELDNAMES = ["asset_name", "category", "assigned_to", "status"]


def load_assets() -> List[Dict[str, str]]:
    if not DATA_PATH.exists():
        return []
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)
    except OSError as e:
        print(f"Error reading file: {e}")
        return []


def save_assets(assets: List[Dict[str, str]]) -> bool:
    try:
        with open(DATA_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(assets)
        return True
    except OSError as e:
        print(f"Error saving file: {e}")
        return False


def display_inventory() -> None:
    assets = load_assets()
    if not assets:
        print("[Notice] No assets found in inventory or file does not exist.")
        return

    print("=" * 65)
    print(f"{'#':<4} | {'Asset Name':<20} | {'Category':<12} | {'Assigned To':<12} | {'Status'}")
    print("-" * 65)
    for idx, item in enumerate(assets, start=1):
        assigned = item.get("assigned_to") or "None"
        print(f"{idx:<4} | {item.get('asset_name',''):<20} | {item.get('category',''):<12} | {assigned:<12} | {item.get('status','')}")
    print("=" * 65)


def assign_asset_core(asset_name: str, employee: str, category: str = "Hardware") -> tuple[bool, str]:
    if not asset_name or not employee:
        return False, "Error: Asset name and Employee name cannot be empty."

    assets = load_assets()

    for item in assets:
        if item.get("asset_name", "").lower() == asset_name.lower():
            if item.get("status", "").upper() == "ASSIGNED":
                current_owner = item.get("assigned_to", "Unknown")
                return False, f"Error: Asset '{asset_name}' is already ASSIGNED to {current_owner}!"
            item["assigned_to"] = employee
            item["status"] = "ASSIGNED"
            save_assets(assets)
            return True, f"Success: '{asset_name}' successfully assigned to {employee}."

    assets.append({
        "asset_name": asset_name,
        "category": category,
        "assigned_to": employee,
        "status": "ASSIGNED"
    })
    save_assets(assets)
    return True, f"Success: New asset '{asset_name}' created and assigned to {employee}."


def return_asset_core(asset_name: str) -> tuple[bool, str]:
    assets = load_assets()
    for item in assets:
        if item.get("asset_name", "").lower() == asset_name.lower():
            if item.get("status", "").upper() != "ASSIGNED":
                return False, f"Notice: Asset '{asset_name}' is not currently assigned."
            item["assigned_to"] = ""
            item["status"] = "AVAILABLE"
            save_assets(assets)
            return True, f"Success: '{asset_name}' has been returned to inventory."
    return False, f"Error: Asset '{asset_name}' was not found in inventory."


def export_report_core() -> tuple[bool, str]:
    assets = load_assets()
    missing_or_assigned = [a for a in assets if a.get("status", "").upper() == "ASSIGNED"]

    try:
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            f.write("=== ASSETS CURRENTLY ASSIGNED / OUT OF INVENTORY ===\n\n")
            if not missing_or_assigned:
                f.write("All assets are currently in stock.\n")
            else:
                for item in missing_or_assigned:
                    f.write(f"- Asset: {item['asset_name']} | Category: {item['category']} | Held by: {item['assigned_to']}\n")
        return True, f"Success: Report successfully exported to '{REPORT_PATH.name}'."
    except OSError as e:
        return False, f"Error exporting report: {e}"

