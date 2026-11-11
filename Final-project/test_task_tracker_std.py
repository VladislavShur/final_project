import unittest
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

import task01

class TestTaskTrackerSTD(unittest.TestCase):
    def setUp(self):
        self.original_data_path = task01.DATA_PATH
        self.test_csv = BASE_DIR / "test_tasks_temp.csv"
        task01.DATA_PATH = self.test_csv
        task01.tasks = []
        if self.test_csv.exists():
            self.test_csv.unlink()

    def tearDown(self):
        if self.test_csv.exists():
            self.test_csv.unlink()
        task01.DATA_PATH = self.original_data_path
        task01.tasks = []

    def test_tc06_negative_read_missing_file(self):
        """TC-06: קריאה כאשר הקובץ חסר (ללא קריסה)"""
        result = task01.load_tasks()
        self.assertFalse(result)
        self.assertEqual(len(task01.tasks), 0)

    def test_tc02_add_task(self):
        """TC-02: הוספת משימה לזיכרון"""
        task01.tasks.append({
            "name": "Login Test",
            "test_suite": "Regression",
            "priority": "High",
            "status": "Pending"
        })
        self.assertEqual(len(task01.tasks), 1)
        self.assertEqual(task01.tasks[0]["name"], "Login Test")

    def test_tc04_save_and_load(self):
        """TC-04 & TC-01: שמירת משימות לקובץ וטעינתן"""
        task01.tasks.append({
            "name": "Checkout Flow",
            "test_suite": "Smoke",
            "priority": "Medium",
            "status": "In Progress"
        })
        saved = task01.save_and_exit()
        self.assertTrue(saved)
        self.assertTrue(self.test_csv.exists())

        # איפוס זיכרון וטעינה מחדש
        task01.tasks = []
        loaded = task01.load_tasks()
        self.assertTrue(loaded)
        self.assertEqual(len(task01.tasks), 1)
        self.assertEqual(task01.tasks[0]["name"], "Checkout Flow")

    def test_bug01_prevent_duplicate_accumulation(self):
        """אימות תיקון Bug #1: טעינה חוזרת לא מכפילה משימות בזיכרון"""
        # שמירת משימה בקובץ
        task01.tasks.append({
            "name": "Single Task",
            "test_suite": "Core",
            "priority": "Low",
            "status": "Pending"
        })
        task01.save_and_exit()

        # קריאה פעמיים ברציפות
        task01.load_tasks()
        task01.load_tasks()
        self.assertEqual(len(task01.tasks), 1, "הזיכרון צבר כפילויות במקום להישאר עם רשומה אחת!")

    def test_tc03_update_status(self):
        """TC-03: עדכון סטטוס משימה קיימת"""
        task01.tasks.append({
            "name": "API Auth",
            "test_suite": "Integration",
            "priority": "High",
            "status": "Pending"
        })
        task01.tasks[0]["status"] = "Done"
        self.assertEqual(task01.tasks[0]["status"], "Done")

if __name__ == "__main__":
    unittest.main(verbosity=2)
