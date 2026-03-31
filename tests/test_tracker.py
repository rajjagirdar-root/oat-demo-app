"""Tests for tracker.py"""
import json
import os
import sys
import pytest
from unittest.mock import patch


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def isolated_tasks_file(tmp_path, monkeypatch):
    """Redirect TASKS_FILE to a temp directory for every test."""
    import tracker
    tasks_file = str(tmp_path / "tasks.json")
    monkeypatch.setattr(tracker, "TASKS_FILE", tasks_file)
    return tasks_file


# ---------------------------------------------------------------------------
# load_tasks
# ---------------------------------------------------------------------------

class TestLoadTasks:
    def test_returns_empty_list_when_no_file(self, isolated_tasks_file):
        import tracker
        assert tracker.load_tasks() == []

    def test_returns_tasks_from_file(self, isolated_tasks_file):
        import tracker
        tasks = [{"id": 1, "description": "Test", "done": False}]
        with open(isolated_tasks_file, "w") as f:
            json.dump(tasks, f)
        assert tracker.load_tasks() == tasks

    def test_returns_multiple_tasks(self, isolated_tasks_file):
        import tracker
        tasks = [
            {"id": 1, "description": "First", "done": False},
            {"id": 2, "description": "Second", "done": True},
        ]
        with open(isolated_tasks_file, "w") as f:
            json.dump(tasks, f)
        assert tracker.load_tasks() == tasks

    def test_returns_empty_list_from_empty_array_file(self, isolated_tasks_file):
        import tracker
        with open(isolated_tasks_file, "w") as f:
            json.dump([], f)
        assert tracker.load_tasks() == []

    def test_invalid_json_exits(self, isolated_tasks_file, capsys):
        import tracker
        with open(isolated_tasks_file, "w") as f:
            f.write("not valid json {{{")
        with pytest.raises(SystemExit):
            tracker.load_tasks()
        assert "invalid JSON" in capsys.readouterr().out

    def test_corrupted_non_list_returns_empty(self, isolated_tasks_file, capsys):
        import tracker
        with open(isolated_tasks_file, "w") as f:
            json.dump({"not": "a list"}, f)
        result = tracker.load_tasks()
        assert result == []
        assert "corrupted" in capsys.readouterr().out

    def test_os_error_exits(self, isolated_tasks_file, capsys):
        import tracker
        with patch("builtins.open", side_effect=OSError("permission denied")):
            with patch("os.path.exists", return_value=True):
                with pytest.raises(SystemExit):
                    tracker.load_tasks()
        assert "Could not read" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# save_tasks
# ---------------------------------------------------------------------------

class TestSaveTasks:
    def test_creates_file(self, isolated_tasks_file):
        import tracker
        tracker.save_tasks([{"id": 1, "description": "Task", "done": False}])
        assert os.path.exists(isolated_tasks_file)

    def test_saved_content_is_valid_json(self, isolated_tasks_file):
        import tracker
        tasks = [{"id": 1, "description": "Task", "done": False}]
        tracker.save_tasks(tasks)
        with open(isolated_tasks_file) as f:
            assert json.load(f) == tasks

    def test_saves_empty_list(self, isolated_tasks_file):
        import tracker
        tracker.save_tasks([])
        with open(isolated_tasks_file) as f:
            assert json.load(f) == []

    def test_overwrites_existing_file(self, isolated_tasks_file):
        import tracker
        tracker.save_tasks([{"id": 1, "description": "Old", "done": False}])
        tracker.save_tasks([{"id": 1, "description": "New", "done": True}])
        with open(isolated_tasks_file) as f:
            assert json.load(f)[0]["description"] == "New"

    def test_roundtrip(self, isolated_tasks_file):
        import tracker
        tasks = [
            {"id": 1, "description": "Alpha", "done": False},
            {"id": 2, "description": "Beta", "done": True},
        ]
        tracker.save_tasks(tasks)
        assert tracker.load_tasks() == tasks

    def test_os_error_exits(self, isolated_tasks_file, capsys):
        import tracker
        with patch("builtins.open", side_effect=OSError("disk full")):
            with pytest.raises(SystemExit):
                tracker.save_tasks([])
        assert "Could not save" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# validate_description
# ---------------------------------------------------------------------------

