"""Encoding and decoding of stream events: the one implementation every service shares.

The contracts in ``contracts.stream`` define *what* an event is; this module defines how an event
becomes bytes on the wire and back, so no microservice needs its own JSON handling.

Wire format
-----------
Each event is one JSON object ``{"type", "sequence", "timestamp", "payload"}`` with

* ``type``       one of :class:`EventType`
* ``sequence``   1, 2, 3, ... per stream, gap-free, starting with ``stream_started``
* ``timestamp``  UTC ISO-8601 ending in ``Z``
* ``payload``    always a JSON object (``{}`` for events without data)

framed either as NDJSON (one object per line) or as Server-Sent Events (``data: <json>``
followed by a blank line). Both framings carry identical events.
"""

from __future__ import annotations

import json
import types
import typing
from collections.abc import AsyncIterable, AsyncIterator, Iterator, Mapping
from dataclasses import MISSING, dataclass, fields, is_dataclass
from typing import Any, Union

from contracts.stream.common.base import (
    BaseEvent,
    ContractViolation,
    EventType,
    parse_timestamp,
    utc_now,
)
from contracts.stream.common.error import ErrorEvent, ErrorEventDTO
from contracts.stream.common.heartbeat import HeartbeatEvent
from contracts.stream.common.input_completed import InputCompletedEvent, InputCompletedEventDTO
from contracts.stream.common.start_stream import StartStreamEvent

EventClass = type[BaseEvent[Any]]


@dataclass(frozen=True, slots=True)
class StreamSchema:
    """The events one direction of one stream may carry.

    ``events`` maps each allowed :class:`EventType` to ``(event class, payload DTO or None)``.
    ``heartbeat``, ``stream_started`` (payload-less) and ``error`` are common to every stream and
    are added unless the schema overrides them.
    """

    name: str
    events: Mapping[EventType, tuple[EventClass, type | None]]

    def resolve(self, event_type: EventType) -> tuple[EventClass, type | None]:
        try:
            return self.events[event_type]
        except KeyError:
            pass
        common = _COMMON_EVENTS.get(event_type)
        if common is None:
            raise ContractViolation(
                f"{self.name}: event type {event_type.value!r} is not part of this stream"
            )
        return common


_COMMON_EVENTS: dict[EventType, tuple[EventClass, type | None]] = {
    EventType.HEARTBEAT: (HeartbeatEvent, None),
    EventType.START_STREAM: (StartStreamEvent, None),
    EventType.ERROR: (ErrorEvent, ErrorEventDTO),
    EventType.INPUT_COMPLETED: (InputCompletedEvent, InputCompletedEventDTO),
}


# --------------------------------------------------------------------------- encoding


def make_event(event_cls: EventClass, sequence: int, payload: Any = None) -> BaseEvent[Any]:  # noqa: ANN401
    """Build an event stamped with the current UTC time."""
    if sequence < 1:
        raise ContractViolation("event sequence must be positive")
    return event_cls(sequence=sequence, timestamp=utc_now(), payload=payload)


class EventSequencer:
    """Numbers the events of one outgoing stream 1, 2, 3, ..."""

    def __init__(self) -> None:
        self._last = 0

    @property
    def last(self) -> int:
        return self._last

    def next(self, event_cls: EventClass, payload: Any = None) -> BaseEvent[Any]:  # noqa: ANN401
        self._last += 1
        return make_event(event_cls, self._last, payload)


def encode_ndjson(event: BaseEvent[Any]) -> bytes:
    """One NDJSON line, including the trailing newline."""
    return (event.to_json(separators=(",", ":")) + "\n").encode("utf-8")


def encode_sse(event: BaseEvent[Any]) -> str:
    """One Server-Sent Events message, including the terminating blank line."""
    return f"data: {event.to_json(separators=(',', ':'))}\n\n"


# --------------------------------------------------------------------------- decoding


def decode_event(raw: str | bytes, schema: StreamSchema) -> BaseEvent[Any]:
    """Parse and validate one event against ``schema``; raises :class:`ContractViolation`."""
    if isinstance(raw, bytes):
        try:
            raw = raw.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ContractViolation(f"{schema.name}: event is not valid UTF-8") from error
    try:
        data = json.loads(raw)
    except ValueError as error:
        raise ContractViolation(f"{schema.name}: event is not valid JSON") from error
    if not isinstance(data, dict):
        raise ContractViolation(f"{schema.name}: event must be a JSON object")

    raw_type, sequence, timestamp, payload = (
        data.get("type"),
        data.get("sequence"),
        data.get("timestamp"),
        data.get("payload"),
    )
    if (
        not isinstance(raw_type, str)
        or not isinstance(sequence, int)
        or isinstance(sequence, bool)
        or not isinstance(timestamp, str)
        or not isinstance(payload, dict)
    ):
        raise ContractViolation(
            f"{schema.name}: event needs string type, integer sequence, string timestamp "
            "and object payload"
        )
    try:
        event_type = EventType(raw_type)
    except ValueError as error:
        raise ContractViolation(f"{schema.name}: unknown event type {raw_type!r}") from error

    event_cls, dto_cls = schema.resolve(event_type)
    return event_cls(
        sequence=sequence,
        timestamp=parse_timestamp(timestamp),
        payload=None if dto_cls is None else _build_dto(dto_cls, payload, schema.name, event_type),
    )


