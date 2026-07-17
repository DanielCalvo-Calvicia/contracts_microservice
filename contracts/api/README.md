# contracts.api README

This document describes every contract class currently available under `contracts.api` and how each one is intended to be used.

It is written to be machine-friendly so other LLMs can quickly discover:

- What classes exist
- Where each class lives
- Which classes are input contracts vs output contracts
- Which classes include streaming fields (`AsyncIterator[...]`)

## Package Purpose

`contracts.api` provides request and response dataclass contracts for microservice operations.

High-level layout:

- `contracts.api.common`: shared base contracts and error response contract
- `contracts.api.microservices.common`: health/readiness/availability contracts
- `contracts.api.microservices.microphone`: microphone control contracts
- `contracts.api.microservices.speaker`: speaker contracts
- `contracts.api.microservices.stepper`: stepper batch and stream contracts
- `contracts.api.microservices.stt`: speech-to-text contracts
- `contracts.api.microservices.tts`: text-to-speech contracts

---

## Shared Base Contracts

### Module: `contracts.api.common.base`

Example import:

```python
from contracts.api.common.base import BaseRequest, BaseResponse
```

#### `BaseRequest[T]`

- Type: generic frozen dataclass
- Fields:
  - `status_code: int`
  - `detail: str`
  - `headers: Optional[dict[str, str]]`
  - `action: str`
  - `status: str`
  - `message: str`
  - `timestamp: float`
  - `metadata: Optional[dict[str, Any]]`
  - `data: Optional[T]`
- Usage:
  - Wraps request DTOs for all microservice request contracts
  - The concrete payload is stored in `data`

#### `BaseResponse[T]`

- Type: generic frozen dataclass
- Fields: same shape as `BaseRequest[T]`
- Usage:
  - Wraps response DTOs for most microservice response contracts
  - The concrete result payload is stored in `data`

### Module: `contracts.api.common.exception`

Example import:

```python
from contracts.api.common.exception import ExceptionApiResponse
```

#### `ExceptionApiResponse[T]`

- Type: generic frozen dataclass
- Fields: same envelope fields as `BaseRequest` and `BaseResponse`
- Usage:
  - Standardized exception/error response envelope

---

## Common Operational Contracts

### Module: `contracts.api.microservices.common.availability`

Example import:

```python
from contracts.api.microservices.common.availability import (
    AvailabilityRequestDTO,
    AvailabilityRequest,
    AvailabilityResponseDTO,
    AvailabilityResponse,
)
```

#### `AvailabilityRequestDTO`

- Empty DTO
- Usage: payload for availability check request

#### `AvailabilityRequest`

- Inherits: `BaseRequest[AvailabilityRequestDTO]`
- Usage: request envelope for availability check

#### `AvailabilityResponseDTO`

- Fields:
  - `is_available: bool`
- Usage: payload indicating availability status

#### `AvailabilityResponse`

- Inherits: `BaseResponse[AvailabilityResponseDTO]`
- Usage: response envelope for availability check

### Module: `contracts.api.microservices.common.health_check`

Example import:

```python
from contracts.api.microservices.common.health_check import (
    HealthCheckRequestDTO,
    HealthCheckRequest,
    HealthCheckResponseDTO,
    HealthCheckResponse,
)
```

#### `HealthCheckRequestDTO`

- Empty DTO
- Usage: payload for health check request

#### `HealthCheckRequest`

- Inherits: `BaseRequest[HealthCheckRequestDTO]`
- Usage: request envelope for health check

#### `HealthCheckResponseDTO`

- Empty DTO
- Usage: payload for health check response

#### `HealthCheckResponse`

- Inherits: `BaseResponse[HealthCheckResponseDTO]`
- Usage: response envelope for health check

### Module: `contracts.api.microservices.common.readiness`

Example import:

```python
from contracts.api.microservices.common.readiness import (
    ReadinessRequestDTO,
    ReadinessRequest,
    ReadinessResponseDTO,
    ReadinessResponse,
)
```

