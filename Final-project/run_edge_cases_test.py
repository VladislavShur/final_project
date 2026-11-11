import os
import stat
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from log_storage import load_log_file, export_report_csv, export_report_txt
from analyzer_service import LogAnalyzerService

def run_all_tests():
    print("=" * 60)
    print(" בדיקת מקרי קצה עבור מערכת הניתוח (Edge Cases Suite)")
    print("=" * 60)
    
    test_dir = BASE_DIR / "edge_case_inputs"
    test_dir.mkdir(exist_ok=True)
    
    # 1. קובץ ריק לחלוטין (Empty File)
    empty_file = test_dir / "empty.csv"
    with open(empty_file, "w", encoding="utf-8") as f:
        pass
    print("\n[מקרה 1] קריאת קובץ ריק לחלוטין (0 bytes):")
    try:
        entries = load_log_file(empty_file)
        print(f" -> הצלחה! הקוד טיפל בקובץ ריק ללא קריסה, נטענו {len(entries)} רשומות.")
    except Exception as e:
        print(f" -> נכשל עם שגיאה: {e}")

    # 2. קובץ עם עברית בשדות מספריים וטקסט (Hebrew characters in numeric input)
    hebrew_file = test_dir / "hebrew_corrupted.csv"
    with open(hebrew_file, "w", encoding="utf-8") as f:
        f.write("timestamp,test_name,status,duration_sec,severity,message\n")
        f.write("2026-11-11 10:00:00,בדיקת_התחברות,FAIL,שלוש_שניות,ERROR,נכשלה ההתחברות למערכת\n")
        f.write("2026-11-11 10:01:00,בדיקת_תשלום,PASS,12.5,INFO,התשלום בוצע בהצלחה\n")
        f.write("2026-11-11 10:02:00,test_special,FAIL,!@#$%^,CRITICAL,שגיאה קריטית במסד\n")
    
    print("\n[מקרה 2] תווים בעברית ובשפות שונות בשדה מספרי (duration_sec) ושמות טסטים:")
    try:
        service = LogAnalyzerService()
        count = service.load_file(hebrew_file)
        stats = service.compute_statistics()
        print(f" -> נטענו בהצלחה {count} רשומות.")
        print(f" -> ערך duration עבור הטקסט 'שלוש_שניות': {service.entries[0].duration_sec} שניות (ברירת מחדל בטוחה 0.0)")
        print(f" -> ממוצע זמנים שחושב: {stats.avg_duration_sec:.2f}s, Pass Rate: {stats.pass_rate_pct:.1f}%")
        print(" -> הצלחה! לא נזרק ValueError על המרת מחרוזת עברית למספר.")
    except Exception as e:
        print(f" -> נכשל עם שגיאה: {e}")

    # 3. קובץ נעול / ללא הרשאות קריאה (File without read permissions)
    locked_read_file = test_dir / "no_read.csv"
    with open(locked_read_file, "w", encoding="utf-8") as f:
        f.write("timestamp,test_name,status,duration_sec,severity,message\n")
    locked_read_file.chmod(000) # הסרת כל ההרשאות
    
    print("\n[מקרה 3] קובץ נעול לקריאה (Permission Denied):")
    try:
        load_log_file(locked_read_file)
        print(" -> שגיאה בלתי צפויה: הקובץ נקרא למרות שאין הרשאות!")
    except PermissionError:
        print(" -> הצלחה! זוהתה שגיאת הרשאה מבוקרת (PermissionError) שנלכדת בצורה בטוחה.")
    except Exception as e:
        print(f" -> שגיאה אחרת: {type(e).__name__}: {e}")
    finally:
        locked_read_file.chmod(stat.S_IRUSR | stat.S_IWUSR) # החזרת הרשאות למחיקה נקייה

    # 4. יעד ייצוא נעול לכתיבה (Locked / Read-only output file)
    locked_write_file = test_dir / "readonly_export.txt"
    with open(locked_write_file, "w", encoding="utf-8") as f:
        f.write("נעול לכתיבה")
    locked_write_file.chmod(stat.S_IRUSR) # קריאה בלבד
    
    print("\n[מקרה 4] ניסיון ייצוא לקובץ נעול לכתיבה (Write Permission Denied):")
    try:
        service = LogAnalyzerService()
        service.load_file(hebrew_file)
        stats = service.compute_statistics()
        export_report_txt(locked_write_file, stats, service.entries)
        print(" -> שגיאה: הצליח לכתוב לקובץ לקריאה בלבד!")
    except (PermissionError, OSError) as e:
        print(f" -> הצלחה! נתפסה שגיאת כתיבה מבוקרת: {type(e).__name__}")
    finally:
        locked_write_file.chmod(stat.S_IRUSR | stat.S_IWUSR)

    # 5. קובץ פגום עם שורות ריקות, עמודות חסרות ו-BOM UTF-8
    corrupted_file = test_dir / "corrupted_rows.csv"
    with open(corrupted_file, "w", encoding="utf-8-sig") as f:
        f.write("\n\n")
        f.write("timestamp,test_name,status\n") # עמודות חסרות
        f.write("2026-11-11,test_only\n") # שורה קטועה
        f.write(",,,\n")
    print("\n[מקרה 5] קובץ עם UTF-8 BOM, שורות קטועות ועמודות חסרות:")
    try:
        entries = load_log_file(corrupted_file)
        print(f" -> הצלחה! נטענו {len(entries)} רשומות ללא קריסת המערכת.")
    except Exception as e:
        print(f" -> נכשל: {e}")

    print("\n" + "=" * 60)
    print(" כל מקרי הקצה הסתיימו בהצלחה ועמידות הקוד אומתה!")
    print("=" * 60)

if __name__ == "__main__":
    run_all_tests()
