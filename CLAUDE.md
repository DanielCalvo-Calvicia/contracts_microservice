# CLAUDE.md: contracts

Python library `contracts-microservice` (import name `contracts`). The single source of truth for the messages OBLIVION services exchange. Status: prototype; not everything here is used yet. Read `README.md`, `PUBLISHING.md`, `contracts/stream/README.md` and `contracts/api/README.md`. **Read the version from `pyproject.toml`**; do not trust a number written elsewhere.

Current state (2026-10-01): version **0.10.0** (uncommitted; HEAD `08cbe31` is 0.9.0): the stepper stream now has real events. `contracts/stream/microservices/stepper/` gained `inbound/stream_started.py` (`stepper_id`), `outbound/stream_started.py`, `outbound/partial.py` (the result of one command: `action`, `success`, `message`) and `inbound/partial.py` now carries `action` (`rotate`/`steps`/`stop`), `rotations`, `steps`, `rpm`, `speed`, `direction` (all but `action` optional). `STEPPER_INBOUND`/`STEPPER_OUTBOUND` carry `stream_started`, `partial` and `completed`. The 0.10.0 wheel is bundled in the seven consumers and every consumer's requirements name it. Branch `feature_ai_claude_2` (tracks `origin/feature_ai_claude_2`, in sync). Last commit `08cbe31` (2026-10-01, "contracts 0.9.0: motion-flow response, RobotContext, robot_context on the message request"). Uncommitted: `tests/e2e/fake_services.py`, `test_real_pipeline.py`, `test_voice_pipeline_wire.py` (modified), `tests/e2e/test_brain_ai_agent_flows.py` (new), and these docs. Tests: `57 passed, 20 skipped` (10 real-LLM tests skipped without `E2E_REAL_LLM=1`, 10 skipped because a consumer has no such requirements file). All seven consumers carry the 0.9.0 wheel in their `vendor/`.

## Contents

- `contracts/stream/`: **in use.** Stream events `{type, sequence, timestamp, payload}`, types `stream_started`, `partial`, `completed`, `input_completed`, `heartbeat`, `error`.
  - `codec.py`: the only encoder/decoder (`EventSequencer`, `encode_ndjson`, `encode_sse`, `NdjsonDecoder`, `SseDecoder`, `iter_events`, `StreamSchema`).
  - `schemas.py`: which events each stream direction may carry: `MICROPHONE_OUTBOUND`, `STT_INBOUND/OUTBOUND`, `TTS_INBOUND/OUTBOUND`, `SPEAKER_INBOUND/OUTBOUND`, `STEPPER_INBOUND/OUTBOUND` (used by stepper's `/process/stream/{id}/set`), and `UPLOAD_ACK` (`TTS_INPUT_ACK` is an alias).
  - `common/` (base, error, heartbeat, input_completed, start_stream) and `microservices/<name>/`: per-service event DTOs. `microservices/speaker/{completed,partial,stream_started}.py` (flat, outside `inbound/`/`outbound/`) are not registered in `schemas.py`; unverified whether anything still imports them.
- `contracts/api/`: request/response dataclasses for non-stream HTTP. **Partly in use**: `common/envelope.py` (`ApiEnvelope`), the `data` shapes of `/health`, `/available`, `/ready`, microphone `MicrophoneConfig`, STT and TTS batch responses, ai-agent's `/session/*` and message responses (flow responses, `MotorDirective`), and `StepperBatchResult`. The session-style requests (`*SessionRequest`, `*StreamAttachRequest`, `SetConfiguration`, `InitOutbound`) are implemented by no service; `tts/set_configuration.py` and `tts/init_outbound.py` still describe an OpenAI TTS engine that does not exist in the code.

## Who uses it

Every service: Brain, microphone, STT, TTS, speaker, ai-agent and stepper. Each installs its bundled wheel from its own `vendor/` (ai-agent's folder has no `_microservice` suffix; see `SERVICE_FOLDERS` in `scripts/bundle.py`). Stepper uses the API envelope and, since 0.10.0, `contracts.stream` (`STEPPER_INBOUND/OUTBOUND`) for `/process/stream/{id}/set`, which executes the commands it receives; Brain still drives the motors through the batch `/control/{id}/...` routes.

## Rules

- **Bundling**: after ANY change here, bump the version in `pyproject.toml` and run `brain_microservice\windows\Scripts\python.exe contracts\scripts\bundle.py` from the workspace root, then update the wheel name in the services' requirements files. `tests/test_bundled_wheels.py` fails on stale or edited copies.
- **Change contracts first, then producers and consumers.** Add the event to `contracts.stream` and `schemas.py`, then update the services, add a conformance test per service, and extend the e2e test.
- Every package folder needs an `__init__.py`. Bump the version when modules are added, removed or renamed. Prefer adding optional fields (the codec ignores unknown payload fields).
- Local development may install it editable (`pip install -e ./contracts`); the requirements files use the bundled wheel. For mypy: `pip install -e ./contracts --config-settings editable_mode=compat`.
- Do not touch `build/`, `dist/`, `*.egg-info` (generated) or the `env/` folder (an old venv, git-ignored). `sitecustomize.py` is a workspace shim (a dataclass compatibility wrapper). Do not remove it unasked.
- Never hand-write event JSON in services. That is exactly what this package exists to prevent.

## Tests

The tests need the services, so run them with the brain venv from the workspace root (about 25 s):

```powershell
brain_microservice\windows\Scripts\python.exe -m pytest contracts\tests -q
```

- `tests/test_stream_codec.py`, `tests/test_api_envelope.py`, `tests/test_bundled_wheels.py`: contract tests and the bundled-wheel check.
- `tests/e2e/test_voice_pipeline_wire.py` starts four real service processes with fake hardware (`fake_services.py`) and checks bytes at the speaker and trace propagation.
- `tests/e2e/test_brain_ai_agent_flows.py`: a real ai-agent process (its real composition root; only the LLM is a keyword script, `fake_services.build_ai_agent`) driven by Brain's real composition root, config defaults, adapters and `BrainService.decide`. Covers the flow order (conversation-flow, then motion-flow), a plain message, a movement sequence, a missing detail asked after the reply, a refused movement, one session per flow, reconnection after an ai-agent restart, the configurable flow list (`AI_AGENT_FLOWS`) and both flows' routes. Needs only ai-agent's venv.
- `tests/e2e/test_real_pipeline.py` is skipped unless `E2E_REAL_LLM=1`: all six services run for real (`real_services.py`: their own `main.py`, whisper, the TTS service's default engine, sounddevice playback, the real LLM, stepper's own mock-hardware mode) and only the *input data* is mocked (phrases synthesized with Windows SAPI by `make_speech.py`, streamed as the microphone's capture). So SAPI makes the *input*; the TTS under test is whatever the TTS default is (Piper `en_GB-alan-medium` if its voice file is present in the TTS `models/` folder, otherwise the pyttsx3 fallback; the file's docstring still says "real TTS (SAPI)", which is stale). It costs LLM calls and plays audio out loud. It needs the provider keys of `ai-agent/config/step_models.json` exported in the environment (never in a file) and a working output device (`SPEAKER_DEVICE_INDEX` is passed through if the default cannot be opened). Not run in this documentation pass.
