# contracts

`contracts-microservice` (import name `contracts`): the shared message definitions of the OBLIVION robot. Every service installs it from a wheel bundled in its own `vendor/` folder, so nothing at runtime depends on this folder.

Version: see `pyproject.toml` (0.10.0 on 2026-10-01). `pyproject.toml` declares Python `>=3.10`, but the code uses `enum.StrEnum` and `datetime.UTC` (3.11+), so treat 3.11 as the real minimum (the workspace venvs use 3.14; unverified on 3.10). No runtime dependencies. Library only: no ports, no environment variables, no HTTP server.

## Layout

```text
contracts/
  stream/                  long-lived event streams (see contracts/stream/README.md)
    codec.py               the only encoder/decoder: EventSequencer, NDJSON/SSE encode and decode, StreamSchema
    schemas.py             which events each stream direction may carry (MICROPHONE_OUTBOUND, STT_*, TTS_*, SPEAKER_*, STEPPER_*, UPLOAD_ACK)
    common/                BaseEvent, EventType, error, heartbeat, input_completed, stream_started
    microservices/<name>/  per-service event DTOs (inbound/ and outbound/)
  api/                     request/response dataclasses for non-stream HTTP (see contracts/api/README.md)
    common/                ApiEnvelope, session, error, stream helpers
    microservices/<name>/  ai_agent, common, microphone, speaker, stepper, stt, tts
scripts/bundle.py          builds the wheel and copies it into every consumer's vendor/
tests/                     codec, envelope, bundled-wheel and end-to-end tests
PUBLISHING.md              how a change reaches the services
```

## Use

```python
from contracts.stream.codec import EventSequencer, NdjsonDecoder, encode_ndjson
from contracts.stream.schemas import TTS_INBOUND
from contracts.api.common.envelope import ApiEnvelope
```

Services never hand-write event JSON: build the event class, encode it with the codec.

## Change a contract

1. Edit `contracts/` (events go in `contracts/stream/` and `schemas.py` first), bump `version` in `pyproject.toml`.
2. From the workspace root: `brain_microservice\windows\Scripts\python.exe contracts\scripts\bundle.py`.
3. Update the wheel name in each service's requirements files, then the producers and consumers.
4. Run the tests.

Details and the reasons are in `PUBLISHING.md`.

## Tests

From the workspace root (they start real service processes with fake hardware):

```powershell
brain_microservice\windows\Scripts\python.exe -m pytest contracts\tests -q
```

Result on 2026-10-01: `57 passed, 20 skipped` in about 25 s. Skipped: 10 tests of `tests/e2e/test_real_pipeline.py` (real LLM; set `E2E_REAL_LLM=1` and export the provider keys of `ai-agent/config/step_models.json`; it plays audio out loud) and 10 parametrized cases of `test_bundled_wheels.py` for requirements files a service does not have. The real-pipeline test and anything needing real devices were not run for this documentation.