def _build_dto(dto_cls: type, payload: dict[str, Any], stream: str, event_type: EventType) -> Any:  # noqa: ANN401
    """Instantiate ``dto_cls`` from ``payload``: required fields must be present and well typed.

    Unknown extra fields are ignored so a producer may add optional data without breaking older
    consumers (additive evolution of a contract is backward compatible).
    """
    hints = typing.get_type_hints(dto_cls)
    values: dict[str, Any] = {}
    for field_ in fields(dto_cls):
        if field_.name not in payload:
            if field_.default is MISSING and field_.default_factory is MISSING:
                raise ContractViolation(
                    f"{stream}: {event_type.value} payload is missing required field "
                    f"{field_.name!r}"
                )
            continue
        value = payload[field_.name]
        if not _matches(hints[field_.name], value):
            raise ContractViolation(
                f"{stream}: {event_type.value} payload field {field_.name!r} must be "
                f"{hints[field_.name]}, got {type(value).__name__}"
            )
        values[field_.name] = value
    return dto_cls(**values)


def _matches(expected: Any, value: Any) -> bool:  # noqa: ANN401
    origin = typing.get_origin(expected)
    if origin in (Union, types.UnionType):
        return any(_matches(option, value) for option in typing.get_args(expected))
    if expected is type(None):
        return value is None
    if expected is bool:
        return isinstance(value, bool)
    if expected is int:
        return isinstance(value, int) and not isinstance(value, bool)
    if expected is float:
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected is str:
        return isinstance(value, str)
    if is_dataclass(expected):
        return isinstance(value, dict)
    return True


# --------------------------------------------------------------------------- stream reading


class SequenceValidator:
    """Checks the lifecycle rules of one incoming stream.

    * sequence numbers are 1, 2, 3, ... without gaps
    * the first event is ``stream_started``
    * ``stream_started`` is sent once
    """

    def __init__(self, stream: str, *, require_stream_started: bool = True) -> None:
        self._stream = stream
        self._require_started = require_stream_started
        self._expected = 1
        self._started = False

    def check(self, event: BaseEvent[Any]) -> None:
        if event.sequence != self._expected:
            raise ContractViolation(
                f"{self._stream}: event sequence must be {self._expected}, got {event.sequence}"
            )
        if event.type == EventType.START_STREAM:
            if self._started:
                raise ContractViolation(f"{self._stream}: stream_started may only be sent once")
            self._started = True
        elif self._require_started and not self._started:
            raise ContractViolation(
                f"{self._stream}: stream_started must be the first event, got {event.type.value}"
            )
        self._expected += 1


class NdjsonDecoder:
    """Incremental NDJSON decoder for byte chunks of arbitrary size."""

    def __init__(self, schema: StreamSchema, *, validate_sequence: bool = True) -> None:
        self._schema = schema
        self._buffer = b""
        self._validator = SequenceValidator(schema.name) if validate_sequence else None

    def feed(self, chunk: bytes) -> Iterator[BaseEvent[Any]]:
        self._buffer += chunk
        while b"\n" in self._buffer:
            line, self._buffer = self._buffer.split(b"\n", 1)
            if line.strip():
                yield self._decode(line)

    def finish(self) -> Iterator[BaseEvent[Any]]:
        """Flush a final line that was not newline-terminated."""
        tail, self._buffer = self._buffer.strip(), b""
        if tail:
            yield self._decode(tail)

    def _decode(self, line: bytes) -> BaseEvent[Any]:
        event = decode_event(line, self._schema)
        if self._validator is not None:
            self._validator.check(event)
        return event


class SseDecoder:
    """Incremental Server-Sent Events decoder (``data:`` lines, blank line ends a message)."""

    def __init__(self, schema: StreamSchema, *, validate_sequence: bool = True) -> None:
        self._schema = schema
        self._buffer = b""
        self._data: list[str] = []
        self._validator = SequenceValidator(schema.name) if validate_sequence else None

    def feed(self, chunk: bytes) -> Iterator[BaseEvent[Any]]:
        self._buffer += chunk
        while b"\n" in self._buffer:
            raw_line, self._buffer = self._buffer.split(b"\n", 1)
            line = raw_line.decode("utf-8", errors="replace").rstrip("\r")
            if not line.strip():
                yield from self._flush()
            elif line.startswith("data:"):
                self._data.append(line.removeprefix("data:").strip())

    def finish(self) -> Iterator[BaseEvent[Any]]:
        tail = self._buffer.decode("utf-8", errors="replace").strip()
        self._buffer = b""
        if tail.startswith("data:"):
            self._data.append(tail.removeprefix("data:").strip())
        yield from self._flush()

    def _flush(self) -> Iterator[BaseEvent[Any]]:
        if not self._data:
            return
        raw, self._data = "\n".join(self._data), []
        event = decode_event(raw, self._schema)
        if self._validator is not None:
            self._validator.check(event)
        yield event


async def iter_events(
    byte_stream: AsyncIterable[bytes],
    schema: StreamSchema,
    *,
    framing: str = "ndjson",
    validate_sequence: bool = True,
) -> AsyncIterator[BaseEvent[Any]]:
    """Decode a stream of byte chunks into contract events.

    Closes ``byte_stream`` when iteration ends or is abandoned, so cancelling the consumer
    cancels the upstream connection.
    """
    if framing == "ndjson":
        decoder: NdjsonDecoder | SseDecoder = NdjsonDecoder(schema, validate_sequence=validate_sequence)
    elif framing == "sse":
        decoder = SseDecoder(schema, validate_sequence=validate_sequence)
    else:
        raise ValueError(f"unknown framing {framing!r}")
    try:
        async for chunk in byte_stream:
            for event in decoder.feed(chunk):
                yield event
        for event in decoder.finish():
            yield event
    finally:
        close = getattr(byte_stream, "aclose", None)
        if close is not None:
            await close()
