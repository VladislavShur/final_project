"""CLI layer: user interface with robust error handling."""

from task_service import TaskService, VALID_PRIORITIES, VALID_STATUSES


def display_tasks(service: TaskService) -> None:
    tasks = service.tasks
    if not tasks:
        print("\nNo tasks currently available.")
        return

    print("\n--- Current Tasks ---")
    print(f"{'#':<4} | {'Name':<25} | {'Priority':<10} | {'Status':<12}")
    print("-" * 58)
    for idx, t in enumerate(tasks, start=1):
        print(f"{idx:<4} | {t.name:<25} | {t.priority:<10} | {t.status:<12}")


def handle_add_task(service: TaskService) -> None:
    print("\n[Add New Task]")
    name = input("Enter task name: ").strip()
    if not name:
        print("Error: Task name cannot be empty.")
        return

    allowed = "/".join(sorted(VALID_PRIORITIES))
    priority = input(f"Enter priority ({allowed}) [default: Medium]: ").strip()
    if not priority:
        priority = "Medium"

    try:
        task = service.add_task(name, priority)
        print(f"Success: Task '{task.name}' added with priority '{task.priority}'.")
    except ValueError as err:
        print(f"Error: {err}")


def handle_update_status(service: TaskService) -> None:
    display_tasks(service)
    tasks = service.tasks
    if not tasks:
        return

    raw_idx = input("\nEnter task number to update: ").strip()
    if not raw_idx.isdigit():
        print("Error: Please enter a valid number.")
        return

    index = int(raw_idx) - 1
    allowed = "/".join(sorted(VALID_STATUSES))
    new_status = input(f"Enter new status ({allowed}): ").strip()

    try:
        updated = service.update_task_status(index, new_status)
        print(f"Success: Task '{updated.name}' status changed to '{updated.status}'.")
    except (IndexError, ValueError) as err:
        print(f"Error: {err}")


def handle_load(service: TaskService) -> None:
    try:
        count = service.load_tasks()
        print(f"Success: Loaded {count} task(s) from file.")
    except RuntimeError as err:
        print(f"Failed to load tasks: {err}")


def handle_save_and_exit(service: TaskService) -> None:
    try:
        count = service.save_tasks()
        print(f"Saved {count} task(s) successfully. Goodbye!")
    except RuntimeError as err:
        print(f"Warning: Could not save tasks to file: {err}")


def run_app() -> None:
    service = TaskService()
    # Attempt initial load automatically if tasks exist
    try:
        service.load_tasks()
    except RuntimeError:
        pass

    menu_text = (
        "\n====================\n"
        " Task Manager Menu\n"
        "====================\n"
        "1. List Tasks\n"
        "2. Add Task\n"
        "3. Update Task Status\n"
        "4. Reload from File\n"
        "5. Save & Exit\n"
        "Choose an option (1-5): "
    )

    while True:
        try:
            choice = input(menu_text).strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting application...")
            break

        if choice == "1":
            display_tasks(service)
        elif choice == "2":
            handle_add_task(service)
        elif choice == "3":
            handle_update_status(service)
        elif choice == "4":
            handle_load(service)
        elif choice == "5":
            handle_save_and_exit(service)
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")


if __name__ == "__main__":
    run_app()

