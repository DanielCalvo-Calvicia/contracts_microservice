"""Where a service's virtualenv interpreter is, on this OS (the services' venv folder is ``windows`` everywhere)."""

import sys
from pathlib import Path

VENV_FOLDER = "windows"


def venv_python(service_dir: Path) -> Path:
    """``<service>/windows/Scripts/python.exe`` on Windows, ``<service>/windows/bin/python`` elsewhere."""
    scripts = ("Scripts", "python.exe") if sys.platform == "win32" else ("bin", "python")
    return service_dir / VENV_FOLDER / scripts[0] / scripts[1]
