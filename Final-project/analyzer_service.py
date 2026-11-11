"""Business logic layer for analyzing test logs and computing statistics."""

from pathlib import Path
from typing import List, Optional
from log_models import LogEntry, RunStatistics
from log_storage import load_log_file, export_report_csv, export_report_txt


class LogAnalyzerService:
    def __init__(self) -> None:
        self._entries: List[LogEntry] = []
        self._loaded_path: Optional[Path] = None

    @property
    def is_loaded(self) -> bool:
        return len(self._entries) > 0

    @property
    def loaded_path(self) -> Optional[Path]:
        return self._loaded_path

    @property
    def entries(self) -> List[LogEntry]:
        return list(self._entries)

    def load_file(self, file_path: Path) -> int:
        """Loads entries from the specified path. Raises FileNotFoundError or IOError on failure."""
        self._entries = load_log_file(file_path)
        self._loaded_path = file_path
        return len(self._entries)

    def compute_statistics(self) -> RunStatistics:
        """Computes execution counts, durations, and pass rate."""
        if not self._entries:
            return RunStatistics(
                total_tests=0,
                passed_count=0,
                failed_count=0,
                other_count=0,
                avg_duration_sec=0.0,
                min_duration_sec=0.0,
                max_duration_sec=0.0,
                pass_rate_pct=0.0
            )

        passed = sum(1 for e in self._entries if e.is_passed)
        failed = sum(1 for e in self._entries if e.is_failed)
        other = len(self._entries) - (passed + failed)

        durations = [e.duration_sec for e in self._entries if e.duration_sec > 0]
        avg_dur = sum(durations) / len(durations) if durations else 0.0
        min_dur = min(durations) if durations else 0.0
        max_dur = max(durations) if durations else 0.0
        pass_rate = (passed / len(self._entries)) * 100 if self._entries else 0.0

        return RunStatistics(
            total_tests=len(self._entries),
            passed_count=passed,
            failed_count=failed,
            other_count=other,
            avg_duration_sec=avg_dur,
            min_duration_sec=min_dur,
            max_duration_sec=max_dur,
            pass_rate_pct=pass_rate
        )

    def filter_by_severity(self, severities: List[str]) -> List[LogEntry]:
        """Filters log entries matching any of the requested severities."""
        upper_set = {s.upper().strip() for s in severities}
        return [e for e in self._entries if e.severity.upper() in upper_set]

    def export_report(self, target_path: Path, severity_filter: Optional[List[str]] = None) -> None:
        """Exports statistical summary and errors to target CSV or TXT file."""
        stats = self.compute_statistics()
        if severity_filter:
            filtered = self.filter_by_severity(severity_filter)
        else:
            filtered = self.filter_by_severity(["ERROR", "CRITICAL", "WARNING"])

        if target_path.suffix.lower() == ".csv":
            export_report_csv(target_path, stats, filtered)
        else:
            export_report_txt(target_path, stats, filtered)

