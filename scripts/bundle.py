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
SERVICES = ("brain", "microphone", "speaker", "stt", "tts")


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
        for service in SERVICES:
            vendor = ROOT / f"{service}_microservice" / "vendor"
            vendor.mkdir(exist_ok=True)
            for old in vendor.glob("contracts_microservice-*.whl"):
                old.unlink()
            shutil.copy2(wheel, vendor / wheel.name)
            print(f"{service}_microservice/vendor/{wheel.name}")
        print(f"requirements must reference ./vendor/{wheel.name}")


if __name__ == "__main__":
    main()