class TestValidateDescription:
    def test_valid_description(self):
        import tracker
        assert tracker.validate_description("Buy milk") == "Buy milk"

    def test_strips_whitespace(self):
        import tracker
        assert tracker.validate_description("  hello  ") == "hello"

    def test_empty_string_exits(self, capsys):
        import tracker
        with pytest.raises(SystemExit):
            tracker.validate_description("")
        assert "empty" in capsys.readouterr().out

    def test_whitespace_only_exits(self, capsys):
        import tracker
        with pytest.raises(SystemExit):
            tracker.validate_description("   ")
        assert "empty" in capsys.readouterr().out

    def test_exactly_max_length_ok(self):
        import tracker
        desc = "a" * tracker.MAX_DESCRIPTION_LENGTH
        assert tracker.validate_description(desc) == desc

    def test_over_max_length_exits(self, capsys):
        import tracker
        desc = "a" * (tracker.MAX_DESCRIPTION_LENGTH + 1)
        with pytest.raises(SystemExit):
            tracker.validate_description(desc)
        assert "too long" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# validate_task_id
# ---------------------------------------------------------------------------

class TestValidateTaskId:
    def test_valid_integer_string(self):
        import tracker
        assert tracker.validate_task_id("5") == 5

    def test_non_integer_exits(self, capsys):
        import tracker
        with pytest.raises(SystemExit):
            tracker.validate_task_id("abc")
        assert "not a valid task ID" in capsys.readouterr().out

    def test_zero_exits(self, capsys):
        import tracker
        with pytest.raises(SystemExit):
            tracker.validate_task_id("0")
        assert "positive integer" in capsys.readouterr().out

    def test_negative_exits(self, capsys):
        import tracker
        with pytest.raises(SystemExit):
            tracker.validate_task_id("-1")
        assert "positive integer" in capsys.readouterr().out

    def test_float_string_exits(self, capsys):
        import tracker
        with pytest.raises(SystemExit):
            tracker.validate_task_id("1.5")

    def test_large_valid_id(self):
        import tracker
        assert tracker.validate_task_id("9999") == 9999


# ---------------------------------------------------------------------------
# add_task
# ---------------------------------------------------------------------------

class TestAddTask:
    def test_adds_task_to_empty_list(self, isolated_tasks_file, capsys):
        import tracker
        tracker.add_task("Buy milk")
        tasks = tracker.load_tasks()
        assert len(tasks) == 1
        assert tasks[0]["description"] == "Buy milk"
        assert tasks[0]["done"] is False
        assert tasks[0]["id"] == 1

    def test_id_is_max_plus_one(self, isolated_tasks_file, capsys):
        import tracker
        tracker.add_task("First")
        tracker.add_task("Second")
        tasks = tracker.load_tasks()
        assert tasks[0]["id"] == 1
        assert tasks[1]["id"] == 2

    def test_prints_added_message(self, isolated_tasks_file, capsys):
        import tracker
        tracker.add_task("Walk the dog")
        assert "Walk the dog" in capsys.readouterr().out

    def test_adds_multiple_tasks(self, isolated_tasks_file, capsys):
        import tracker
        tracker.add_task("Task A")
        tracker.add_task("Task B")
        tracker.add_task("Task C")
        assert len(tracker.load_tasks()) == 3

    def test_new_task_is_not_done(self, isolated_tasks_file, capsys):
        import tracker
        tracker.add_task("Test task")
        assert tracker.load_tasks()[0]["done"] is False

    def test_empty_description_exits(self, isolated_tasks_file, capsys):
        import tracker
        with pytest.raises(SystemExit):
            tracker.add_task("")

    def test_description_stripped(self, isolated_tasks_file, capsys):
        import tracker
        tracker.add_task("  padded  ")
        assert tracker.load_tasks()[0]["description"] == "padded"

    def test_description_with_special_chars(self, isolated_tasks_file, capsys):
        import tracker
        desc = 'Task with "quotes" & <special> chars'
        tracker.add_task(desc)
        assert tracker.load_tasks()[0]["description"] == desc

    def test_id_computed_from_max_not_count(self, isolated_tasks_file, capsys):
        import tracker
        tasks = [{"id": 5, "description": "existing", "done": False}]
        with open(isolated_tasks_file, "w") as f:
            json.dump(tasks, f)
        tracker.add_task("New task")
        loaded = tracker.load_tasks()
        assert loaded[-1]["id"] == 6


# ---------------------------------------------------------------------------
# list_tasks
# ---------------------------------------------------------------------------

