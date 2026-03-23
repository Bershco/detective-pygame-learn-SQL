"""Path helpers for source runs and packaged desktop builds."""

import os
import sys
from pathlib import Path


APP_DATA_DIRNAME = "SQLDetectiveAcademy"


def resource_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    return Path(__file__).resolve().parent


def resource_path(name: str) -> Path:
    return resource_dir() / name


def user_data_dir() -> Path:
    home = Path.home()
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", home / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = home / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", home / ".local" / "share"))
    path = base / APP_DATA_DIRNAME
    path.mkdir(parents=True, exist_ok=True)
    return path
