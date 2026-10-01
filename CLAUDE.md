# CLAUDE.md: contracts

Python library `contracts-microservice` (import name `contracts`). The single source of truth for the messages OBLIVION services exchange. Status: prototype. Not everything here is used yet. Read `PUBLISHING.md` and `contracts/stream/README.md`. **Read the current version from `pyproject.toml`** (it was 0.8.0 on 2026-09-22, with seven vendored wheels — every service except `stepper_microservice`'s own stream endpoint, which is unimplemented, see below); do not trust a number written elsewhere.

Current state (2026-09-30): version 0.9.0, bundled into the seven consumers (not yet committed): ai-agent now hosts two agents (flows), so `contracts/api/microservices/ai_agent/` gained `motion.py` (`AIAgentMotionMessageResponse`: `directives` = the ordered movement list, `awaiting_user_input`), `RobotContext` in `decision.py` (what motion-flow decided, sent to conversation-flow) and `AIAgentMessageRequest.robot_context`. `AIAgentMessageResponse.directive` is kept for compatibility but conversation-flow never sets it any more. Earlier: branch `feature_ai_claude`. 0.7.0 added `contracts/api/microservices/ai_agent/` (session and movement-directive contracts) and made `ai-agent` a consumer; `contracts/scripts/bundle.py` and `contracts/tests/test_bundled_wheels.py` now key off `SERVICE_FOLDERS` (folder names) instead of assuming every consumer ends in `_microservice`. 0.7.1 added `error_code` to `AIAgentStartSessionResponse`/`AIAgentEndSessionResponse` (ai-agent's session-not-found signal, matching `AIAgentMessageResponse`). 0.8.0 registered `STEPPER_INBOUND`/`STEPPER_OUTBOUND` in `contracts/stream/schemas.py` (the event dataclasses already existed, unregistered) and made `stepper_microservice` a consumer: its `/health`, `/available` and `/control/{id}/...` batch routes now answer with `ApiEnvelope`/`StepperBatchResult`. Its `/process/stream/{id}/set` route does not use `contracts.stream` yet — it's a stub that reads and discards every event server-side (`StepperService.execute_stream`), so wiring the codec into it now wouldn't fix anything real; that's separate, unstarted work.

## Contents

- `contracts/stream/`: **in use.** Stream events `{type, sequence, timestamp, payload}` with types `stream_started`, `partial`, `completed`, `input_completed`, `heartbeat`, `error`.
  - `codec.py`: the only encoder/decoder (`EventSequencer`, `encode_ndjson`, `encode_sse`, `NdjsonDecoder`, `SseDecoder`, `iter_events`).
  - `schemas.py`: which events each stream direction may carry: `MICROPHONE_OUTBOUND`, `STT_INBOUND/OUTBOUND`, `TTS_INBOUND/OUTBOUND`, `SPEAKER_INBOUND/OUTBOUND`, and `UPLOAD_ACK` (`TTS_INPUT_ACK` is an alias).
  - `common/` (base event types, `input_completed`) and `microservices/<name>/`: per-service event DTOs.
- `contracts/api/`: request/response dataclasses (`common/`, `microservices/{ai_agent,microphone,speaker,stepper,stt,tts}`). **Partly in use**: `common/envelope.py` (`ApiEnvelope`) and the `data` shapes of `/health`, `/available`, `/ready`, microphone `/start`, STT and TTS batch, ai-agent's `/session/*` responses (since 0.7.0), and (since 0.8.0) `StepperBatchResult` for stepper's `/control/{id}/...` routes. The generic session-style requests (attach stream, TTS SetConfiguration) are implemented by no service.

## Who uses it

Every service: Brain, microphone, STT, TTS, speaker, ai-agent and stepper (each installs its bundled wheel from `vendor/` via its requirements files; ai-agent's folder has no `_microservice` suffix, see `contracts/scripts/bundle.py`'s `SERVICE_FOLDERS`).

## Rules

- **Bundling**: each service installs contracts from `<service>/vendor/contracts_microservice-<version>.whl`. After ANY change here, bump the version in `pyproject.toml` and run `brain_microservice\windows\Scripts\python.exe contracts\scripts\bundle.py`, then update the wheel name in the services' requirements. `tests/test_bundled_wheels.py` fails on stale or edited copies.
- **Change contracts first, then producers and consumers.** Add the event to `contracts.stream` and `schemas.py`, then update the services, add a conformance test per service, and extend the e2e test.
- Every package folder needs an `__init__.py`. Bump the version when modules are added, removed or renamed.
- For local development the service venvs may install it editable (`pip install -e ./contracts`); the requirements files use the bundled wheel. For mypy use `pip install -e ./contracts --config-settings editable_mode=compat`.
- Do not touch `build/`, `dist/` or `*.egg-info` (generated). `sitecustomize.py` is a workspace shim. Do not remove it unasked.
- Never hand-write event JSON in services. That is exactly what this package exists to prevent.

## Tests

The tests here need the services, so run them with the brain venv from the workspace root:

```powershell
brain_microservice\windows\Scripts\python.exe -m pytest contracts\tests -q
```

It includes contract tests and `tests/e2e/test_voice_pipeline_wire.py`, which starts four real service processes with fake hardware and checks bytes at the speaker and trace propagation.

`tests/e2e/test_real_pipeline.py` is different and is skipped unless `E2E_REAL_LLM=1`: all six services run for real (`real_services.py`: their own `main.py`, whisper, SAPI, sounddevice playback, the real LLM, stepper's own mock-hardware mode) and only the *input data* is mocked (phrases synthesized with SAPI by `make_speech.py`, streamed as the microphone's capture). It costs LLM calls and plays audio out loud. It needs the provider keys of `ai-agent/config/step_models.json` exported in the environment (never in a file), and a working output device (`SPEAKER_DEVICE_INDEX` is passed through if the default one cannot be opened).
