"""Storage & File parsing layer for raw test logs and report export.

Strictly adheres to safe cross-platform file handling rules:
- Uses pathlib.Path
- Context managers (with open)
- Explicit UTF-8 encoding
- Checks for file existence and handles exceptions gracefully
"""

import csv
import re
from pathlib import Path
from typing import List
from log_models import LogEntry, RunStatistics


def resolve_safe_path(user_input_path: str, default_dir: Path) -> Path:
    """Safely resolves user path against default directory if relative."""
    clean_str = user_input_path.strip().strip("'\"")
    raw_path = Path(clean_str)
    if raw_path.is_absolute():
        return raw_path
    return (default_dir / raw_path).resolve()


def _parse_csv_logs(file_path: Path) -> List[LogEntry]:
    entries: List[LogEntry] = []
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row_idx, row in enumerate(reader, start=2):
            try:
                # Support case-insensitive key names
                row_lower = {k.strip().lower(): (v.strip() if v else "") for k, v in row.items() if k}
                timestamp = row_lower.get("timestamp", "")
                test_name = row_lower.get("test_name", row_lower.get("test", f"test_{row_idx}"))
                status = row_lower.get("status", "UNKNOWN").upper()
                duration_str = row_lower.get("duration_sec", row_lower.get("duration", "0"))
                try:
                    duration = float(duration_str)
                except ValueError:
                    duration = 0.0
                severity = row_lower.get("severity", "INFO").upper()
                message = row_lower.get("message", row_lower.get("error", ""))

                entries.append(LogEntry(
                    timestamp=timestamp,
                    test_name=test_name,
                    status=status,
                    duration_sec=duration,
                    severity=severity,
                    message=message
                ))
            except Exception:
                continue
    return entries


def _parse_txt_logs(file_path: Path) -> List[LogEntry]:
    """Parses standard structured log text lines:
    e.g. '2026-11-11 12:00:00 [ERROR] test_login - Duration: 1.25s - Status: FAILED - message...'
    or comma/pipe separated lines.
    """
    entries: List[LogEntry] = []
    # Regex fallback for semi-structured log line
    pattern = re.compile(
        r"^(?P<timestamp>[\d\-: ]+)?\s*(?:\[(?P<severity>[A-Z]+)\])?\s*(?P<test_name>[\w\-.]+)?\s*[-|]?\s*(?:Duration:\s*(?P<duration>[\d.]+)s?)?\s*[-|]?\s*(?:Status:\s*(?P<status>[A-Z]+))?\s*[-|]?\s*(?P<message>.*)$",
        re.IGNORECASE
    )

    with open(file_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, start=1):
            line_str = line.strip()
            if not line_str or line_str.startswith("#"):
                continue

            match = pattern.match(line_str)
            if match:
                data = match.groupdict()
                duration = 0.0
                if data.get("duration"):
                    try:
                        duration = float(data["duration"])
                    except ValueError:
                        duration = 0.0

                entries.append(LogEntry(
                    timestamp=(data.get("timestamp") or "").strip(),
                    test_name=(data.get("test_name") or f"test_{idx}").strip(),
                    status=(data.get("status") or "UNKNOWN").upper().strip(),
                    duration_sec=duration,
                    severity=(data.get("severity") or "INFO").upper().strip(),
                    message=(data.get("message") or "").strip()
                ))
            else:
                # General fallback: treat line as message
                entries.append(LogEntry(
                    timestamp="",
                    test_name=f"test_{idx}",
                    status="UNKNOWN",
                    duration_sec=0.0,
                    severity="INFO",
                    message=line_str
                ))
    return entries


def load_log_file(file_path: Path) -> List[LogEntry]:
    """Loads and parses log entries from either CSV or TXT file."""
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    suffix = file_path.suffix.lower()
    if suffix == ".csv":
        return _parse_csv_logs(file_path)
    return _parse_txt_logs(file_path)


def export_report_csv(file_path: Path, stats: RunStatistics, filtered_errors: List[LogEntry]) -> None:
    """Exports summary and error details to a CSV file."""
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["=== TEST EXECUTION SUMMARY ==="])
        writer.writerow(["Total Tests", stats.total_tests])
        writer.writerow(["Passed", stats.passed_count])
        writer.writerow(["Failed", stats.failed_count])
        writer.writerow(["Other", stats.other_count])
        writer.writerow(["Pass Rate (%)", f"{stats.pass_rate_pct:.2f}%"])
        writer.writerow(["Avg Duration (s)", f"{stats.avg_duration_sec:.2f}"])
        writer.writerow(["Min Duration (s)", f"{stats.min_duration_sec:.2f}"])
        writer.writerow(["Max Duration (s)", f"{stats.max_duration_sec:.2f}"])
        writer.writerow([])
        writer.writerow(["=== FILTERED ERROR / WARNING DETAILS ==="])
        writer.writerow(["Timestamp", "Test Name", "Status", "Duration (s)", "Severity", "Message"])
        for err in filtered_errors:
            writer.writerow([err.timestamp, err.test_name, err.status, err.duration_sec, err.severity, err.message])


def export_report_txt(file_path: Path, stats: RunStatistics, filtered_errors: List[LogEntry]) -> None:
    """Exports a human-readable summary report to a TXT file."""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("           TEST EXECUTION SUMMARY REPORT\n")
        f.write("=" * 60 + "\n")
        f.write(f"Total Tests Run   : {stats.total_tests}\n")
        f.write(f"Passed Tests      : {stats.passed_count}\n")
        f.write(f"Failed Tests      : {stats.failed_count}\n")
        f.write(f"Other Tests       : {stats.other_count}\n")
        f.write(f"Pass Rate         : {stats.pass_rate_pct:.2f}%\n")
        f.write(f"Average Duration  : {stats.avg_duration_sec:.2f}s\n")
        f.write(f"Min Duration      : {stats.min_duration_sec:.2f}s\n")
        f.write(f"Max Duration      : {stats.max_duration_sec:.2f}s\n")
        f.write("=" * 60 + "\n\n")

        f.write("--- Filtered Errors & Warnings ---\n")
        if not filtered_errors:
            f.write("No matching error or warning entries found.\n")
        else:
            for idx, entry in enumerate(filtered_errors, start=1):
                f.write(f"[{idx}] [{entry.severity}] {entry.test_name} (Status: {entry.status}, Duration: {entry.duration_sec}s)\n")
                if entry.timestamp:
                    f.write(f"    Time   : {entry.timestamp}\n")
                if entry.message:
                    f.write(f"    Message: {entry.message}\n")
                f.write("-" * 50 + "\n")

