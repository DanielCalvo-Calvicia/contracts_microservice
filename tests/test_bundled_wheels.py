"""Every microservice carries the same contracts as ``/contracts``: no stale or edited copies."""

import re
import zipfile
from pathlib import Path

import pytest

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
VERSION = re.search(r'^version = "(.+)"', (CONTRACTS / "pyproject.toml").read_text(), re.M).group(1)
WHEEL = f"contracts_microservice-{VERSION}-py3-none-any.whl"
FIX = "run: brain_microservice/windows/Scripts/python.exe contracts/scripts/bundle.py"


def _source_files() -> dict[str, bytes]:
    return {
        path.relative_to(CONTRACTS).as_posix(): path.read_bytes()
        for path in (CONTRACTS / "contracts").rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix in {".py", ".typed"}
    }


@pytest.mark.parametrize("service", SERVICE_FOLDERS)
def test_the_bundled_wheel_is_current_and_identical_to_the_source(service: str) -> None:
    wheel = ROOT / service / "vendor" / WHEEL
    assert wheel.exists(), f"{service}: {WHEEL} missing; {FIX}"
    others = [p.name for p in wheel.parent.glob("contracts_microservice-*.whl") if p.name != WHEEL]
    assert not others, f"{service}: stale wheels {others}; {FIX}"

    with zipfile.ZipFile(wheel) as archive:
        bundled = {
            name: archive.read(name)
            for name in archive.namelist()
            if name.startswith("contracts/") and not name.endswith("/")
        }
    source = _source_files()
    assert sorted(bundled) == sorted(source), f"{service}: file list differs; {FIX}"
    changed = [name for name in source if bundled[name].replace(b"\r\n", b"\n") != source[name].replace(b"\r\n", b"\n")]
    assert not changed, f"{service}: differs from /contracts in {changed[:5]}; {FIX}"


@pytest.mark.parametrize("service", SERVICE_FOLDERS)
@pytest.mark.parametrize("name", ["requirements.windows.txt", "requirements.linux.txt", "requirements.txt"])
def test_requirements_install_the_bundled_wheel_not_a_sibling_path(service: str, name: str) -> None:
    path = ROOT / service / name
    if not path.exists():
        pytest.skip(f"{service} has no {name}")
    text = path.read_text()
    assert "-e ../contracts" not in text, f"{path.name} still points outside the service folder"
    assert f"./vendor/{WHEEL}" in text, f"{path.name} does not install ./vendor/{WHEEL}"