#### `ReadinessRequestDTO`

- Empty DTO
- Usage: payload for readiness check request

#### `ReadinessRequest`

- Inherits: `BaseRequest[ReadinessRequestDTO]`
- Usage: request envelope for readiness check

#### `ReadinessResponseDTO`

- Fields:
  - `is_ready: bool`
- Usage: payload indicating readiness status

#### `ReadinessResponse`

- Inherits: `BaseResponse[ReadinessResponseDTO]`
- Usage: response envelope for readiness check

---

## Microphone Contracts

### Module: `contracts.api.microservices.microphone.start`

Example import:

```python
from contracts.api.microservices.microphone.start import (
    MicrophoneStartRequestDTO,
    MicrophoneStartRequest,
    MicrophoneStartResponseDTO,
    MicrophoneStartResponse,
)
```

#### `MicrophoneStartRequestDTO`

- Fields:
  - `sample_rate: int = 16000`
  - `channels: int = 1`
  - `format: str = "pcm16"`
- Usage: start microphone stream configuration

#### `MicrophoneStartRequest`

- Inherits: `BaseRequest[MicrophoneStartRequestDTO]`
- Usage: request envelope for microphone start

#### `MicrophoneStartResponseDTO`

- Fields:
  - `stream: AsyncIterator[bytes]`
  - `sample_rate: int`
- Usage: payload carrying outbound audio stream and rate

#### `MicrophoneStartResponse`

- Inherits: `BaseResponse[MicrophoneStartResponseDTO]`
- Usage: response envelope for microphone start

### Module: `contracts.api.microservices.microphone.stop`

Example import:

```python
from contracts.api.microservices.microphone.stop import (
    MicrophoneStopRequestDTO,
    MicrophoneStopRequest,
    MicrophoneStopResponseDTO,
    MicrophoneStopResponse,
)
```

#### `MicrophoneStopRequestDTO`

- Empty DTO
- Usage: payload to stop microphone stream

#### `MicrophoneStopRequest`

- Inherits: `BaseRequest[MicrophoneStopRequestDTO]`
- Usage: request envelope for microphone stop

#### `MicrophoneStopResponseDTO`

- Fields:
  - `success: bool = True`
- Usage: payload confirming stop operation

#### `MicrophoneStopResponse`

- Inherits: `BaseResponse[MicrophoneStopResponseDTO]`
- Usage: response envelope for microphone stop

---

## Speaker Contracts

### Module: `contracts.api.microservices.speaker.start`

Example import:

```python
from contracts.api.microservices.speaker.start import (
    SpeakerStartRequestDTO,
    SpeakerStartRequest,
    SpeakerStartResponseDTO,
    SpeakerStartResponse,
)
```

#### `SpeakerStartRequestDTO`

- Fields:
  - `audio_stream: AsyncIterator[bytes]`
  - `sample_rate: int = 24000`
  - `channels: int = 1`
- Usage: inbound audio stream plus playback configuration

#### `SpeakerStartRequest`

- Inherits: `BaseRequest[SpeakerStartRequestDTO]`
- Usage: request envelope for speaker start

#### `SpeakerStartResponseDTO`

- Fields:
  - `success: bool`
  - `message: str`
- Usage: payload confirming speaker start handling

#### `SpeakerStartResponse`

- Inherits: `BaseResponse[SpeakerStartResponseDTO]`
- Usage: response envelope for speaker start

---

## Stepper Contracts

### Module: `contracts.api.microservices.stepper.batch`

Example import:

```python
from contracts.api.microservices.stepper.batch import (
    StepperBatchStartRequestDTO,
    StepperBatchStartRequest,
    StepperBatchStartResponseDTO,
    StepperBatchStartResponse,
)
```

#### `StepperBatchStartRequestDTO`

