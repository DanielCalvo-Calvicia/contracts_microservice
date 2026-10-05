"""The stream schemas of the OBLIVION topology: which events each direction of each stream carries.

Brain coordinates every flow; a service never talks to another service's stream directly:

    Microphone --MICROPHONE_OUTBOUND--> Brain --STT_INBOUND--> STT
    STT --STT_OUTBOUND--> Brain --TTS_INBOUND--> TTS
    TTS --TTS_OUTBOUND--> Brain --SPEAKER_INBOUND--> Speaker
    Speaker --SPEAKER_OUTBOUND--> Brain (playback result)

Audio on every ``bytes_base64`` field is raw little-endian PCM16, mono unless the stream's
``stream_started`` event says otherwise. No service converts audio for another: TTS produces the
format Brain asks for, the microphone reports the rate it captures at, and Brain passes those
numbers on unchanged.

The microphone cuts what it hears into utterances (silence detection lives there) and sends one
``utterance`` event per finished utterance with its whole audio; Brain hands each to STT as an
``utterance`` event, and STT only transcribes it.
"""

from __future__ import annotations

from contracts.stream.codec import StreamSchema
from contracts.stream.common.base import EventType
from contracts.stream.microservices.microphone.outbound.completed import (
    MicrophoneCompletedOutboundEvent,
    MicrophoneCompletedOutboundEventDTO,
)
from contracts.stream.microservices.microphone.outbound.utterance import (
    MicrophoneUtteranceEvent,
    MicrophoneUtteranceEventDTO,
)
from contracts.stream.microservices.microphone.outbound.stream_started import (
    MicrophoneStreamStartedEvent,
    MicrophoneStreamStartedEventDTO,
)
from contracts.stream.microservices.speaker.inbound.completed import (
    SpeakerCompletedInboundEvent,
    SpeakerCompletedInboundEventDTO,
)
from contracts.stream.microservices.speaker.inbound.stream_started import (
    SpeakerStreamStartedInboundEvent,
    SpeakerStreamStartedInboundEventDTO,
)
from contracts.stream.microservices.speaker.inbound.partial import (
    SpeakerPartialInboundEvent,
    SpeakerPartialInboundEventDTO,
)
from contracts.stream.microservices.speaker.outbound.completed import (
    SpeakerCompletedOutboundEvent,
    SpeakerCompletedOutboundEventDTO,
)
from contracts.stream.microservices.speaker.outbound.stream_started import (
    SpeakerStreamStartedEvent,
    SpeakerStreamStartedEventDTO,
)
from contracts.stream.microservices.stepper.inbound.completed import (
    StepperCompletedInboundEvent,
    StepperCompletedInboundEventDTO,
)
from contracts.stream.microservices.stepper.inbound.partial import (
    StepperPartialInboundEvent,
    StepperPartialInboundEventDTO,
)
from contracts.stream.microservices.stepper.inbound.stream_started import (
    StepperStreamStartedInboundEvent,
    StepperStreamStartedInboundEventDTO,
)
from contracts.stream.microservices.stepper.outbound.completed import (
    StepperCompletedOutboundEvent,
    StepperCompletedOutboundEventDTO,
)
from contracts.stream.microservices.stepper.outbound.partial import (
    StepperPartialOutboundEvent,
    StepperPartialOutboundEventDTO,
)
from contracts.stream.microservices.stepper.outbound.stream_started import (
    StepperStreamStartedOutboundEvent,
    StepperStreamStartedOutboundEventDTO,
)
from contracts.stream.microservices.stt.inbound.completed import (
    STTCompletedInboundEvent,
    STTCompletedInboundEventDTO,
)
from contracts.stream.microservices.stt.inbound.stream_started import (
    STTStreamStartedInboundEvent,
    STTStreamStartedInboundEventDTO,
)
from contracts.stream.microservices.stt.inbound.utterance import (
    STTUtteranceInboundEvent,
    STTUtteranceInboundEventDTO,
)
from contracts.stream.microservices.stt.outbound.completed import (
    STTCompletedOutboundEvent,
    STTCompletedOutboundEventDTO,
)
from contracts.stream.microservices.stt.outbound.partial import (
    STTPartialOutboundEvent,
    STTPartialOutboundEventDTO,
)
from contracts.stream.microservices.tts.inbound.completed import (
    TTSCompletedInboundEvent,
    TTSCompletedInboundEventDTO,
)
from contracts.stream.microservices.tts.inbound.partial import (
    PartialInboundEvent as TTSPartialInboundEvent,
)
from contracts.stream.microservices.tts.inbound.partial import (
    PartialInboundEventDTO as TTSPartialInboundEventDTO,
)
from contracts.stream.microservices.tts.outbound.completed import (
    CompletedOutboundEvent as TTSCompletedOutboundEvent,
)
from contracts.stream.microservices.tts.outbound.completed import (
    CompletedOutboundEventDTO as TTSCompletedOutboundEventDTO,
)
from contracts.stream.microservices.tts.outbound.stream_started import (
    TTSStreamStartedOutboundEvent,
    TTSStreamStartedOutboundEventDTO,
)
from contracts.stream.microservices.tts.outbound.partial import (
    PartialOutboundEvent as TTSPartialOutboundEvent,
)
from contracts.stream.microservices.tts.outbound.partial import (
    PartialOutboundEventDTO as TTSPartialOutboundEventDTO,
)

