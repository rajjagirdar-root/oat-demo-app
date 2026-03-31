"""Simple task tracker CLI."""
import json
import sys
import os

TASKS_FILE = "tasks.json"
MAX_DESCRIPTION_LENGTH = 500


def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE) as f:
            data = json.load(f)
        if not isinstance(data, list):
            print(f"Error: {TASKS_FILE} is corrupted (expected a list). Starting fresh.")
            return []
        return data
    except json.JSONDecodeError as e:
        print(f"Error: {TASKS_FILE} contains invalid JSON: {e}")
        print("Tip: Delete or fix the file to continue.")
        sys.exit(1)
    except OSError as e:
        print(f"Error: Could not read {TASKS_FILE}: {e}")
        sys.exit(1)


def save_tasks(tasks):
    try:
        with open(TASKS_FILE, "w") as f:
            json.dump(tasks, f, indent=2)
    except OSError as e:
        print(f"Error: Could not save tasks to {TASKS_FILE}: {e}")
        sys.exit(1)


def validate_description(description):
    if not description or not description.strip():
        print("Error: Task description cannot be empty.")
        print("Usage: tracker.py add <description>")
        sys.exit(1)
    if len(description) > MAX_DESCRIPTION_LENGTH:
        print(f"Error: Task description is too long ({len(description)} chars). Maximum is {MAX_DESCRIPTION_LENGTH}.")
        sys.exit(1)
    return description.strip()


def validate_task_id(raw_id):
    try:
        task_id = int(raw_id)
    except ValueError:
        print(f"Error: '{raw_id}' is not a valid task ID. Please provide a positive integer.")
        sys.exit(1)
    if task_id <= 0:
        print(f"Error: Task ID must be a positive integer, got {task_id}.")
        sys.exit(1)
    return task_id


def add_task(description):
    description = validate_description(description)
    tasks = load_tasks()
    task_id = max((t["id"] for t in tasks), default=0) + 1
    task = {"id": task_id, "description": description, "done": False}
    tasks.append(task)
    save_tasks(tasks)
    print(f"Added task {task_id}: {description}")


def list_tasks():
    tasks = load_tasks()
    if not tasks:
        print("No tasks yet. Add one with: tracker.py add <description>")
        return
    for t in tasks:
        status = "✓" if t["done"] else " "
        print(f"  [{status}] {t['id']}. {t['description']}")


def complete_task(task_id):
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            if t["done"]:
                print(f"Task {task_id} is already marked as done.")
                return
            t["done"] = True
            save_tasks(tasks)
            print(f"Done: {t['description']}")
            return
    print(f"Error: Task {task_id} not found.")
    print("Tip: Run 'tracker.py list' to see available task IDs.")
    sys.exit(1)


def delete_task(task_id):
    tasks = load_tasks()
    original_count = len(tasks)
    filtered = [t for t in tasks if t["id"] != task_id]
    if len(filtered) == original_count:
        print(f"Error: Task {task_id} not found.")
        print("Tip: Run 'tracker.py list' to see available task IDs.")
        sys.exit(1)
    save_tasks(filtered)
    print(f"Deleted task {task_id}.")


USAGE = """Usage: tracker.py <command> [args]

Commands:
  add <description>   Add a new task
  list                List all tasks
  done <id>           Mark a task as complete
  delete <id>         Delete a task

Examples:
  tracker.py add "Buy groceries"
  tracker.py list
  tracker.py done 1
  tracker.py delete 2"""


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(USAGE)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "add":
        if len(sys.argv) < 3:
            print("Error: 'add' requires a description.")
            print("Usage: tracker.py add <description>")
            sys.exit(1)
        add_task(" ".join(sys.argv[2:]))

    elif cmd == "list":
        list_tasks()

    elif cmd == "done":
        if len(sys.argv) < 3:
            print("Error: 'done' requires a task ID.")
            print("Usage: tracker.py done <id>")
            sys.exit(1)
        complete_task(validate_task_id(sys.argv[2]))

    elif cmd == "delete":
        if len(sys.argv) < 3:
            print("Error: 'delete' requires a task ID.")
            print("Usage: tracker.py delete <id>")
            sys.exit(1)
        delete_task(validate_task_id(sys.argv[2]))

    else:
        print(f"Error: Unknown command '{cmd}'.")
        print(USAGE)
        sys.exit(1)
