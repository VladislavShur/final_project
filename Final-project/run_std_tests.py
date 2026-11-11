import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

import asset_tracker

class TestAssetTrackerSTD(unittest.TestCase):
    def setUp(self):
        # קובץ בדיקות מבודד
        self.original_data_path = asset_tracker.DATA_PATH
        self.original_report_path = asset_tracker.REPORT_PATH
        self.test_data_path = BASE_DIR / "test_assets.csv"
        self.test_report_path = BASE_DIR / "test_missing_report.txt"
        
        asset_tracker.DATA_PATH = self.test_data_path
        asset_tracker.REPORT_PATH = self.test_report_path
        
        if self.test_data_path.exists():
            self.test_data_path.unlink()
        if self.test_report_path.exists():
            self.test_report_path.unlink()

    def tearDown(self):
        if self.test_data_path.exists():
            self.test_data_path.unlink()
        if self.test_report_path.exists():
            self.test_report_path.unlink()
        asset_tracker.DATA_PATH = self.original_data_path
        asset_tracker.REPORT_PATH = self.original_report_path

    def test_tc01_display_inventory_empty_and_populated(self):
        """TC-01: הצגת מלאי הציוד כאשר הקובץ חסר ולאחר אכלוס"""
        self.assertEqual(asset_tracker.load_assets(), [])
        
        # אכלוס נתונים
        asset_tracker.assign_asset_core("Laptop Pro", "Alice")
        items = asset_tracker.load_assets()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["asset_name"], "Laptop Pro")
        self.assertEqual(items[0]["assigned_to"], "Alice")

    def test_tc02_assign_asset_happy_path(self):
        """TC-02: השאלת ציוד לעובד בהצלחה"""
        success, msg = asset_tracker.assign_asset_core("MacBook M2", "John")
        self.assertTrue(success)
        self.assertIn("assigned to John", msg)
        
        # בדיקה בקובץ
        items = asset_tracker.load_assets()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["status"], "ASSIGNED")

    def test_tc03_export_report_happy_path(self):
        """TC-03: ייצוא דוח נכסים מושאלים/חסרים לקובץ טקסט"""
        asset_tracker.assign_asset_core("Monitor 4K", "Bob")
        success, msg = asset_tracker.export_report_core()
        self.assertTrue(success)
        self.assertTrue(self.test_report_path.exists())
        
        content = self.test_report_path.read_text(encoding="utf-8")
        self.assertIn("Monitor 4K", content)
        self.assertIn("Bob", content)

    def test_tc04_bug01_prevent_double_assignment(self):
        """אימות תיקון Bug #1: מניעת כפילות שיוך של נכס תפוס"""
        # שיוך ראשון
        ok1, msg1 = asset_tracker.assign_asset_core("Laptop A", "Alice")
        self.assertTrue(ok1)
        
        # שיוך שני לאותו נכס כשהוא עדיין Assigned
        ok2, msg2 = asset_tracker.assign_asset_core("Laptop A", "Bob")
        self.assertFalse(ok2)
        self.assertIn("already ASSIGNED to Alice", msg2)
        
        # וידוא שלא נוצרה כפילות בקובץ
        items = asset_tracker.load_assets()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["assigned_to"], "Alice")

    def test_tc05_bug02_prevent_data_overwrite(self):
        """אימות תיקון Bug #2: מניעת דריסת נתונים היסטוריים בהוספת נכס חדש"""
        # הוספת 2 נכסים בזה אחר זה
        asset_tracker.assign_asset_core("Item 1", "User 1")
        asset_tracker.assign_asset_core("Item 2", "User 2")
        
        # וידוא ששני הפריטים שמורים בקובץ ללא דריסה
        items = asset_tracker.load_assets()
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["asset_name"], "Item 1")
        self.assertEqual(items[1]["asset_name"], "Item 2")

    def test_tc06_return_asset(self):
        """בדיקת החזרת ציוד ועדכון הסטטוס ל-AVAILABLE"""
        asset_tracker.assign_asset_core("Headphones", "Charlie")
        ok, msg = asset_tracker.return_asset_core("Headphones")
        self.assertTrue(ok)
        
        items = asset_tracker.load_assets()
        self.assertEqual(items[0]["status"], "AVAILABLE")
        self.assertEqual(items[0]["assigned_to"], "")

if __name__ == "__main__":
    unittest.main(verbosity=2)