class TestListTasks:
    def test_prints_no_tasks_when_empty(self, isolated_tasks_file, capsys):
        import tracker
        tracker.list_tasks()
        assert "No tasks yet" in capsys.readouterr().out

    def test_prints_task_description(self, isolated_tasks_file, capsys):
        import tracker
        tracker.add_task("Do laundry")
        capsys.readouterr()
        tracker.list_tasks()
        assert "Do laundry" in capsys.readouterr().out

    def test_prints_done_status_checkmark(self, isolated_tasks_file, capsys):
        import tracker
        tasks = [{"id": 1, "description": "Done", "done": True}]
        with open(isolated_tasks_file, "w") as f:
            json.dump(tasks, f)
        tracker.list_tasks()
        assert "✓" in capsys.readouterr().out

    def test_prints_undone_status(self, isolated_tasks_file, capsys):
        import tracker
        tracker.add_task("Pending task")
        capsys.readouterr()
        tracker.list_tasks()
        assert "[ ]" in capsys.readouterr().out

    def test_prints_all_tasks(self, isolated_tasks_file, capsys):
        import tracker
        tracker.add_task("Alpha")
        tracker.add_task("Beta")
        tracker.add_task("Gamma")
        capsys.readouterr()
        tracker.list_tasks()
        out = capsys.readouterr().out
        assert "Alpha" in out
        assert "Beta" in out
        assert "Gamma" in out

    def test_prints_task_ids(self, isolated_tasks_file, capsys):
        import tracker
        tracker.add_task("Task one")
        tracker.add_task("Task two")
        capsys.readouterr()
        tracker.list_tasks()
        out = capsys.readouterr().out
        assert "1." in out
        assert "2." in out


# ---------------------------------------------------------------------------
# complete_task
# ---------------------------------------------------------------------------

class TestCompleteTask:
    def test_marks_task_done(self, isolated_tasks_file, capsys):
        import tracker
        tracker.add_task("Finish report")
        capsys.readouterr()
        tracker.complete_task(1)
        assert tracker.load_tasks()[0]["done"] is True

    def test_prints_done_message(self, isolated_tasks_file, capsys):
        import tracker
        tracker.add_task("Clean kitchen")
        capsys.readouterr()
        tracker.complete_task(1)
        assert "Clean kitchen" in capsys.readouterr().out

    def test_not_found_exits(self, isolated_tasks_file, capsys):
        import tracker
        with pytest.raises(SystemExit):
            tracker.complete_task(99)
        assert "not found" in capsys.readouterr().out.lower()

    def test_only_target_task_marked_done(self, isolated_tasks_file, capsys):
        import tracker
        tracker.add_task("Task A")
        tracker.add_task("Task B")
        tracker.add_task("Task C")
        capsys.readouterr()
        tracker.complete_task(2)
        tasks = tracker.load_tasks()
        assert tasks[0]["done"] is False
        assert tasks[1]["done"] is True
        assert tasks[2]["done"] is False

    def test_already_done_prints_message(self, isolated_tasks_file, capsys):
        import tracker
        tasks = [{"id": 1, "description": "Already done", "done": True}]
        with open(isolated_tasks_file, "w") as f:
            json.dump(tasks, f)
        tracker.complete_task(1)
        assert "already" in capsys.readouterr().out.lower()

    def test_complete_task_with_no_tasks_exits(self, isolated_tasks_file, capsys):
        import tracker
        with pytest.raises(SystemExit):
            tracker.complete_task(1)


# ---------------------------------------------------------------------------
# delete_task
# ---------------------------------------------------------------------------

class TestDeleteTask:
    def test_removes_task_from_list(self, isolated_tasks_file, capsys):
        import tracker
        tracker.add_task("Temporary")
        capsys.readouterr()
        tracker.delete_task(1)
        assert tracker.load_tasks() == []

    def test_prints_deleted_message(self, isolated_tasks_file, capsys):
        import tracker
        tracker.add_task("Remove me")
        capsys.readouterr()
        tracker.delete_task(1)
        assert "1" in capsys.readouterr().out

    def test_deletes_only_target_task(self, isolated_tasks_file, capsys):
        import tracker
        tracker.add_task("Keep A")
        tracker.add_task("Delete B")
        tracker.add_task("Keep C")
        capsys.readouterr()
        tracker.delete_task(2)
        descriptions = [t["description"] for t in tracker.load_tasks()]
        assert "Keep A" in descriptions
        assert "Delete B" not in descriptions
        assert "Keep C" in descriptions

    def test_delete_nonexistent_exits(self, isolated_tasks_file, capsys):
        import tracker
        tracker.add_task("Existing")
        capsys.readouterr()
        with pytest.raises(SystemExit):
            tracker.delete_task(999)
        assert "not found" in capsys.readouterr().out.lower()

    def test_delete_from_empty_list_exits(self, isolated_tasks_file, capsys):
        import tracker
        with pytest.raises(SystemExit):
            tracker.delete_task(1)