- Fields:
  - `stepper_id: str`
  - `action: str`
  - `value: float = 0.0`
  - `speed: float = 0.0`
  - `direction: str = "forward"`
- Usage: single batch command input for stepper motor

#### `StepperBatchStartRequest`

- Inherits: `BaseRequest[StepperBatchStartRequestDTO]`
- Usage: request envelope for stepper batch operation

#### `StepperBatchStartResponseDTO`

- Fields:
  - `success: bool`
  - `message: str`
- Usage: payload with batch execution result

#### `StepperBatchStartResponse`

- Inherits: `BaseResponse[StepperBatchStartResponseDTO]`
- Usage: response envelope for stepper batch operation

### Module: `contracts.api.microservices.stepper.stream`

Example import:

```python
from contracts.api.microservices.stepper.stream import (
    StepperStreamRequestDTO,
    StepperStreamRequest,
    StepperStreamResponseDTO,
    StepperStreamResponse,
)
```

#### `StepperStreamRequestDTO`

- Fields:
  - `stepper_id: str`
  - `command_stream: AsyncIterator[dict[str, Any]]`
- Usage: streamed command input for stepper control

#### `StepperStreamRequest`

- Inherits: `BaseRequest[StepperStreamRequestDTO]`
- Usage: request envelope for stepper stream operation

#### `StepperStreamResponseDTO`

- Fields:
  - `success: bool`
  - `message: str`
- Usage: payload with stream processing acceptance/result

#### `StepperStreamResponse`

- Inherits: `BaseResponse[StepperStreamResponseDTO]`
- Usage: response envelope for stepper stream operation

---

## STT Contracts

### Module: `contracts.api.microservices.stt.process_batch`

Example import:

```python
from contracts.api.microservices.stt.process_batch import (
    STTProcessBatchStartRequestDTO,
    STTProcessBatchStartRequest,
    STTProcessBatchStartResponseDTO,
    STTProcessBatchStartResponse,
)
```

#### `STTProcessBatchStartRequestDTO`

- Fields:
  - `audio_data: bytes`
  - `sample_rate: int = 16000`
- Usage: batch STT input audio bytes

#### `STTProcessBatchStartRequest`

- Inherits: `BaseRequest[STTProcessBatchStartRequestDTO]`
- Usage: request envelope for batch STT

#### `STTProcessBatchStartResponseDTO`

- Fields:
  - `text: str`
- Usage: transcription output text

#### `STTProcessBatchStartResponse`

- Inherits: `BaseResponse[STTProcessBatchStartResponseDTO]`
- Usage: response envelope for batch STT

### Module: `contracts.api.microservices.stt.process_stream`

Example import:

```python
from contracts.api.microservices.stt.process_stream import (
    STTProcessStreamStartRequestDTO,
    STTProcessStreamStartRequest,
    STTProcessStreamStartResponseDTO,
    STTProcessStreamStartResponse,
)
```

#### `STTProcessStreamStartRequestDTO`

- Fields:
  - `audio_stream: AsyncIterator[bytes]`
  - `sample_rate: int = 16000`
  - `chunk_size: int = 1024`
  - `silence_threshold: int = 150`
  - `silence_limit_seconds: float = 2.0`
- Usage: streaming STT input and stream processing configuration

#### `STTProcessStreamStartRequest`

- Inherits: `BaseRequest[STTProcessStreamStartRequestDTO]`
- Usage: request envelope for stream STT processing

#### `STTProcessStreamStartResponseDTO`

- Fields:
  - `text_stream: AsyncIterator[str]`
- Usage: streamed transcription output

#### `STTProcessStreamStartResponse`

- Inherits: `BaseResponse[STTProcessStreamStartResponseDTO]`
- Usage: response envelope for stream STT processing

### Module: `contracts.api.microservices.stt.set_stream`

Example import:

