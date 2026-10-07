# contracts.api

Request/response dataclasses for the non-stream HTTP side of the services. Regenerated from the code on 2026-10-01 (version 0.10.0); the module list below is complete, the field lists are what the classes declare.

Everything here is a plain (frozen) dataclass. **Most of it is not used yet**: the "Used by" column says who really imports each class. Stream events live in `contracts.stream`, not here.

## Wire format of control endpoints

Every non-stream endpoint answers with `ApiEnvelope` (`contracts/api/common/envelope.py`):

| field | type |
|---|---|
| `action` | `str` |
| `status` | `"success"` \| `"accepted"` \| `"error"` |
| `status_code` | `int` |
| `message` | `str` |
| `data` | the payload below, or `None` |
| `timestamp` | `float`, seconds since the epoch (defaults to now) |

`data` is one of the response dataclasses in this package. `ApiEnvelope` is used by microphone, STT, TTS, speaker, stepper and ai-agent.

## `common/`

| module | classes | notes |
|---|---|---|
| `base.py` | `Command[T]` (`data`, `metadata`), `Result[T]` (`ok`, `message`, `data`, `error_code`, `metadata`) | generic wrappers, not used by a service |
| `envelope.py` | `ApiEnvelope[T]`, `EnvelopeStatus` | used by six services |
| `error.py` | `ErrorDetails` (`code`, `message`, `retryable`, `details`), `ErrorResult` (`error`, `context`) | not used by a service |
| `session.py` | `SessionCreateRequest[ConfigT]` (`config`, `client_id`, `correlation_id`), `SessionCreateResponse` (`session_id`, `state`, `created_at`), `SessionStatusRequest/Response`, `SessionCloseRequest` (`session_id`, `reason`), `SessionCloseResponse` (`session_id`, `closed`, `closed_at`), `SessionState` (`created`, `active`, `closing`, `closed`, `failed`) | base of the `*Session*` contracts below; no service exposes sessions this way |
| `stream.py` | `ByteStream`, `TextStream`, `StreamDirection` (`inbound`/`outbound`), `StreamBinding`, `ByteStreamProcessor` (protocol) | typing helpers |

## `microservices/common/`

| module | request | response | Used by |
|---|---|---|---|
| `health_check.py` | `HealthCheckRequest` | `HealthCheckResponse(healthy)` | microphone, STT, TTS, speaker, stepper, ai-agent (`GET /health`) |
| `availability.py` | `AvailabilityRequest(service_name)` | `AvailabilityResponse(is_available, reason)` | the same, plus Brain (`GET /available`) |
| `readiness.py` | `ReadinessRequest(component)` | `ReadinessResponse(is_ready, pending_reason)` | speaker |
| `get_stream.py` | `GetStreamRequest(session_id)` | `GetStreamResponse(stream)` | nobody |
| `set_stream.py` | `SetStreamRequest(session_id, stream)` | `SetStreamResponse(success, message)` | nobody |

## `microservices/ai_agent/` (since 0.7.0; one message route for every flow since 0.13.0)

| module | classes |
|---|---|
| `session.py` | `AIAgentStartSessionRequest(username, email, session_name)`, `AIAgentStartSessionResponse(success, session_id, message, error_code)`, `AIAgentEndSessionRequest(session_id)`, `AIAgentEndSessionResponse(success, message, error_code)`, `AIAgentMessageRequest(session_id, message, speak_movements)`, `AIAgentMessageResponse(success, response, message, error_code, directives, awaiting_user_input, flow)` |
| `decision.py` | `MotorDirective(arm: left\|right, degrees, direction: forward\|reverse)`, `AgentFlowName` (`identification`, `conversation`, `special`, `movement`) |

Used by Brain and ai-agent. Since 0.13.0 Brain makes one call per message to `POST /session/message`: ai-agent identifies the message, runs one flow and answers with `flow`, `response`, `directives` and `awaiting_user_input`. `speak_movements` (request) is Brain's switch for a spoken line on a movement. 0.14.0 removed what the old two-route design needed: `AIAgentMotionMessageResponse` (`motion.py`), `RobotContext`, `AIAgentMessageRequest.robot_context` and the single `AIAgentMessageResponse.directive`.

## `microservices/microphone/`

`start.py`: `MicrophoneConfig(sample_rate=16000, channels=1, encoding="pcm16", frame_ms=20, chunk_size=1024, device_id)` (used by Brain and microphone), `MicrophoneStartSessionRequest`, `MicrophoneStartSessionResponse(accepted_config)`.
`stop.py`: `MicrophoneStopSessionRequest`, `MicrophoneStopSessionResponse`.

## `microservices/speaker/`

`start.py`: `SpeakerConfig(sample_rate=24000, channels=1, encoding="pcm16", output_device_id)`, `SpeakerStartSessionRequest`, `SpeakerStartSessionResponse(accepted_config)`.
`stream.py`: `SpeakerStreamAttachRequest(session_id, direction, chunk_bytes, content_type)`, `SpeakerStreamAttachResponse(session_id, accepted, message)`. Not used by a service.

## `microservices/stepper/`

`batch.py`: `StepperBatchCommand(stepper_id, action: rotate\|steps\|stop, value, speed, direction)` (not used), `StepperBatchResult(success, message)` (used by Brain and stepper for `/control/{id}/...`).
`stream.py`: `StepperStreamConfig`, `StepperStartStreamSessionRequest/Response`, `StepperStreamAttachRequest/Response`. Not used: stepper's stream route uses `contracts.stream` events instead of these session contracts.

## `microservices/stt/`

`process_batch.py`: `STTProcessBatchRequest(audio_data, sample_rate=16000, language, model)`, `STTProcessBatchResponse(text, confidence)` (used by Brain and STT).
`process_stream.py`: `STTStreamConfig(sample_rate=16000, channels=1, language, model)` (STT does not cut utterances any more: the microphone does, see the stream README), `STTProcessStreamSessionRequest/Response`.
`set_stream.py`: `STTSetStreamRequest/Response`. `get_stream.py`: `STTGetStreamRequest/Response`. The stream and session ones are not used by a service.

## `microservices/tts/`

`process_batch.py`: `ProcessBatchRequest(text, sample_rate=22050, channels=1, session_id)`, `ProcessBatchResponse(audio_data_base64, sample_rate, channels)` (the response is used by TTS).
`set_configuration.py`: `SetConfigurationRequest/Response` and `init_outbound.py`: `InitOutboundRequest/Response`. **Not used, and they describe an OpenAI TTS engine** (voices `alloy`, `nova`, ..., model `gpt-4o-mini-tts`, adapter `openai`) that does not exist in the TTS service, whose engines are Piper and pyttsx3. Treat them as legacy.

## Notes

- Audio on any `*_base64` field is raw PCM16 mono and is never converted between services.
- A consumer-side check of "who imports what" was a scoped grep of `from contracts.api...` imports in each service (excluding venvs and `vendor/`) on 2026-10-01; it does not see dynamic imports.
