"""Conformance tests of the shared stream codec and the topology schemas."""

import asyncio

import pytest

from contracts.stream import schemas
from contracts.stream.codec import (
    EventSequencer,
    NdjsonDecoder,
    SseDecoder,
    decode_event,
    encode_ndjson,
    encode_sse,
    iter_events,
)
from contracts.stream.common.base import ContractViolation, EventType
from contracts.stream.common.error import ErrorEvent, ErrorEventDTO
from contracts.stream.common.heartbeat import HeartbeatEvent
from contracts.stream.microservices.microphone.outbound.stream_started import (
    MicrophoneStreamStartedEvent,
    MicrophoneStreamStartedEventDTO,
)
from contracts.stream.microservices.microphone.outbound.completed import (
    MicrophoneCompletedOutboundEvent,
    MicrophoneCompletedOutboundEventDTO,
)
from contracts.stream.microservices.microphone.outbound.partial import (
    MicrophonePartialEvent,
    MicrophonePartialEventDTO,
)
from contracts.stream.microservices.tts.outbound.partial import PartialOutboundEvent, PartialOutboundEventDTO


def _mic_events():
    sequencer = EventSequencer()
    return [
        sequencer.next(
            MicrophoneStreamStartedEvent,
            MicrophoneStreamStartedEventDTO(message="started", sample_rate=16000, channels=1),
        ),
        sequencer.next(MicrophonePartialEvent, MicrophonePartialEventDTO(bytes_base64="AAE=")),
        sequencer.next(HeartbeatEvent),
        sequencer.next(
            MicrophoneCompletedOutboundEvent,
            MicrophoneCompletedOutboundEventDTO(reason="completed", output_bytes_base64=""),
        ),
    ]


def test_timestamp_is_utc_with_z_and_payload_is_always_an_object() -> None:
    wire = encode_ndjson(_mic_events()[0]).decode()
    assert '"timestamp":"' in wire
    assert wire.split('"timestamp":"')[1].split('"')[0].endswith("Z")
    assert '"sample_rate":16000' in wire
    assert '"payload":{}' in encode_ndjson(_mic_events()[2]).decode()  # heartbeat has no data


def test_ndjson_round_trip_preserves_types_payloads_and_order() -> None:
    events = _mic_events()
    decoder = NdjsonDecoder(schemas.MICROPHONE_OUTBOUND)
    body = b"".join(encode_ndjson(e) for e in events)
    # feed in awkward 7-byte slices: framing must not depend on chunk boundaries
    decoded = [d for i in range(0, len(body), 7) for d in decoder.feed(body[i : i + 7])]
    assert [d.type for d in decoded] == [e.type for e in events]
    assert [d.sequence for d in decoded] == [1, 2, 3, 4]
    assert decoded[1].payload == MicrophonePartialEventDTO(bytes_base64="AAE=")
    assert decoded[0].payload.sample_rate == 16000
    assert decoded[2].payload is None  # heartbeat carries no data


def test_sse_round_trip() -> None:
    events = _mic_events()
    decoder = SseDecoder(schemas.MICROPHONE_OUTBOUND)
    body = "".join(encode_sse(e) for e in events).encode()
    assert [e.type for e in [*decoder.feed(body), *decoder.finish()]] == [e.type for e in events]


def test_error_event_round_trip_on_every_schema() -> None:
    event = ErrorEvent(
        sequence=1,
        timestamp=_mic_events()[0].timestamp,
        payload=ErrorEventDTO(code="boom", message="failed", recoverable=False),
    )
    for schema in (
        schemas.MICROPHONE_OUTBOUND,
        schemas.STT_INBOUND,
        schemas.STT_OUTBOUND,
        schemas.TTS_INBOUND,
        schemas.TTS_OUTBOUND,
        schemas.SPEAKER_INBOUND,
        schemas.SPEAKER_OUTBOUND,
    ):
        decoded = decode_event(encode_ndjson(event), schema)
        assert decoded.type is EventType.ERROR and decoded.payload.code == "boom"


@pytest.mark.parametrize(
    "line",
    [
        b"not json\n",
        b"[]\n",
        b'{"type":"partial","sequence":1,"timestamp":"2026-01-01T00:00:00Z"}\n',  # no payload
        b'{"type":"nope","sequence":1,"timestamp":"2026-01-01T00:00:00Z","payload":{}}\n',
        b'{"type":"partial","sequence":true,"timestamp":"2026-01-01T00:00:00Z","payload":{}}\n',
        b'{"type":"partial","sequence":1,"timestamp":"2026-01-01T00:00:00","payload":{"bytes_base64":"x"}}\n',
        b'{"type":"partial","sequence":1,"timestamp":"2026-01-01T00:00:00Z","payload":{}}\n',  # field missing
        b'{"type":"partial","sequence":1,"timestamp":"2026-01-01T00:00:00Z","payload":{"bytes_base64":5}}\n',
    ],
)
def test_malformed_events_are_rejected(line: bytes) -> None:
    with pytest.raises(ContractViolation):
        decode_event(line, schemas.MICROPHONE_OUTBOUND)


