import json
from dataclasses import asdict, dataclass, is_dataclass
from datetime import UTC, datetime
from enum import Enum, StrEnum
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class ContractViolation(ValueError):
    """A stream message does not conform to the project stream contract."""


def utc_now() -> datetime:
    """Timezone-aware "now" in UTC; the only clock stream events should be stamped with."""
    return datetime.now(UTC)


def format_timestamp(value: datetime) -> str:
    """Wire form of an event timestamp: UTC ISO-8601 with microseconds and a ``Z`` suffix.

    Naive datetimes are interpreted as UTC. Every consumer requires the ``Z`` form, so the
    contract (not each service) owns this formatting.
    """
    if value.tzinfo is not None:
        value = value.astimezone(UTC)
    return value.replace(tzinfo=None).isoformat(timespec="microseconds") + "Z"


def parse_timestamp(value: str) -> datetime:
    """Inverse of :func:`format_timestamp`; the wire form must be UTC and end with ``Z``."""
    if not value.endswith("Z"):
        raise ContractViolation(f"timestamp must be UTC ISO-8601 ending in Z: {value!r}")
    try:
        return datetime.fromisoformat(value.removesuffix("Z") + "+00:00")
    except ValueError as error:
        raise ContractViolation(f"timestamp is not ISO-8601: {value!r}") from error


class EventType(StrEnum):
    HEARTBEAT = "heartbeat"
    START_STREAM = "stream_started"
    PARTIAL = "partial"
    UTTERANCE = "utterance"
    COMPLETED = "completed"
    INPUT_COMPLETED = "input_completed"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class BaseEvent(Generic[T]):
    type: EventType
    sequence: int
    timestamp: datetime
    payload: T

    @staticmethod
    def _serialize_value(value: Any) -> Any:
        if isinstance(value, datetime):
            return format_timestamp(value)
        if isinstance(value, Enum):
            return value.value
        if is_dataclass(value) and not isinstance(value, type):
            return {
                key: BaseEvent._serialize_value(item)
                for key, item in asdict(value).items()
            }
        if isinstance(value, dict):
            return {
                str(key): BaseEvent._serialize_value(item)
                for key, item in value.items()
            }
        if isinstance(value, (list, tuple, set)):
            return [BaseEvent._serialize_value(item) for item in value]
        return value

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self._serialize_value(self.type),
            "sequence": self.sequence,
            "timestamp": self._serialize_value(self.timestamp),
            # The envelope requires ``payload`` to be an object; payload-less events send ``{}``.
            "payload": {} if self.payload is None else self._serialize_value(self.payload),
        }

    def to_json(self, **kwargs: Any) -> str:
        return json.dumps(self.to_dict(), **kwargs)