# ---------------------------------------------------------------------------
# CLI entry point (__main__ dispatch — replicated with TASKS_FILE patched)
# ---------------------------------------------------------------------------

def _run_cli(args, isolated_tasks_file):
    import tracker

    argv = ["tracker.py"] + args
    with patch.object(sys, "argv", argv):
        with patch.object(tracker, "TASKS_FILE", isolated_tasks_file):
            if len(sys.argv) < 2:
                print(tracker.USAGE)
                return 1

            cmd = sys.argv[1]

            if cmd == "add":
                if len(sys.argv) < 3:
                    print("Error: 'add' requires a description.")
                    return 1
                try:
                    tracker.add_task(" ".join(sys.argv[2:]))
                except SystemExit as e:
                    return e.code

            elif cmd == "list":
                tracker.list_tasks()

            elif cmd == "done":
                if len(sys.argv) < 3:
                    print("Error: 'done' requires a task ID.")
                    return 1
                try:
                    tracker.complete_task(tracker.validate_task_id(sys.argv[2]))
                except SystemExit as e:
                    return e.code

            elif cmd == "delete":
                if len(sys.argv) < 3:
                    print("Error: 'delete' requires a task ID.")
                    return 1
                try:
                    tracker.delete_task(tracker.validate_task_id(sys.argv[2]))
                except SystemExit as e:
                    return e.code

            else:
                print(f"Error: Unknown command '{cmd}'.")
                print(tracker.USAGE)
                return 1

    return 0


class TestCLIEntryPoint:
    def test_no_args_returns_1(self, isolated_tasks_file, capsys):
        assert _run_cli([], isolated_tasks_file) == 1

    def test_no_args_prints_usage(self, isolated_tasks_file, capsys):
        _run_cli([], isolated_tasks_file)
        assert "Usage" in capsys.readouterr().out

    def test_add_command(self, isolated_tasks_file, capsys):
        import tracker
        _run_cli(["add", "New", "Task"], isolated_tasks_file)
        assert tracker.load_tasks()[0]["description"] == "New Task"

    def test_list_command(self, isolated_tasks_file, capsys):
        import tracker
        tracker.add_task("List me")
        capsys.readouterr()
        _run_cli(["list"], isolated_tasks_file)
        assert "List me" in capsys.readouterr().out

    def test_done_command(self, isolated_tasks_file, capsys):
        import tracker
        tracker.add_task("Mark done")
        capsys.readouterr()
        _run_cli(["done", "1"], isolated_tasks_file)
        assert tracker.load_tasks()[0]["done"] is True

    def test_delete_command(self, isolated_tasks_file, capsys):
        import tracker
        tracker.add_task("Delete me")
        capsys.readouterr()
        _run_cli(["delete", "1"], isolated_tasks_file)
        assert tracker.load_tasks() == []

    def test_unknown_command(self, isolated_tasks_file, capsys):
        assert _run_cli(["foobar"], isolated_tasks_file) == 1
        assert "Unknown command" in capsys.readouterr().out

    def test_add_without_args_returns_1(self, isolated_tasks_file, capsys):
        assert _run_cli(["add"], isolated_tasks_file) == 1

    def test_done_without_args_returns_1(self, isolated_tasks_file, capsys):
        assert _run_cli(["done"], isolated_tasks_file) == 1

    def test_delete_without_args_returns_1(self, isolated_tasks_file, capsys):
        assert _run_cli(["delete"], isolated_tasks_file) == 1

    def test_done_invalid_id(self, isolated_tasks_file, capsys):
        assert _run_cli(["done", "abc"], isolated_tasks_file) == 1

    def test_delete_invalid_id(self, isolated_tasks_file, capsys):
        assert _run_cli(["delete", "abc"], isolated_tasks_file) == 1
