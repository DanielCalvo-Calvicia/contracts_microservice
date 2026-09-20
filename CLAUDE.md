# CLAUDE.md: contracts

Python library `contracts-microservice` (v0.6.0, import name `contracts`). The single source of truth for the messages OBLIVION services exchange. Status: prototype. Not everything here is used yet. Read `PUBLISHING.md` and `contracts/stream/README.md`.

## Contents

- `contracts/stream/`: **in use.** Stream events `{type, sequence, timestamp, payload}` with types `stream_started`, `partial`, `completed`, `heartbeat`, `error`.
  - `codec.py`: the only encoder/decoder (`EventSequencer`, `encode_ndjson`, `encode_sse`, `NdjsonDecoder`, `SseDecoder`, `iter_events`).
  - `schemas.py`: which events each stream direction may carry (`MICROPHONE_OUTBOUND`, `STT_INBOUND/OUTBOUND`, `TTS_INBOUND/OUTBOUND`, `SPEAKER_INBOUND/OUTBOUND`, `TTS_INPUT_ACK`).
  - `microservices/<name>/`: per-service event DTOs.
- `contracts/api/`: request/response dataclasses. **Partly in use**: `common/envelope.py` (`ApiEnvelope`, the JSON envelope of every non-stream answer) and the `data` shapes of `/health`, `/available`, `/ready`, microphone `/start`, STT and TTS batch. The session-style requests (StartSession, attach stream, TTS SetConfiguration) are still not implemented by any service.

## Who uses it

Brain, microphone, STT, TTS and speaker (each installs its bundled wheel from `vendor/` via its requirements files). `stepper_microservice` and `ai-agent` do not use it yet.

## Rules

- **Bundling**: each service installs contracts from `<service>/vendor/contracts_microservice-<version>.whl` (its requirements point there). After ANY change here, bump the version in `pyproject.toml` and run `brain_microservice\windows\Scripts\python.exe contracts\scripts\bundle.py`, then update the wheel name in the services' requirements. `tests/test_bundled_wheels.py` fails on stale or edited copies.

- **Change contracts first, then producers and consumers.** Add the event to `contracts.stream` and `schemas.py`, then update the services, add a conformance test per service, and extend the e2e test.
- Every package folder needs an `__init__.py`. Bump the version in `pyproject.toml` when modules are added, removed or renamed.
- For local development the service venvs may install it editable from the workspace (`pip install -e ./contracts`); the requirements files use the bundled wheel. For mypy use `pip install -e ./contracts --config-settings editable_mode=compat`.
- Do not touch `build/`, `dist/` or `*.egg-info` (generated). `sitecustomize.py` is a workspace shim. Do not remove it unasked.
- Never hand-write event JSON in services. That is exactly what this package exists to prevent.

## Tests

The tests here need the services, so run them with the brain venv from the workspace root:

```powershell
brain_microservice\windows\Scripts\python.exe -m pytest contracts\tests -q
```

It includes contract tests and `tests/e2e`, which starts four real service processes with fake hardware and checks bytes at the speaker and trace propagation.
