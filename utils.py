"""Utility functions for the task tracker."""
import datetime


def format_date(dt=None):
    if dt is not None and not isinstance(dt, datetime.datetime):
        raise TypeError(f"format_date expects a datetime object, got {type(dt).__name__}")
    if dt is None:
        dt = datetime.datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M")


def truncate(text, max_len=50):
    if not isinstance(text, str):
        raise TypeError(f"truncate expects a string, got {type(text).__name__}")
    if not isinstance(max_len, int) or max_len < 1:
        raise ValueError(f"truncate max_len must be a positive integer, got {max_len!r}")
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."


def confirm(prompt):
    if not prompt or not isinstance(prompt, str):
        raise ValueError("confirm requires a non-empty string prompt")
    try:
        response = input(f"{prompt} (y/n): ")
    except EOFError:
        return False
    return response.strip().lower() in ("y", "yes")
