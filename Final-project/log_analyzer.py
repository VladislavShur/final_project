"""CLI Interface for Test Log Analyzer & Exporter."""

import sys
from pathlib import Path
from log_models import RunStatistics
from log_storage import resolve_safe_path
from analyzer_service import LogAnalyzerService

BASE_DIR = Path(__file__).resolve().parent


def display_stats(stats: RunStatistics) -> None:
    print("\n" + "=" * 45)
    print("         TEST EXECUTION STATISTICS")
    print("=" * 45)
    print(f"Total Tests Run       : {stats.total_tests}")
    print(f"Passed Tests          : {stats.passed_count}")
    print(f"Failed Tests          : {stats.failed_count}")
    print(f"Other (Skipped/etc.)  : {stats.other_count}")
    print(f"Pass Rate             : {stats.pass_rate_pct:.2f}%")
    print("-" * 45)
    print(f"Average Duration      : {stats.avg_duration_sec:.2f} seconds")
    print(f"Min Duration          : {stats.min_duration_sec:.2f} seconds")
    print(f"Max Duration          : {stats.max_duration_sec:.2f} seconds")
    print("=" * 45)


def handle_load_file(service: LogAnalyzerService) -> None:
    print("\n[Option 1: Load Log File]")
    user_input = input("Enter path to CSV/TXT log file: ").strip()
    if not user_input:
        print("Error: Path cannot be empty.")
        return

    safe_path = resolve_safe_path(user_input, BASE_DIR)
    try:
        count = service.load_file(safe_path)
        print(f"Success: Successfully loaded {count} log entries from '{safe_path.name}'.")
    except FileNotFoundError:
        print(f"Error: File not found at '{safe_path}'.")
    except Exception as err:
        print(f"Error loading file: {err}")


def handle_show_stats(service: LogAnalyzerService) -> None:
    if not service.is_loaded:
        print("\nNotice: No log file loaded yet. Please use Option 1 first.")
        return

    stats = service.compute_statistics()
    display_stats(stats)


def handle_filter_errors(service: LogAnalyzerService) -> None:
    if not service.is_loaded:
        print("\nNotice: No log file loaded yet. Please use Option 1 first.")
        return

    print("\n[Option 3: Filter Errors by Severity]")
    print("Select severity level to filter:")
    print("  1. ERROR only")
    print("  2. WARNING only")
    print("  3. Both ERROR and WARNING")
    choice = input("Choice (1-3) [default: 3]: ").strip()

    if choice == "1":
        severities = ["ERROR", "CRITICAL"]
    elif choice == "2":
        severities = ["WARNING"]
    else:
        severities = ["ERROR", "CRITICAL", "WARNING"]

    results = service.filter_by_severity(severities)
    print(f"\nFound {len(results)} matching entries:")
    if not results:
        print("  None found.")
        return

    print(f"{'#':<4} | {'Severity':<8} | {'Test Name':<28} | {'Status':<8} | {'Message'}")
    print("-" * 75)
    for idx, r in enumerate(results, start=1):
        msg_preview = (r.message[:35] + "...") if len(r.message) > 35 else r.message
        print(f"{idx:<4} | {r.severity:<8} | {r.test_name:<28} | {r.status:<8} | {msg_preview}")


def handle_export_report(service: LogAnalyzerService) -> None:
    if not service.is_loaded:
        print("\nNotice: No log file loaded yet. Please use Option 1 first.")
        return

    print("\n[Option 4: Export Processed Report]")
    export_filename = input("Enter output filename (e.g., summary_report.txt or report.csv): ").strip()
    if not export_filename:
        export_filename = "summary_report.txt"

    target_path = resolve_safe_path(export_filename, BASE_DIR)

    print("Include in error breakdown:")
    print("  1. All issues (ERROR & WARNING)")
    print("  2. ERROR only")
    choice = input("Choice (1-2) [default: 1]: ").strip()
    filter_list = ["ERROR", "CRITICAL"] if choice == "2" else ["ERROR", "CRITICAL", "WARNING"]

    try:
        service.export_report(target_path, filter_list)
        print(f"Success: Report successfully exported to '{target_path}'.")
    except Exception as err:
        print(f"Error during export: {err}")


def run_cli() -> None:
    service = LogAnalyzerService()

    # If a sample file exists in current directory, inform user
    sample_csv = BASE_DIR / "sample_test_logs.csv"
    if sample_csv.exists():
        try:
            service.load_file(sample_csv)
            print(f"(Auto-loaded default sample logs: {sample_csv.name})")
        except Exception:
            pass

    menu_text = (
        "\n=========================================\n"
        "  Test Log Analyzer & Exporter (CLI)\n"
        "=========================================\n"
        "1. Load log file from path\n"
        "2. Display run statistics (Passed/Failed/Durations)\n"
        "3. Filter errors by severity (ERROR / WARNING)\n"
        "4. Export processed summary report (CSV / TXT)\n"
        "5. Exit\n"
        "Select an option (1-5): "
    )

    while True:
        try:
            choice = input(menu_text).strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting analyzer...")
            break

        if choice == "1":
            handle_load_file(service)
        elif choice == "2":
            handle_show_stats(service)
        elif choice == "3":
            handle_filter_errors(service)
        elif choice == "4":
            handle_export_report(service)
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid selection. Please enter a valid number (1-5).")


if __name__ == "__main__":
    run_cli()

