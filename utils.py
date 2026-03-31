"""Utility functions for the task tracker."""
import datetime

def format_date(dt=None):
    if dt is None:
        dt = datetime.datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M")

def truncate(text, max_len=50):
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."

def confirm(prompt):
    response = input(f"{prompt} (y/n): ")
    return response.lower() in ("y", "yes")