def test_event_not_in_the_stream_schema_is_rejected() -> None:
    wire = encode_ndjson(
        PartialOutboundEvent(
            sequence=1,
            timestamp=_mic_events()[0].timestamp,
            payload=PartialOutboundEventDTO(bytes_base64="AA==", byte_count=1, chunk_index=0),
        )
    )
    # TTS audio partials are legal on tts.outbound but a text stream has a different partial shape
    decode_event(wire, schemas.TTS_OUTBOUND)
    with pytest.raises(ContractViolation):
        decode_event(wire, schemas.STT_OUTBOUND)  # payload lacks "text"


def test_extra_payload_fields_are_tolerated() -> None:
    line = (
        b'{"type":"partial","sequence":1,"timestamp":"2026-01-01T00:00:00Z",'
        b'"payload":{"bytes_base64":"AA==","future_field":1}}'
    )
    assert decode_event(line, schemas.MICROPHONE_OUTBOUND).payload.bytes_base64 == "AA=="


def test_sequence_gaps_and_missing_stream_started_are_rejected() -> None:
    events = _mic_events()
    with pytest.raises(ContractViolation):
        list(NdjsonDecoder(schemas.MICROPHONE_OUTBOUND).feed(encode_ndjson(events[1])))  # not started
    decoder = NdjsonDecoder(schemas.MICROPHONE_OUTBOUND)
    list(decoder.feed(encode_ndjson(events[0])))
    with pytest.raises(ContractViolation):
        list(decoder.feed(encode_ndjson(events[2])))  # sequence 3 instead of 2


def test_iter_events_streams_in_order_and_closes_the_source() -> None:
    closed = []

    class Source:
        def __init__(self) -> None:
            self._chunks = [encode_ndjson(e) for e in _mic_events()]

        def __aiter__(self):
            return self

        async def __anext__(self) -> bytes:
            if not self._chunks:
                raise StopAsyncIteration
            return self._chunks.pop(0)

        async def aclose(self) -> None:
            closed.append(True)

    async def run():
        return [e async for e in iter_events(Source(), schemas.MICROPHONE_OUTBOUND)]

    assert [e.sequence for e in asyncio.run(run())] == [1, 2, 3, 4]
    assert closed == [True]


# ---- audio format announced in stream_started, and the upload acknowledgement event
def test_audio_bearing_streams_announce_their_format_in_stream_started():
    from contracts.stream.common.base import EventType
    from contracts.stream.microservices.speaker.inbound.stream_started import (
        SpeakerStreamStartedInboundEvent,
        SpeakerStreamStartedInboundEventDTO,
    )
    from contracts.stream.microservices.stt.inbound.stream_started import (
        STTStreamStartedInboundEvent,
        STTStreamStartedInboundEventDTO,
    )
    from contracts.stream.microservices.tts.outbound.stream_started import (
        TTSStreamStartedOutboundEvent,
        TTSStreamStartedOutboundEventDTO,
    )

    for schema, event_cls, dto_cls in (
        (schemas.STT_INBOUND, STTStreamStartedInboundEvent, STTStreamStartedInboundEventDTO),
        (schemas.TTS_OUTBOUND, TTSStreamStartedOutboundEvent, TTSStreamStartedOutboundEventDTO),
        (schemas.SPEAKER_INBOUND, SpeakerStreamStartedInboundEvent, SpeakerStreamStartedInboundEventDTO),
    ):
        event = EventSequencer().next(event_cls, dto_cls(sample_rate=24000, channels=1))
        decoded = decode_event(encode_ndjson(event), schema)
        assert decoded.type is EventType.START_STREAM
        assert (decoded.payload.sample_rate, decoded.payload.channels) == (24000, 1)
        with pytest.raises(ContractViolation):  # a bare stream_started no longer satisfies these streams
            decode_event(
                b'{"type":"stream_started","sequence":1,"timestamp":"2026-01-01T00:00:00Z","payload":{}}',
                schema,
            )


def test_input_completed_is_a_common_event_that_cannot_be_mistaken_for_content():
    from contracts.stream.common.input_completed import InputCompletedEvent, InputCompletedEventDTO

    event = EventSequencer().next(InputCompletedEvent, InputCompletedEventDTO())
    for schema in (schemas.UPLOAD_ACK, schemas.STT_OUTBOUND, schemas.TTS_OUTBOUND):
        decoded = decode_event(encode_ndjson(event), schema)
        assert decoded.type is EventType.INPUT_COMPLETED and decoded.payload.reason == "end_of_input"
    assert EventType.INPUT_COMPLETED is not EventType.COMPLETED