```python
from contracts.api.microservices.stt.set_stream import (
    STTSetStreamStartRequestDTO,
    STTSetStreamStartRequest,
    STTSetStreamStartResponseDTO,
    STTSetStreamStartResponse,
)
```

#### `STTSetStreamStartRequestDTO`

- Fields:
  - `audio_stream: AsyncIterator[bytes]`
  - `sample_rate: int = 16000`
  - `chunk_size: int = 1024`
  - `silence_threshold: int = 150`
  - `silence_limit_seconds: float = 2.0`
- Usage: set inbound audio stream for STT session/flow

#### `STTSetStreamStartRequest`

- Inherits: `BaseRequest[STTSetStreamStartRequestDTO]`
- Usage: request envelope for setting STT stream

#### `STTSetStreamStartResponseDTO`

- Fields:
  - `accepted: bool`
- Usage: acknowledgment that stream was accepted

#### `STTSetStreamStartResponse`

- Inherits: `BaseResponse[STTSetStreamStartResponseDTO]`
- Usage: response envelope for set-stream operation

### Module: `contracts.api.microservices.stt.get_stream`

Example import:

```python
from contracts.api.microservices.stt.get_stream import (
    STTGetStreamStartRequestDTO,
    STTGetStreamStartRequest,
    STTGetStreamStartResponseDTO,
    STTGetStreamStartResponse,
)
```

#### `STTGetStreamStartRequestDTO`

- Empty DTO
- Usage: request payload for obtaining STT text stream

#### `STTGetStreamStartRequest`

- Inherits: `BaseRequest[STTGetStreamStartRequestDTO]`
- Usage: request envelope for get-stream operation

#### `STTGetStreamStartResponseDTO`

- Fields:
  - `text_stream: AsyncIterator[str]`
- Usage: outbound text stream payload

#### `STTGetStreamStartResponse`

- Inherits: `BaseResponse[STTGetStreamStartResponseDTO]`
- Usage: response envelope for get-stream operation

---

## TTS Contracts

### Module: `contracts.api.microservices.tts.process_batch`

Example import:

```python
from contracts.api.microservices.tts.process_batch import (
    TTSProcessBatchRequestDTO,
    TTSProcessBatchRequest,
    TTSProcessBatchResponseDTO,
    TTSProcessBatchResponse,
)
```

#### `TTSProcessBatchRequestDTO`

- Fields:
  - `text: str`
  - `sample_rate: int = 22050`
  - `channels: int = 1`
- Usage: batch TTS synthesis input

#### `TTSProcessBatchRequest`

- Inherits: `BaseRequest[TTSProcessBatchRequestDTO]`
- Usage: request envelope for batch TTS

#### `TTSProcessBatchResponseDTO`

- Fields:
  - `audio_data_base64: str`
  - `sample_rate: int`
  - `channels: int`
- Usage: synthesized audio payload encoded as base64

#### `TTSProcessBatchResponse`

- Inherits: `BaseResponse[TTSProcessBatchResponseDTO]`
- Usage: response envelope for batch TTS

### Module: `contracts.api.microservices.tts.process_stream`

Example import:

```python
from contracts.api.microservices.tts.process_stream import (
    TTSProcessRequestDTO,
    TTSProcessRequest,
    TTSProcessResponseDTO,
    TTSProcessResponse,
)
```

#### `TTSProcessRequestDTO`

- Fields:
  - `text_stream: AsyncIterator[bytes]`
  - `sample_rate: int = 22050`
  - `channels: int = 1`
- Usage: streaming text input plus output audio configuration

#### `TTSProcessRequest`

- Inherits: `BaseRequest[TTSProcessRequestDTO]`
- Usage: request envelope for stream TTS processing

#### `TTSProcessResponseDTO`

- Fields:
  - `content: AsyncIterator[str] | AsyncIterator[bytes]`
  - `media_type: str`
  - `status_code: int`
  - `headers: dict[str, str]`
- Usage: outbound stream payload and HTTP-style metadata

