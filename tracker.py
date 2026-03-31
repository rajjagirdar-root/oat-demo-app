"""Simple task tracker CLI."""
import json
import sys
import os

TASKS_FILE = "tasks.json"

def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE) as f:
        return json.load(f)

def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)

def add_task(description):
    tasks = load_tasks()
    task = {"id": len(tasks) + 1, "description": description, "done": False}
    tasks.append(task)
    save_tasks(tasks)
    print(f"Added: {description}")

def list_tasks():
    tasks = load_tasks()
    if not tasks:
        print("No tasks yet.")
        return
    for t in tasks:
        status = "✓" if t["done"] else " "
        print(f"  [{status}] {t['id']}. {t['description']}")

def complete_task(task_id):
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            t["done"] = True
            save_tasks(tasks)
            print(f"Done: {t['description']}")
            return
    print(f"Task {task_id} not found")

def delete_task(task_id):
    tasks = load_tasks()
    tasks = [t for t in tasks if t["id"] != task_id]
    save_tasks(tasks)
    print(f"Deleted task {task_id}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: tracker.py [add|list|done|delete] [args]")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "add" and len(sys.argv) > 2:
        add_task(" ".join(sys.argv[2:]))
    elif cmd == "list":
        list_tasks()
    elif cmd == "done" and len(sys.argv) > 2:
        complete_task(int(sys.argv[2]))
    elif cmd == "delete" and len(sys.argv) > 2:
        delete_task(int(sys.argv[2]))
    else:
        print("Unknown command")
