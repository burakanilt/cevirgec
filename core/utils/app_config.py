"""
Small persistent key/value store shared with i18n (~/.cevirgec_pdf/config.json).

Used by the PDF viewer for "recent files" and "last read page" memory.
Every write is read-modify-write so keys owned by other modules (e.g. "language")
are preserved.
"""
import json
import os
from typing import Any

from core.utils.i18n import CONFIG_PATH

MAX_RECENT_FILES = 12
MAX_LAST_PAGES = 200


def _load() -> dict:
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
    except Exception:
        pass
    return {}


def _save(data: dict) -> None:
    try:
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def get_value(key: str, default: Any = None) -> Any:
    return _load().get(key, default)


def set_value(key: str, value: Any) -> None:
    data = _load()
    data[key] = value
    _save(data)


def _norm(path: str) -> str:
    return os.path.normcase(os.path.abspath(path))


# ---------------------------------------------------------------- recent files
def get_recent_files(existing_only: bool = True) -> list[str]:
    files = get_value("viewer_recent_files", [])
    if not isinstance(files, list):
        return []
    if existing_only:
        files = [f for f in files if isinstance(f, str) and os.path.isfile(f)]
    return files


def add_recent_file(path: str) -> None:
    path = os.path.abspath(path)
    files = [f for f in get_recent_files(existing_only=False) if _norm(f) != _norm(path)]
    files.insert(0, path)
    set_value("viewer_recent_files", files[:MAX_RECENT_FILES])


def clear_recent_files() -> None:
    set_value("viewer_recent_files", [])


# ------------------------------------------------------------ last read page
def get_last_page(path: str) -> int:
    pages = get_value("viewer_last_pages", {})
    if not isinstance(pages, dict):
        return 0
    try:
        return max(0, int(pages.get(_norm(path), 0)))
    except (TypeError, ValueError):
        return 0


def set_last_page(path: str, page: int) -> None:
    data = _load()
    pages = data.get("viewer_last_pages", {})
    if not isinstance(pages, dict):
        pages = {}
    key = _norm(path)
    pages.pop(key, None)          # re-insert so the newest entry is last
    if page > 0:
        pages[key] = int(page)
    while len(pages) > MAX_LAST_PAGES:
        pages.pop(next(iter(pages)))
    data["viewer_last_pages"] = pages
    _save(data)
