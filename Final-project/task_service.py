"""Business logic layer: Task entity and TaskService operations."""

from dataclasses import dataclass
from typing import List, Dict, Optional
from storage import load_tasks_from_file, save_tasks_to_file

VALID_PRIORITIES = {"Low", "Medium", "High"}
VALID_STATUSES = {"Pending", "In Progress", "Completed"}


@dataclass
class Task:
    name: str
    priority: str = "Medium"
    status: str = "Pending"

    def to_dict(self) -> Dict[str, str]:
        return {
            "name": self.name,
            "priority": self.priority,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "Task":
        return cls(
            name=data.get("name", ""),
            priority=data.get("priority", "Medium") or "Medium",
            status=data.get("status", "Pending") or "Pending"
        )


class TaskService:
    def __init__(self) -> None:
        self._tasks: List[Task] = []

    @property
    def tasks(self) -> List[Task]:
        return list(self._tasks)

    def add_task(self, name: str, priority: str = "Medium") -> Task:
        name_clean = name.strip()
        if not name_clean:
            raise ValueError("Task name cannot be empty.")

        priority_cap = priority.strip().capitalize()
        if priority_cap not in VALID_PRIORITIES:
            raise ValueError(f"Invalid priority '{priority}'. Allowed: {', '.join(sorted(VALID_PRIORITIES))}")

        new_task = Task(name=name_clean, priority=priority_cap, status="Pending")
        self._tasks.append(new_task)
        return new_task

    def update_task_status(self, index: int, new_status: str) -> Task:
        if index < 0 or index >= len(self._tasks):
            raise IndexError("Task index out of range.")
        status_cap = new_status.strip().title()
        if status_cap not in VALID_STATUSES:
            raise ValueError(f"Invalid status '{new_status}'. Allowed: {', '.join(sorted(VALID_STATUSES))}")
        self._tasks[index].status = status_cap
        return self._tasks[index]

    def load_tasks(self) -> int:
        raw_list = load_tasks_from_file()
        self._tasks = [Task.from_dict(row) for row in raw_list]
        return len(self._tasks)

    def save_tasks(self) -> int:
        save_tasks_to_file([task.to_dict() for task in self._tasks])
        return len(self._tasks)

