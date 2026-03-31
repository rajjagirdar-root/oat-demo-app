# Task Tracker

A simple command-line task tracker built in Python. Tasks are stored locally in a JSON file, making it lightweight and dependency-free.

## Features

- Add tasks with a description
- List all tasks with their completion status
- Mark tasks as done
- Delete tasks
- No external dependencies — pure Python standard library

## Getting Started

### Prerequisites

- Python 3.6 or higher

### Installation

Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/rajjagirdar-root/oat-demo-app.git
cd oat-demo-app
```

No additional packages need to be installed.

### Quick Start

```bash
# Add your first task
python3 tracker.py add "Buy groceries"

# List all tasks
python3 tracker.py list

# Mark a task as done (use the task ID shown in the list)
python3 tracker.py done 1

# Delete a task
python3 tracker.py delete 1
```

## Usage

### Commands

| Command | Description | Example |
|---|---|---|
| `add <description>` | Add a new task | `python3 tracker.py add "Write unit tests"` |
| `list` | List all tasks with status | `python3 tracker.py list` |
| `done <id>` | Mark a task as complete | `python3 tracker.py done 2` |
| `delete <id>` | Delete a task | `python3 tracker.py delete 3` |

### Example Session

```bash
$ python3 tracker.py add "Buy groceries"
Added: Buy groceries

$ python3 tracker.py add "Write unit tests"
Added: Write unit tests

$ python3 tracker.py add "Read book"
Added: Read book

$ python3 tracker.py list
  [ ] 1. Buy groceries
  [ ] 2. Write unit tests
  [ ] 3. Read book

$ python3 tracker.py done 1
Done: Buy groceries

$ python3 tracker.py list
  [✓] 1. Buy groceries
  [ ] 2. Write unit tests
  [ ] 3. Read book

$ python3 tracker.py delete 2
Deleted task 2

$ python3 tracker.py list
  [✓] 1. Buy groceries
  [ ] 3. Read book
```

## Architecture

```
oat-demo-app/
├── tracker.py      # CLI entry point and core task operations
├── utils.py        # Shared utility functions
└── tasks.json      # Auto-generated task storage (created on first use)
```

### Module Overview

#### `tracker.py`

The main application file. Handles CLI argument parsing and delegates to task operation functions:

- `load_tasks()` — Reads `tasks.json` from disk; returns an empty list if the file doesn't exist yet
- `save_tasks(tasks)` — Persists the task list to `tasks.json` with pretty-print formatting
- `add_task(description)` — Creates a new task with an auto-incremented ID and `done: false`
- `list_tasks()` — Prints all tasks, prefixing each with `[✓]` (done) or `[ ]` (pending)
- `complete_task(task_id)` — Finds a task by ID and sets `done: true`
- `delete_task(task_id)` — Filters out the task with the given ID and saves the result

#### `utils.py`

Reusable helper functions:

- `format_date(dt=None)` — Returns a formatted date string (`YYYY-MM-DD HH:MM`); defaults to now
- `truncate(text, max_len=50)` — Truncates long strings with a `...` suffix
- `confirm(prompt)` — Prompts the user for a yes/no confirmation; returns a boolean

### Data Format

Tasks are stored in `tasks.json` as a JSON array. Each task object has the following shape:

```json
[
  {
    "id": 1,
    "description": "Buy groceries",
    "done": false
  },
  {
    "id": 2,
    "description": "Write unit tests",
    "done": true
  }
]
```

### Data Flow

```
CLI args (sys.argv)
       │
       ▼
  tracker.py         Parses command and arguments
       │
       ▼
 Task function        add_task / list_tasks / complete_task / delete_task
       │
       ▼
  tasks.json          JSON file on disk (read + written on every operation)
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m "Add my feature"`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

## License

This project is open source and available under the [MIT License](LICENSE).
