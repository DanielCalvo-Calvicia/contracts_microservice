# Publishing `contracts-microservice`

How a change to this package reaches the services. Rewritten on 2026-10-01 to match what the workspace really does: **the services do not install contracts from a package index or from Git; each carries a bundled wheel in its own `vendor/` folder.** The older text of this file described a PyPI/Git flow that nothing uses.

## The rule

If you add, remove, rename or change anything under `contracts/contracts/`, then in this order:

1. Bump `version` in `pyproject.toml`. Use a new version for every change; a reused version can leave a stale wheel in a consumer's cache.
2. From the workspace root run `brain_microservice\windows\Scripts\python.exe contracts\scripts\bundle.py`. It builds the wheel (`pip wheel --no-deps`) and copies it to `<service>/vendor/` of every consumer, deleting the older `contracts_microservice-*.whl` there.
3. Update the wheel file name in each consumer's requirements files (`./vendor/contracts_microservice-<version>-py3-none-any.whl`). The script prints the name to use.
4. Update producers and consumers, add a conformance test per service, extend the e2e tests.
5. Run `brain_microservice\windows\Scripts\python.exe -m pytest contracts\tests -q`. `tests/test_bundled_wheels.py` fails when a bundled wheel is missing, stale or differs from the source, or when a requirements file does not reference the current wheel (or still has `-e ../contracts`).
6. Reinstall in each service venv (`pip install ./vendor/<wheel>`) to see the change at runtime. Editable installs of `./contracts` are fine for development but are not what ships.

## Consumers

`SERVICE_FOLDERS` in `scripts/bundle.py` (and in `tests/test_bundled_wheels.py`): `brain_microservice`, `microphone_microservice`, `speaker_microservice`, `stt_microservice`, `tts_microservice`, `ai-agent`, `stepper_microservice`. A new consumer must be added to both lists.

## Package layout

The source tree is rooted at `contracts/`, the import package. `pyproject.toml` discovers packages with `include = ["contracts*"]`, so **every package directory needs an `__init__.py`**, and `py.typed` is shipped as package data.

```text
contracts/__init__.py
contracts/api/{__init__.py, common/, microservices/<name>/}
contracts/stream/{__init__.py, codec.py, schemas.py, common/, microservices/<name>/}
```

## Checking the wheel

```powershell
brain_microservice\windows\Scripts\python.exe -m zipfile -l tts_microservice\vendor\contracts_microservice-<version>-py3-none-any.whl
```

Expected: the module paths of `contracts/...` are listed. A wheel with only a `.dist-info` means package discovery failed.

## Troubleshooting

- A service still behaves like the old contract: it has an old wheel installed in its venv, or its requirements still name the old wheel. Reinstall from `vendor/`.
- `test_bundled_wheels.py` says "differs from /contracts": you edited a file after bundling (or edited a bundled copy). Run `bundle.py` again.
- Mypy cannot see `contracts`: install it editable in compat mode, `pip install -e ./contracts --config-settings editable_mode=compat`.
- `bundle.py` and `contracts/build/`, `dist/`, `*.egg-info` are generated; do not edit or commit them by hand.

## Not used

Publishing to PyPI or an internal index, and installing from `git+https://github.com/DanielCalvo-Calvicia/contracts.git@<tag>` (the remote of this repo is `https://github.com/DanielCalvo-Calvicia/contracts.git`), are possible in principle but are not the workflow here and were not tried.