MICROPHONE_OUTBOUND = StreamSchema(
    "microphone.outbound",
    {
        EventType.START_STREAM: (MicrophoneStreamStartedEvent, MicrophoneStreamStartedEventDTO),
        EventType.UTTERANCE: (MicrophoneUtteranceEvent, MicrophoneUtteranceEventDTO),
        EventType.COMPLETED: (MicrophoneCompletedOutboundEvent, MicrophoneCompletedOutboundEventDTO),
    },
)

STT_INBOUND = StreamSchema(
    "stt.inbound",
    {
        EventType.START_STREAM: (STTStreamStartedInboundEvent, STTStreamStartedInboundEventDTO),
        EventType.UTTERANCE: (STTUtteranceInboundEvent, STTUtteranceInboundEventDTO),
        EventType.COMPLETED: (STTCompletedInboundEvent, STTCompletedInboundEventDTO),
    },
)

STT_OUTBOUND = StreamSchema(
    "stt.outbound",
    {
        EventType.PARTIAL: (STTPartialOutboundEvent, STTPartialOutboundEventDTO),
        EventType.COMPLETED: (STTCompletedOutboundEvent, STTCompletedOutboundEventDTO),
    },
)

TTS_INBOUND = StreamSchema(
    "tts.inbound",
    {
        EventType.PARTIAL: (TTSPartialInboundEvent, TTSPartialInboundEventDTO),
        EventType.COMPLETED: (TTSCompletedInboundEvent, TTSCompletedInboundEventDTO),
    },
)

TTS_OUTBOUND = StreamSchema(
    "tts.outbound",
    {
        EventType.START_STREAM: (TTSStreamStartedOutboundEvent, TTSStreamStartedOutboundEventDTO),
        EventType.PARTIAL: (TTSPartialOutboundEvent, TTSPartialOutboundEventDTO),
        EventType.COMPLETED: (TTSCompletedOutboundEvent, TTSCompletedOutboundEventDTO),
    },
)

# What STT and TTS answer on the *request* that uploads to them: ``stream_started`` when the upload
# is accepted, then ``input_completed`` once the sender ended its stream, or ``error`` if the upload
# failed. Only common events; nothing here can be mistaken for a transcript or audio.
UPLOAD_ACK = StreamSchema("upload.ack", {})
TTS_INPUT_ACK = UPLOAD_ACK  # kept name

SPEAKER_INBOUND = StreamSchema(
    "speaker.inbound",
    {
        EventType.START_STREAM: (SpeakerStreamStartedInboundEvent, SpeakerStreamStartedInboundEventDTO),
        EventType.PARTIAL: (SpeakerPartialInboundEvent, SpeakerPartialInboundEventDTO),
        EventType.COMPLETED: (SpeakerCompletedInboundEvent, SpeakerCompletedInboundEventDTO),
    },
)

SPEAKER_OUTBOUND = StreamSchema(
    "speaker.outbound",
    {
        EventType.START_STREAM: (SpeakerStreamStartedEvent, SpeakerStreamStartedEventDTO),
        EventType.COMPLETED: (SpeakerCompletedOutboundEvent, SpeakerCompletedOutboundEventDTO),
    },
)

# Stepper's stream endpoint (``/process/stream/{id}/set``): Brain (or any sender) streams motor
# commands as ``partial`` events and the service answers, per command, with a ``partial`` result and
# closes with ``completed``. The upload also carries ``stream_started`` so the motor is named once.
STEPPER_INBOUND = StreamSchema(
    "stepper.inbound",
    {
        EventType.START_STREAM: (StepperStreamStartedInboundEvent, StepperStreamStartedInboundEventDTO),
        EventType.PARTIAL: (StepperPartialInboundEvent, StepperPartialInboundEventDTO),
        EventType.COMPLETED: (StepperCompletedInboundEvent, StepperCompletedInboundEventDTO),
    },
)

STEPPER_OUTBOUND = StreamSchema(
    "stepper.outbound",
    {
        EventType.START_STREAM: (StepperStreamStartedOutboundEvent, StepperStreamStartedOutboundEventDTO),
        EventType.PARTIAL: (StepperPartialOutboundEvent, StepperPartialOutboundEventDTO),
        EventType.COMPLETED: (StepperCompletedOutboundEvent, StepperCompletedOutboundEventDTO),
    },
)
