import json
import os
from threading import Lock

import fauxlogger as _log

json_lock = Lock()
DATA_DIR = os.getenv("DATA_DIR") or "./data"


def ensure_dir(directory: str):
    if not os.path.exists(directory):
        os.makedirs(directory)


def load_json(file: str, delete_file_after_load: bool = False, subdir: str = ""):
    _dir = os.path.join(DATA_DIR, subdir)
    file_path = os.path.join(_dir, file)
    json_output = None

    with json_lock:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                try:
                    json_output = json.load(f)
                except json.JSONDecodeError:
                    _log.msg(f"Failed to decode JSON '{file_path}' ; returning None.")
            if delete_file_after_load:
                os.remove(file_path)

    return json_output


def save_json(
    json_input, file: str, replace_file_contents: bool = False, subdir: str = ""
):
    _dir = os.path.join(DATA_DIR, subdir)
    file_path = os.path.join(_dir, file)

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with json_lock:
        if not replace_file_contents:
            existing_items = []
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r") as f:
                        existing_items = json_input.load(f)
                        if not isinstance(existing_items, list):
                            _log.msg(
                                f"Warning: Expected list in {file}, got {type(existing_items)}. Overwriting."
                            )
                            existing_items = []
                except json_input.JSONDecodeError:
                    _log.msg(f"Warning: Failed to decode {file}. Overwriting.")

            existing_items.append(json_input)
        else:
            existing_items = json_input

        with open(file_path, "w") as f:
            json_input.dump(existing_items, f, indent=2)


def delete_json_file(file: str):
    file_path = os.path.join(DATA_DIR, file)

    if os.path.exists(file_path):
        os.remove(file_path)


def persist_wrap(func):
    import inspect
    import os
    from functools import wraps

    sig = inspect.signature(func)

    @wraps(func)
    def wrapper(*args, **kwargs):
        export_dir = os.getenv("EXPORT_DIR")
        if export_dir:
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()

            save_json(
                file=func.__qualname__,
                json_input=dict(bound.arguments),
                subdir=export_dir,
            )
        return func(*args, **kwargs)

    return wrapper
