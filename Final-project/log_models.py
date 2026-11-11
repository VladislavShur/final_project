"""Data models for test log entries and summary statistics."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class LogEntry:
    timestamp: str
    test_name: str
    status: str       # PASSED, FAILED, SKIPPED, ERROR, etc.
    duration_sec: float
    severity: str     # INFO, WARNING, ERROR, CRITICAL
    message: str = ""

    @property
    def is_passed(self) -> bool:
        return self.status.upper() == "PASSED"

    @property
    def is_failed(self) -> bool:
        return self.status.upper() in {"FAILED", "FAIL", "ERROR"}


@dataclass
class RunStatistics:
    total_tests: int
    passed_count: int
    failed_count: int
    other_count: int
    avg_duration_sec: float
    min_duration_sec: float
    max_duration_sec: float
    pass_rate_pct: float