#### `TTSProcessResponse`

- Inherits: `TTSProcessResponseDTO`
- Usage: concrete response class for stream TTS

### Module: `contracts.api.microservices.tts.set_stream`

Example import:

```python
from contracts.api.microservices.tts.set_stream import (
    TTSSetStreamRequestDTO,
    TTSSetStreamRequest,
    TTSSetStreamResponseDTO,
    TTSSetStreamResponse,
)
```

#### `TTSSetStreamRequestDTO`

- Fields:
  - `text_stream: AsyncIterator[str]`
  - `sample_rate: int = 22050`
  - `channels: int = 1`
- Usage: set inbound text stream for TTS processing

#### `TTSSetStreamRequest`

- Inherits: `BaseRequest[TTSSetStreamRequestDTO]`
- Usage: request envelope for set-stream operation

#### `TTSSetStreamResponseDTO`

- Fields:
  - `content: AsyncIterator[str] | AsyncIterator[bytes]`
  - `media_type: str`
  - `status_code: int`
  - `headers: dict[str, str]`
- Usage: outbound stream payload and HTTP-style metadata

#### `TTSSetStreamResponse`

- Inherits: `TTSSetStreamResponseDTO`
- Usage: concrete response class for set-stream response

### Module: `contracts.api.microservices.tts.get_stream`

Example import:

```python
from contracts.api.microservices.tts.get_stream import (
    TTSGetStreamRequestDTO,
    TTSGetStreamRequest,
    TTSGetStreamResponseDTO,
    TTSGetStreamResponse,
)
```

#### `TTSGetStreamRequestDTO`

- Empty DTO
- Usage: request payload for fetching TTS output stream

#### `TTSGetStreamRequest`

- Inherits: `BaseRequest[TTSGetStreamRequestDTO]`
- Usage: request envelope for get-stream operation

#### `TTSGetStreamResponseDTO`

- Fields:
  - `content: AsyncIterator[str] | AsyncIterator[bytes]`
  - `media_type: str`
  - `status_code: int`
  - `headers: dict[str, str]`
- Usage: outbound stream payload and HTTP-style metadata

#### `TTSGetStreamResponse`

- Inherits: `TTSGetStreamResponseDTO`
- Usage: concrete response class for get-stream response

---

## Minimal Usage Patterns

### Create request envelope with DTO payload

```python
from contracts.api.microservices.tts.process_batch import (
    TTSProcessBatchRequest,
    TTSProcessBatchRequestDTO,
)

request = TTSProcessBatchRequest(
    status_code=200,
    detail="ok",
    headers=None,
    action="tts.process_batch",
    status="accepted",
    message="start",
    timestamp=0.0,
    metadata={"trace_id": "abc"},
    data=TTSProcessBatchRequestDTO(text="Hello world"),
)
```

### Create response envelope with DTO result

```python
from contracts.api.microservices.stt.process_batch import (
    STTProcessBatchStartResponse,
    STTProcessBatchStartResponseDTO,
)

response = STTProcessBatchStartResponse(
    status_code=200,
    detail="ok",
    headers=None,
    action="stt.process_batch",
    status="completed",
    message="done",
    timestamp=0.0,
    metadata=None,
    data=STTProcessBatchStartResponseDTO(text="transcribed text"),
)
```

---

## Notes for LLM Consumers

- Most operations follow this pattern:
  - `XxxRequestDTO` -> domain payload
  - `XxxRequest` -> `BaseRequest[XxxRequestDTO]`
  - `XxxResponseDTO` -> result payload
  - `XxxResponse` -> `BaseResponse[XxxResponseDTO]`
- Streaming operations use `AsyncIterator[...]` in DTO fields.
- TTS streaming responses (`get_stream`, `set_stream`, `process_stream`) currently use response classes that inherit DTO classes directly instead of `BaseResponse[...]`.
- All `__init__.py` files are currently empty package markers.
