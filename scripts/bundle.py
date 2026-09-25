"""Builds the contracts wheel and places it in every microservice that uses it.

    brain_microservice/windows/Scripts/python.exe contracts/scripts/bundle.py

Each service then installs contracts from its own folder (``./vendor/<wheel>`` in its requirements),
so a single service can be built or shipped on its own (Docker image, another machine) without
the rest of the workspace. ``contracts/tests/test_bundled_wheels.py`` fails when a bundled copy
differs from this source tree, so run this after every change to ``contracts/``.
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS = ROOT / "contracts"
# Folder names of every consumer. Most are "<service>_microservice"; ai-agent is the exception.
SERVICE_FOLDERS = (
    "brain_microservice",
    "microphone_microservice",
    "speaker_microservice",
    "stt_microservice",
    "tts_microservice",
    "ai-agent",
    "stepper_microservice",
)


def build_wheel(into: Path) -> Path:
    subprocess.run(
        [sys.executable, "-m", "pip", "wheel", "--no-deps", "--wheel-dir", str(into), str(CONTRACTS)],
        check=True,
    )
    (wheel,) = into.glob("contracts_microservice-*.whl")
    return wheel


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        wheel = build_wheel(Path(tmp))
        for folder in SERVICE_FOLDERS:
            vendor = ROOT / folder / "vendor"
            vendor.mkdir(exist_ok=True)
            for old in vendor.glob("contracts_microservice-*.whl"):
                old.unlink()
            shutil.copy2(wheel, vendor / wheel.name)
            print(f"{folder}/vendor/{wheel.name}")
        print(f"requirements must reference ./vendor/{wheel.name}")


if __name__ == "__main__":
    main()
