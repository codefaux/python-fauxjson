import json
import os
from pathlib import Path
from threading import Lock

import fauxlogger as _log

item_lock = Lock()
DATA_DIR = os.getenv("DATA_DIR") or "./data"


def ensure_dir(directory: str):
    if not os.path.exists(directory):
        os.makedirs(directory)


def load_item(file: str, remove_after: bool = False) -> dict | None:
    file_path = os.path.join(DATA_DIR, file)

    with item_lock:
        if os.path.exists(file_path):
            item = None
            with open(file_path, "r") as f:
                try:
                    item = json.load(f)
                except json.JSONDecodeError:
                    _log.msg(f"Failed to decode JSON '{file_path}' ; returning None.")
            if remove_after:
                os.remove(file_path)

            return item


def delete_item_file(file: str):
    file_path = os.path.join(DATA_DIR, file)

    if os.path.exists(file_path):
        os.remove(file_path)


def save_item(item, file: str, replace: bool = False, subdir: str = ""):
    _dir = os.path.join(DATA_DIR, subdir)
    file_path = os.path.join(_dir, file)

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with item_lock:
        if not replace:
            existing_items = []
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r") as f:
                        existing_items = json.load(f)
                        if not isinstance(existing_items, list):
                            _log.msg(
                                f"Warning: Expected list in {file}, got {type(existing_items)}. Overwriting."
                            )
                            existing_items = []
                except json.JSONDecodeError:
                    _log.msg(f"Warning: Failed to decode {file}. Overwriting.")

            existing_items.append(item)
        else:
            existing_items = item

        with open(file_path, "w") as f:
            json.dump(existing_items, f, indent=2)
