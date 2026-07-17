import json
from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime
from enum import Enum, StrEnum
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class EventType(StrEnum):
    HEARTBEAT = "heartbeat"
    START_STREAM = "stream_started"
    PARTIAL = "partial"
    COMPLETED = "completed"
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
            return value.isoformat()
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
            "payload": self._serialize_value(self.payload),
        }

    def to_json(self, **kwargs: Any) -> str:
        return json.dumps(self.to_dict(), **kwargs)



